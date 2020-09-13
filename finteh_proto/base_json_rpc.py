from typing import Any, Optional
from uuid import UUID, uuid4
from marshmallow_dataclass import dataclass


class JSONRPCAPIResultAndError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class JSONRPCAPIParseError(Exception):
    def __init__(self, message: str, data: Optional[Any]) -> None:
        super().__init__(message, data)


class JSONRPCAPIInvalidRequest(Exception):
    def __init__(self, message: str, data: Optional[Any]) -> None:
        super().__init__(message, data)


class JSONRPCAPIMethodNotFound(Exception):
    def __init__(self, message: str, data: Optional[Any]) -> None:
        super().__init__(message, data)


class JSONRPCAPIInvalidParams(Exception):
    def __init__(self, message: str, data: Optional[Any]) -> None:
        super().__init__(message, data)


class JSONRPCAPIInternalError(Exception):
    def __init__(self, message: str, data: Optional[Any]) -> None:
        super().__init__(message, data)


class JSONRPCAPIServerError(Exception):
    def __init__(self, code: int, message: str, data: Optional[Any]) -> None:
        super().__init__(code, message, data)


@dataclass
class JSONRPCRequest:
    jsonrpc: str
    method: str
    id: UUID
    params: Optional[Any] = None


@dataclass
class JSONRPCRequestInternalParams:
    _coroutine_id: Optional[UUID] = None


@dataclass
class JSONRPCError:
    code: int
    message: str
    data: Optional[Any] = None


@dataclass
class JSONRPCResponse:
    jsonrpc: str
    result: Optional[Any]
    error: Optional[JSONRPCError]
    id: UUID
