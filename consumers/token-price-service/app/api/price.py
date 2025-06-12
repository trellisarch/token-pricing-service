from fastapi import APIRouter, Body, HTTPException, Depends, Header
from app.config.config import Config
from app.logger.log import get_logger
from app.models.token_price import get_latest_prices, get_prices_closest_to_timestamp
from app.schemas.token_price import (
    TokenPricesResponse,
    TokenPricesRequest,
    TokenPrice,
    LsuPrice,
    HistoricalPriceRequest,
    HistoricalPriceResponse,
    HistoricalTokenPrice,
)
from app.utils.lsus import get_lsu_redemption_values
from prometheus_client import Histogram
import time

logger = get_logger()
price_router = APIRouter()

request_duration_with_lsus = Histogram(
    "token_price_request_duration_with_lsus",
    "Request duration with lsus parameter",
    buckets=[0.1, 0.3, 0.5, 0.8, 1, 1.5, 2, 5, 10],
)
request_duration_without_lsus = Histogram(
    "token_price_request_duration_without_lsus",
    "Request duration without lsus parameter",
    buckets=[0.1, 0.3, 0.5, 0.8, 1, 1.5, 2, 5, 10],
)


@price_router.post("/tokens", response_model=TokenPricesResponse)
async def get_tokens_prices(data: TokenPricesRequest = Body(...)):
    start_time = time.time()

    currency = data.currency
    tokens = data.tokens
    lsus = data.lsus

    if currency.upper() not in Config.SUPPORTED_CURRENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Currency: {currency} not supported. Supported currencies: "
            f"{Config.SUPPORTED_CURRENCIES}",
        )

    token_prices = []
    token_prices.extend(get_latest_prices(tokens))

    if len(lsus) > 0:
        lsus_prices = get_lsu_redemption_values(addresses=lsus)
    else:
        lsus_prices = []

    logger.info(lsus_prices)
    token_price_response = TokenPricesResponse(
        tokens=[TokenPrice(**token_price.__dict__) for token_price in token_prices],
        lsus=[LsuPrice(**lsu_price.__dict__) for lsu_price in lsus_prices],
    )

    if len(lsus) > 0:
        request_duration_with_lsus.observe(time.time() - start_time)
    else:
        request_duration_without_lsus.observe(time.time() - start_time)

    return token_price_response


def api_key_auth(x_api_key: str = Header(...)):
    if x_api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")


@price_router.post("/historicalPrice", response_model=HistoricalPriceResponse)
async def get_historical_price(
    data: HistoricalPriceRequest = Body(...),
    _: None = Depends(api_key_auth),
):
    """
    Returns price for each token at the time closest to the given timestamp.
    """
    if not data.tokens or not isinstance(data.tokens, list) or len(data.tokens) == 0:
        raise HTTPException(status_code=400, detail="Token list must be provided.")
    if not isinstance(data.timestamp, int):
        raise HTTPException(
            status_code=400, detail="Timestamp must be an integer (unix seconds)."
        )

    prices = get_prices_closest_to_timestamp(data.tokens, data.timestamp)

    missing_tokens = [
        token for token in data.tokens if token not in prices or prices[token] is None
    ]
    if missing_tokens:
        raise HTTPException(
            status_code=424,
            detail=f"Price missing for tokens: {', '.join(missing_tokens)}",
        )

    resp = {}
    for token, price in prices.items():
        resp[token] = HistoricalTokenPrice(
            usd_price=price.usd_price,
            last_updated_at=price.last_updated_at,
        )
    return HistoricalPriceResponse(prices=resp)
