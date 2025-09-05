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
