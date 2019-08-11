import json
import base64

from aligi import types


class HTTPRequest:
    """解析阿里云API网关传递的数据"""

    def __init__(self, event: str, context: types.FCContext):
        self.context = context
        self.event = json.loads(event)
        self._header = {
            "CONTENT-TYPE": "text/plain",
            "CONTENT-LENGTH": 0,
        }
        self._header.update({k.upper(): v for k, v in self.event['headers'].items()})

    @property
    def path(self) -> str:
        return self.event['path']

    @property
    def method(self) -> str:
        return self.event['httpMethod'].upper()

    @property
    def header(self) -> dict:
        return self._header

    @property
    def query(self) -> dict:
        return self.event['queryParameters']

    @property
    def query_string(self) -> str:
        return "?" + "&".join([f"{k}={v}" for k, v in self.query.items()])

    @property
    def param(self) -> dict:
        return self.event['pathParameters']

    @property
    def body(self) -> bytes:
        if self.event['isBase64Encoded']:
            return base64.b64decode(self.event['body'])
        return self.event['body'].encode("UTF-8")
