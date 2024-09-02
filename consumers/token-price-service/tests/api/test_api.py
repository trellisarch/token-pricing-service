import json

import requests


def test_api_return_prices():
    body = {"currency": "USD", "lsus": [], "tokens": []}
    tokens = requests.post("https://dev-token-price.extratools.works/tokens").json()

    for token in tokens:
        body["tokens"] = [token["resource_address"]]
        token_price = requests.post(
            url="https://dev-token-price.extratools.works/price/tokens",
            json=body,
        )
        assert token_price.status_code == 200
        print(json.dumps(token_price.json(), indent=4))
