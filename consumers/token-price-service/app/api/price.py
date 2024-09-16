from fastapi import APIRouter, Body, HTTPException
from app.config.config import Config
from app.logger.log import get_logger
from app.models.token_price import get_latest_prices
from app.schemas.token_price import (
    TokenPricesResponse,
    TokenPricesRequest,
    TokenPrice,
    LsuPrice,
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
