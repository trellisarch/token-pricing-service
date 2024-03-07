import pytest
from unittest.mock import patch
from requests import JSONDecodeError
from radixdlt.lib.coingecko import process_coin_gecko_prices


@pytest.fixture
def mock_requests():
    with patch("radixdlt.lib.coingecko.requests") as mock:
        yield mock


@pytest.fixture
def mock_insert_price():
    with patch("radixdlt.lib.coingecko.OracleTokenPrice.insert_price") as mock:
        yield mock


def test_process_coin_gecko_prices_success(mock_requests, mock_insert_price):
    mock_response = mock_requests.get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "bitcoin": {"usd": 25000},
        "ethereum": {"usd": 1700},
        "radix": {"usd": 0.2},
        "tether": {"usd": 1},
        "usd-coin": {"usd": 1},
    }

    result = process_coin_gecko_prices()
    mock_requests.get.assert_called_once()

    expected_prices = {
        "BTC/XRD": 125000,
        "ETH/XRD": 8500,
        "USDT/XRD": 1 / 0.2,
        "XRD/XRD": 1,
        "USDC/XRD": 1 / 0.2,
    }

    for pair in result.keys():
        assert float(expected_prices[pair]) == float(result[pair])

    assert mock_insert_price.call_count == 5

    mock_insert_price.assert_any_call("BTC/XRD", float(125000), "CoinGecko")
    mock_insert_price.assert_any_call("ETH/XRD", float(8500), "CoinGecko")


def test_process_coin_gecko_prices_api_failure(mock_requests):
    mock_requests.get.side_effect = Exception("API Error")
    prices = process_coin_gecko_prices()
    assert prices == {}


def test_process_coin_gecko_response_not_200(mock_requests):
    mock_response = mock_requests.get.return_value
    mock_response.status_code.return_value = 400
    prices = process_coin_gecko_prices()
    assert prices == {}


def test_process_coin_gecko_response_not_json(mock_requests):
    mock_response = mock_requests.get.return_value
    mock_response.status_code = 200
    mock_response.json.side_effect = JSONDecodeError("JSON decode error", "", 0)
    prices = process_coin_gecko_prices()
    assert prices == {}
