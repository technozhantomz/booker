from abc import ABC, abstractmethod
from uuid import UUID
from enum import Enum

from marshmallow_dataclass import dataclass

from booker.dto import DataTransferClass, Amount
from booker.api import APIStream, api_method, api_client, api_server


class OrderType(Enum):
    TRASH = 0
    DEPOSIT = 1
    WITHDRAWAL = 2


class TxStatus(Enum):
    ERROR = 0
    WAIT = 1
    RECEIVED_NOT_CONFIRMED = 2
    RECEIVED_AND_CONFIRMED = 3


class TxError(Enum):
    NO_ERROR = 0
    UNKNOWN_ERROR = 1


@dataclass
class Order(DataTransferClass):
    order_id: UUID
    order_type: OrderType
    comleted: bool
    in_tx_coin: str
    in_tx_from: str
    in_tx_to: str
    in_tx_hash: str
    in_tx_amount: Amount
    in_tx_created_at: int
    in_tx_status: TxStatus
    in_tx_error: TxError
    in_tx_confirmations: int
    out_tx_coin: str
    out_tx_from: str
    out_tx_to: str
    out_tx_hash: str
    out_tx_amount: Amount
    out_tx_created_at: int
    out_tx_status: TxStatus
    out_tx_error: TxError
    out_tx_confirmations: int


class AbstractOrderAPI(ABC):
    @api_method
    @abstractmethod
    async def new_order(self, args: Order) -> APIStream[None, None]:
        yield None


    @api_method
    @abstractmethod
    async def update_order(self, args: Order) -> APIStream[None, None]:
        yield None


@api_client
class OrderAPIClient(AbstractOrderAPI):
    ...


@api_server
class OrderAPIServer(AbstractOrderAPI):
    ...
