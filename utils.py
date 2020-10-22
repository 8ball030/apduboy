from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, List, Protocol


class Scheme(IntEnum):
    P2PKH = 0x00
    P2SH_P2WPKH = 0x01
    P2WPKH = 0x02

    @classmethod
    def is_member(cls, item: Any) -> bool:
        return item in {each.value for each in cls}


BIP32_HARDEN_BIT = 0x80000000


@dataclass
class DerivationPath:
    _path_list: List[int] = field(default_factory=list)

    def __truediv__(self, level: int) -> "DerivationPath":
        return DerivationPath(self._path_list + [level])

    @property
    def account(self) -> int:
        if self.depth < 3:
            raise ValueError(f"Insufficient HD tree depth: {self.depth}")
        return self._path_list[2]

    @property
    def parent(self) -> "DerivationPath":
        return DerivationPath(self._path_list[:-1])

    @property
    def path(self) -> str:
        return "/".join(self._serialize_level(level) for level in self._path_list)

    @staticmethod
    def _serialize_level(level: int) -> str:
        if level & BIP32_HARDEN_BIT:
            value = level - BIP32_HARDEN_BIT
            return f"{value}'"
        return f"{level}"

    @property
    def depth(self) -> int:
        return len(self._path_list)

    def to_list(self) -> List[int]:
        return self._path_list

    def __repr__(self) -> str:
        return f"m/{self.path}"

    __str__ = __repr__


def h(value: int) -> int:
    return value + BIP32_HARDEN_BIT


m = DerivationPath()


class LedgerClient(Protocol):
    def apdu_exchange(self, INS: int, data: bytes, P1: int, P2: int) -> bytes:
        ...
