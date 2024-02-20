import datetime

from fastapi import APIRouter, Body

from app.logger.log import get_logger
from app.models.token_price import TokenPrice
from app.schemas.test import AddTokenRequest, AddTokenPriceRequest
from app.models.token import Token as TokenModel
from app.schemas.token import Token as TokenSchema
from app.schemas.token_price import TokenPrice as TokenPriceSchema

logger = get_logger()
test_router = APIRouter()


@test_router.post("/token", response_model=TokenSchema)
async def add_tokens(add_token_request: AddTokenRequest = Body(...)):
    resource_address = add_token_request.resource_address
    symbol = add_token_request.symbol
    name = add_token_request.name

    TokenModel.insert_new(resource_address, symbol, name)

    token_schema = TokenSchema(
        resource_address=resource_address,
        symbol=symbol,
        name=name,
        price=0,
        currency="USD",
        id=0,
    )
    logger.info(token_schema)
    return token_schema


@test_router.post("/price", response_model=TokenPriceSchema)
async def add_price(add_token_price_request: AddTokenPriceRequest = Body(...)):
    resource_address = add_token_price_request.resource_address
    usd_price = add_token_price_request.usd_price

    TokenPrice.insert_new(resource_address, usd_price)

    token_price_schema = TokenPriceSchema(
        resource_address=resource_address,
        usd_price=usd_price,
        last_updated_at=datetime.datetime.now(),
    )
    logger.info(token_price_schema)
    return token_price_schema
