from datetime import datetime
from typing import Optional, List, Dict
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


class HistoricalPriceRequest(BaseModel):
    tokens: List[str]
    timestamp: int  # Unix timestamp (seconds)


class HistoricalTokenPrice(BaseModel):
    usd_price: float
    last_updated_at: datetime


class HistoricalPriceResponse(BaseModel):
    prices: Dict[str, HistoricalTokenPrice]


class TokenPricesRequest(BaseModel):
    currency: str
    lsus: Optional[List[str]] = []
    tokens: Optional[List[str]] = []
