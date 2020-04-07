from typing import List
import asyncio
from asgi.server import ASGIServer
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


@app.get("/")
async def root():
    print("hello from /")
    return {"hello": "world"}


class Model(BaseModel):
    id: int
    name: str


@app.post("/create")
async def create(i: Model):
    print("hello from /create")
    return f"created {i}"


if __name__ == "__main__":
    server = ASGIServer("127.0.0.1", 5000, app)
    asyncio.run(server.serve_forever())
