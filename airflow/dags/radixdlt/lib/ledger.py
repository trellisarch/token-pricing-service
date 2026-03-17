import logging
from decimal import Decimal

import requests

from radixdlt.config.config import Config

HEADERS = {"Content-Type": "application/json"}

PREVIEW_FLAGS = {
    "use_free_credit": True,
    "assume_all_signature_proofs": True,
    "skip_epoch_check": True,
    "disable_auth_checks": False,
}

SIGNER_PUBLIC_KEYS = [
    {
        "key_type": "EcdsaSecp256k1",
        "key_hex": "0388207bf34f38fe057884e1efba2f54d1bfb3daf59894db12b1709315cfc77617",
    }
]


def get_current_epoch():
    response = requests.post(
        url=f"{Config.NETWORK_GATEWAY}/status/gateway-status",
        headers=HEADERS,
        json={},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["ledger_state"]["epoch"]


def preview_transaction(manifest, epoch):
    payload = {
        "manifest": manifest,
        "start_epoch_inclusive": epoch,
        "end_epoch_exclusive": epoch + 2,
        "tip_percentage": 0,
        "nonce": 1,
        "signer_public_keys": SIGNER_PUBLIC_KEYS,
        "flags": PREVIEW_FLAGS,
    }
    response = requests.post(
        url=f"{Config.NETWORK_GATEWAY}/transaction/preview",
        headers=HEADERS,
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_c9_price(component_address, epoch):
    manifest = f'CALL_METHOD\nAddress("{component_address}")\n"get_price"\n;'
    data = preview_transaction(manifest, epoch)
    price_str = data["receipt"]["output"][0]["programmatic_json"]["fields"][0]["value"]
    logging.info(f"C9 pool {component_address} price: {price_str}")
    return Decimal(price_str)


def get_ociswap_price(component_address, epoch):
    manifest = f'CALL_METHOD\nAddress("{component_address}")\n"price_sqrt"\n;'
    data = preview_transaction(manifest, epoch)
    price_sqrt = Decimal(data["receipt"]["output"][0]["programmatic_json"]["fields"][0]["value"])
    price = price_sqrt ** 2
    logging.info(f"Ociswap pool {component_address} price_sqrt: {price_sqrt}, price: {price}")
    return price


def get_pool_price(component_address, dex, epoch):
    if dex == "ociswap":
        return get_ociswap_price(component_address, epoch)
    return get_c9_price(component_address, epoch)
