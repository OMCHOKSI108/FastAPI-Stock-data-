from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Quote(BaseModel):
    symbol: str
    price: float
    timestamp: str

class SubscribeRequest(BaseModel):
    symbol: str

# New schemas for options and analytics endpoints
class IndexPriceResponse(BaseModel):
    symbol: str
    lastPrice: float
    pChange: float
    change: float
    timestamp: str

class StockPriceResponse(BaseModel):
    symbol: str
    companyName: str
    lastPrice: float
    pChange: float
    change: float
    timestamp: str

class FetchOptionsRequest(BaseModel):
    index: str
    num_strikes: int = 50

class FetchOptionsExpiryRequest(BaseModel):
    index: str
    expiry: str
    num_strikes: int = 30

class OptionStrikeData(BaseModel):
    strikePrice: float
    expiryDate: str
    CE_openInterest: Optional[float] = None
    CE_lastPrice: Optional[float] = None
    CE_totalTradedVolume: Optional[float] = None
    PE_openInterest: Optional[float] = None
    PE_lastPrice: Optional[float] = None
    PE_totalTradedVolume: Optional[float] = None

class OptionsSnapshotResponse(BaseModel):
    meta: Dict[str, Any]
    rows: List[OptionStrikeData]

class PCRResponse(BaseModel):
    pcr_by_oi: float
    pcr_by_volume: float

class TopOIStrike(BaseModel):
    strikePrice: float
    openInterest: float

class TopOIResponse(BaseModel):
    resistance_strikes: List[TopOIStrike]
    support_strikes: List[TopOIStrike]

class MaxPainResponse(BaseModel):
    max_pain_strike: Optional[int] = None
    total_loss_value: int

class AnalyticsSummaryResponse(BaseModel):
    pcr: PCRResponse
    top_oi: TopOIResponse
    max_pain: MaxPainResponse
    underlying_price: float

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

# Auth related schemas
class User(BaseModel):
    id: int
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str
