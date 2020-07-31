from functools import partial
from decimal import Decimal
import asyncio

from aiopg.sa import create_engine as create_db_engine
from aiohttp import ClientWebSocketResponse, web
from aiohttp.web import Application, Request, WebSocketResponse
from aiohttp.test_utils import TestClient, TestServer

from booker.rpc.api import APIStream, api_method, api_client, api_server
from booker.rpc.ws_jsonrpc_api import WSJSONRPCAPIsClient, WSJSONRPCAPIsServer
from booker.gateway.dto import (
    OrderType,
    TxError,
    ValidateAddress,
    ValidatedAddress,
    GetDepositAddress,
    DepositAddress,
    NewInOrder,
    NewOutOrder
)
from booker.rpc.gateway.api import (
    AbstractGatewayBookerOrderAPI,
    AbstractGatewayBookerOrderAPIClient
)
from booker.frontend.dto import NewInOrder
from booker.http.handlers import new_in_order, get_order
from booker.app import AppContext


@api_server
class GatewayBookerOrderAPIServer(AbstractGatewayBookerOrderAPI):
    ...


class MockETHGatewayBookerOrderAPIClient(AbstractGatewayBookerOrderAPIClient):
    ...


class MockETHGatewayBookerOrderAPIServer(GatewayBookerOrderAPIServer):
    @api_method
    async def validate_address(
        self,
        args: ValidateAddress
    ) -> APIStream[ValidatedAddress, None]:
        yield ValidatedAddress(valid=True)


    @api_method
    async def get_deposit_address(
        self,
        args: GetDepositAddress
    ) -> APIStream[DepositAddress, None]:
        if args.out_tx_to is None:
            raise ValueError('Unknown address')

        if args.out_tx_to == 'kwaskoff':
            yield DepositAddress(tx_to='0x8901c9bF56581513a158eEf00794FBb0D698f2Ed')
        else:
            raise ValueError('Unknown address')


    @api_method
    async def new_in_order(self, args: NewInOrder) -> APIStream[None, None]:
        await self.order_requests.put(args)

        yield None


    @api_method
    async def new_out_order(self, args: NewOutOrder) -> APIStream[None, None]:
        await self.order_requests.put(args)

        yield None


class MockBTSGatewayBookerOrderAPIClient(AbstractGatewayBookerOrderAPIClient):
    ...


class MockBTSGatewayBookerOrderAPIServer(GatewayBookerOrderAPIServer):
    @api_method
    async def validate_address(
        self,
        args: ValidateAddress
    ) -> APIStream[ValidatedAddress, None]:
        yield ValidatedAddress(valid=True)


    @api_method
    async def get_deposit_address(
        self,
        args: GetDepositAddress
    ) -> APIStream[DepositAddress, None]:
        if args.out_tx_to is not None:
            raise ValueError('Unknown address')

        yield DepositAddress(tx_to='finteh-usdt')


    @api_method
    async def new_in_order(self, args: NewInOrder) -> APIStream[None, None]:
        yield None


    @api_method
    async def new_out_order(self, args: NewOutOrder) -> APIStream[None, None]:
        yield None


async def ws_rpc(
    server: WSJSONRPCAPIsServer,
    request: Request
) -> WebSocketResponse:
    stream = WebSocketResponse()

    await stream.prepare(request)

    task = server.add_stream(stream)

    await task

    return stream


class TestAppContext(AppContext):
    async def run(self) -> None:
        self.db_engine = await create_db_engine(
            host=self.config.db_host,
            port=self.config.db_port,
            user=self.config.db_user,
            password=self.config.db_password,
            database=self.config.db_database
        )

        apis_server = WSJSONRPCAPIsServer()

        eth_server = MockETHGatewayBookerOrderAPIServer()

        apis_server.api_register(eth_server)

        async def eth_gateway_client_ws_stream_constructor(
        ) -> ClientWebSocketResponse:
            http_client = TestClient(server)
            client_ws_stream = await http_client.ws_connect('/ws-rpc')

            return client_ws_stream

        eth_apis_client = WSJSONRPCAPIsClient(
            stream_constructor=eth_gateway_client_ws_stream_constructor
        )
        self.gateway_ws_clients['USDT'] = MockETHGatewayBookerOrderAPIClient(
            apis_client=eth_apis_client
        )

        bts_server = MockBTSGatewayBookerOrderAPIServer()

        apis_server.api_register(bts_server)

        async def bts_gateway_client_ws_stream_constructor(
        ) -> ClientWebSocketResponse:
            http_client = TestClient(server)
            client_ws_stream = await http_client.ws_connect('/ws-rpc')

            return client_ws_stream

        bts_apis_client = WSJSONRPCAPIsClient(
            stream_constructor=bts_gateway_client_ws_stream_constructor
        )
        self.gateway_ws_clients['FINTEH.USDT'] = MockBTSGatewayBookerOrderAPIClient(
            apis_client=bts_apis_client
        )

        self.http_app.add_routes([
            web.get('/ws-rpc', partial(ws_rpc, apis_server)),
            web.post('/orders', partial(new_in_order, self)),
            web.get('/orders/{order_id}', partial(get_order, self))
        ])

        server = TestServer(self.http_app)

        await server.start_server()

        client = TestClient(server)

        new_order = NewInOrder(
            in_tx_coin='USDT',
            in_tx_amount=Decimal('0.1'),
            out_tx_coin='FINTEH.USDT',
            out_tx_to='kwaskoff'
        )
        new_order_schema = NewInOrder.Schema()
        rq_payload = new_order_schema.dump(new_order)

        response = await client.post('/orders', json=rq_payload)

        assert response.status == 200
        await response.json()

        cancel_signal = asyncio.Event()

        try:
            await asyncio.wait({asyncio.create_task(cancel_signal.wait())})
        finally:
            self.db_engine.close()
            await self.db_engine.wait_closed()

            raise


async def test_order_api() -> None:
    context = TestAppContext()

    await context.run()
