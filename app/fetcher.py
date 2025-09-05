import os
import asyncio
import json
from typing import List
import logging
from .cache import InMemoryCache
from .providers import yfinance_provider, finnhub_provider, alphavantage_provider

logger = logging.getLogger(__name__)

FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "60"))
PROVIDER = os.getenv("PROVIDER", "YFINANCE").upper()
SUB_FILE = "subscriptions.json"

PROVIDER_MAP = {
    "YFINANCE": yfinance_provider,
    "FINNHUB": finnhub_provider,
    "ALPHAVANTAGE": alphavantage_provider,
}

async def load_subscriptions() -> List[str]:
    if os.path.exists(SUB_FILE):
        try:
            with open(SUB_FILE, "r") as f:
                data = json.load(f)
                return data.get("symbols", [])
        except Exception:
            return []
    return []

async def save_subscriptions(symbols: List[str]):
    try:
        with open(SUB_FILE, "w") as f:
            json.dump({"symbols": symbols}, f)
    except Exception as e:
        logger.error(f"Save subscriptions error: {e}")

async def background_fetcher(app):
    """Long-running background task. Use app.state to access cache and subscriptions."""
    cache: InMemoryCache = app.state.cache
    # load persisted list
    subs = await load_subscriptions()
    if not subs:
        # fallback to env
        start_symbols = os.getenv("FETCH_SYMBOLS", "RELIANCE.NS,INFY.NS")
        subs = [s.strip() for s in start_symbols.split(",") if s.strip()]
    app.state.subscriptions = subs

    provider_module = PROVIDER_MAP.get(PROVIDER, yfinance_provider)
    logger.info(f"Using provider: {PROVIDER}")

    while True:
        symbols = list(getattr(app.state, "subscriptions", []))
        if not symbols:
            await asyncio.sleep(FETCH_INTERVAL)
            continue
        for s in symbols:
            try:
                q = await provider_module.get_quote(s)
                if q:
                    await cache.set(s, q)
            except Exception as e:
                logger.error(f"Fetch error for {s}: {e}")
            await asyncio.sleep(0.2)
        await save_subscriptions(symbols)
        await asyncio.sleep(FETCH_INTERVAL)
