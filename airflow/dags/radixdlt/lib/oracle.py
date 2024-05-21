import logging
import requests

from radixdlt.config.config import Config
from radixdlt.lib.ret import create_transaction


def update_oracle(coin_gecko_prices, cmc_prices, pyth_prices, c9_prices):
    transaction_metadata = {"transactions": [], "txn_intent_hash": ""}
    logging.info(f"C9 prices: {c9_prices}")
    logging.info(f"Gecko prices: {coin_gecko_prices}")
    logging.info(f"CMC prices: {cmc_prices}")
    logging.info(f"Pyth prices: {pyth_prices}")

    for pair, pyth_price in pyth_prices.items():
        cmc_price = cmc_prices.get(pair, None)
        gecko_price = coin_gecko_prices.get(pair, None)

        if cmc_price is None and gecko_price is None:
            logging.info(f"Both gecko and cmc prices for {pair} are None")
        else:
            logging.info(f"Checking pair: {pair}")
            logging.info(f"Gecko price: {gecko_price}")
            logging.info(f"CMC price: {cmc_price}")
            logging.info(f"PYTH price: {pyth_prices[pair]}")

            logging.info("Using CMC price as primary source. Using CMC to compare pyth")
            if cmc_price is not None:
                cmc_lowest_price = (
                    cmc_price - cmc_price * Config.ORACLE_PRICE_DIFF_TRIGGER
                )
                cmc_highest_price = (
                    cmc_price + cmc_price * Config.ORACLE_PRICE_DIFF_TRIGGER
                )
                if cmc_lowest_price < pyth_prices[pair] < cmc_highest_price:
                    logging.info(f"CMC lower limit: {cmc_lowest_price}")
                    logging.info(f"CMC higher limit: {cmc_highest_price}")
                    logging.info(f"Pyth price: {pyth_price}")
                    transaction_metadata["transactions"].append(
                        {"base": pair.split("/")[0], "price": pyth_prices[pair]}
                    )
            else:
                if gecko_price is not None:
                    logging.info("CMC price is None. using Gecko instead")
                    gecko_lowest_price = (
                        gecko_price - gecko_price * Config.ORACLE_PRICE_DIFF_TRIGGER
                    )
                    gecko_highest_price = (
                        gecko_price + gecko_price * Config.ORACLE_PRICE_DIFF_TRIGGER
                    )
                    if gecko_lowest_price < pyth_prices[pair] < gecko_highest_price:
                        logging.info(f"Gecko lower limit: {gecko_lowest_price}")
                        logging.info(f"Gecko higher limit: {gecko_highest_price}")
                        logging.info(f"Pyth price: {pyth_price}")
                        transaction_metadata["transactions"].append(
                            {"base": pair.split("/")[0], "price": pyth_prices[pair]}
                        )
    transaction_metadata["transactions"].append(
        {"base": "LSULP", "price": c9_prices[0]["price"]}
    )
    if len(transaction_metadata["transactions"]) > 0:
        logging.info(transaction_metadata)
        notarized_transaction_hex, address, txn_intent_hash = create_transaction(
            transaction_metadata["transactions"]
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
