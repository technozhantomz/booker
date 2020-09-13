from enum import Enum
import json


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
    BAD_ASSET = 2
    LESS_MIN = 3
    GREATER_MAX = 4
    NO_MEMO = 5
    FLOOD_MEMO = 6
    OP_COLLISION = 7
    TX_HASH_NOT_FOUND = 8


PUBLIC_ENUMS = {"OrderType": OrderType, "TxStatus": TxStatus, "TxError": TxError}


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in PUBLIC_ENUMS.values():
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)


def as_enum(d):
    if isinstance(d, dict):
        for k, v in d.items():
            if k == "__enum__":
                name, member = d["__enum__"].split(".")
                return getattr(PUBLIC_ENUMS[name], member)
    else:
        return d
