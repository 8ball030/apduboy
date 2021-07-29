from dataclasses import dataclass
from typing import NamedTuple, Optional

import rlp
from construct import (
    Byte,
    Bytes,
    BytesInteger,
    GreedyBytes,
    Int8ub,
    Int32ub,
    PascalString,
    Prefixed,
    PrefixedArray,
    Struct,
)

from .lib.bip32 import DerivationPath
from .utils import LedgerClient, chunk

address = rlp.sedes.Binary.fixed_length(20, allow_empty=True)

Wei = 1
GWei = 10 ** 9
Ether = 10 ** 18


class Transaction(rlp.Serializable):
    fields = (
        ("nonce", rlp.sedes.big_endian_int),
        ("gas_price", rlp.sedes.big_endian_int),
        ("gas", rlp.sedes.big_endian_int),
        ("to", address),
        ("value", rlp.sedes.big_endian_int),
        ("data", rlp.sedes.binary),
    )


def sign_transaction(path: DerivationPath, tx: Transaction):
    INS = 0x04
    P2 = 0x00

    path_construct = PrefixedArray(Byte, Int32ub)
    path_apdu = path_construct.build(path.to_list())

    data = path_apdu + rlp.encode(tx)

    class DeviceResponse(NamedTuple):
        v: int
        r: int
        s: int

    def f(client: LedgerClient) -> DeviceResponse:
        raw_response = bytes()

        for idx, each in enumerate(chunk(data, 255)):
            P1 = 0x00 if idx == 0 else 0x80
            raw_response = client.apdu_exchange(INS, each, P1, P2)

        response_template = Struct(
            v=BytesInteger(1),
            r=BytesInteger(32),
            s=BytesInteger(32),
        )
        parsed_response = response_template.parse(raw_response)

        return DeviceResponse(
            v=parsed_response.v,
            r=parsed_response.r,
            s=parsed_response.s,
        )

    return f


@dataclass
class GetEthPublicAddressOpts:
    display_address: bool
    return_chain_code: bool = False


def get_eth_public_address(path: DerivationPath, opts: GetEthPublicAddressOpts):
    INS = 0x02
    P1 = 0x01 if opts.display_address else 0x00
    P2 = 0x01 if opts.return_chain_code else 0x00

    path_construct = PrefixedArray(Byte, Int32ub)
    path_apdu = path_construct.build(path.to_list())

    data = path_apdu

    class DeviceResponse(NamedTuple):
        public_key: bytes
        address: str
        chain_code: Optional[bytes]

    def f(client: LedgerClient) -> DeviceResponse:
        response = client.apdu_exchange(INS, data, P1, P2)

        struct_kwargs = dict(
            public_key=Prefixed(Int8ub, GreedyBytes),
            address=PascalString(Int8ub, "ascii"),
        )
        if opts.return_chain_code:
            struct_kwargs["chain_code"] = Bytes(32)

        response_template = Struct(**struct_kwargs)

        parsed_response = response_template.parse(response)
        return DeviceResponse(
            public_key=parsed_response.public_key,
            address=parsed_response.address,
            chain_code=parsed_response.chain_code if opts.return_chain_code else None,
        )

    return f
