from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import sys
import os

# Add the parent directory to sys.path to import data_gather_stocks
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.data_gather_stocks import fetch_index_price, fetch_stock_price
from app.schemas import IndexPriceResponse, StockPriceResponse, User
from app.auth import get_current_user

router = APIRouter()

@router.get("/price/index/{index}", response_model=IndexPriceResponse)
async def get_index_price(index: str):
    """
    Get latest price data for a given NSE index.
    """
    try:
        data = fetch_index_price(index.upper())
        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])

        return IndexPriceResponse(
            symbol=data['symbol'],
            lastPrice=data['lastPrice'],
            pChange=data['pChange'],
            change=data['change'],
            timestamp=data['timestamp']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch index price: {str(e)}")


@router.get("/price/index", response_model=IndexPriceResponse)
async def get_index_price_query(index: Optional[str] = None):
    """Query-parameter compatible endpoint: /price/index?index=NIFTY
    This keeps backwards compatibility with clients that use query parameters.
    """
    if not index:
        raise HTTPException(status_code=400, detail="Missing required query parameter: index")

    # Basic validation: if user passed a stock symbol like 'YESBANK.NS', return a clear error
    if ".NS" in index.upper() or index.strip().upper().endswith('.NS'):
        raise HTTPException(status_code=400, detail=f"Provided symbol '{index}' looks like a stock symbol; this endpoint expects an index name (for example: NIFTY, BANKNIFTY)")

    try:
        data = fetch_index_price(index.upper())
        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])

        return IndexPriceResponse(
            symbol=data['symbol'],
            lastPrice=data['lastPrice'],
            pChange=data['pChange'],
            change=data['change'],
            timestamp=data['timestamp']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch index price: {str(e)}")

@router.get("/price/stock/{symbol}", response_model=StockPriceResponse)
async def get_stock_price(symbol: str):
    """
    Get latest price data for a given NSE stock symbol.
    """
    try:
        data = fetch_stock_price(symbol.upper())
        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])

        return StockPriceResponse(
            symbol=data['symbol'],
            companyName=data['companyName'],
            lastPrice=data['lastPrice'],
            pChange=data['pChange'],
            change=data['change'],
            timestamp=data['timestamp']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock price: {str(e)}")


@router.get("/price/stock", response_model=StockPriceResponse)
async def get_stock_price_query(symbol: Optional[str] = None):
    """Query-parameter compatible endpoint: /price/stock?symbol=RELIANCE.NS or ?symbol=RELIANCE
    This keeps backwards compatibility with clients that use query parameters.
    """
    if not symbol:
        raise HTTPException(status_code=400, detail="Missing required query parameter: symbol")

    sym = symbol.upper().strip()

    # Try direct lookup first, then try appending .NS (common for NSE stocks)
    try:
        data = fetch_stock_price(sym)
        if 'error' in data:
            # fallback: if symbol doesn't end with .NS, try appending it
            if not sym.endswith('.NS'):
                try_sym = f"{sym}.NS"
                data = fetch_stock_price(try_sym)

        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])

        return StockPriceResponse(
            symbol=data['symbol'],
            companyName=data['companyName'],
            lastPrice=data['lastPrice'],
            pChange=data['pChange'],
            change=data['change'],
            timestamp=data['timestamp']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock price: {str(e)}")
