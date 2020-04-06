import asyncio
import socket
from .http_parse import HttpRequestParser
from .http_response import make_response


class Session:
    def __init__(self, client_socket, address):
        self.loop = asyncio.get_event_loop()
        self.client_socket = client_socket
        self.address = address
        self.trigger_send_response = asyncio.Event()
        self.response_sent = False
        self.parser = HttpRequestParser(self)

    async def run(self):
        self.loop.create_task(self.send_response())
        while True:
            if self.response_sent:
                break
            data = await self.loop.sock_recv(self.client_socket, 1024)
            print(f"Received {data}")
            self.parser.feed_data(data)
        self.client_socket.close()
        print(f"Socket with {self.address} closed.")

    async def send_response(self):
        await self.trigger_send_response.wait()
        body = b"<html><body>Hello World</body></html>"
        response = make_response(status_code=200, headers=[], body=body)
        await self.loop.sock_sendall(self.client_socket, response)
        print("Response sent.")
        self.response_sent = True

    def on_url(self, url):
        print(f"Received url: {url}")

    def on_header(self, name: bytes, value: bytes):
        print(f"Received header: ({name}, {value})")

    def on_body(self, body: bytes):
        print(f"Received body: {body}")

    def on_message_complete(self):
        print("Received request completely.")
        self.trigger_send_response.set()


async def serve_forever(host, port):
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(1)
    server_socket.setblocking(False)

    loop = asyncio.get_event_loop()
    while True:
        client_socket, address = await loop.sock_accept(server_socket)
        print(f"Socket established with {address}.")
        session = Session(client_socket, address)
        loop.create_task(session.run())
