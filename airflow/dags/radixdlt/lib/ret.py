import json
import logging
import random
from os import getenv
from os.path import abspath, dirname, join
import requests
from radix_engine_toolkit import (
    PrivateKey,
    derive_virtual_account_address_from_public_key,
    TransactionHeader,
    Instructions,
    TransactionManifest,
    TransactionBuilder,
)

from radixdlt.config.config import Config


def create_transaction(transaction_metadata):
    private_key_bytes_hex = getenv("PRIVATE_KEY_BYTES", None)
    private_key_bytes = bytes.fromhex(private_key_bytes_hex)
    private_key = PrivateKey.new_secp256k1(private_key_bytes)
    address = derive_virtual_account_address_from_public_key(
        public_key=private_key.public_key(), network_id=2
    )

    network_id = Config.NETWORK_ID
    tx_construction_metadata = requests.post(
        url=f"{Config.NETWORK_GATEWAY}/transaction/construction"
    )

    start_epoch = tx_construction_metadata.json()["ledger_state"]["epoch"]
    transaction_header = TransactionHeader(
        nonce=random.randint(0, 0xFFFFFFFF),
        tip_percentage=1,
        network_id=network_id,
        notary_is_signatory=True,
        end_epoch_exclusive=start_epoch + 20,
        start_epoch_inclusive=start_epoch,
        notary_public_key=private_key.public_key(),
    )
    config_file_path = join(
        dirname(dirname(abspath(__file__))), "dags", "radixdlt", "config.json"
    )
    quotes = ""
    quote_config = json.loads(open(config_file_path).read())
    for quote in quote_config["base_resources"]:
        if quote["symbol"] in [metadata["base"] for metadata in transaction_metadata]:
            quote_price = [
                metadata["price"]
                for metadata in transaction_metadata
                if metadata["base"] == quote["symbol"]
            ][0]
            quotes += f"""
Tuple(
    Address("{quote["resource_address"]}"),
    Address("{quote_config["quote_resource"]["resource_address"]}")
) => Decimal("{quote_price}"),
"""

    instructions_list = f"""
CALL_METHOD
    Address("{Config.ORACLE_LOCK_FEE_ADDRESS}")
    "lock_fee"
    Decimal("{Config.ORACLE_LOCK_FEE}");
CALL_METHOD
    Address("{quote_config["oracle_address"]}")
    "set_price_batch"
    Map<Tuple, Decimal>(
        {quotes[:-1]}
    );
"""

    instructions = Instructions.from_string(
        string=instructions_list, network_id=network_id
    )
    transaction_manifest = TransactionManifest(instructions, [])

    notarized_transaction = (
        TransactionBuilder()
        .header(transaction_header)
        .manifest(transaction_manifest)
        .sign_with_private_key(private_key)
        .notarize_with_private_key(private_key)
    )
    logging.info(
        f"Transaction to be sent: {notarized_transaction.intent_hash().as_str()}"
    )
    return (
        "".join(hex(i)[2:].zfill(2) for i in notarized_transaction.compile()),
        address,
    )
