from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
import os
from ..providers import binance_provider
from ..schemas import CryptoQuote, HistoricalData

router = APIRouter()

# Load subscriptions
SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'subscriptions.json')
with open(SUBSCRIPTIONS_FILE, 'r') as f:
    subscriptions = json.load(f)

CRYPTO_SYMBOLS = [item['symbol'] for item in subscriptions['crypto']]

@router.get("/list", response_model=List[str])
async def get_available_crypto():
    """Get list of all available cryptocurrencies"""
    return CRYPTO_SYMBOLS

@router.get("/quote/{symbol}", response_model=CryptoQuote)
async def get_crypto_quote(symbol: str):
    """Get cryptocurrency quote from Binance"""
    symbol = symbol.upper()
    if symbol not in CRYPTO_SYMBOLS:
        raise HTTPException(status_code=404, detail="Crypto symbol not in available list")
    
    try:
        quote = await binance_provider.get_crypto_price(symbol)
        if quote:
            return CryptoQuote(
                symbol=quote['symbol'],
                price=quote['price'],
                timestamp=quote['timestamp']
            )
        else:
            raise HTTPException(status_code=404, detail="Failed to fetch quote")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical/{symbol}", response_model=HistoricalData)
async def get_crypto_historical(symbol: str, interval: str = Query("1d", description="Interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M"), limit: int = Query(100, description="Limit: 1-1000")):
    """Get historical data for cryptocurrency from Binance"""
    symbol = symbol.upper()
    if symbol not in CRYPTO_SYMBOLS:
        raise HTTPException(status_code=404, detail="Crypto symbol not in available list")
    
    try:
        data = await binance_provider.get_crypto_historical(symbol, interval, limit)
        if data:
            return HistoricalData(symbol=symbol, period=f"{interval}_{limit}", data=data)
        else:
            raise HTTPException(status_code=404, detail="No historical data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
