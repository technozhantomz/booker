from aiopg.sa import SAConnection as SAConn
from aiopg.sa.result import RowProxy
from sqlalchemy.sql import insert, delete, update, select, join
import sqlalchemy as sa
from booker_api.db.models import Tx, Order
from finteh_proto.enums import OrderType, TxError
from finteh_proto.utils import object_as_dict


async def insert_tx(conn: SAConn, tx: Tx) -> bool:
    try:
        _tx = object_as_dict(tx)
        await conn.execute(insert(Tx).values(**_tx))
        return True
    except Exception as ex:
        return False


async def update_tx(
    conn: SAConn, tx: Tx
) -> None:
    _tx = object_as_dict(tx)
    await conn.execute(
        update(Tx)
        .values(**_tx)
        .where(Tx.tx_id == tx.tx_id)
    )


async def delete_tx(
    conn: SAConn, tx_id) -> None:
    await conn.execute(
        delete(Tx).where(Tx.tx_id == tx_id)
        )


async def insert_order(conn: SAConn, order: Order):
    try:
        _order = object_as_dict(order)
        await conn.execute(insert(Order).values(**_order))
        return True
    except Exception as ex:
        return False


async def safe_insert_order(conn: SAConn, in_tx: Tx, out_tx: Tx, order: Order):
    async with conn.begin('SERIALIZABLE') as transaction:
        try:
            _in_res = await insert_tx(conn, in_tx)
            _out_res = await insert_tx(conn, out_tx)
            _order_res = await insert_order(conn, order)
            assert _in_res
            assert _out_res
            assert _order_res
            return True
        except Exception as ex:
            return False


async def delete_order(conn: SAConn, order_id) -> bool:
    r = await conn.execute(
        delete(Order).where(Order.id == order_id)
        )
    if r:
        return True


async def select_all_orders(conn: SAConn):
    cursor = await conn.execute(
        select([Order]).as_scalar())
    orders = await cursor.fetchall()
    if orders:
        return orders
    else:
        return []


async def select_orders_to_process(conn: SAConn) -> RowProxy:
    in_tx = sa.alias(Tx, name='in_tx')
    out_tx = sa.alias(Tx, name='out_tx')
    j_in = join(Order, in_tx, Order.in_tx == in_tx.c.id.label(name="in_tx_id"))
    j_out = join(j_in, out_tx, Order.out_tx == out_tx.c.id.label(name="out_tx_id"))

    where = (
        (Order.order_type != OrderType.TRASH)
        & (in_tx.c.error == TxError.NO_ERROR)
        & (in_tx.c.confirmations >= in_tx.c.max_confirmations)
        & (out_tx.c.tx_id == None)
    )

    q = select([Order.id,
                Order.order_type,
                
                in_tx.c.coin.label('in_tx_coin'),
                in_tx.c.tx_id.label('in_tx_id'),
                in_tx.c.from_address.label('in_tx_from_address'),
                in_tx.c.to_address.label('in_tx_to_address'),
                in_tx.c.amount.label('in_tx_amount'),
                in_tx.c.created_at.label('in_tx_created_at'),
                in_tx.c.error.label('in_tx_error'),
                in_tx.c.confirmations.label('in_tx_confirmations'),
                in_tx.c.max_confirmations.label('in_tx_max_confirmations'),

                out_tx.c.coin.label('out_tx_coin'),
                out_tx.c.tx_id.label('out_tx_id'),
                out_tx.c.from_address.label('out_tx_from_address'),
                out_tx.c.to_address.label('out_tx_to_address'),
                out_tx.c.amount.label('out_tx_amount'),
                out_tx.c.created_at.label('out_tx_created_at'),
                out_tx.c.error.label('out_tx_error'),
                out_tx.c.confirmations.label('out_tx_confirmations'),
                out_tx.c.max_confirmations.label('out_tx_max_confirmations'),

                ]
               ).select_from(j_in).select_from(j_out).where(where)
    cursor = await conn.execute(q)
    subs = await cursor.fetchall()

    if subs:
        return subs
    else:
        return []
