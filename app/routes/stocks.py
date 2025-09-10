from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
import os
from ..providers import yfinance_provider, alphavantage_provider
from ..schemas import StockQuote, HistoricalData

router = APIRouter()

# Load subscriptions
SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'subscriptions.json')
with open(SUBSCRIPTIONS_FILE, 'r') as f:
    subscriptions = json.load(f)

INDIAN_STOCKS = subscriptions['stocks']['indian']
US_STOCKS = subscriptions['stocks']['us']
ALL_STOCKS = INDIAN_STOCKS + US_STOCKS

@router.get("/indian/list", response_model=List[str])
async def get_indian_stocks():
    """Get list of Indian stocks"""
    return INDIAN_STOCKS

@router.get("/us/list", response_model=List[str])
async def get_us_stocks():
    """Get list of US stocks"""
    return US_STOCKS

@router.get("/list", response_model=List[str])
async def get_available_stocks():
    """Get list of all available stocks (Indian + US)"""
    return ALL_STOCKS

@router.get("/quote/IND/{symbol}", response_model=StockQuote)
async def get_indian_stock_quote(symbol: str):
    """Get Indian stock quote"""
    symbol = symbol.upper()
    if symbol not in INDIAN_STOCKS:
        raise HTTPException(status_code=404, detail="Stock symbol not in Indian stocks list")
    
    try:
        quote = await yfinance_provider.get_quote(symbol)
        if quote:
            return StockQuote(
                symbol=quote['symbol'],
                lastPrice=quote['price'],
                timestamp=quote['timestamp']
            )
        else:
            raise HTTPException(status_code=404, detail="Failed to fetch quote")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical/IND/{symbol}", response_model=HistoricalData)
async def get_indian_stock_historical(symbol: str, period: str = Query("1d", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")):
    """Get historical data for Indian stock"""
    symbol = symbol.upper()
    if symbol not in INDIAN_STOCKS:
        raise HTTPException(status_code=404, detail="Stock symbol not in Indian stocks list")
    
    try:
        data = await yfinance_provider.get_historical(symbol, period)
        if data:
            return HistoricalData(symbol=symbol, period=period, data=data)
        else:
            raise HTTPException(status_code=404, detail="No historical data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quote/US/{symbol}", response_model=StockQuote)
async def get_us_stock_quote(symbol: str):
    """Get US stock quote"""
    symbol = symbol.upper()
    if symbol not in US_STOCKS:
        raise HTTPException(status_code=404, detail="Stock symbol not in US stocks list")
    
    try:
        quote = await yfinance_provider.get_quote(symbol)
        if quote:
            return StockQuote(
                symbol=quote['symbol'],
                lastPrice=quote['price'],
                timestamp=quote['timestamp']
            )
        else:
            raise HTTPException(status_code=404, detail="Failed to fetch quote")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical/US/{symbol}", response_model=HistoricalData)
async def get_us_stock_historical(symbol: str, period: str = Query("1d", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")):
    """Get historical data for US stock"""
    symbol = symbol.upper()
    if symbol not in US_STOCKS:
        raise HTTPException(status_code=404, detail="Stock symbol not in US stocks list")
    
    try:
        data = await yfinance_provider.get_historical(symbol, period)
        if data:
            return HistoricalData(symbol=symbol, period=period, data=data)
        else:
            raise HTTPException(status_code=404, detail="No historical data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index/US/{symbol}", response_model=StockQuote)
async def get_us_index_quote(symbol: str):
    """Get US index quote (e.g. GSPC, DJI, IXIC, VIX)"""
    # Map common names to Yahoo Finance symbols
    index_mapping = {
        'SP500': '^GSPC',
        'DOW': '^DJI', 
        'NASDAQ': '^IXIC',
        'VIX': '^VIX',
        'RUSSELL': '^RUT',
        'GSPC': '^GSPC',
        'DJI': '^DJI',
        'IXIC': '^IXIC'
    }
    
    symbol = symbol.upper()
    yf_symbol = index_mapping.get(symbol, f'^{symbol}')
    
    try:
        quote = await yfinance_provider.get_quote(yf_symbol)
        if quote:
            return StockQuote(
                symbol=symbol,
                lastPrice=quote['price'],
                timestamp=quote['timestamp']
            )
        else:
            raise HTTPException(status_code=404, detail="Failed to fetch index quote")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index/US/{symbol}/historical", response_model=HistoricalData)
async def get_us_index_historical(symbol: str, period: str = Query("1d", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")):
    """Get historical data for US index"""
    # Map common names to Yahoo Finance symbols
    index_mapping = {
        'SP500': '^GSPC',
        'DOW': '^DJI', 
        'NASDAQ': '^IXIC',
        'VIX': '^VIX',
        'RUSSELL': '^RUT',
        'GSPC': '^GSPC',
        'DJI': '^DJI',
        'IXIC': '^IXIC'
    }
    
    symbol = symbol.upper()
    yf_symbol = index_mapping.get(symbol, f'^{symbol}')
    
    try:
        data = await yfinance_provider.get_historical(yf_symbol, period)
        if data:
            return HistoricalData(symbol=symbol, period=period, data=data)
        else:
            raise HTTPException(status_code=404, detail="No historical data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index/BSE/{symbol}", response_model=StockQuote)
async def get_bse_index_quote(symbol: str):
    """Get BSE index quote (e.g. SENSEX, BSESN)"""
    # Map common names to Yahoo Finance symbols
    index_mapping = {
        'SENSEX': '^BSESN',
        'BSESN': '^BSESN',
        'BANKEX': '^BSEBANK',
        'AUTO': '^CNXAUTO',
        'FINANCE': '^CNXFIN',
        'IT': '^CNXIT',
        'METAL': '^CNXMETAL',
        'PHARMA': '^CNXPHARMA',
        'REALTY': '^CNXREALTY'
    }
    
    symbol = symbol.upper()
    yf_symbol = index_mapping.get(symbol, f'^{symbol}')
    
    try:
        quote = await yfinance_provider.get_quote(yf_symbol)
        if quote:
            return StockQuote(
                symbol=symbol,
                lastPrice=quote['price'],
                timestamp=quote['timestamp']
            )
        else:
            raise HTTPException(status_code=404, detail="Failed to fetch BSE index quote")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index/BSE/{symbol}/historical", response_model=HistoricalData)
async def get_bse_index_historical(symbol: str, period: str = Query("1d", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")):
    """Get historical data for BSE index"""
    # Map common names to Yahoo Finance symbols
    index_mapping = {
        'SENSEX': '^BSESN',
        'BSESN': '^BSESN',
        'BANKEX': '^BSEBANK',
        'AUTO': '^CNXAUTO',
        'FINANCE': '^CNXFIN',
        'IT': '^CNXIT',
        'METAL': '^CNXMETAL',
        'PHARMA': '^CNXPHARMA',
        'REALTY': '^CNXREALTY'
    }
    
    symbol = symbol.upper()
    yf_symbol = index_mapping.get(symbol, f'^{symbol}')
    
    try:
        data = await yfinance_provider.get_historical(yf_symbol, period)
        if data:
            return HistoricalData(symbol=symbol, period=period, data=data)
        else:
            raise HTTPException(status_code=404, detail="No historical data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
