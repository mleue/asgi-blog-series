import asyncio
from asgi.server import serve_forever


if __name__ == "__main__":
    asyncio.run(serve_forever("127.0.0.1", 5000))
