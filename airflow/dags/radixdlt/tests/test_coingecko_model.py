import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from radixdlt.models.coingecko_api.token_prices import CoinGeckoTokenData, Base


@pytest.fixture
def mock_session():
    with patch(
        "radixdlt.models.coingecko_api.token_prices.get_session",
        return_value=MagicMock(spec=Session),
    ) as mock:
        yield mock


@pytest.fixture
def sample_price_data():
    return {
        "prices": [
            [1724198400000, 0.02332048453228811],
            [1724245829000, 0.023533990114612397],
        ],
        "market_caps": [
            [1724198400000, 26591625.134631317],
            [1724245829000, 26848536.67778237],
        ],
        "total_volumes": [
            [1724198400000, 232396.90180502433],
            [1724245829000, 241495.94947722007],
        ],
    }


def test_get_token_prices_success(sample_price_data):
    with patch(
        "radixdlt.models.coingecko_api.token_prices.requests.Session.get",
        return_value=MagicMock(status_code=200, json=lambda: sample_price_data),
    ) as mock_get:
        result = CoinGeckoTokenData.get_token_prices("bitcoin", "usd")
        assert result == sample_price_data
        mock_get.assert_called_once()


def test_fetch_and_save_data_success(mock_session, sample_price_data):
    with patch(
        "radixdlt.models.coingecko_api.token_prices.CoinGeckoTokenData.get_token_prices",
        return_value=sample_price_data,
    ):
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_existing_data = []
        mock_session_instance.query.return_value.filter.return_value.filter.return_value = (
            mock_existing_data
        )

        CoinGeckoTokenData.fetch_and_save_data("bitcoin")

        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()


def test_fetch_and_save_data_failure(mock_session):
    with patch(
        "radixdlt.models.coingecko_api.token_prices.CoinGeckoTokenData.get_token_prices",
        return_value=None,
    ):
        with pytest.raises(
            Exception, match="Failed to retrieve data from Coingecko API"
        ):
            CoinGeckoTokenData.fetch_and_save_data("bitcoin")


def test_get_weekly_average():
    existing_token_data = [
        CoinGeckoTokenData(price=10.0, volume=1000, marketcap=10000),
        CoinGeckoTokenData(price=20.0, volume=2000, marketcap=20000),
    ]
    result = CoinGeckoTokenData.get_weekly_average(
        existing_token_data, 30.0, 3000, 30000
    )
    assert result["weeklyMovingAvgPrice"] == 20.0
    assert result["weeklyMovingAvgVolume"] == 2000.0
    assert result["weeklyMovingAvgMarketCap"] == 20000.0
