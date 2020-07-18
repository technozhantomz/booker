from typing import List, Generator
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
    streams: List[asyncio.Task]
    new_streams: List[asyncio.Task]
    new_stream: asyncio.Event


    def __init__(self) -> None:
        super().__init__()

        self.streams = []
        self.new_streams = []
        self.new_stream = asyncio.Event()
    

    def add_stream(self, stream: WebSocketResponse) -> asyncio.Task:
        stream_poller = self.poll_stream(stream)
        stream_poller_task = asyncio.create_task(stream_poller)

        self.new_streams.append(stream_poller_task.__await__())
        self.new_stream.set()

        return stream_poller_task


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


    def __await__(self) -> Generator[None, None, None]:
        while True:
            streams = list(enumerate(self.streams)).reverse()

            if not streams and not self.new_streams:
                wait = self.new_stream.wait().__await__()

                while True:
                    try:
                        next = wait.send(None)
                    except (StopIteration, asyncio.CancelledError):
                        break

                    yield next

            self.new_stream.clear()
            self.streams.extend(self.new_streams)
            self.new_streams = []

            for number, stream in streams:
                try:
                    next = stream.send(None)
                except (StopIteration, asyncio.CancelledError):
                    self.streams.pop(number)

                    yield None

                    continue

                try:
                    yield next
                except asyncio.CancelledError as exception:
                    streams = list(enumerate(self.streams)).reverse()

                    for number, stream in streams:
                        try:
                            stream.throw(exception)
                        except (StopIteration, asyncio.CancelledError):
                            self.streams.pop(number)

                            yield None

                    raise


    async def poll(self) -> None:
        return await self
