import json
from uuid import uuid4

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
    async def init_new_tx_request(self, order: OrderDTO) -> TransactionDTO:
        """Requesting remote Gateway instance to broadcast new (out-) transaction.
        Using when old (in-) transaction are completed"""
        call_result = await self.call(
            "init_new_tx", id=str(uuid4()), params=order.to_dump()
        )
        resp_data = json.loads(call_result[1]["params"])
        return TransactionDTO(**resp_data)

    @BaseClient.safe_call_execute
    async def get_deposit_address_request(self, deposit_address: DepositAddressDTO):
        """Requesting remote Gateway's deposit address"""
        call_result = await self.call(
            "get_deposit_address", id=str(uuid4()), params=deposit_address.to_dump()
        )
        resp_data = json.loads(call_result[1]["params"])
        return DepositAddressDTO(**resp_data)

    @BaseClient.safe_call_execute
    async def validate_address_request(self, user_address: ValidateAddressDTO):
        call_result = await self.call(
            "validate_address", id=str(uuid4()), params=user_address.to_dump()
        )
        resp_data = json.loads(call_result[1]["params"])
        return ValidateAddressDTO(**resp_data)
