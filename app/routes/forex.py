# app/routes/forex.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from ..schemas import ForexQuote, ForexPair, ForexHistoricalData
from ..providers import forex_provider

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/pairs", response_model=List[ForexPair])
def get_available_pairs():
    """Get list of available forex currency pairs."""
    pairs = forex_provider.get_available_pairs()
    return [ForexPair(**pair) for pair in pairs]

@router.get("/quote", response_model=ForexQuote)
async def get_forex_quote(
    symbol: str = Query(..., description="Forex pair symbol, e.g. EURUSD, GBPUSD")
):
    """Get current quote for a forex currency pair."""
    symbol = symbol.upper()
    data = await forex_provider.get_forex_quote(symbol)

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for forex pair {symbol}. Available pairs: {list(forex_provider.FOREX_PAIRS.keys())}"
        )

    return ForexQuote(**data)

@router.get("/historical", response_model=ForexHistoricalData)
async def get_forex_historical(
    symbol: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
    period: str = Query("1d", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
):
    """Get historical data for a forex currency pair."""
    symbol = symbol.upper()
    data = await forex_provider.get_forex_historical(symbol, period)

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data found for forex pair {symbol}"
        )

    return ForexHistoricalData(
        symbol=symbol,
        period=period,
        data=data,
        timestamp=data[-1]["timestamp"] if data else None
    )

@router.get("/quotes", response_model=List[ForexQuote])
async def get_multiple_forex_quotes(
    symbols: str = Query(..., description="Comma-separated list of forex pairs, e.g. EURUSD,GBPUSD,USDJPY")
):
    """Get current quotes for multiple forex currency pairs."""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    results = []

    for symbol in symbol_list:
        data = await forex_provider.get_forex_quote(symbol)
        if data:
            results.append(ForexQuote(**data))
        else:
            logger.warning(f"No data found for forex pair {symbol}")

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for any of the requested forex pairs: {symbols}"
        )

    return results
