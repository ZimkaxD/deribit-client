from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriceResponse(BaseModel):
    id: int
    ticker: str
    price: Decimal
    timestamp: int

    model_config = ConfigDict(from_attributes=True)