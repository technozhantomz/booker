import json

from aiohttp_json_rpc import JsonRpcClient
from aiohttp_json_rpc.exceptions import RpcError

from aiohttp.client_exceptions import ClientConnectorError
from uuid import uuid4
from finteh_proto.dto import JSONRPCResponse, JSONRPCRequest, JSONRPCError
from finteh_proto.utils import get_logger


log = get_logger("JsonRpcClient")


class BaseClient(JsonRpcClient):
    def __init__(self, ctx=None, host="0.0.0.0", port=8080):
        super().__init__()
        self.ctx = ctx
        self._host = host
        self._port = port

    async def ping(self):
        """Just RPC string ping-pong"""
        call_result = await self.call("ping")
        return call_result

    @classmethod
    def safe_call_execute(cls, cli_request):
        async def process_call(self: BaseClient, *args, **kwargs):
            try:
                await self.connect(self._host, self._port)

                method_name, params, dto_response = await cli_request(
                    self, *args, **kwargs
                )
                assert dto_response
                req = JSONRPCRequest(
                    method=method_name, params=params.to_dump(), id=str(uuid4())
                )
                log.info(f"Sending request =>> {req}")
                call = json.loads(await self.call(**req))

                assert bool(call.get("error")) ^ bool(call.get("result"))
                assert req.id == call["id"]

                if call.get("error"):
                    result = JSONRPCError(
                        message=call["error"]["message"], code=call["error"]["code"]
                    )
                else:
                    dto = dto_response(**call["result"])
                    _result = JSONRPCResponse(
                        id=call["id"], result=dto.normalize(), error=None
                    )
                    result = _result.result

                log.info(f"Receiving request <== {result}")

            except ClientConnectorError as ex:

                result = JSONRPCError(
                    code=ex.args[1].errno,
                    message=f"Unable to connect ws server on {self._host}:{self._port}",
                )
            except RpcError as ex:
                result = JSONRPCError(code=ex.error_code, message=ex.message)
            except Exception as ex:
                result = JSONRPCError(code=1, message=str(ex))

            if self._ws:
                await self.disconnect()
            return result

        return process_call
