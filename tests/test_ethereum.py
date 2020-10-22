from ethereum import Ether, GWei, Transaction, sign_transaction
from lib.bip32 import h, m


def test_sign_transaction(ethereum_app):
    path = m / h(44) / h(60) / h(777) / 0 / 0
    tx = Transaction(
        nonce=0,
        gas_price=50 * GWei,
        gas=21000,
        data=b"",
        to=bytes.fromhex("004ec07d2329997267ec62b4166639513386f32e"),
        value=32 * Ether,
    )

    cmd = sign_transaction(path=path, tx=tx)
    response = cmd(ethereum_app)

    assert response.v == 28
    assert (
        response.r == 0xEC227AF09EED28F853F9A83792085A15D7A1EC726ED25AD0F25B31B58BD05A77
    )
    assert (
        response.s == 0x6AA425D410B894C99757DFCE1C1536700AA543430D667F9F2B49B4B6AE8D4037
    )
