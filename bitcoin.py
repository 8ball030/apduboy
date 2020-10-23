from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple, Optional

from construct import (
    Byte,
    Bytes,
    GreedyBytes,
    Int8ub,
    Int32ub,
    PascalString,
    Prefixed,
    PrefixedArray,
    Struct,
)

from lib.bip32 import DerivationPath
from utils import LedgerClient


class Scheme(IntEnum):
    P2PKH = 0x00
    P2SH_P2WPKH = 0x01
    P2WPKH = 0x02

    @classmethod
    def is_member(cls, item: int) -> bool:
        return item in {each.value for each in cls}


def get_random():
    INS = 0xC0
    P1 = 0x00
    P2 = 0x00

    def f(client: LedgerClient) -> bytes:
        return client.apdu_exchange(INS, b"", P1, P2)

    return f


@dataclass
class GetWalletPublicKeyOpts:
    display_address: bool
    scheme: Optional[Scheme] = None


def get_wallet_public_key(path: DerivationPath, opts: GetWalletPublicKeyOpts):
    # TODO: support user-validation token

    if opts.scheme is not None and not Scheme.is_member(opts.scheme):
        raise ValueError(f"unrecognized Scheme value: {opts.scheme}")

    INS = 0x40
    P1 = 0x01 if opts.display_address else 0x00
    P2 = opts.scheme.value if opts.scheme is not None else Scheme.P2PKH

    if opts.display_address and path.depth != 5:
        raise ValueError(
            f"cannot derive address at BIP-32 path {path}: invalid depth {path.depth}"
        )

    if opts.scheme is not None and path.depth != 5:
        raise ValueError(
            f"scheme not expected at BIP-32 path {path}: {opts.scheme.name}"
        )

    path_construct = PrefixedArray(Byte, Int32ub)
    path_apdu = path_construct.build(path.to_list())

    data = path_apdu

    class DeviceResponse(NamedTuple):
        public_key: bytes
        address: str
        chain_code: bytes

    def f(client: LedgerClient) -> DeviceResponse:
        response = client.apdu_exchange(INS, data, P1, P2)

        response_template = Struct(
            public_key=Prefixed(Int8ub, GreedyBytes),
            address=PascalString(Int8ub, "ascii"),
            chain_code=Bytes(32),
        )

        parsed_response = response_template.parse(response)
        return DeviceResponse(
            public_key=parsed_response.public_key,
            address=parsed_response.address,
            chain_code=parsed_response.chain_code,
        )

    return f

    return f


def get_coin_version():
    INS = 0x16
    P1 = 0x00
    P2 = 0x00

    class DeviceResponse(NamedTuple):
        p2pkh_prefix: bytes
        p2sh_prefix: bytes
        coin_family: int
        coin_name: str
        coin_ticker: str

    def f(client: LedgerClient) -> DeviceResponse:
        response = client.apdu_exchange(INS, b"", P1, P2)

        response_template = Struct(
            p2pkh_prefix=Bytes(2),
            p2sh_prefix=Bytes(2),
            coin_family=Int8ub,
            coin_name=PascalString(Int8ub, "ascii"),
            coin_ticker=PascalString(Int8ub, "ascii"),
        )

        parsed_response = response_template.parse(response)
        return DeviceResponse(
            p2pkh_prefix=parsed_response.p2pkh_prefix,
            p2sh_prefix=parsed_response.p2sh_prefix,
            coin_family=parsed_response.coin_family,
            coin_name=parsed_response.coin_name,
            coin_ticker=parsed_response.coin_ticker,
        )

    return f
