import asyncio
import socket
from .http_parse import HttpRequestParser
from .http_response import make_response
from .asgi import ASGIRequest, ASGIResponse


class Session:
    def __init__(self, client_socket, address, app):
        self.loop = asyncio.get_event_loop()
        self.client_socket = client_socket
        self.address = address
        self.app = app
        self.trigger_run_asgi = asyncio.Event()
        self.parser = HttpRequestParser(self)
        self.request = ASGIRequest()
        self.response = ASGIResponse()

    async def run(self):
        self.loop.create_task(self.run_asgi())
        while True:
            if self.response.is_complete:
                break
            data = await self.loop.sock_recv(self.client_socket, 1024)
            print(f"Received {data}")
            self.parser.feed_data(data)
        self.client_socket.close()
        print(f"Socket with {self.address} closed.")

    # ASGI Server protocol methods
    async def run_asgi(self):
        await self.trigger_run_asgi.wait()
        await self.app(self.request.to_scope(), self.receive, self.send)

    async def receive(self):
        while True:
            await self.request.trigger_more_body.wait()
            return self.request.to_event()

    async def send(self, event):
        self.response.feed_event(event)
        if self.response.is_complete:
            resp_http = self.response.to_http()
            await self.loop.sock_sendall(self.client_socket, resp_http)
            print("Response sent.")

    # HTTP parser callbacks
    def on_url(self, url):
        print(f"Received url: {url}")
        self.request.http_method = self.parser.http_method.decode("utf-8")
        self.request.path = url.decode("utf-8")

    def on_header(self, name: bytes, value: bytes):
        print(f"Received header: ({name}, {value})")
        self.request.headers.append((name, value))

    def on_headers_complete(self):
        print("Received all headers.")
        self.trigger_run_asgi.set()

    def on_body(self, body: bytes):
        print(f"Received body: {body}")
        self.request.body_buffer += body
        self.request.trigger_more_body.set()

    def on_message_complete(self):
        print("Received request completely.")
        self.request.last_body = True
        self.request.trigger_more_body.set()


class ASGIServer:
    def __init__(self, host: str, port: int, app):
        self.host = host
        self.port = port
        self.app = app

    async def serve_forever(self):
        server_socket = socket.socket()
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        server_socket.setblocking(False)

        loop = asyncio.get_event_loop()
        while True:
            client_socket, address = await loop.sock_accept(server_socket)
            print(f"Socket established with {address}.")
            session = Session(client_socket, address, self.app)
            loop.create_task(session.run())
