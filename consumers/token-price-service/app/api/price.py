from fastapi import APIRouter, Body, HTTPException
from app.config.config import Config
from app.logger.log import get_logger
from app.models.token_price import get_latest_price
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

    if currency not in Config.SUPPORTED_CURRENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Currency: {currency} not supported. Supported currencies: "
            f"{Config.SUPPORTED_CURRENCIES}",
        )

    token_prices = []
    for resource_address in tokens:
        latest_price = get_latest_price(resource_address)
        if latest_price:
            token_prices.append(latest_price)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Resource: {resource_address} does not have a price",
            )
    lsus_prices = get_lsu_redemption_values(addresses=lsus)
    logger.info(lsus_prices)
    token_price_response = TokenPricesResponse(
        tokens=[TokenPrice(**token_price.__dict__) for token_price in token_prices],
        lsus=[LsuPrice(**lsu_price.__dict__) for lsu_price in lsus_prices],
    )

    return token_price_response
