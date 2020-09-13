import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy_utils as sa_utils

from finteh_proto.enums import OrderType, TxError


Base = declarative_base()


class Tx(Base):
    __tablename__ = "txs"

    id = sa.Column(sa_utils.UUIDType, primary_key=True)
    coin = sa.Column(sa.String, nullable=False)
    tx_id = sa.Column(sa.String)
    from_address = sa.Column(sa.String)
    to_address = sa.Column(sa.String)
    amount = sa.Column(sa.Numeric(78, 36), nullable=False, server_default="0.0")
    created_at = sa.Column(
        sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()
    )
    error = sa.Column(sa.Enum(TxError), nullable=False, server_default="NO_ERROR")
    confirmations = sa.Column(sa.Integer, nullable=False, server_default="0")
    max_confirmations = sa.Column(sa.Integer, nullable=False, server_default="0")
    __table_args__ = (sa.UniqueConstraint("coin", "tx_id"),)


class Order(Base):
    __tablename__ = "orders"

    id = sa.Column(sa_utils.UUIDType, primary_key=True, nullable=False)
    in_tx = sa.Column(sa_utils.UUIDType, sa.ForeignKey("txs.id"), nullable=False)
    out_tx = sa.Column(sa_utils.UUIDType, sa.ForeignKey("txs.id"), nullable=False)
    order_type = sa.Column(sa.Enum(OrderType), nullable=False, server_default="TRASH")
