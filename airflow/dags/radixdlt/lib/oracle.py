import logging
import requests

from radixdlt.config.config import Config
from radixdlt.lib.c9 import build_quotes
from radixdlt.lib.pyth import validate_prices
from radixdlt.lib.radix_charts import validate_prices as validate_charts_prices
from radixdlt.lib.ret import create_transaction


class OracleUpdater:

    @staticmethod
    def update_prices(pyth_prices, c9_prices, radix_charts_prices):
        quotes = []

        quotes.extend(validate_prices(pyth_prices))
        quotes.extend(build_quotes(c9_prices))
        quotes.extend(validate_charts_prices(radix_charts_prices))

        transaction_metadata = {"quotes": quotes, "txn_intent_hash": ""}
        if len(transaction_metadata["quotes"]) > 0:
            logging.info(transaction_metadata)
            notarized_transaction_hex, address, txn_intent_hash = create_transaction(
                transaction_metadata["quotes"]
            )
            submit_transaction_body = {
                "notarized_transaction_hex": notarized_transaction_hex
            }
            response = requests.post(
                url=f"{Config.NETWORK_GATEWAY}/transaction/submit",
                json=submit_transaction_body,
            )
            logging.info("Oracle price update transaction submitted successfully")
            logging.info(response.text)
            transaction_metadata["txn_intent_hash"] = txn_intent_hash
            return transaction_metadata
        else:
            logging.info("Nothing to update")
            raise
