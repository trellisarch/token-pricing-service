from fastapi import APIRouter

from app.config.currency import Currency
from app.logger.log import get_logger
from app.schemas.token import Token
from app.models.token import Token as TokenModel


logger = get_logger()
tokens_router = APIRouter()


@tokens_router.post("", response_model=list[Token])
async def get_tokens():
    mapped_tokens = []
    tokens = TokenModel.get_latest_prices()
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
