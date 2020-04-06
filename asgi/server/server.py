import asyncio
import socket


async def handle_socket(client_socket):
    loop = asyncio.get_event_loop()
    while True:
        data = await loop.sock_recv(client_socket, 1024)
        print(f"Received {data}")
        if data == b"":
            break
        await loop.sock_sendall(client_socket, data)
    client_socket.close()


async def serve_forever(host, port):
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(1)
    server_socket.setblocking(False)

    loop = asyncio.get_event_loop()
    while True:
        client_socket, address = await loop.sock_accept(server_socket)
        print(f"Socket established with {address}.")
        loop.create_task(handle_socket(client_socket))
