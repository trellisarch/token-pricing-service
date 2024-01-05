from datetime import datetime
from pydantic import BaseModel


class TokenPrice(BaseModel):
    resource_address: str
    usd_price: float
    usd_market_cap: float
    usd_vol_24h: float
    last_updated_at: datetime


class LsuPrice(BaseModel):
    resource_address: str
    xrd_redemption_value: float
    usd_price: float
