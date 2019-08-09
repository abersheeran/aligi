import json
import typing
import base64

from aligi.types import FCContext, WSGIApp
from aligi.core import Request


class BodyTypeError(Exception):
    pass


class WSGI:

    def __init__(self, event: str, context: FCContext):
        self.request = Request(event, context)
        self.set_environ()
        self.data = {}

    def set_environ(self):
        self.environ = {
            "REQUEST_METHOD": self.request.method,
            "SCRIPT_NAME": "",
            "PATH_INFO": self.request.path,
            "QUERY_STRING": self.request.query_string,
            "CONTENT_TYPE": self.request.header['CONTENT-TYPE'],
            "CONTENT_LENGTH": self.request.header['CONTENT-LENGTH'],
            "SERVER_NAME": "127.0.0.1",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.1",
        }
        self.environ.update({f"HTTP_{k}": v for k, v in self.request.header})

    def start_response(self, status: str, headers: typing.Iterable(typing.Tuple(str, str)), exc_info: str = ""):
        self.data.update({
            "statusCode": int(status[:3]),
            "headers": {
                header[0]: header[1] for header in headers
            },
        })

    def mount(self, wsgi: WSGIApp):
        body = wsgi(self.environ, self.start_response)
        if isinstance(body, bytes):
            self.data.update({
                "body": base64.b64encode(b"".join(body)),
                "isBase64Encoded": True
            })
        elif isinstance(body, str):
            self.data.update({
                "body": body,
                "isBase64Encoded": False
            })
        else:
            raise BodyTypeError(f"body type: {type(body)}")

    def get_response(self):
        return json.dumps(self.data)
