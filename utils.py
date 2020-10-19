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
class Derivation:
    _path_list: List["Level"] = field(default_factory=list)

    def __truediv__(self, level: "Level") -> "Derivation":
        return Derivation(self._path_list + [level])

    @property
    def account(self) -> int:
        if self.depth < 3:
            raise ValueError(f"Insufficient HD tree depth: {self.depth}")
        return self._path_list[2].value

    @property
    def parent(self) -> "Derivation":
        return Derivation(self._path_list[:-1])

    @property
    def path(self) -> str:
        return "/".join(str(level) for level in self._path_list)

    @property
    def depth(self) -> int:
        return len(self._path_list)

    def to_list(self) -> List[int]:
        return [level.value for level in self._path_list]

    def __repr__(self) -> str:
        return f"m/{self.path}"

    __str__ = __repr__


@dataclass
class Level:
    _value: int

    @property
    def value(self) -> int:
        return self._value

    def h(self) -> "Level":
        return Level(self._value + BIP32_HARDEN_BIT)

    def __str__(self) -> str:
        if self._value & BIP32_HARDEN_BIT:
            value = self._value - BIP32_HARDEN_BIT
            return f"{value}'"
        return f"{self._value}"


m = Derivation()


class LedgerClient(Protocol):
    def apdu_exchange(self, INS: int, data: bytes, P1: int, P2: int) -> bytes:
        ...
