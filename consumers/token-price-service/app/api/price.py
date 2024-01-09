from fastapi import APIRouter, Body, HTTPException
from app.config.config import Config
from app.logger.log import get_logger
from app.models.token_price import get_latest_price
from app.schemas.token_price import TokenPrice
from app.utils.lsus import get_lsu_redemption_values

logger = get_logger()
price_router = APIRouter()


@price_router.post("/tokens", response_model=list[TokenPrice])
async def get_tokens_prices(data: dict = Body(...)):
    currency = data.get("currency")
    tokens = data.get("tokens", [])
    lsus = data.get("lsus", [])

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

    logger.info(token_prices)
    for resource_address in lsus:
        token_prices.append(get_lsu_redemption_values(resource_address))
    return token_prices
