from enum import IntEnum
from itertools import islice
from typing import Any, List, Protocol


class LedgerClient(Protocol):
    def apdu_exchange(self, INS: int, data: bytes, P1: int, P2: int) -> bytes:
        ...


def chunk(seq: bytes, size: int) -> List[bytes]:
    it = iter(seq)
    chunks = list(iter(lambda: tuple(islice(it, size)), ()))

    return [bytes(each) for each in chunks]
