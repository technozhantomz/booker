import logging
from aiopg.sa.result import RowProxy
from sqlalchemy import inspect


def get_logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(level=logging.INFO)
    formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    log.addHandler(ch)

    return log


def object_as_dict(obj) -> dict:
    """Represent any sqlalchemy model object as python dict"""
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
