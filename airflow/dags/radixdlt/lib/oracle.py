import logging
import requests
from radixdlt.config.config import Config
from radixdlt.lib.ret import create_transaction


def update_oracle(coin_gecko_prices, cmc_prices, pyth_prices):
    transaction_metadata = []
    logging.info(f"Gecko prices: {coin_gecko_prices}")
    logging.info(f"CMC prices: {cmc_prices}")
    logging.info(f"Pyth prices: {pyth_prices}")
    for pair, gecko_price in coin_gecko_prices.items():
        cmc_price = cmc_prices.get(pair, None)
        if cmc_price is not None:
            logging.info(f"Checking pair: {pair}")
            logging.info(f"Gecko price: {gecko_price}")
            logging.info(f"CMC price: {cmc_price}")
            logging.info(f"PYTH price: {pyth_prices[pair]}")

            gecko_lowest_price = gecko_price - gecko_price * 5 / 100
            gecko_highest_price = gecko_price + gecko_price * 5 / 100

            cmc_lowest_price = cmc_price - cmc_price * 5 / 100
            cmc_highest_price = cmc_price + cmc_price * 5 / 100

            if (gecko_lowest_price < pyth_prices[pair] < gecko_highest_price) or (
                cmc_lowest_price < pyth_prices[pair] < cmc_highest_price
            ):
                transaction_metadata.append(
                    {"base": pair.split("/")[0], "price": pyth_prices[pair]}
                )
    if len(transaction_metadata) > 0:
        logging.info(transaction_metadata)
        notarized_transaction_hex, address, txn_intent_hash = create_transaction(
            transaction_metadata
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
        return txn_intent_hash
    else:
        logging.info("Nothing to update")
        raise
