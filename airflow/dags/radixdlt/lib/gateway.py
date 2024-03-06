import logging
from time import sleep

import requests
from radixdlt.config.config import Config


def is_transaction_committed(txn_intent_hash):
    retry_attempts = 0
    transaction_committed = False
    body = {"intent_hash": txn_intent_hash}
    while retry_attempts < 6 and not transaction_committed:
        txn_status = requests.post(
            url=f"{Config.NETWORK_GATEWAY}/transaction/status",
            json=body,
            headers={"accept": "application/json"},
        )
        logging.info(f"Transaction status: {txn_status.text}")
        if txn_status.status_code == 200:
            if txn_status.json()["status"] == "CommittedSuccess":
                transaction_committed = True
        sleep(10)
        retry_attempts += 1
    return transaction_committed
