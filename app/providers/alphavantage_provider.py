# Optional: simple AlphaVantage daily intraday fetch (note: strict rate limits)
import os
import httpx
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
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

async def get_historical(
    symbol: str,
    period: str = "1d",
    interval: str = "1d",
    start: str = None,
    end: str = None
) -> Optional[list]:
    """Fetch historical data from AlphaVantage."""
    if not API_KEY:
        logger.warning("ALPHAVANTAGE_KEY not set")
        return None

    async with httpx.AsyncClient(timeout=20) as c:
        try:
            # Determine which function to use based on interval
            if interval in ["1m", "5m", "15m", "30m", "60m"]:
                function = "TIME_SERIES_INTRADAY"
                # Map interval to AlphaVantage format
                interval_map = {
                    "1m": "1min",
                    "5m": "5min",
                    "15m": "15min",
                    "30m": "30min",
                    "60m": "60min"
                }
                av_interval = interval_map.get(interval, "1min")
            elif interval in ["1d", "5d", "1wk", "1mo"]:
                function = "TIME_SERIES_DAILY"
                av_interval = None
            elif interval == "1wk":
                function = "TIME_SERIES_WEEKLY"
                av_interval = None
            elif interval == "1mo":
                function = "TIME_SERIES_MONTHLY"
                av_interval = None
            else:
                logger.warning(f"AlphaVantage doesn't support interval: {interval}")
                return None

            params = {
                "function": function,
                "symbol": symbol,
                "apikey": API_KEY,
                "outputsize": "compact"
            }

            if av_interval:
                params["interval"] = av_interval

            r = await c.get(BASE, params=params)
            r.raise_for_status()
            data = r.json()

            # Parse the response based on function
            if function == "TIME_SERIES_INTRADAY":
                time_series_key = f"Time Series ({av_interval})"
            elif function == "TIME_SERIES_DAILY":
                time_series_key = "Time Series (Daily)"
            elif function == "TIME_SERIES_WEEKLY":
                time_series_key = "Weekly Time Series"
            elif function == "TIME_SERIES_MONTHLY":
                time_series_key = "Monthly Time Series"

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
            logger.error(f"AlphaVantage historical data error for {symbol}: {e}")
            return None
