from dataclasses import dataclass, field
from typing import List

BIP32_HARDEN_BIT = 0x80000000


@dataclass
class Derivation:
    _path_list: List["Level"] = field(default_factory=list)

    def __truediv__(self, level: int) -> "Derivation":
        return Derivation(self._path_list + [Level(level)])

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
        if not self._path_list:
            return "m"

        return "m/" + "/".join(str(level) for level in self._path_list)

    def to_list(self) -> List[int]:
        return [level.value for level in self._path_list]

    @property
    def depth(self) -> int:
        return len(self._path_list)

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.path


@dataclass
class Level:
    _value: int

    @property
    def value(self) -> int:
        return self._value

    def __str__(self) -> str:
        if self._value & BIP32_HARDEN_BIT:
            value = self._value - BIP32_HARDEN_BIT
            return f"{value}'"
        return f"{self._value}"


m = Derivation()


def h(value: int) -> int:
    return value + BIP32_HARDEN_BIT
