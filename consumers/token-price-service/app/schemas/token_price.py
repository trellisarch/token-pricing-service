from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TokenPrice(BaseModel):
    resource_address: str
    usd_price: float
    last_updated_at: datetime


class LsuPrice(BaseModel):
    resource_address: str
    xrd_redemption_value: float
    usd_price: float


class TokenPricesResponse(BaseModel):
    tokens: Optional[list[TokenPrice]] = Field(default=None)
    lsus: Optional[list[LsuPrice]] = Field(default=None)


class TokenPricesRequest(BaseModel):
    currency: str
    lsus: Optional[List[str]] = []
    tokens: Optional[List[str]] = []
