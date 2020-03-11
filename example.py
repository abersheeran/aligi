import json

from flask import Flask
from aligi import WSGI

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


# 阿里云无服务函数的入口
handler = WSGI(app)


if __name__ == "__main__":
    print(
        handler(
            json.dumps(
                {
                    "path": "/",
                    "httpMethod": "GET",
                    "headers": {"Content-Length": 0, "Content-Type": "text/plain"},
                    "queryParameters": {},
                    "pathParameters": {},
                    "body": "",
                    "isBase64Encoded": False,
                }
            ),
            None,
        )
    )
