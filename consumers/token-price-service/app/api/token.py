from fastapi import APIRouter

from app.config.currency import Currency
from app.logger.log import get_logger
from app.models.token import fetch_tokens_with_latest_price
from app.schemas.token import Token


logger = get_logger()
tokens_router = APIRouter()


@tokens_router.post("/", response_model=list[Token])
async def get_tokens():
    tokens = fetch_tokens_with_latest_price()

    mapped_tokens = []
    for token_obj, price_obj in tokens:
        token_data = {
            "id": token_obj.id,
            "resource_address": token_obj.resource_address,
            "symbol": token_obj.symbol,
            "name": token_obj.name,
            "price": price_obj.usd_price,
            "currency": Currency.USD,
        }
        mapped_token = Token(**token_data)
        mapped_tokens.append(mapped_token)

    logger.info(mapped_tokens)
    return mapped_tokens
