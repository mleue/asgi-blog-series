import json
from typing import List, Tuple, Optional, Any


class BaseResponse:
    def __init__(
        self,
        status_code: int = 200,
        headers: Optional[List[Tuple[bytes, bytes]]] = None,
        body: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.headers = headers if headers is not None else []
        self.body = self.body_conversion(body) if body is not None else b""
        self.add_content_type_and_content_length()

    def add_content_type_and_content_length(self):
        header_names = {name for name, value in self.headers}
        if not b"Content-Type" in header_names:
            self.headers.append((b"Content-Type", self.content_type))
        if self.body and not b"Content-Length" in header_names:
            content_length = str(len(self.body)).encode("utf-8")
            self.headers.append((b"Content-Length", content_length))

    def get_response_start_event(self):
        return {
            "type": "http.response.start",
            "status": self.status_code,
            "headers": self.headers,
        }

    def get_response_body_event(self):
        return {
            "type": "http.response.body",
            "body": self.body,
            "more_body": False,
        }


class PlainTextResponse(BaseResponse):
    content_type = b"plain/text"

    @classmethod
    def body_conversion(cls, body):
        return body.encode("utf-8")


class HTMLResponse(BaseResponse):
    content_type = b"plain/html"

    @classmethod
    def body_conversion(cls, body):
        return body.encode("utf-8")


class JSONResponse(BaseResponse):
    content_type = b"application/json"

    @classmethod
    def body_conversion(cls, body):
        return json.dumps(body).encode("utf-8")
