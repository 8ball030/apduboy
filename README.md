# apduboy
APDUs for Humans ™️

apduboy provides a collection of Pythonic stubs that generate APDUs to communicate with the Ledger Nano S hardware wallet.

```py
from apduboy.ethereum import Ether, GWei, Transaction, sign_transaction
from apduboy.lib.bip32 import h, m

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
    response = cmd(device)  # device can be anything that provides an APDU exchange.
```

apduboy is currently in alpha. Please do NOT use this for signing real transactions.
