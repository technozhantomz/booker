"""Some example of gateway's handlers.
You can change, add and remove handlers depending on gateway's architecture"""

import json

from finteh_proto.server import BaseServer
from finteh_proto.dto import (
    CreatedEmptyOrderDTO,
    TransactionDTO,
    OrderDTO,
    DepositAddressDTO,
    ValidateAddressDTO,
)


class GatewayServer(BaseServer):
    def __init__(self, host="0.0.0.0", port=8080, ctx=None):
        super(GatewayServer, self).__init__(host, port, ctx)

        self.add_methods(
            ("", self.validate_address),
            ("", self.get_deposit_address),
            ("", self.init_new_tx),
            ("", self.create_empty_order),
        )

    async def init_new_tx(self, request):
        order = OrderDTO.Schema().load(request.msg[1]["params"])

        # TODO Doing check and broadcast stuff

        out_tx = order.in_tx
        return self.jsonrpc_response(request, out_tx)

    async def get_deposit_address(self, request):
        # Do not forget to overwrite this method to implement returning real deposit address
        deposit_address_body = DepositAddressDTO.Schema().load(request.msg[1]["params"])
        assert deposit_address_body.user
        deposit_address_body.deposit_address = "DEPOSIT ADDRESS"
        return self.jsonrpc_response(request, deposit_address_body)

    async def validate_address(self, request):
        # Do not forget to overwrite this method to implement gateway side blockchain address validation
        validate_address_body = ValidateAddressDTO.Schema().load(
            request.msg[1]["params"]
        )

        assert validate_address_body.user
        validate_address_body.is_valid = True

        return self.jsonrpc_response(request, validate_address_body)

    async def create_empty_order(self, request):
        return self.jsonrpc_response(request, CreatedEmptyOrderDTO(created=True))
