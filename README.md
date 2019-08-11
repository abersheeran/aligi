# aligi

Aliyun Gateway Interface

为无服务函数计算作为阿里云 API 后端运行提供转析。

## 为什么会有这个库？

使用 Flask，Django 等支持标准 WSGI 协议的 Web 框架创建无服务函数时，使用HTTP触发器才能让它们正常运行。

但如果想使用无服务函数作为阿里云 API 网关的后端时，则无法直接使用这些函数，只能通过网络调用，这显然是不够高效、并且费钱的。

## 如何安装

在项目根目录下执行

```
pip install -t . aligi
```

## 如何使用

以下为一个最小的 Flask 样例

```python
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
```

其中`app`可以是任意一个标准 WSGI Application。

在 Django 项目中，它一般在项目的`wsgi.py`里。

