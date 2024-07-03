from os import getenv

import requests

API_URL = getenv("API_URL", "https://dev-token-price.extratools.works")


def test_get_all_tokens():
    tokens = requests.post(f"{API_URL}/tokens").json()
    for token in tokens:
        assert token["id"] != ""
        assert token["resource_address"].startswith("resource_rdx")


def test_get_price_for_single_token():
    body = {
        "currency": "USD",
        "lsus": [],
        "tokens": [
            "resource_rdx1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxradxrd",
        ],
    }
    prices = requests.post(f"{API_URL}/price/tokens", json=body).json()
    for token in body["tokens"]:
        token_price = [
            price for price in prices["tokens"] if price["resource_address"] == token
        ][0]
        assert token_price["usd_price"] > 0


def test_get_prices_for_multiple_token():
    body = {
        "currency": "USD",
        "lsus": [],
        "tokens": [
            "resource_rdx1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxradxrd",
            "resource_rdx1t52pvtk5wfhltchwh3rkzls2x0r98fw9cjhpyrf3vsykhkuwrf7jg8",
        ],
    }
    prices = requests.post(f"{API_URL}/price/tokens", json=body).json()
    for token in body["tokens"]:
        token_price = [
            price for price in prices["tokens"] if price["resource_address"] == token
        ][0]
        assert token_price["usd_price"] > 0
