import typing
from typing import TypeVar, Generic


def print_type(obj: typing.Any, suffix: str = ""):
    try:
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue
            print(f"{suffix}- Key {key}: {type(value)}", flush=True)
            print_type(value, "  ")
    except AttributeError:
        pass


class Credentials(Generic[TypeVar('T')]):

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        security_token: str
    ):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.security_token = security_token


class ServiceMeta(Generic[TypeVar('T')]):

    def __init__(
        self,
        service_name: str,
        log_project: str,
        log_store: str,
        qualifier: str,
        version_id: str
    ):
        self.name = service_name
        self.log_project = log_project
        self.log_store = log_store
        self.qualifier = qualifier
        self.version_id = version_id


class FunctionMeta(Generic[TypeVar('T')]):

    def __init__(
            self,
            name: str,
            handler: str,
            memory: int,
            timeout: int,
            initializer: str,
            initialization_timeout: int
    ):
        self.name = name
        self.handler = handler
        self.memory = memory
        self.timeout = timeout
        self.initializer = initializer
        self.initialization_timeout = initialization_timeout


class FCContext(Generic[TypeVar('T')]):

    def __init__(
        self,
        account_id: str,
        request_id: str,
        credentials: Credentials,
        function_meta: FunctionMeta,
        service_meta: ServiceMeta,
        region: str
    ):
        self.request_id = request_id
        self.credentials = credentials
        self.function = function_meta
        self.service = service_meta
        self.region = region
        self.account_id = account_id


WSGIApp = typing.Callable[
    [
        typing.Dict,
        typing.Callable[
            [
                str,
                typing.Iterable[typing.Tuple[str, str]]
            ], None
        ]
    ], typing.Iterable
]
