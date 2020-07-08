import pytest

import asyncio
from uuid import uuid4
from decimal import Decimal
import logging

import zmq
from aiozmq import create_zmq_stream

from booker.dto import Amount
from booker.api import APIStream, api_method
from booker.zmq_jsonrpc_api import ZMQJSONRPCAPIsClient, ZMQJSONRPCAPIsServer
from booker.booker_gateway_api import (
    OrderType,
    TxStatus,
    TxError,
    Order,
    OrderAPIClient,
    OrderAPIServer
)


new_order = Order(
    order_id=uuid4(),
    order_type=OrderType.DEPOSIT,
    comleted=False,
    in_tx_coin='USDT',
    in_tx_from='',
    in_tx_to='',
    in_tx_hash='',
    in_tx_amount=Decimal('50'),
    in_tx_created_at=0,
    in_tx_status=TxStatus.WAIT,
    in_tx_error=TxError.NO_ERROR,
    in_tx_confirmations=0,
    out_tx_coin='FINTEH.USDT',
    out_tx_from='finteh-usdt',
    out_tx_to='kwaskoff',
    out_tx_hash='',
    out_tx_amount=Decimal('49.5'),
    out_tx_created_at=0,
    out_tx_status=TxStatus.WAIT,
    out_tx_error=TxError.NO_ERROR,
    out_tx_confirmations=0,
)


class MockOrderAPIClient(OrderAPIClient):
    ...


class MockOrderAPIServer(OrderAPIServer):
    @api_method
    async def new_order(self, args: Order) -> APIStream[None, None]:
        assert args == new_order

        yield None


    @api_method
    async def update_order(self, args: Order) -> APIStream[None, None]:
        yield None


@pytest.mark.asyncio
async def test_new_order() -> None:
    server_stream = await create_zmq_stream(
        zmq.REP,
        bind='tcp://127.0.0.1:*'
    )
    address = list(server_stream.transport.bindings())[0]
    client_stream = await create_zmq_stream(zmq.REQ, connect=address)
    apis_server = ZMQJSONRPCAPIsServer(stream=server_stream)
    server = MockOrderAPIServer()

    apis_server.api_register(server)

    server_task = asyncio.create_task(apis_server.poll())
    apis_client = ZMQJSONRPCAPIsClient(stream=client_stream)
    client = MockOrderAPIClient(apis_client=apis_client)
    coroutine = client.new_order(new_order)

    assert await coroutine.asend(None) == None

    with pytest.raises(StopAsyncIteration):
        await coroutine.asend(None)

    server_task.cancel()
