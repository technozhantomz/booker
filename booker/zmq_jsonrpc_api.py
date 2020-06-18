import logging

from aiozmq import ZmqStream

from booker.jsonrpc_api import JSONRPCAPIsClient, JSONRPCAPIsServer


class ZMQJSONRPCAPIsClient(JSONRPCAPIsClient):
    stream: ZmqStream


    def __init__(self, stream: ZmqStream) -> None:
        super().__init__()

        self.stream = stream


    async def _message_send_parent_transport_1(self, request: str) -> str:
        data_request = [request.encode('ascii')]

        self.stream.write(data_request)

        data_response = await self.stream.read()
        response = data_response[0]

        return response


class ZMQJSONRPCAPIsServer(JSONRPCAPIsServer):
    stream: ZmqStream


    def __init__(self, stream: ZmqStream) -> None:
        super().__init__()

        self.stream = stream


    async def poll(self) -> None:
        while True:
            try:
                data_request = await self.stream.read()
            except BaseException as exception:
                logging.exception(exception)

                raise exception

            try:
                request = data_request[0]
                response = await self.message_dispatch(request)
                data_response = [response.encode('ascii')]
            except BaseException as exception:
                logging.exception(exception)

                continue

            try:
                self.stream.write(data_response)
            except BaseException as exception:
                logging.exception(exception)

                raise exception
