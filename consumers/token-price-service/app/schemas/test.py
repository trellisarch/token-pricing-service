from datetime import datetime
from pydantic import BaseModel


class AddTokenRequest(BaseModel):
    resource_address: str
    symbol: str
    name: str


class AddTokenPriceRequest(BaseModel):
    resource_address: str
    usd_price: float
