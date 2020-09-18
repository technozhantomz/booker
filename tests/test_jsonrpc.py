"""Some example how to implement your wsjsonrpc- clients and servers with methods
from finteh_proto.BaseSever and finteh_proto.BaseClient"""

import pytest

from finteh_proto.server import BaseServer, JsonRpcRequest
from finteh_proto.dto import *
from finteh_proto.client import BaseClient
from uuid import uuid4


@dataclass
class TestInternalDTO(DataTransferClass):
    test_amount: int


@dataclass
class TestDTORequest(DataTransferClass):
    test_uuid: UUID
    test_internal_dto: TestInternalDTO


@dataclass
class TestDTOResponse(DataTransferClass):
    processed: bool


class ExampleServer(BaseServer):
    def __init__(self, host="0.0.0.0", port=8080, ctx=None):
        super(ExampleServer, self).__init__(host, port, ctx)
        self.add_methods(("", self.test_method),
                         ("",  self.test_server_fail))
        pass

    async def test_method(self, request: JsonRpcRequest):
        req_data = TestDTORequest.Schema().load(request.msg[1]["params"])
        assert req_data.test_internal_dto.test_amount == 10
        response = TestDTOResponse(processed=True)
        return self.jsonrpc_response(request, response)

    async def test_server_fail(self, request: JsonRpcRequest):
        try:
            1 / 0
        except Exception as ex:
            response = ex
        return self.jsonrpc_response(request, response)


class ExampleClient(BaseClient):
    def __init__(
        self,
        ctx=None,
        host="0.0.0.0",
        port=8080,
    ):
        super().__init__(ctx, host, port)

    @BaseClient.safe_call_execute
    async def test_request(self, test_dto: TestDTORequest) -> tuple:
        return "test_method", test_dto, TestDTOResponse

    @BaseClient.safe_call_execute
    async def test_client_side_error(self, test_dto):
        1/0
        return "test_method", test_dto, TestDTOResponse

    @BaseClient.safe_call_execute
    async def test_server_fail_request(self, test_dto: TestDTORequest) -> tuple:
        return "test_server_fail", test_dto, TestDTOResponse


@pytest.mark.asyncio
async def test_jsonrpc_request_success():
    s = ExampleServer()
    await s.start()
    c = ExampleClient()

    start_dto = TestDTORequest(test_uuid=uuid4(), test_internal_dto=TestInternalDTO(test_amount=10))

    r = await c.test_request(start_dto)
    assert isinstance(r, TestDTOResponse)

    await s.stop()


@pytest.mark.asyncio
async def test_jsonrpc_client_error():
    s = ExampleServer()
    await s.start()
    c = ExampleClient()

    start_dto = TestDTORequest(test_uuid=uuid4(), test_internal_dto=TestInternalDTO(test_amount=10))

    r = await c.test_client_side_error(start_dto)
    print(r)
    assert isinstance(r, JSONRPCError)
    assert r.message == 'division by zero'

    await s.stop()


@pytest.mark.asyncio
async def test_jsonrpc_server_error():
    s = ExampleServer()
    await s.start()
    c = ExampleClient()

    start_dto = TestDTORequest(test_uuid=uuid4(), test_internal_dto=TestInternalDTO(test_amount=10))

    r = await c.test_server_fail_request(start_dto)
    assert isinstance(r, JSONRPCError)
    assert r.message == 'Internal Error'
    assert r.code == -32603

    await s.stop()
