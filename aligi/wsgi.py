import io
import json
import base64
from typing import Dict, Any, Union, Iterable, Tuple

from aligi.types import FCContext, WSGIApp, Environ, StartResponse
from aligi.core import HTTPRequest


class ErrorWriter:
    """处理错误日志则继承于此"""

    def flush(self) -> None:
        pass

    def write(self, msg: str) -> None:
        pass

    def writelines(self, seq: str) -> None:
        pass


def build_environ(
    request: HTTPRequest, errors: ErrorWriter = ErrorWriter()
) -> Dict[str, Any]:
    environ = {
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(request.body),
        "wsgi.errors": errors,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": True,
    }

    environ.update(
        {
            "REQUEST_METHOD": request.method,
            "SCRIPT_NAME": "",
            "PATH_INFO": request.path,
            "QUERY_STRING": request.query_string,
            "CONTENT_TYPE": request.header["CONTENT-TYPE"],
            "CONTENT_LENGTH": request.header["CONTENT-LENGTH"],
            "SERVER_NAME": "127.0.0.1",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.0",
        }
    )
    environ.update({f"HTTP_{k}": v for k, v in request.header.items()})
    return environ


def create_start_response(data: dict) -> StartResponse:
    """
    绑定 start_response 到 data
    """

    def start_response(
        status: str, headers: Iterable[Tuple[str, str]], exc_info: str = "",
    ) -> None:
        """
        WSGI 标准 start_response, 传递 status code 与 headers
        """
        data.update(
            {
                "statusCode": int(status[:3]),
                "headers": {header[0]: header[1] for header in headers},
            }
        )

    return start_response


class WSGI:
    """
    包裹 WSGI application, 使其同时可接受 WSGI 调用/阿里云 API 网关调用
    """

    def __init__(self, app: WSGIApp, errors: ErrorWriter = ErrorWriter()):
        self.app = app
        self.errors = errors

    def __call__(
        self,
        event_or_environ: Union[str, Environ],
        context_or_start_response: Union[FCContext, StartResponse],
    ) -> Union[Iterable[Union[str, bytes]], str]:
        if not isinstance(event_or_environ, str):  # WSGI 接口调用
            return self.app(event_or_environ, context_or_start_response)
        # 处理 API 网关调用
        request = HTTPRequest(event_or_environ, context_or_start_response)
        resp_dict = {}
        environ = build_environ(request, self.errors)
        start_response = create_start_response(resp_dict)
        body: typing.Iterable = self.app(environ, start_response)
        resp_dict.update(
            {
                "body": base64.b64encode(b"".join(body)).decode("utf8"),
                "isBase64Encoded": True,
            }
        )
        return json.dumps(resp_dict)
