from fastapi import APIRouter

from app.config.currency import Currency
from app.logger.log import get_logger

from app.models.token_price import get_whitelisted_tokens
from app.schemas.token import Token

logger = get_logger()
tokens_router = APIRouter()


@tokens_router.post("", response_model=list[Token])
async def get_tokens():
    mapped_tokens = []
    tokens = get_whitelisted_tokens()
    for symbol, price in tokens.items():
        token_data = {
            "id": price["id"],
            "resource_address": price["resource_address"],
            "symbol": price["symbol"],
            "name": price["name"],
            "price": price["usd_price"],
            "currency": Currency.USD,
        }
        mapped_token = Token(**token_data)
        mapped_tokens.append(mapped_token)
    logger.debug(mapped_tokens)
    return mapped_tokens
