import dataclasses
from typing import ClassVar, Type, Optional, Any
from decimal import Decimal
import datetime
from uuid import UUID

from marshmallow import Schema as MarshmallowSchema, fields
from marshmallow_dataclass import dataclass, NewType as MarshmallowNewType
from finteh_proto.enums import TxError, OrderType


class DTOInvalidType(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass
class DataTransferClass(dict):
    Schema: ClassVar[Type[MarshmallowSchema]] = MarshmallowSchema

    def update(self, dto) -> None:
        dto_dict = dataclasses.asdict(dto)

        for key, value in dto_dict.items():
            if value is not None:
                setattr(self, key, value)


def amount_field(*args, **kwargs):
    return fields.Decimal(*args, **kwargs, as_string=True)


Amount = MarshmallowNewType("Amount", Decimal, field=amount_field)


@dataclass
class TransactionDTO(DataTransferClass):
    coin: str
    to_address: str
    from_address: str
    amount: Amount
    created_at: datetime.datetime = datetime.datetime.now()
    error: TxError = TxError.NO_ERROR
    tx_id: str = None
    confirmations: int = 0
    max_confirmations: int = 0


@dataclass
class OrderDTO(DataTransferClass):
    order_id: UUID = None
    in_tx: TransactionDTO = None
    out_tx: TransactionDTO = None
    order_type: OrderType = OrderType.TRASH


@dataclass
class DepositAddressDTO(DataTransferClass):
    user: str = None
    deposit_address: str = None


@dataclass
class ValidateAddressDTO(DataTransferClass):
    user: str
    is_valid: bool = None


@dataclass
class UpdateTxDTO(DataTransferClass):
    is_updated: bool = False


@dataclass
class JSONRPCError(DataTransferClass):
    code: int
    message: str
    data: Optional[Any] = None


@dataclass
class JSONRPCResponse(DataTransferClass):
    id: UUID
    result: Optional[Any]
    error: Optional[JSONRPCError]


@dataclass
class JSONRPCRequest(DataTransferClass):
    id: UUID
    method: str
    params: Optional[Any]
