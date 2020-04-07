import asyncio
from dataclasses import dataclass, field
from typing import List, Tuple
from .http_response import make_response


@dataclass
class ASGIRequest:
    http_method: str = ""
    path: str = ""
    headers: List[Tuple[bytes, bytes]] = field(default_factory=lambda: [])
    body_buffer: bytes = b""
    trigger_more_body: asyncio.Event = asyncio.Event()
    last_body: bool = False

    def to_scope(self):
        path_parts = self.path.split("?")
        scope = {
            "type": "http",
            "asgi": {"version": "2.1", "spec_version": "2.1"},
            "http_version": "1.1",
            "method": self.http_method,
            "scheme": "http",
            "path": path_parts[0],
            "query_string": path_parts[1] if len(path_parts) > 1 else "",
            "headers": self.headers,
        }
        return scope

    def to_event(self):
        event = {
            "type": "http.request",
            "body": self.body_buffer,
            "more_body": not self.last_body,
        }
        self.body_buffer = b""
        return event


@dataclass
class ASGIResponse:
    status_code: int = 200
    headers: List[Tuple[bytes, bytes]] = field(default_factory=lambda: [])
    body: bytes = b""
    is_complete: bool = False

    def to_http(self):
        return make_response(self.status_code, self.headers, self.body)

    def feed_event(self, event):
        if event["type"] == "http.response.start":
            self.status_code = event["status"]
            self.headers = event["headers"]
        elif event["type"] == "http.response.body":
            self.body += event.get("body", b"")
            if not event.get("more_body", False):
                self.is_complete = True
