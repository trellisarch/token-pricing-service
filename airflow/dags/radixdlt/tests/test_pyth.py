from unittest.mock import patch

import pytest
from radixdlt.lib.pyth import get_pyth_prices, process_pyth_prices


@pytest.fixture
def mock_insert_price():
    with patch("radixdlt.lib.pyth.OracleTokenPrice.insert_price") as mock:
        yield mock


@pytest.mark.asyncio
async def test_get_pyth_prices_success():
    prices = await get_pyth_prices()
    assert prices["BTC/USD"] is not None
    assert prices["ETH/USD"] is not None
    assert prices["USDC/USD"] is not None
    assert prices["USDT/USD"] is not None
    assert prices["XRD/USD"] is not None


def test_process_pyth_prices_success(mock_insert_price):
    prices = process_pyth_prices()
    assert prices["BTC/XRD"] is not None
    assert prices["ETH/XRD"] is not None
    assert prices["USDC/XRD"] is not None
    assert prices["USDT/XRD"] is not None
