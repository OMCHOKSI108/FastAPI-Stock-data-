from pydantic import BaseModel
from typing import Optional

class Quote(BaseModel):
    symbol: str
    price: float
    timestamp: str

class SubscribeRequest(BaseModel):
    symbol: str
