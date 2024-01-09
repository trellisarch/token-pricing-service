from datetime import datetime
from pydantic import BaseModel


class TokenPrice(BaseModel):
    resource_address: str
    usd_price: float
    last_updated_at: datetime
    error: str


class TokenPricesResponse(BaseModel):
    tokens: list[TokenPrice]
    lsus: list[TokenPrice]
