from finteh_proto.client import BaseClient
from finteh_proto.dto import TransactionDTO, OrderDTO, UpdateOrderDTO


class GatewaySideClient(BaseClient):
    """Interact with booker remote service.
    Import this class to Gateway app"""

    def __init__(self, ctx=None, host="0.0.0.0", port=8080):
        super().__init__(ctx, host, port)

    @BaseClient.safe_call_execute
    async def create_order_request(self, order: OrderDTO) -> tuple:
        """Requesting remote Booker instance to create new order.
        When gateway see new valid transaction in blockchain, it send notifications with tx params.
        Booker will response with just-created Order with id
        Require valid transaction that will become in_tx in returned order"""
        return "create_order", order, OrderDTO

    @BaseClient.safe_call_execute
    async def update_order_request(self, order: OrderDTO) -> tuple:
        """Requesting remote Booker instance to update existing transaction.
        Booker will check new params, update database and response"""
        return "update_order", order, UpdateOrderDTO
