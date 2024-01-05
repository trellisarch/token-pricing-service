from fastapi import APIRouter, Body, HTTPException
from app.config.config import Config
from app.logger.log import get_logger
from app.models.token_price import get_latest_price
from app.schemas.token_price import TokenPrice, LsuPrice
from app.utils.lsus import get_lsu_redemption_values

logger = get_logger()
price_router = APIRouter()


@price_router.post("/tokens", response_model=list[TokenPrice])
async def get_tokens_prices(data: dict = Body(...)):
    currency = data.get("currency")
    tokens = data.get("tokens", [])

    if currency not in Config.SUPPORTED_CURRENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Currency: {currency} not supported. Supported currencies: "
            f"{Config.SUPPORTED_CURRENCIES}",
        )

    token_prices = []
    for resource_address in tokens:
        token_prices.append(get_latest_price(resource_address))
    logger.info(token_prices)
    return token_prices


@price_router.post("/lsus", response_model=list[LsuPrice])
async def get_lsus_prices(data: dict = Body(...)):
    currency = data.get("currency")
    lsus = data.get("lsus", [])

    if currency not in Config.SUPPORTED_CURRENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Currency: {currency} not supported. Supported currencies: "
            f"{Config.SUPPORTED_CURRENCIES}",
        )

    lsus_prices = []
    for resource_address in lsus:
        lsus_prices.append(get_lsu_redemption_values(resource_address))
    logger.info(lsus_prices)
    return lsus_prices
