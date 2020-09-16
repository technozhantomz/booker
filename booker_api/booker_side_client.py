from finteh_proto.client import BaseClient
from finteh_proto.dto import (
    OrderDTO,
    DepositAddressDTO,
    ValidateAddressDTO,
    TransactionDTO,
)


class BookerSideClient(BaseClient):
    """Interact with remote gateway.
    Import this class to Booker app"""

    def __init__(
        self,
        gateway_name="AbstractGateway",
        gateway_side="Not spec",
        ctx=None,
        host="0.0.0.0",
        port=8080,
    ):
        super().__init__(ctx, host, port)
        self.gateway_name = gateway_name
        self.gateway_side = gateway_side

    def __repr__(self):
        return f"{self.gateway_name}-{self.gateway_side}-{self.__class__.__name__}"

    @BaseClient.safe_call_execute
    async def init_new_tx_request(self, order: OrderDTO) -> tuple:
        """Requesting remote Gateway instance to broadcast new (out-) transaction.
        Using when old (in-) transaction are completed"""
        return "init_new_tx", order, TransactionDTO

    @BaseClient.safe_call_execute
    async def get_deposit_address_request(
        self, deposit_address: DepositAddressDTO
    ) -> tuple:
        """Requesting remote Gateway's deposit address"""
        return "get_deposit_address", deposit_address, DepositAddressDTO

    @BaseClient.safe_call_execute
    async def validate_address_request(self, user_address: ValidateAddressDTO) -> tuple:
        return "validate_address", user_address, ValidateAddressDTO
