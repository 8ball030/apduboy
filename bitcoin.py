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

from utils import DerivationPath, LedgerClient, Scheme


def get_random():
    INS = 0xC0
    P1 = 0x00
    P2 = 0x00

    def f(client: LedgerClient) -> bytes:
        return client.apdu_exchange(INS, b"", P1, P2)

    return f


def get_wallet_public_key(display_address: bool, scheme: Optional[Scheme] = None):
    # TODO: support user-validation token

    if scheme is not None and not Scheme.is_member(scheme):
        raise ValueError(f"unrecognized Scheme value: {scheme}")

    INS = 0x40
    P1 = 0x01 if display_address else 0x00
    P2 = scheme.value if scheme is not None else Scheme.P2PKH

    def f(path: DerivationPath):
        if display_address and path.depth != 5:
            raise ValueError(
                f"cannot derive address at BIP-32 path {path}: invalid depth {path.depth}"
            )

        if scheme and path.depth != 5:
            raise ValueError(
                f"scheme not expected at BIP-32 path {path}: {scheme.name}"
            )

        path_construct = PrefixedArray(Byte, Int32ub)
        path_apdu = path_construct.build(path.to_list())

        data = path_apdu

        class DeviceResponse(NamedTuple):
            public_key: bytes
            address: str
            chain_code: bytes

        def g(client: LedgerClient) -> DeviceResponse:
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

        return g

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
