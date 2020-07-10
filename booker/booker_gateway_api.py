from typing import Optional
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
class ValidateAddress(DataTransferClass):
    tx_to: str


@dataclass
class ValidatedAddress(DataTransferClass):
    valid: bool


@dataclass
class GetDepositAddress(DataTransferClass):
    out_tx_to: Optional[str] = None


@dataclass
class DepositAddress(DataTransferClass):
    tx_to: str


@dataclass
class NewInOrder(DataTransferClass):
    """Create a new inbound order with order_id identifier.
    """
    order_id: UUID
    order_type: OrderType
    in_tx_coin: str
    in_tx_to: str
    in_tx_amount: Amount
    out_tx_coin: str
    out_tx_to: Optional[str] = None


@dataclass
class NewOutOrder(DataTransferClass):
    """Create a new outbound order with order_id identifier.
    """
    order_id: UUID
    order_type: OrderType
    in_tx_coin: str
    in_tx_hash: str
    """
    A transaction identifier, simple or composite, consisting of a transaction
    identifier and an index, for example, 'txid:output_index'.
    """
    in_tx_from: str
    in_tx_to: str
    in_tx_amount: Amount
    in_tx_created_at: int
    in_tx_status: TxStatus
    in_tx_error: TxError
    in_tx_confirmations: int
    out_tx_coin: str
    out_tx_to: str


@dataclass
class NewInTxOrder(DataTransferClass):
    """Creates a new inbound transaction in the Booker database and binds it to
    the order with the order_id identifier.
    """
    order_id: UUID
    tx_hash: str
    """A transaction identifier, simple or composite, consisting of a
    transaction identifier and an index, for example, 'txid:output_index'.
    """
    tx_from: str
    tx_amount: Amount
    tx_created_at: int
    tx_status: TxStatus
    tx_error: TxError
    tx_confirmations: int
    memo_to: Optional[str] = None


@dataclass
class NewOutTxOrder(DataTransferClass):
    """
    Creates a new outbound transaction in the Booker database and binds it to
    the order with the order_id identifier.
    """
    order_id: UUID
    tx_hash: str
    """A transaction identifier, simple or composite, consisting of a
    transaction identifier and an index, for example, 'txid:output_index'.
    """
    tx_from: str
    tx_amount: Amount
    tx_created_at: int
    tx_status: TxStatus
    tx_error: TxError
    tx_confirmations: int


@dataclass
class UpdateTxOrder(DataTransferClass):
    """Updates a transaction in the Booker database that is bound to the order
    with the order_id identifier.
    """
    order_id: UUID
    tx_status: TxStatus
    tx_error: TxError
    tx_confirmations: int


@dataclass
class NewInTx(DataTransferClass):
    """Creates a new inbound transaction with tx_hash identifier in the Booker
    database without binding to the order.
    """
    tx_hash: str
    """ A transaction identifier, simple or composite, consisting of a
    transaction identifier and an index, for example, 'txid:output_index'.
    """
    tx_from: str
    tx_to: str
    tx_amount: Amount
    tx_created_at: int
    tx_status: TxStatus
    tx_error: TxError
    tx_confirmations: int
    memo_to: Optional[str] = None


@dataclass
class NewOutTx(DataTransferClass):
    """Creates a new outbound transaction with tx_hash identifier in the Booker
    database without binding to the order.
    """
    tx_hash: str
    """A transaction identifier, simple or composite, consisting of a
    transaction identifier and an index, for example, 'txid:output'.
    """
    tx_from: str
    tx_to: str
    tx_amount: Amount
    tx_created_at: int
    tx_status: TxStatus
    tx_error: TxError
    tx_confirmations: int


@dataclass
class UpdateTx(DataTransferClass):
    """Updates a transaction with tx_hash identifier in a Booker database that
    isn't bound to the order.
    """
    tx_hash: str
    """A transaction identifier, simple or composite, consisting of a
    transaction identifier and an index, for example, 'txid:output'.
    """
    tx_status: TxStatus
    tx_error: TxError
    tx_confirmations: int


