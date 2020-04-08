from typing import Dict
from dataclasses import dataclass


@dataclass
class Request:
    query: Dict[str, str]
    headers: Dict[bytes, bytes]
    body: bytes = b""

    @classmethod
    def from_scope(cls, scope: Dict):
        query = {}
        if scope["query_string"]:
            qs = scope["query_string"]
            query = dict(entry.split("=") for entry in qs.split("&"))
        headers = dict(scope["headers"])
        return cls(query, headers)

    async def fetch_body(self, receive):
        while True:
            event = await receive()
            self.body += event["body"]
            if not event["more_body"]:
                break
