from decimal import Decimal
from dataclasses import dataclass
import dataclasses
import json
import datetime
from uuid import UUID
from typing import Optional, Any

from finteh_proto.enums import TxError, OrderType, EnumEncoder, Enum, as_enum


@dataclass
class DataTransferClass:
    def __init__(self):
        super().__init__()

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def normalize(self):
        return self

    def to_dump(self):
        """Return json-encoded string ready to send with ws-json-rpc. Works recursive for dict objects"""
        return json.dumps(self._dict_to_str(dataclasses.asdict(self)), cls=EnumEncoder)

    def _dict_to_str(self, _dict: dict):
        # TODO replace this later
        for k, v in _dict.items():
            if isinstance(v, dict):
                _dict[k] = self._dict_to_str(v)
            if isinstance(v, Decimal):
                _dict[k] = str(v)
            if isinstance(v, datetime.datetime):
                _dict[k] = str(v)
            if isinstance(v, UUID):
                _dict[k] = str(v)

        return _dict


@dataclass
class TransactionDTO(DataTransferClass):
    coin: str
    tx_id: str
    to_address: str
    from_address: str
    amount: Decimal
    created_at: datetime.datetime = datetime.datetime.now()
    error: TxError = TxError.NO_ERROR
    confirmations: int = 0
    max_confirmations: int = 0

    def normalize(self):
        """Cast types after init from json.loads()"""
        self.error = as_enum(self.error)
        self.amount = Decimal(self.amount)
        if not (isinstance(self.created_at, datetime.datetime)):
            self.created_at = datetime.datetime.strptime(
                self.created_at, "%Y-%m-%d %H:%M:%S.%f"
            )
        return self


@dataclass
class OrderDTO(DataTransferClass):
    order_id: UUID = None
    in_tx: TransactionDTO = None
    out_tx: TransactionDTO = None
    order_type: OrderType = OrderType.TRASH

    def normalize(self):
        """Cast types after init from json.loads()"""
        if self.order_type:
            if not (isinstance(self.order_type, OrderType)):
                self.order_type = as_enum(self.order_type)
        if self.in_tx:
            if not isinstance(self.in_tx, TransactionDTO):
                self.in_tx = TransactionDTO(**self.in_tx).normalize()
        if self.out_tx:
            if not isinstance(self.out_tx, TransactionDTO):
                self.out_tx = TransactionDTO(**self.out_tx).normalize()
        return self


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
    result: Optional[Any]
    error: Optional[JSONRPCError]
    id: UUID


@dataclass
class JSONRPCRequest(DataTransferClass):
    method: str
    id: UUID
    params: Optional[Any] = None