@dataclass
class BindTxOrder(DataTransferClass):
    """Bind a transaction with tx_hash identifier to an order with identifier
    order_id.
    """
    order_id: UUID
    tx_hash: str
    """A transaction identifier, simple or composite, consisting of a
    transaction identifier and an index, for example, 'txid:output'.
    """


class AbstractBookerGatewayOrderAPI(ABC):
    @api_method
    @abstractmethod
    async def new_in_tx_order(
        self,
        args: NewInTxOrder
    ) -> APIStream[None, None]:
        """Creates a new inbound transaction in the Booker database and binds it
        to the order with the order_id identifier.
        """
        yield None


    @api_method
    @abstractmethod
    async def update_in_tx_order(
        self,
        args: UpdateTxOrder
    ) -> APIStream[None, None]:
        """Updates a inbound transaction in the Booker database that is bound to
        the order with the order_id identifier.
        """
        yield None


    @api_method
    @abstractmethod
    async def new_out_tx_order(
        self,
        args: NewOutTxOrder
    ) -> APIStream[None, None]:
        """Creates a new outbound transaction in the Booker database and binds
        it to the order with the order_id identifier.
        """
        yield None


    @api_method
    @abstractmethod
    async def update_out_tx_order(
        self,
        args: UpdateTxOrder
    ) -> APIStream[None, None]:
        """Updates a outbound transaction in the Booker database that is bound
        to the order with the order_id identifier.
        """
        yield None


    @api_method
    @abstractmethod
    async def new_in_tx(self, args: NewInTx) -> APIStream[None, None]:
        """Creates a new inbound transaction with tx_hash identifier in the
        Booker database without binding to the order.
        """
        yield None


    @api_method
    @abstractmethod
    async def update_in_tx(self, args: UpdateTx) -> APIStream[None, None]:
        """Updates a inbound transaction with tx_hash identifier in a Booker
        database that isn't bound to the order.
        """
        yield None


    @api_method
    @abstractmethod
    async def new_out_tx(self, args: NewOutTx) -> APIStream[None, None]:
        """Creates a new outbound transaction with tx_hash identifier in the
        Booker database without binding to the order.
        """
        yield None


    @api_method
    @abstractmethod
    async def update_out_tx(self, args: UpdateTx) -> APIStream[None, None]:
        """Updates a outbound transaction with tx_hash identifier in a Booker
        database that isn't bound to the order.
        """
        yield None


    @api_method
    @abstractmethod
    async def bind_tx_order(self, args: BindTxOrder) -> APIStream[None, None]:
        """Bind a transaction with tx_hash identifier to an order with
        identifier order_id.
        """
        yield None


@api_server
class AbstractBookerGatewayOrderAPIServer(AbstractBookerGatewayOrderAPI):
    ...


class AbstractGatewayBookerOrderAPI(ABC):
    @api_method
    @abstractmethod
    async def validate_address(
        self,
        args: ValidateAddress
    ) -> APIStream[ValidatedAddress, None]:
        yield None


    @api_method
    @abstractmethod
    async def get_deposit_address(
        self,
        args: GetDepositAddress
    ) -> APIStream[DepositAddress, None]:
        yield None


    @api_method
    @abstractmethod
    async def new_in_order(self, args: NewInOrder) -> APIStream[None, None]:
        """Create a new inbound order with order_id identifier.
        """
        yield None


    @api_method
    @abstractmethod
    async def new_out_order(self, args: NewOutOrder) -> APIStream[None, None]:
        """Create a new outbound order with order_id identifier.
        """
        yield None


@api_client
class AbstractGatewayBookerOrderAPIClient(AbstractGatewayBookerOrderAPI):
    ...


class GatewayBookerOrderAPIClient(AbstractGatewayBookerOrderAPIClient):
    ...
