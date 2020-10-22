from typing import NamedTuple

import rlp
from construct import Byte, BytesInteger, Int32ub, PrefixedArray, Struct

from lib.bip32 import DerivationPath
from utils import LedgerClient, chunk

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
