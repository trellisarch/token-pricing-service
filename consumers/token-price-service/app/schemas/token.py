from pydantic import BaseModel


class Token(BaseModel):
    id: int
    resource_address: str
    symbol: str
    name: str
    price: float
