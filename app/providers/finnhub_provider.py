# Optional: example Finnhub provider using httpx
import os
import httpx
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

API_KEY = os.getenv("FINNHUB_KEY")
BASE = "https://finnhub.io/api/v1"

async def get_quote(symbol: str) -> Optional[dict]:
    if not API_KEY:
        logger.warning("FINNHUB_KEY not set")
        return None
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            # Finnhub supports quote endpoint
            r = await c.get(f"{BASE}/quote", params={"symbol": symbol, "token": API_KEY})
            r.raise_for_status()
            data = r.json()
            # data has c (current), t (timestamp)
            return {"symbol": symbol.upper(), "price": float(data.get("c", 0)), "timestamp": str(data.get("t", ""))}
        except Exception as e:
            logger.error(f"Finnhub error for {symbol}: {e}")
            return None

async def get_historical(
    symbol: str,
    period: str = "1d",
    interval: str = "1d",
    start: str = None,
    end: str = None
) -> Optional[list]:
    """Fetch historical data from Finnhub (limited to recent data)."""
    if not API_KEY:
        logger.warning("FINNHUB_KEY not set")
        return None

    async with httpx.AsyncClient(timeout=15) as c:
        try:
            # Finnhub has limited historical data, mainly for recent periods
            # Use TIME_SERIES_DAILY for daily data
            if interval in ["1d", "5d", "1wk"]:
                function = "TIME_SERIES_DAILY"
                if interval == "5d":
                    function = "TIME_SERIES_DAILY"  # Finnhub doesn't have 5d specifically
            elif interval in ["1m", "5m", "15m", "30m", "1h"]:
                function = "TIME_SERIES_INTRADAY"
            else:
                logger.warning(f"Finnhub doesn't support interval: {interval}")
                return None

            params = {
                "function": function,
                "symbol": symbol,
                "apikey": API_KEY,
                "outputsize": "compact"
            }

            if function == "TIME_SERIES_INTRADAY":
                # Map interval to Finnhub format
                interval_map = {
                    "1m": "1min",
                    "5m": "5min",
                    "15m": "15min",
                    "30m": "30min",
                    "1h": "60min"
                }
                params["interval"] = interval_map.get(interval, "1min")

            r = await c.get(BASE, params=params)
            r.raise_for_status()
            data = r.json()

            # Parse the response
            if function == "TIME_SERIES_INTRADAY":
                time_series_key = f"Time Series ({params['interval']})"
            else:
                time_series_key = "Time Series (Daily)"

            time_series = data.get(time_series_key, {})
            if not time_series:
                return None

            historical = []
            for timestamp, values in time_series.items():
                historical.append({
                    "timestamp": timestamp,
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(values.get("5. volume", 0))
                })

            # Sort by timestamp
            historical.sort(key=lambda x: x["timestamp"])
            return historical

        except Exception as e:
            logger.error(f"Finnhub historical data error for {symbol}: {e}")
            return None
