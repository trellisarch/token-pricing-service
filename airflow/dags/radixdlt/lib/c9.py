import requests
from radix_engine_toolkit import (
    Address,
    Decimal,
    TransactionManifest,
    ManifestBuilder,
    ManifestBuilderAddress,
)

from radixdlt.lib.price_provider import BasePriceProvider
from radixdlt.models.oracles.c9_price import C9Price


class C9PriceProvider(BasePriceProvider):

    def __init__(self):
        self.prices = {}

    @staticmethod
    def get_pair_price(pair: Address) -> Decimal:
        manifest: TransactionManifest = (
            ManifestBuilder()
            .call_method(
                ManifestBuilderAddress.STATIC(pair), method_name="get_price", args=[]
            )
            .build(0x01)
        )

        return Decimal(
            requests.post(
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
            ).json()["receipt"]["output"][0]["programmatic_json"]["fields"][0]["value"]
        )

    def process_prices(self):
        price = self.get_pair_price(
            Address(
                "component_rdx1crdhl7gel57erzgpdz3l3vr64scslq4z7vd0xgna6vh5fq5fnn9xas"
            )
        )
        C9Price.insert_c9_price(
            price=price.as_str(),
            source_address="component_rdx1crdhl7gel57erzgpdz3l3vr64scslq4z7vd0xgna6vh5fq5fnn9xas",
        )
        self.prices["LSULP"] = C9Price.get_average_price()


def build_quotes(prices):
    quotes = []
    for base in prices.keys():
        quotes.append({"base": base, "price": prices[base]})
    return quotes
