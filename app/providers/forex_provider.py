# app/providers/forex_provider.py
import yfinance as yf
import asyncio
import pandas as pd
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Common forex pairs
FOREX_PAIRS = {
    "EURUSD": {"base": "EUR", "quote": "USD", "description": "Euro vs US Dollar"},
    "GBPUSD": {"base": "GBP", "quote": "USD", "description": "British Pound vs US Dollar"},
    "USDJPY": {"base": "USD", "quote": "JPY", "description": "US Dollar vs Japanese Yen"},
    "USDCHF": {"base": "USD", "quote": "CHF", "description": "US Dollar vs Swiss Franc"},
    "AUDUSD": {"base": "AUD", "quote": "USD", "description": "Australian Dollar vs US Dollar"},
    "USDCAD": {"base": "USD", "quote": "CAD", "description": "US Dollar vs Canadian Dollar"},
    "NZDUSD": {"base": "NZD", "quote": "USD", "description": "New Zealand Dollar vs US Dollar"},
    "EURJPY": {"base": "EUR", "quote": "JPY", "description": "Euro vs Japanese Yen"},
    "GBPJPY": {"base": "GBP", "quote": "JPY", "description": "British Pound vs Japanese Yen"},
    "EURGBP": {"base": "EUR", "quote": "GBP", "description": "Euro vs British Pound"},
}

async def get_forex_quote(symbol: str) -> Optional[dict]:
    """Fetch current forex quote for a currency pair."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_forex_quote, symbol)

def _sync_forex_quote(symbol: str):
    try:
        # yfinance forex symbols are formatted as EURUSD=X
        yf_symbol = f"{symbol}=X"
        ticker = yf.Ticker(yf_symbol)

        # Get current data
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            return None

        last = data.iloc[-1]
        price = float(last['Close'])

        # Get bid/ask if available
        try:
            info = ticker.info
            bid = info.get('bid')
            ask = info.get('ask')
        except:
            bid = None
            ask = None

        pair_info = FOREX_PAIRS.get(symbol.upper(), {})
        base_currency = pair_info.get('base', symbol[:3])
        quote_currency = pair_info.get('quote', symbol[3:])

        return {
            "symbol": symbol.upper(),
            "base_currency": base_currency,
            "quote_currency": quote_currency,
            "price": price,
            "bid": bid,
            "ask": ask,
            "timestamp": last.name.to_pydatetime().isoformat()
        }
    except Exception as e:
        logger.error(f"Forex quote fetch error for {symbol}: {e}")
        return None

async def get_forex_historical(symbol: str, period: str = "1d") -> Optional[list]:
    """Fetch historical forex data."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_forex_historical, symbol, period)

def _sync_forex_historical(symbol: str, period: str) -> Optional[list]:
    try:
        yf_symbol = f"{symbol}=X"
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period=period)

        if data.empty:
            return None

        # Convert to list of dicts
        historical = []
        for idx, row in data.iterrows():
            historical.append({
                "timestamp": idx.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
            })
        return historical
    except Exception as e:
        logger.error(f"Forex historical fetch error for {symbol}: {e}")
        return None

def get_available_pairs() -> List[Dict[str, str]]:
    """Get list of available forex pairs."""
    return [
        {
            "symbol": symbol,
            "base_currency": info["base"],
            "quote_currency": info["quote"],
            "description": info["description"]
        }
        for symbol, info in FOREX_PAIRS.items()
    ]
