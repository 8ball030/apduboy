import pytest

from bitcoin import Scheme, get_coin_version, get_random, get_wallet_public_key
from lib.bip32 import h, m


def test_get_coin_version_main(bitcoin_app):
    cmd = get_coin_version()
    response = cmd(bitcoin_app)

    assert response.p2pkh_prefix == b"\x00\x00"
    assert response.p2sh_prefix == b"\x00\x05"
    assert response.coin_family == 1
    assert response.coin_name == "Bitcoin"
    assert response.coin_ticker == "BTC"


def test_get_coin_version_test(bitcoin_test_app):
    cmd = get_coin_version()
    response = cmd(bitcoin_test_app)

    assert response.p2pkh_prefix == b"\x00o"
    assert response.p2sh_prefix == b"\x00\xc4"
    assert response.coin_family == 1
    assert response.coin_name == "Bitcoin"
    assert response.coin_ticker == "TEST"


def test_get_random(bitcoin_app):
    cmd = get_random()
    response = cmd(bitcoin_app)

    assert isinstance(response, bytes)
    assert len(response) == 248


@pytest.mark.parametrize("display_address", (True, False))
def test_get_wallet_public_key_legacy(bitcoin_test_app, display_address):
    cmd = get_wallet_public_key(display_address=display_address, scheme=Scheme.P2PKH)(
        path=m / h(44) / h(1) / h(7) / 0 / 777
    )

    response = cmd(bitcoin_test_app)

    assert response.address == "mwHRzWZSUSav1opmBpnom7wKPRjGC8qWYC"
    assert (
        response.public_key.hex()
        == "04c8021771fc9dd53da490cee6b7b54f6fb8beb3e7b1eee5a2dbd2d8c60ad832fc0210f91bc6873896740a6fafdc7a2bcb1380e515734e6de8a4972e56440addf6"
    )
    assert (
        response.chain_code.hex()
        == "593213670d5a15f2ea57f9e5958c7bca5a7cce4b6c191d1aeba7b7c515a3c539"
    )


@pytest.mark.parametrize("display_address", (True, False))
def test_get_wallet_public_key_segwit(bitcoin_test_app, display_address):
    cmd = get_wallet_public_key(
        display_address=display_address, scheme=Scheme.P2SH_P2WPKH
    )(path=m / h(49) / h(1) / h(7) / 0 / 777)

    response = cmd(bitcoin_test_app)

    assert response.address == "2NBjBQekDvoQuL6bqfFRgusWXMXA5uzfGp9"
    assert (
        response.public_key.hex()
        == "0485eef1aa16f53c383f13ba5f41d71d90b44d0e4665c9ba395e606a0886d741d46da346c52482f87744411de26c50652321f1cd0de4350f30ce9232a906de5308"
    )
    assert (
        response.chain_code.hex()
        == "4cfcf5a463ac7daf49e5baa98c614e3c09068a7d1f6da3d6a3c2088c4de64430"
    )


@pytest.mark.parametrize("display_address", (True, False))
def test_get_wallet_public_key_native_segwit(bitcoin_test_app, display_address):
    cmd = get_wallet_public_key(display_address=display_address, scheme=Scheme.P2WPKH)(
        path=m / h(84) / h(1) / h(7) / 0 / 777
    )

    response = cmd(bitcoin_test_app)

    assert response.address == "tb1qs0nfj5vm66ak6pp8jc33rf4jlwyk6qexx5fndf"
    assert (
        response.public_key.hex()
        == "04098039e2b4fd5b0f9875eacbe3b60a241ec504b42b93ade7f51a6f2b5a871ebff334a3de29825d23ba893da71d9f5dbf15c8e0cfc498c9d2fcaac9dfc237f4fb"
    )
    assert (
        response.chain_code.hex()
        == "f8568410d2b75789c405f1a376641fe1088c4ac83acb46ab25f0f80e46cfb252"
    )


def test_get_wallet_public_key_invalid_scheme():
    with pytest.raises(ValueError):
        get_wallet_public_key(display_address=False, scheme=0xDEADBEEF)(
            path=m / h(84) / h(1) / h(7) / 0 / 777
        )


def test_get_wallet_public_key_invalid_depth():
    with pytest.raises(ValueError):
        get_wallet_public_key(display_address=True, scheme=Scheme.P2PKH)(
            path=m / h(84)  # m/84'  => BIP-32 level 1
        )

    # m/84'/1'/7'/0/0/0  => BIP-32 level 6
    path = m / h(84) / h(1) / h(7) / 0 / 0 / 0
    with pytest.raises(ValueError):
        get_wallet_public_key(display_address=True, scheme=Scheme.P2PKH)(path=path)


def test_get_wallet_public_key_unexpected_scheme():
    with pytest.raises(ValueError):
        get_wallet_public_key(display_address=True, scheme=Scheme.P2PKH)(
            path=m / h(84)  # m/84'  => BIP-32 level 1
        )


def test_get_wallet_public_key_depth_3(bitcoin_test_app):
    cmd = get_wallet_public_key(display_address=False, scheme=None)(
        path=m / h(84) / h(1) / h(7)  # BIP-32 level 3
    )

    response = cmd(bitcoin_test_app)

    assert (
        response.public_key.hex()
        == "04c940923a4ee100656ebe410e138a5c2ac4bdd8c1f0373c6e0b88e098b24a2bcc0bde921db41b706bdf1ab344f106b9d082d425a33aa3572f7f1216557b327de1"
    )
    assert (
        response.chain_code.hex()
        == "ed8692b2a96463c1a456656fa74879226b4d313118a88ee4998e9a7cc2fc0b4a"
    )
