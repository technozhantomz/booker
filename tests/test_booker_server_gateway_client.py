import datetime
from uuid import uuid4

from booker_api.booker_server import BookerServer
from gateway_api.gateway_side_client import GatewaySideClient
from finteh_proto.dto import *
from finteh_proto.enums import TxError

import pytest


TEST_TX = TransactionDTO(
    amount=Decimal("10.1"),
    tx_id="some:hash",
    coin="USDT",
    to_address="one",
    from_address="two",
    confirmations=0,
    max_confirmations=1,
    created_at=datetime.datetime.now(),
)

TEST_ORDER = OrderDTO(order_id=uuid4(), in_tx=TEST_TX)


@pytest.mark.asyncio
async def test_booker_server_and_gateway_client():
    server = BookerServer()
    await server.start()
    client = GatewaySideClient(port=8888)

    in_tx = TEST_TX
    out_tx = TransactionDTO(to_address="prefix.one")

    order_to_create_dto = OrderDTO(in_tx=in_tx, out_tx=out_tx)

    created_order = await client.create_order_request(order_to_create_dto)

    assert isinstance(created_order, OrderDTO)
    assert created_order.order_id
    assert isinstance(created_order.in_tx, TransactionDTO)
    assert isinstance(created_order.in_tx.error, TxError)
    assert isinstance(created_order.in_tx.amount, Decimal)
    assert created_order.in_tx.amount == TEST_TX.amount

    created_order.in_tx.confirmations = 1
    assert created_order.in_tx.confirmations == 1

    updated_tx = await client.update_order_request(created_order)

    assert isinstance(updated_tx, UpdateOrderDTO)
    assert updated_tx.is_updated

    await server.stop()
