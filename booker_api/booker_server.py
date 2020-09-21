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
from finteh_proto.dto import TransactionDTO, OrderDTO, UpdateTxDTO, DepositAddressDTO
from finteh_proto.enums import OrderType

from booker_api.db.queries import (
    safe_insert_order,
    update_tx,
    get_tx_by_tx_id,
    select_order_by_id,
    insert_order,
)
from booker_api.db.models import Tx, Order
from booker_api.frontend_dto import (
    Order as FrontendOrderDTO,
    NewInOrder as FrontendNewInOrderDTO,
    InOrder as FrontendInOrderDTO,
)
from booker_api.config import Config


class BookerServer(BaseServer):
    def __init__(self, host="0.0.0.0", port=8080, ctx=None):
        super(BookerServer, self).__init__(host, port, ctx)
        self.app.router.add_route("GET", "/orders/get_order", self.get_order)
        self.app.router.add_route("POST", "/orders/new_in_order", self.new_in_order)
        self.add_methods(("", self.create_order), ("", self.update_tx))

    async def create_order(self, request):
        """Receiving new (IN) transaction, creating OUT transaction template and Order"""
        in_tx = TransactionDTO.Schema().load(request.msg[1]["params"])

        # TODO replace this mock
        out_tx = TransactionDTO(
            amount=in_tx.amount,
            tx_id=None,
            coin=in_tx.coin,
            to_address=in_tx.coin,
            from_address=in_tx.coin,
            confirmations=0,
            max_confirmations=1,
            created_at=datetime.datetime.now(),
        )

        if self.ctx:
            prefix = self.ctx.cfg.exchange_prefix
        else:
            prefix = Config.exchange_prefix

        if prefix in in_tx.coin:
            order_type = OrderType.WITHDRAWAL
        else:
            order_type = OrderType.DEPOSIT
        order = OrderDTO(
            order_id=uuid4(), in_tx=in_tx, out_tx=out_tx, order_type=order_type
        )

        if self.ctx:
            async with self.ctx.db_engine.acquire() as conn:
                in_tx_model = Tx(id=uuid4(), **dataclasses.asdict(in_tx))
                out_tx_model = Tx(id=uuid4(), **dataclasses.asdict(out_tx))
                order_model = Order(
                    id=order.order_id,
                    in_tx=in_tx_model.id,
                    out_tx=out_tx_model.id,
                    order_type=order.order_type,
                )
                await safe_insert_order(conn, in_tx_model, out_tx_model, order_model)

        return self.jsonrpc_response(request, order)

    async def update_tx(self, request):
        """Update existing transaction"""
        tx_dto = TransactionDTO.Schema().load(request.msg[1]["params"])

        if self.ctx:
            async with self.ctx.db_engine.acquire() as conn:
                tx_db_data = await get_tx_by_tx_id(conn, tx_dto.tx_id)
                tx_model_instance = Tx(
                    id=tx_db_data["id"], **dataclasses.asdict(tx_dto)
                )
                await update_tx(conn, tx_model_instance)

        updated_tx = UpdateTxDTO(is_updated=True)

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
        request_payload = await request.json()

        # new_order_schema = FrontendInOrderDTO.Schema()
        # new_order = new_order_schema.load(request_payload)
        # todo fix this mock

        order = Order(id=uuid4(), order_type=OrderType.TRASH)

        async with self.ctx.db_engine.acquire() as conn:
            await insert_order(conn, order)

        order_dto = FrontendInOrderDTO(order_id=order.id, in_tx_to="MOCK")
        rs_payload = order_dto.Schema().dump(order_dto)
        response = http_json_response(rs_payload)

        return response
