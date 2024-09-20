import time
import requests
from radix_engine_toolkit import (
    Address,
    Decimal,
    TransactionManifest,
    ManifestBuilder,
    ManifestBuilderAddress,
)

from radixdlt.config.config import Config
from radixdlt.lib.price_provider import BasePriceProvider


class C9PriceProvider(BasePriceProvider):

    def __init__(self):
        self.prices = {}

    @staticmethod
    def get_pair_price(pair: Address) -> Decimal:
        manifest: TransactionManifest = (
            ManifestBuilder()
            .call_method(
                ManifestBuilderAddress.STATIC(pair), "get_dex_valuation_xrd", []
            )
            .call_method(
                ManifestBuilderAddress.STATIC(pair),
                "get_liquidity_token_total_supply",
                [],
            )
            .build(0x01)
        )
        start_time = time.time()

        try:
            response = requests.post(
                "https://mainnet.radixdlt.com/transaction/preview",
                json={
                    "manifest": manifest.instructions().as_str(),
                    "blobs_hex": [],
                    "start_epoch_inclusive": 1,
                    "end_epoch_exclusive": 2,
                    "tip_percentage": 0,
                    "nonce": 1,
                    "signer_public_keys": [],
                    "flags": {
                        "use_free_credit": True,
                        "assume_all_signature_proofs": True,
                        "skip_epoch_check": True,
                    },
                },
            )
            # Record the duration in milliseconds
            duration = (time.time() - start_time) * 1000  # convert to milliseconds
            Config.statsDClient.timing('oracle.c9_txn_preview.request_time', duration)
            
            if response.status_code not in (200, 204):
                Config.statsDClient.incr("dag_oracle.c9_txn_preview.failed")
                raise Exception("Cavirnine returned error")

            Config.statsDClient.incr("dag_oracle.c9_txn_preview.passed")
                        
            outputs =response.json()["receipt"]["output"]
            dex_valuation_xrd: Decimal = Decimal(outputs[0]["programmatic_json"]["value"])
            liquidity_token_total_supply: Decimal = Decimal(
                outputs[1]["programmatic_json"]["value"]
            )
            price_lsulp_to_xrd: Decimal = dex_valuation_xrd.div(
                liquidity_token_total_supply
            )
            Config.statsDClient.incr(f"dag_oracle.c9_txn_preview.fetch.lslup.passed")
            return price_lsulp_to_xrd
        except Exception:
            Config.statsDClient.incr("dag_oracle.c9_txn_preview.failed")
            Config.statsDClient.incr(f"dag_oracle.c9_txn_preview.fetch.lslup.failed")
            
            raise

    def process_prices(self):
        price = self.get_pair_price(Address(Config.CAVIAR_NINE_COMPONENT_ADDRESS))
        self.prices["LSULP"] = price.as_str()


def build_quotes(prices):
    quotes = []
    for base in prices.keys():
        quotes.append({"base": base, "price": prices[base]})
    return quotes
