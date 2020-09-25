from decimal import Decimal
import datetime
import dataclasses

from finteh_proto.dto import (
    TransactionDTO,
    OrderDTO,
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    ValidateAddressDTO,
    DepositAddressDTO,
)
from finteh_proto.enums import TxError, OrderType
from booker_api.frontend_dto import NewInOrder, InOrder, Order as FrontendOrderDTO
from uuid import uuid4


TEST_TX = TransactionDTO(
    amount=Decimal("10.1"),
    tx_id="some:hash",
    coin="USDT",
    to_address="one",
    from_address="two",
    confirmations=0,
    max_confirmations=1,
    created_at=datetime.datetime.now(),
    error=TxError.NO_ERROR,
)


def test_tx_dto():
    assert isinstance(TEST_TX, TransactionDTO)

    dump = TEST_TX.Schema().dump(TEST_TX)

    loads = TEST_TX.Schema().load(dump)

    assert TEST_TX.amount == loads.amount
    assert TEST_TX.error == loads.error
    assert type(loads.error) == TxError


def test_order_dto():
    order = OrderDTO(order_id=uuid4(), in_tx=TEST_TX)
    assert isinstance(order, OrderDTO)
    assert isinstance(order.in_tx, TransactionDTO)
    assert isinstance(order.in_tx.error, TxError)

    dump = order.Schema().dump(order)

    loads = order.Schema().load(dump)

    assert order.in_tx.amount == loads.in_tx.amount
    assert isinstance(loads.in_tx, TransactionDTO)
    assert type(loads.order_type) == type(order.order_type)


def test_jsonrpcrequest_validate_address():
    v = ValidateAddressDTO(user="test_user", is_valid=True)
    req = JSONRPCRequest(method="method", id=uuid4(), params=dataclasses.asdict(v))
    req_dump = req.Schema().dump(req)

    req_loads = JSONRPCRequest.Schema().load(req_dump)
    params_load = ValidateAddressDTO(**req_loads.params)
    assert isinstance(req_loads, JSONRPCRequest)
    assert isinstance(params_load, ValidateAddressDTO)
    assert params_load.is_valid == v.is_valid


def test_jsonrpcresponse_validate_address():
    v = ValidateAddressDTO(user="test_user", is_valid=True)
    resp = JSONRPCResponse(id=uuid4(), result=v, error=None)
    resp_dump = resp.Schema().dump(resp)

    resp_loads = JSONRPCResponse.Schema().load(resp_dump)
    result_loads = resp_loads.result
    assert isinstance(resp_loads, JSONRPCResponse)
    assert isinstance(result_loads, ValidateAddressDTO)
    assert result_loads.is_valid == v.is_valid


def test_jsonrpcresponse_order():

    o = OrderDTO(order_id=uuid4(), in_tx=TEST_TX, order_type=OrderType.DEPOSIT)

    resp = JSONRPCResponse(id=uuid4(), result=o, error=None)

    resp_dump = resp.Schema().dump(resp)

    resp_loads = JSONRPCResponse.Schema().load(resp_dump)
    result_loads = resp_loads.result
    assert isinstance(resp_loads, JSONRPCResponse)
    assert isinstance(result_loads, OrderDTO)
    assert resp_loads.result.in_tx == o.in_tx
    assert resp_loads.result.in_tx.amount == o.in_tx.amount == TEST_TX.amount


def test_frontend_dto():
    new_in_order_data = {
        "in_tx_coin": "Some_coin",
        "in_tx_amount": 0,
        "out_tx_coin": "FINTEH.coin",
        "out_tx_to": "Some_address",
    }

    new_in_order = NewInOrder(**new_in_order_data)


def test_dict():
    for k, v in dataclasses.asdict(TEST_TX).items():
        print(k, v)
