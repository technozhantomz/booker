from typing import AbstractSet, Awaitable
import asyncio
import logging

from aiohttp import ClientWebSocketResponse
from aiohttp.web import WebSocketResponse

from booker.jsonrpc_api import JSONRPCAPIsClient, JSONRPCAPIsServer


class WSJSONRPCAPIsClient(JSONRPCAPIsClient):
    stream: ClientWebSocketResponse


    def __init__(self, stream: ClientWebSocketResponse) -> None:
        super().__init__()

        self.stream = stream


    async def _message_send_parent_transport_1(self, request: str) -> str:
        await self.stream.send_str(request)

        response = await self.stream.receive_str()

        return response


class WSJSONRPCAPIsServer(JSONRPCAPIsServer):
    tasks: AbstractSet[Awaitable[None]]
    new_stream: asyncio.Event


    def __init__(self) -> None:
        super().__init__()

        self.tasks = {*()}
        self.new_stream = asyncio.Event()
    

    def add_stream(self, stream: WebSocketResponse) -> Awaitable[None]:
        stream_poller = asyncio.create_task(self.poll_stream(stream))
        self.tasks |= {stream_poller}

        self.new_stream.set()

        return stream_poller


    async def poll_stream(self, ws: WebSocketResponse) -> None:
        while True:
            try:
                request = await ws.receive_str()
            except BaseException as exception:
                logging.exception(exception)

                raise exception

            try:
                response = await self.message_dispatch(request)
            except BaseException as exception:
                logging.exception(exception)

                continue

            try:
                await ws.send_str(response)
            except BaseException as exception:
                logging.exception(exception)

                raise exception


    async def poll(self) -> None:
        self.new_task.clear()

        new_stream = self.new_stream.wait()
        self.tasks |= {asyncio.create_task(new_stream)}

        while True:
            tasks, self.tasks = self.tasks, {*()}
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED
            )

            self.tasks |= pending

            if new_stream in done:
                self.new_task.clear()

                new_stream = self.new_task.wait()
                self.tasks |= {asyncio.create_task(new_stream)}
