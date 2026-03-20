import json
from os import getenv

import requests

API_URL = getenv("API_URL", "https://token-price-service.radixdlt.com")


def test_api_return_prices():
    body = {"currency": "USD", "lsus": [], "tokens": []}
    tokens = requests.post(f"{API_URL}/tokens").json()

    for token in tokens:
        body["tokens"] = [token["resource_address"]]
        token_price = requests.post(
            url=f"{API_URL}/price/tokens",
            json=body,
        )
        assert token_price.status_code == 200
        print(json.dumps(token_price.json(), indent=4))
