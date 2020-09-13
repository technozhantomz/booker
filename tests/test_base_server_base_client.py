import pytest
import aiohttp

from finteh_proto.server import BaseServer
from finteh_proto.client import BaseClient


@pytest.mark.asyncio
async def test_base_ping_pong():
    server = BaseServer()
    await server.start()

    client = BaseClient()
    await client.connect("0.0.0.0", 8080)

    call_result = await client.ping()
    assert call_result == "pong"

    await client.disconnect()
    await server.stop()


@pytest.mark.asyncio
async def test_base_status():
    server = BaseServer()
    await server.start()

    r = await aiohttp.ClientSession().get("http://0.0.0.0:8080/status")
    assert r.status == 200
    assert await r.text() == "Ok"

    await server.stop()
