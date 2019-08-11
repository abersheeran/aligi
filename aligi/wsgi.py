import io
import json
import typing
import base64

from aligi.types import FCContext, WSGIApp
from aligi.core import HTTPRequest


class BodyTypeError(Exception):
    pass


class ErrorWriter:
    """处理错误日志则继承于此"""

    def flush(self) -> None:
        pass

    def write(self, msg: str) -> None:
        pass

    def writelines(self, seq: str) -> None:
        pass


class WSGI:

    def __init__(self, event: str, context: FCContext):
        self.request = HTTPRequest(event, context)
        self.environ = {
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
            "wsgi.input": io.BytesIO(self.request.body),
            "wsgi.errors": self.errors,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": True,
        }
        self.update_environ()
        self.raw_data = {}

    @property
    def errors(self) -> ErrorWriter:
        """
        如果需要自定义处理错误日志, 则需要覆盖此属性
        """
        return ErrorWriter()

    def update_environ(self) -> None:
        self.environ.update({
            "REQUEST_METHOD": self.request.method,
            "SCRIPT_NAME": "",
            "PATH_INFO": self.request.path,
            "QUERY_STRING": self.request.query_string,
            "CONTENT_TYPE": self.request.header['CONTENT-TYPE'],
            "CONTENT_LENGTH": self.request.header['CONTENT-LENGTH'],
            "SERVER_NAME": "127.0.0.1",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.1",
        })
        self.environ.update({f"HTTP_{k}": v for k, v in self.request.header.items()})

    def start_response(
        self,
        status: str,
        headers: typing.Iterable[typing.Tuple[str, str]],
        exc_info: str = ""
    ) -> None:
        """
        WSGI 标准 start_response, 传递状态码与HTTP头部
        """
        self.raw_data.update({
            "statusCode": int(status[:3]),
            "headers": {
                header[0]: header[1] for header in headers
            },
        })

    def mount(self, wsgi: WSGIApp) -> None:
        """挂载并调用标准 WSGI Application"""
        body: typing.Iterable = wsgi(self.environ, self.start_response)
        body = b"".join(body)
        self.raw_data.update({
            "body": base64.b64encode(body).decode("utf8"),
            "isBase64Encoded": True
        })

    def get_response(self) -> str:
        """返回 JSON 字符串的结果"""
        return json.dumps(self.raw_data)
