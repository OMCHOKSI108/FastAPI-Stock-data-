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
