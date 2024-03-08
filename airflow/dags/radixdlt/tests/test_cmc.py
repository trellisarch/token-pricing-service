from datetime import datetime
from unittest.mock import patch, MagicMock
import requests
from radixdlt.config.config import Config
from radixdlt.lib.cmc import process_cmc_prices
from radixdlt.models.oracles.token_price import OracleTokenPrice


class TestProcessCmcPrices:

    @patch.object(Config, "ORACLE_CMC_PAIRS")
    @patch.object(OracleTokenPrice, "insert_price")
    def test_successful_price_retrieval(self, mock_insert_price, mock_cmc_pairs):
        utc_now_seconds = int(datetime.utcnow().timestamp())
        now_date = datetime.utcfromtimestamp(utc_now_seconds)
        now_string = now_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        mock_cmc_pairs.split.return_value = ["BTC/XRD", "ETH/XRD"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "BTC": [
                    {"last_updated": now_string, "quote": {"XRD": {"price": 40000}}}
                ],
                "ETH": [
                    {"quote": {"XRD": {"price": 1000}}, "last_updated": now_string}
                ],
            }
        }
        with patch.object(requests, "get", return_value=mock_response):
            process_cmc_prices()
            mock_insert_price.assert_any_call("BTC/XRD", 40000, "CMC")
            mock_insert_price.assert_any_call("ETH/XRD", 1000, "CMC")
