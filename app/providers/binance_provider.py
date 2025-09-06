# app/providers/binance_provider.py
import os
import httpx
import asyncio
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://api.binance.com"

async def get_crypto_price(symbol: str) -> Optional[dict]:
    """Fetch current crypto price from Binance."""
    url = f"{BASE_URL}/api/v3/ticker/price?symbol={symbol.upper()}"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return {
                "symbol": data["symbol"],
                "price": float(data["price"]),
                "timestamp": str(asyncio.get_event_loop().time())
            }
        except Exception as e:
            logger.error(f"Binance error for {symbol}: {e}")
            return None

async def get_crypto_historical(symbol: str, interval: str = "1d", limit: int = 100) -> Optional[List[dict]]:
    """Fetch historical crypto data from Binance."""
    url = f"{BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            historical = []
            for kline in data:
                historical.append({
                    "timestamp": str(kline[0] / 1000),  # Convert ms to seconds
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5])
                })
            return historical
        except Exception as e:
            logger.error(f"Binance historical error for {symbol}: {e}")
            return None
