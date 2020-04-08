from typing import Callable
from dataclasses import dataclass
from .request import Request
from .response import PlainTextResponse, BaseResponse


class ASGIApplication:
    def __init__(self):
        self.path_operations = dict()

    def _register_path_operation(
        self, path: str, http_method: str, func: Callable
    ):
        po = PathOperation(path, http_method)
        self.path_operations[po] = func

    def _create_register_decorator(self, path: str, http_method: str):
        def decorator(func: Callable):
            self._register_path_operation(path, http_method, func)
            return func

        return decorator

    def get(self, path: str):
        return self._create_register_decorator(path, "GET")

    def post(self, path: str):
        return self._create_register_decorator(path, "POST")

    async def __call__(self, scope, receive, send):
        po = PathOperation(scope["path"], scope["method"])
        func = self.path_operations.get(po)
        if func is None:
            response = PlainTextResponse(status_code=404)
        else:
            request = Request.from_scope(scope)
            await request.fetch_body(receive)
            ret = await func(request=request)
            if isinstance(ret, BaseResponse):
                response = ret
            else:
                response = PlainTextResponse(body=ret)
        await send(response.get_response_start_event())
        await send(response.get_response_body_event())


@dataclass(frozen=True, eq=True)
class PathOperation:
    path: str
    http_method: str
