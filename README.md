# apduboy
APDUs for Humans ™️

apduboy provides a collection of Pythonic stubs that generate APDUs to communicate with the Ledger Nano S hardware wallet.

### Retrieve Ethereum addresses

```py
from ledgerwallet.client import LedgerClient
from ledgerwallet.transport import enumerate_devices

from ethereum import GetEthPublicAddressOpts, get_eth_public_address
from lib.bip32 import h, m

client = LedgerClient(enumerate_devices()[0])
opts = GetEthPublicAddressOpts(display_address=False, return_chain_code=False)

for index in range(5):
    path = m / h(44) / h(60) / h(index) / 0 / 0
    cmd = get_eth_public_address(path=path, opts=opts)
    response = cmd(client)
    print(f"Address at path {path} => 0x{response.address}")

```

### Retrieve Bitcoin addresses

```py
from ledgerwallet.client import LedgerClient
from ledgerwallet.transport import enumerate_devices

from bitcoin import GetWalletPublicKeyOpts, get_wallet_public_key
from lib.bip32 import h, m

client = LedgerClient(enumerate_devices()[0])

path = m / h(84) / h(1) / h(7) / 0 / 1234
opts = GetWalletPublicKeyOpts(display_address=False, scheme=None)
cmd = get_wallet_public_key(path=path, opts=opts)
response = cmd(client)
print(f"Address at path {path} => {response.address}")
```

### Generate a cryptographically secure random number

```py
from ledgerwallet.client import LedgerClient
from ledgerwallet.transport import enumerate_devices

from bitcoin import get_random

client = LedgerClient(enumerate_devices()[0])

cmd = get_random()
response = cmd(client)
print(f"True Random Number (hex): {response.hex()}")
```

### Sign Ethereum Transaction

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
