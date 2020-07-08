from aiohttp import web
from aiohttp.web import Application
from aiohttp.test_utils import TestClient, TestServer

from booker.http.handlers import status as http_status_handler


async def test_http_status_handler() -> None:
    app = Application()

    app.add_routes([web.get('/', http_status_handler)])

    server = TestServer(app)
    client = TestClient(server)

    await client.start_server()

    response = await client.get('/')

    assert response.status == 200
    assert await response.text() == 'Ok'
