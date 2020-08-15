import io
import json
import base64
import typing
from types import TracebackType
from typing import (
    Any,
    Iterable,
    Callable,
    Tuple,
    Dict,
    MutableMapping,
    Type,
    Optional,
)

__version__ = (1, 1, 0)


#########################################
# Context 类型定义
# https://help.aliyun.com/document_detail/158208.html#title-88g-cnq-6mb
#########################################


def print_type(obj: Any, suffix: str = ""):
    """
    在阿里云 Serverless 中查看类型所用
    """
    try:
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue
            print(f"{suffix}- Key {key}: {type(value)}", flush=True)
            print_type(value, "  ")
    except AttributeError:
        pass


class Credentials:
    access_key_id: str
    access_key_secret: str
    security_token: str


class ServiceMeta:
    name: str
    log_project: str
    log_store: str
    qualifier: str
    version_id: str


class FunctionMeta:
    name: str
    handler: str
    memory: int
    timeout: int
    initializer: str
    initialization_timeout: int


class FCContext:
    account_id: str
    request_id: str
    credentials: Credentials
    function: FunctionMeta
    service: ServiceMeta
    region: str


# WSGI: view PEP3333
ExcInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]

Environ = MutableMapping[str, Any]

StartResponse = Callable[[str, Iterable[Tuple[str, str]], Optional[ExcInfo]], None]

WSGIApp = Callable[[Environ, StartResponse], Iterable[bytes]]


class HTTPRequest:
    """
    包装阿里云 API 网关传入参数
    """

    def __init__(self, event: bytes, context: FCContext):
        self.context = context
        self.event = json.loads(event)

    @property
    def method(self) -> str:
        return self.event["httpMethod"].upper()

    @property
    def path(self) -> str:
        return self.event["path"]

    @property
    def header(self) -> Dict[str, str]:
        return {k.lower(): v for k, v in self.event["headers"].items()}

    @property
    def query(self) -> Dict[str, Any]:
        return self.event["queryParameters"]

    @property
    def param(self) -> Dict[str, Any]:
        return self.event["pathParameters"]

    @property
    def body(self) -> bytes:
        if self.event["isBase64Encoded"]:
            return base64.b64decode(self.event["body"])
        return self.event["body"].encode("utf8")


class Errors:
    """
    wsgi.errors
    """

    def flush(self) -> None:
        pass

    def write(self, msg: str) -> None:
        pass

    def writelines(self, seq: str) -> None:
        pass


def build_environ(request: HTTPRequest, errors: Errors) -> Dict[str, Any]:
    """
    参考 https://www.python.org/dev/peps/pep-3333/ 构建 environ
    """
    headers = {
        f"HTTP_{k.upper().replace('-','_')}": v for k, v in request.header.items()
    }
    environ = {
        # 保持与阿里云函数计算 HTTP 触发器的一致
        "fc.context": request.context,
        "fc.request_uri": request.path,
        # WSGI 标准值
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(request.body),
        "wsgi.errors": errors,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": True,
        "SERVER_NAME": "127.0.0.1",
        "SERVER_PORT": "80",
        "SERVER_PROTOCOL": "HTTP/1.0",
        "REQUEST_METHOD": request.method,
        "SCRIPT_NAME": "",
        "PATH_INFO": request.path,
        "QUERY_STRING": "?" + "&".join([f"{k}={v}" for k, v in request.query.items()]),
        "CONTENT_TYPE": headers.pop("HTTP_CONTENT_TYPE", ""),
        "CONTENT_LENGTH": headers.pop("HTTP_CONTENT_LENGTH", ""),
    }
    environ.update(headers)
    return environ


def create_start_response(data: dict) -> StartResponse:
    """
    绑定 start_response 到 data
    """

    def start_response(
        status: str,
        headers: Iterable[Tuple[str, str]],
        exc_info: Tuple[
            Type[BaseException], BaseException, Optional[TracebackType]
        ] = None,
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
        if exc_info is not None:
            raise exc_info[1]

    return start_response


class WSGI:
    """
    包裹 WSGI application, 使其同时可接受 WSGI 调用/阿里云 API 网关调用
    """

    def __init__(self, app: WSGIApp, errors: Errors = Errors()):
        self.app = app
        self.errors = errors

    @typing.overload
    def __call__(self, event: bytes, context: FCContext) -> str:
        """
        阿里云 API 网关触发器
        """

    @typing.overload
    def __call__(
        self, environ: Environ, start_response: StartResponse
    ) -> Iterable[bytes]:
        """
        阿里云 HTTP 触发器: WSGI 协议
        """

    def __call__(self, event_or_environ, context_or_start_response):
        if not isinstance(event_or_environ, bytes):  # WSGI 接口调用
            return self.app(event_or_environ, context_or_start_response)
        # 处理 API 网关调用
        request = HTTPRequest(event_or_environ, context_or_start_response)
        resp_dict: Dict[str, Any] = {}
        environ = build_environ(request, self.errors)
        start_response = create_start_response(resp_dict)
        body: Iterable[bytes] = [block for block in self.app(environ, start_response)]

        resp_dict.update(
            {
                "body": base64.b64encode(b"".join(body)).decode("utf8"),
                "isBase64Encoded": True,
            }
        )
        return json.dumps(resp_dict)
