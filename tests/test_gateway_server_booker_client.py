import datetime
from uuid import uuid4

from gateway_api.gateway_server import GatewayServer
from finteh_proto.dto import (
    TransactionDTO,
    OrderDTO,
    DepositAddressDTO,
    ValidateAddressDTO,
    Decimal,
    CreatedEmptyOrderDTO,
    EmptyTransactionDTO,
    EmptyOrderDTO,
)
from booker_api.booker_side_client import BookerSideClient

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

TEST_ORDER = OrderDTO(order_id=str(uuid4()), in_tx=TEST_TX)


# @pytest.mark.skip
@pytest.mark.asyncio
async def test_booker_client_create_empty_order():
    test_empty_in_tx = EmptyTransactionDTO(coin="USDT", to_address="kwaskoff")
    test_empty_out_tx = EmptyTransactionDTO(
        coin="FINTEH.USDT", to_address="0x3d354a13bb077f15e31e02bf169c103aa60af90a"
    )

    test_empty_order = EmptyOrderDTO(
        order_id=uuid4(), in_tx=test_empty_in_tx, out_tx=test_empty_out_tx
    )

    server = GatewayServer()
    await server.start()

    client = BookerSideClient()

    empty_order = await client.create_empty_order_request(test_empty_order)

    assert isinstance(empty_order, CreatedEmptyOrderDTO)
    assert empty_order.created

    await server.stop()


@pytest.mark.asyncio
async def test_booker_client_deposit_address():
    server = GatewayServer()
    await server.start()
    client = BookerSideClient()

    deposit_address_body = DepositAddressDTO(user="kwaskoff")
    deposit_address = await client.get_deposit_address_request(deposit_address_body)

    assert isinstance(deposit_address, DepositAddressDTO)
    assert deposit_address.deposit_address == "DEPOSIT ADDRESS"
    print(deposit_address.deposit_address)
    await server.stop()


@pytest.mark.asyncio
async def test_booker_client_validate_address():
    server = GatewayServer()
    await server.start()
    client = BookerSideClient()

    validate_address_body = ValidateAddressDTO(user="one")
    validated_address = await client.validate_address_request(validate_address_body)

    assert isinstance(validated_address, ValidateAddressDTO)
    assert validated_address.is_valid

    await server.stop()


@pytest.mark.asyncio
async def test_booker_client_init_new_tx():
    server = GatewayServer()
    await server.start()
    client = BookerSideClient()

    assert not TEST_ORDER.out_tx
    out_tx = await client.init_new_tx_request(TEST_ORDER)

    assert isinstance(out_tx, TransactionDTO)
    assert out_tx.coin

    await server.stop()
