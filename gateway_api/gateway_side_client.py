from uuid import uuid4
import json
from finteh_proto.client import BaseClient
from finteh_proto.dto import TransactionDTO, OrderDTO, UpdateTxDTO


class GatewaySideClient(BaseClient):
    """Interact with booker remote service.
    Import this class to Gateway app"""

    def __init__(self, ctx=None, host="0.0.0.0", port=8080):
        super().__init__(ctx, host, port)

    @BaseClient.safe_call_execute
    async def create_order_request(self, tx: TransactionDTO) -> OrderDTO:
        """Requesting remote Booker instance to create new order.
        When gateway see new valid transaction in blockchain, it send notifications with tx params.
        Booker will response with just-created Order with id
        Require valid transaction that will become in_tx in returned order"""
        call_result = await self.call(
            "create_order", id=str(uuid4()), params=tx.to_dump()
        )
        order_data = json.loads(call_result[1]["params"])

        return OrderDTO(order_id=order_data["order_id"], in_tx=tx)

    @BaseClient.safe_call_execute
    async def update_tx_request(self, order: TransactionDTO) -> UpdateTxDTO:
        """Requesting remote Booker instance to update existing transaction.
        Booker will check new params, update database and response"""
        call_result = await self.call(
            "update_tx", id=str(uuid4()), params=order.to_dump()
        )
        updated_order_data = json.loads(call_result[1]["params"])

        return UpdateTxDTO(is_updated=updated_order_data["is_updated"])
