import typing
from typing import (
    TypeVar,
    Generic,
    MutableMapping,
    Any,
    Iterable,
    Callable,
    Tuple,
    Union,
)


def print_type(obj: typing.Any, suffix: str = ""):
    try:
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue
            print(f"{suffix}- Key {key}: {type(value)}", flush=True)
            print_type(value, "  ")
    except AttributeError:
        pass


class Credentials(Generic[TypeVar("T")]):
    access_key_id: str
    access_key_secret: str
    security_token: str


class ServiceMeta(Generic[TypeVar("T")]):
    name: str
    log_project: str
    log_store: str
    qualifier: str
    version_id: str


class FunctionMeta(Generic[TypeVar("T")]):
    name: str
    handler: str
    memory: int
    timeout: int
    initializer: str
    initialization_timeout: int


class FCContext(Generic[TypeVar("T")]):
    account_id: str
    request_id: str
    credentials: Credentials
    function: FunctionMeta
    service: ServiceMeta
    region: str


# WSGI: view PEP3333
Environ = MutableMapping[str, Any]
StartResponse = Callable[[str, Iterable[Tuple[str, str]]], None]
WSGIApp = Callable[[Environ, StartResponse], Iterable[Union[str, bytes]]]
