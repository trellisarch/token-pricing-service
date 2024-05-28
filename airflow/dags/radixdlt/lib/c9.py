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

        outputs = requests.post(
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
        ).json()["receipt"]["output"]

        dex_valuation_xrd: Decimal = Decimal(outputs[0]["programmatic_json"]["value"])
        liquidity_token_total_supply: Decimal = Decimal(
            outputs[1]["programmatic_json"]["value"]
        )
        price_lsulp_to_xrd: Decimal = dex_valuation_xrd.div(
            liquidity_token_total_supply
        )
        return price_lsulp_to_xrd

    def process_prices(self):
        price = self.get_pair_price(Address(Config.CAVIAR_NINE_COMPONENT_ADDRESS))
        self.prices["LSULP"] = price.as_str()


def build_quotes(prices):
    quotes = []
    for base in prices.keys():
        quotes.append({"base": base, "price": prices[base]})
    return quotes
