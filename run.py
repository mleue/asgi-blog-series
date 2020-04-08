from typing import List
import asyncio
from asgi.server import ASGIServer
from asgi.application import ASGIApplication, Request
from asgi.application.response import JSONResponse
from pydantic import BaseModel


app = ASGIApplication()


@app.get("/")
async def root(request: Request):
    print("hello from /")
    return {"hello": "world"}


@app.post("/create")
async def create(request: Request):
    print("hello from /create")
    return JSONResponse(body=f"created {request.body}")


if __name__ == "__main__":
    server = ASGIServer("127.0.0.1", 5000, app)
    asyncio.run(server.serve_forever())
