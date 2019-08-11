import json

from flask import Flask
from aligi.wsgi import WSGI
from aligi.types import FCContext

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


def handler(event: str, context: FCContext):
    """阿里云无服务函数的入口"""
    wsgi = WSGI(event, context)
    wsgi.mount(app)
    return wsgi.get_response()


if __name__ == "__main__":
    print(handler(json.dumps({
        "path": "/",
        "httpMethod": "GET",
        "headers": {
            "Content-Length": 0,
            "Content-Type": "text/plain"
        },
        "queryParameters": {},
        "pathParameters": {},
        "body": "",
        "isBase64Encoded": False
    }), None))
