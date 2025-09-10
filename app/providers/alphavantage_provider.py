# Optional: simple AlphaVantage daily intraday fetch (note: strict rate limits)
import os
import httpx
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

API_KEY = os.getenv("V53HR23RXCGZS2KL")
BASE = "https://www.alphavantage.co/query"

async def get_quote(symbol: str) -> Optional[dict]:
    if not API_KEY:
        logger.warning("ALPHAVANTAGE_KEY not set")
        return None
    async with httpx.AsyncClient(timeout=15) as c:
        try:
            r = await c.get(BASE, params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": "1min",
                "apikey": API_KEY,
                "outputsize": "compact",
            })
            r.raise_for_status()
            j = r.json()
            ts_series = j.get("Time Series (1min)", {})
            if not ts_series:
                return None
            # get latest timestamp
            latest_ts = sorted(ts_series.keys())[-1]
            price = float(ts_series[latest_ts]["4. close"])
            return {"symbol": symbol.upper(), "price": price, "timestamp": latest_ts}
        except Exception as e:
            logger.error(f"AlphaVantage error for {symbol}: {e}")
            return None
