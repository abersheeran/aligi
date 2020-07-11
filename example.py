import json

from bottle import Bottle, request
from aligi import WSGI

app = Bottle()


@app.route("/")
def hello_world():
    print(request.environ)
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
                    "headers": {"Content-Type": "text/plain", "X-Only-Test": "aligi"},
                    "queryParameters": {},
                    "pathParameters": {},
                    "body": "",
                    "isBase64Encoded": False,
                }
            ),
            None,
        )
    )
