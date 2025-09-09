import os
import asyncio
import json
from typing import List
import logging
from .cache import InMemoryCache
from .providers import yfinance_provider, finnhub_provider, alphavantage_provider, binance_provider

logger = logging.getLogger(__name__)

FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "60"))
PROVIDER = os.getenv("PROVIDER", "YFINANCE").upper()
SUB_FILE = "subscriptions.json"

PROVIDER_MAP = {
    "YFINANCE": yfinance_provider,
    "FINNHUB": finnhub_provider,
    "ALPHAVANTAGE": alphavantage_provider,
}

def is_crypto_symbol(symbol: str) -> bool:
    """
    Determine if a symbol is a cryptocurrency based on common patterns.
    """
    symbol = symbol.upper()
    # Common crypto patterns
    crypto_patterns = [
        'USDT', 'BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'AVAX',
        'MATIC', 'LINK', 'UNI', 'AAVE', 'SUSHI', 'COMP', 'MKR',
        'YFI', 'BAL', 'CRV', 'XRP', 'LTC', 'BCH', 'ETC', 'DOGE',
        'SHIB', 'CAKE', 'SXP', 'ALICE'
    ]

    # Check if symbol ends with common quote currencies or contains crypto patterns
    for pattern in crypto_patterns:
        if pattern in symbol:
            return True

    return False

def get_provider_for_symbol(symbol: str):
    """
    Get the appropriate provider for a given symbol.
    """
    if is_crypto_symbol(symbol):
        return binance_provider
    else:
        return PROVIDER_MAP.get(PROVIDER, yfinance_provider)

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

    logger.info(f"Using default provider: {PROVIDER}")

    while True:
        symbols = list(getattr(app.state, "subscriptions", []))
        if not symbols:
            await asyncio.sleep(FETCH_INTERVAL)
            continue

        for s in symbols:
            try:
                # Get the appropriate provider for this symbol
                provider = get_provider_for_symbol(s)
                logger.debug(f"Fetching {s} using {provider.__name__}")

                # Use the appropriate fetch method based on provider
                if provider == binance_provider:
                    # For Binance, use get_crypto_price
                    q = await provider.get_crypto_price(s)
                else:
                    # For other providers, use get_quote
                    q = await provider.get_quote(s)

                if q:
                    await cache.set(s, q)
                    logger.debug(f"Successfully cached {s}")
                else:
                    logger.warning(f"No data received for {s}")

            except Exception as e:
                logger.error(f"Fetch error for {s}: {e}")
            await asyncio.sleep(0.2)

        await save_subscriptions(symbols)
        await asyncio.sleep(FETCH_INTERVAL)
