import logging
from decimal import Decimal

import requests

HEADERS = {"Content-Type": "application/json"}

MAINNET_GATEWAY = "https://mainnet.radixdlt.com"

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
        url=f"{MAINNET_GATEWAY}/status/gateway-status",
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
        url=f"{MAINNET_GATEWAY}/transaction/preview",
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
    output_json = data["receipt"]["output"][0]["programmatic_json"]

    # Precision pools return PreciseDecimal directly at top level
    # Basic pools return Enum with PreciseDecimal in fields[0]
    if "fields" in output_json:
        price_sqrt_str = output_json["fields"][0]["value"]
    else:
        price_sqrt_str = output_json["value"]

    price_sqrt = Decimal(price_sqrt_str)
    price = price_sqrt**2
    logging.info(
        f"Ociswap pool {component_address} price_sqrt: {price_sqrt}, price: {price}"
    )
    return price


def get_pool_price(component_address, dex, epoch, base, quote):
    """Returns XRD per non-XRD token, regardless of pool base/quote arrangement.

    If base is XRD, raw price is already XRD per token — returned as-is.
    If quote is XRD (base is the token), raw price is tokens per XRD — return reciprocal.
    """
    if dex == "ociswap":
        raw_price = get_ociswap_price(component_address, epoch)
    else:
        raw_price = get_c9_price(component_address, epoch)

    if base == "XRD":
        return raw_price
    else:
        return Decimal(1) / raw_price
