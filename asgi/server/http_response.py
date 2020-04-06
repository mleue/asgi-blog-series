from typing import List, Tuple
import http


def create_status_line(status_code: int = 200):
    code = str(status_code).encode()
    code_phrase = http.HTTPStatus(status_code).phrase.encode()
    return b"HTTP/1.1 " + code + b" " + code_phrase + b"\r\n"


def format_headers(headers: List[Tuple[bytes, bytes]]):
    return b"".join([key + b": " + value + b"\r\n" for key, value in headers])


def make_response(
    status_code: int = 200,
    headers: List[Tuple[bytes, bytes]] = None,
    body: bytes = b"",
):
    if headers is None:
        headers = []
    if body:
        headers.append((b"Content-Length", str(len(body)).encode("utf-8")))
    content = [
        create_status_line(status_code),
        format_headers(headers),
        b"\r\n" if body else b"",
        body,
    ]
    return b"".join(content)
