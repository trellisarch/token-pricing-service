from os import getenv

import requests
from app.config.config import Config
import time

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


def test_historical_price():
    tokens = [
        "resource_rdx1thrvr3xfs2tarm2dl9emvs26vjqxu6mqvfgvqjne940jv0lnrrg7rw"  # xUSDT
    ]
    timestamp = 1712142074
    body = {
        "tokens": tokens,
        "timestamp": timestamp,
    }
    headers = {"x-api-key": Config.API_KEY}
    resp = requests.post(f"{API_URL}/price/historicalPrice", json=body, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "prices" in data
    assert tokens[0] in data["prices"]
    price_info = data["prices"][tokens[0]]
    assert price_info["usd_price"] > 0
    assert "last_updated_at" in price_info
    assert "resource_address" not in price_info
