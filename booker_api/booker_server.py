import json
from uuid import uuid4, UUID
import dataclasses
import datetime

from aiohttp.web import (
    Request as HTTPRequest,
    Response as HTTPResponse,
    json_response as http_json_response,
)

from finteh_proto.server import BaseServer
from finteh_proto.dto import (
    TransactionDTO,
    OrderDTO,
    UpdateOrderDTO,
    DepositAddressDTO,
    JSONRPCError,
    EmptyTransactionDTO,
    EmptyOrderDTO,
)
from finteh_proto.enums import OrderType, TxError
from finteh_proto.utils import get_logger

from booker_api.db.queries import (
    safe_insert_order,
    safe_update_order,
    select_order_by_id,
)
from booker_api.db.models import Tx, Order
from booker_api.frontend_dto import (
    Order as FrontendOrderDTO,
    NewInOrder as FrontendNewInOrderDTO,
    InOrder as FrontendInOrderDTO,
)
from booker_api.config import Config

log = get_logger("Booker Server")


class BookerServer(BaseServer):
    def __init__(self, host="0.0.0.0", port=8080, ctx=None):
        super(BookerServer, self).__init__(host, port, ctx)
        self.app.router.add_route("GET", "/orders/get_order", self.get_order)
        self.app.router.add_route("POST", "/orders/new_in_order", self.new_in_order)
        self.add_methods(("", self.create_order), ("", self.update_order))

    async def create_order(self, request):
        """Receiving Order with new (IN) transaction, creating OUT transaction template and Order_id"""
        order_dto = OrderDTO.Schema().load(request.msg[1]["params"])

        # TODO take_fee
        order_dto.out_tx.amount = order_dto.in_tx.amount

        if self.ctx:
            prefix = self.ctx.cfg.exchange_prefix
        else:
            prefix = Config.exchange_prefix

        if prefix in order_dto.in_tx.coin:
            order_dto.order_type = OrderType.WITHDRAWAL
            order_dto.out_tx.coin = str(order_dto.in_tx.coin).replace(f"{prefix}.", "")
        else:
            order_dto.order_type = OrderType.DEPOSIT
            order_dto.out_tx.coin = f"{prefix}.{order_dto.in_tx.coin}"

        order_dto.order_id = uuid4()

        if self.ctx:
            async with self.ctx.db_engine.acquire() as conn:
                in_tx_model = Tx(id=uuid4(), **dataclasses.asdict(order_dto.in_tx))
                out_tx_model = Tx(id=uuid4(), **dataclasses.asdict(order_dto.out_tx))
                order_model = Order(
                    id=order_dto.order_id,
                    in_tx=in_tx_model.id,
                    out_tx=out_tx_model.id,
                    order_type=order_dto.order_type,
                )
                await safe_insert_order(conn, in_tx_model, out_tx_model, order_model)

        return self.jsonrpc_response(request, order_dto)

    async def update_order(self, request):
        """Update existing transaction"""
        order_dto = OrderDTO.Schema().load(request.msg[1]["params"])

        if self.ctx:
            async with self.ctx.db_engine.acquire() as conn:
                await safe_update_order(conn, order_dto)

        updated_tx = UpdateOrderDTO(is_updated=True)

        return self.jsonrpc_response(request, updated_tx)

    async def get_order(self, request: HTTPRequest) -> HTTPResponse:
        """Get order object by frontend request with http"""
        if not self.ctx:
            return http_json_response({"error": "Booker App is not run"})
        if not request.query.get("order_id"):
            return http_json_response({"error": "Order_id is not specified"})
        order_id = request.query["order_id"]
        try:
            UUID(order_id)
        except Exception as ex:
            return http_json_response({"error": f"Order_id has wrong format: {ex}"})

        async with self.ctx.db_engine.acquire() as conn:
            order = await select_order_by_id(conn, order_id)

        if not order:
            return http_json_response({"error": f"There is no order {order_id}"})

        order_dto = FrontendOrderDTO(**order)
        order_dto = order_dto.Schema().dump(order_dto)
        return http_json_response(order_dto)

    async def new_in_order(self, request: HTTPRequest) -> HTTPResponse:
        """Create (empty) order object by frontend request with http"""
        if not self.ctx:
            return http_json_response({"error": "Booker App is not run"})

        request_payload = await request.json()
        new_order = FrontendNewInOrderDTO(**request_payload)

        if self.ctx.cfg.exchange_prefix in new_order.in_tx_coin:
            return http_json_response(
                {"error": "You can not create withdrawal order with http"}
            )

        assert self.ctx.cfg.exchange_prefix in new_order.out_tx_coin
        client_name = new_order.in_tx_coin
        order_type = OrderType.DEPOSIT

        try:
            client = self.ctx.gateways_clients[client_name]["native"]
        except KeyError:
            return http_json_response(
                {"error": f"Native{client_name} gateway client is not available now"}
            )

        deposit_address = await client.get_deposit_address_request(
            DepositAddressDTO(user=new_order.out_tx_to)
        )

        in_tx = Tx(
            id=uuid4(),
            coin=new_order.in_tx_coin,
            to_address=new_order.out_tx_to,
            amount=new_order.in_tx_amount,
            created_at=datetime.datetime.now(),
            error=TxError.NO_ERROR,
            confirmations=0,
            max_confirmations=0,
        )

        out_tx = Tx(
            id=uuid4(),
            coin=new_order.out_tx_coin,
            to_address=new_order.out_tx_to,
            amount=0,
            created_at=datetime.datetime.now(),
            error=TxError.NO_ERROR,
            confirmations=0,
            max_confirmations=0,
        )

        order = Order(
            id=uuid4(), in_tx=in_tx.id, out_tx=out_tx.id, order_type=order_type
        )

        async with self.ctx.db_engine.acquire() as conn:
            insert = await safe_insert_order(conn, in_tx, out_tx, order)
            if not insert:
                return http_json_response({"error": "Unable to create order now"})

        log.info(f"Order {order.id} created")

        in_tx_dto = EmptyTransactionDTO(
            coin=in_tx.coin, to_address=deposit_address.deposit_address
        )

        out_tx_dto = EmptyTransactionDTO(coin=out_tx.coin, to_address=out_tx.to_address)

        order_dto = EmptyOrderDTO(order_id=order.id, in_tx=in_tx_dto, out_tx=out_tx_dto)

        notify = await client.create_empty_order_request(order_dto)

        if not isinstance(notify, JSONRPCError):
            log.info(
                f"Successfully copy order {order_dto.order_id} to native{client_name} gateway"
            )
        else:
            log.info(
                f"Unable to create copy of empty order {order_dto.order_id} on native{client_name} gateway: {notify.message}"
            )

        order_dto = FrontendInOrderDTO(
            order_id=order.id, in_tx_to=deposit_address.deposit_address
        )

        rs_payload = order_dto.Schema().dump(order_dto)
        response = http_json_response(rs_payload)

        return response
