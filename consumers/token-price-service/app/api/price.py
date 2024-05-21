from fastapi import APIRouter, Body, HTTPException
from app.config.config import Config
from app.logger.log import get_logger
from app.models.token_price import get_latest_prices, get_latest_price
from app.schemas.token_price import (
    TokenPricesResponse,
    TokenPricesRequest,
    TokenPrice,
    LsuPrice,
)
from app.utils.lsus import get_lsu_redemption_values

logger = get_logger()
price_router = APIRouter()


@price_router.post("/tokens", response_model=TokenPricesResponse)
async def get_tokens_prices(data: TokenPricesRequest = Body(...)):
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
    for token in tokens:
        token_prices.append(get_latest_price(token))

    if len(lsus) > 0:
        lsus_prices = get_lsu_redemption_values(addresses=lsus)
    else:
        lsus_prices = []
    logger.info(lsus_prices)
    token_price_response = TokenPricesResponse(
        tokens=[TokenPrice(**token_price.__dict__) for token_price in token_prices],
        lsus=[LsuPrice(**lsu_price.__dict__) for lsu_price in lsus_prices],
    )

    return token_price_response
