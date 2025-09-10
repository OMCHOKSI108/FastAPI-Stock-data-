from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Quote(BaseModel):
    symbol: str
    price: float
    timestamp: str

class SubscribeRequest(BaseModel):
    symbol: str

class StockQuote(BaseModel):
    symbol: str
    companyName: Optional[str] = None
    lastPrice: Optional[float] = None
    pChange: Optional[float] = None
    change: Optional[float] = None
    timestamp: str

class CryptoQuote(BaseModel):
    symbol: str
    price: float
    timestamp: str

class HistoricalData(BaseModel):
    symbol: str
    period: str
    data: List[Dict[str, Any]]

class IndexPriceResponse(BaseModel):
    symbol: str
    lastPrice: float
    pChange: float
    change: float
    timestamp: str

class FetchOptionsRequest(BaseModel):
    index: str
    num_strikes: int = 25

class FetchExpiryRequest(BaseModel):
    index: str
    expiry: str
    num_strikes: int = 25

class FetchResultMeta(BaseModel):
    createdAtUTC: str
    indexName: str
    nearestExpiry: Optional[str] = None
    selectedExpiry: Optional[str] = None
    underlyingValue: Optional[float] = None
    atmStrike: Optional[int] = None
    selectedStrikesRange: Optional[List[int]] = None
    totalStrikesFetched: Optional[int] = None

class AnalyticsResponse(BaseModel):
    meta: FetchResultMeta
    pcr: Dict[str, float]
    top_oi: Dict[str, List[Dict[str, Any]]]
    max_pain: Dict[str, Any]

class OptionPriceResponse(BaseModel):
    symbol: str
    strike: float
    expiry: str
    option_type: str  # 'CE' or 'PE'
    lastPrice: Optional[float] = None
    openInterest: Optional[int] = None
    volume: Optional[int] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    timestamp: str

class DirectOptionsData(BaseModel):
    index: str
    expiry: str
    underlying_value: float
    options: List[Dict[str, Any]]
    timestamp: str

class OptionStrikeData(BaseModel):
    index: str
    strike: float
    expiry: str
    option_type: str  # 'CE', 'PE', or 'BOTH'
    ce_data: Optional[Dict[str, Any]] = None
    pe_data: Optional[Dict[str, Any]] = None
    underlying_value: float
    timestamp: str

class OptionHistoricalData(BaseModel):
    symbol: str
    strike: float
    expiry: str
    option_type: str
    period: str
    data: List[Dict[str, Any]]
    timestamp: str

class ForexQuote(BaseModel):
    symbol: str
    base_currency: str
    quote_currency: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    timestamp: str

class ForexPair(BaseModel):
    symbol: str
    base_currency: str
    quote_currency: str
    description: str

class ForexHistoricalData(BaseModel):
    symbol: str
    period: str
    data: List[Dict[str, Any]]
    timestamp: str
