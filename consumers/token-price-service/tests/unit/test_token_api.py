from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

mock_tokens = {
    "BTC": {
        "id": 1,  # Integer ID
        "resource_address": "btc_address",
        "symbol": "BTC",
        "name": "Bitcoin",
        "usd_price": 30000,
    },
    "ETH": {
        "id": 2,  # Integer ID
        "resource_address": "eth_address",
        "symbol": "ETH",
        "name": "Ethereum",
        "usd_price": 2000,
    },
}


def test_get_tokens():
    with patch(
        "app.api.token.get_whitelisted_tokens", return_value=mock_tokens
    ) as mock_get_whitelisted_tokens:
        response = client.post("/tokens")
        assert response.status_code == 200

        tokens = response.json()
        assert len(tokens) == 2

        assert tokens[0] == {
            "id": 1,
            "resource_address": "btc_address",
            "symbol": "BTC",
            "name": "Bitcoin",
            "price": 30000,
            "currency": "USD",
        }
        assert tokens[1] == {
            "id": 2,
            "resource_address": "eth_address",
            "symbol": "ETH",
            "name": "Ethereum",
            "price": 2000,
            "currency": "USD",
        }

        # Verify patching worked
        assert mock_get_whitelisted_tokens.called
