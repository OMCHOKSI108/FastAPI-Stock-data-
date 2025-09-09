import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from .cache import InMemoryCache
from .schemas import Quote, SubscribeRequest
from .fetcher import background_fetcher, load_subscriptions
from .providers import yfinance_provider, finnhub_provider, alphavantage_provider, binance_provider
from .routes import market, options, analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROVIDER = os.getenv("PROVIDER", "YFINANCE").upper()
PROVIDER_MAP = {
    "YFINANCE": yfinance_provider,
    "FINNHUB": finnhub_provider,
    "ALPHAVANTAGE": alphavantage_provider,
}

app = FastAPI(title="FastStockAPI")

origins = [
    "http://localhost:5173",  # React local dev
    "https://your-production-frontend.com"  # Replace with your production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include new routers
app.include_router(
    market.router,
    prefix="/api/v1/market",
    tags=["market"]
)

app.include_router(
    options.router,
    prefix="/api/v1/options",
    tags=["options"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"]
)

@app.on_event("startup")
async def startup():
    # init cache
    app.state.cache = InMemoryCache()
    # ensure subscriptions exist
    app.state.subscriptions = await load_subscriptions()
    # start background fetcher
    app.state.fetch_task = asyncio.create_task(background_fetcher(app))

@app.on_event("shutdown")
async def shutdown():
    task = getattr(app.state, "fetch_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/quotes", response_model=Dict[str, Quote])
async def get_all_quotes():
    return await app.state.cache.get_all()

@app.get("/quote/{symbol}", response_model=Quote)
async def get_quote(symbol: str):
    data = await app.state.cache.get(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Symbol not found in cache")
    return data

@app.get("/fetch/{symbol}", response_model=Quote)
async def fetch_quote(symbol: str):
    provider_module = PROVIDER_MAP.get(PROVIDER, yfinance_provider)
    q = await provider_module.get_quote(symbol)
    if q:
        await app.state.cache.set(symbol, q)
        return q
    else:
        raise HTTPException(status_code=404, detail="Failed to fetch quote")

@app.get("/historical/{symbol}")
async def get_historical(symbol: str, period: str = "1d"):
    provider_module = PROVIDER_MAP.get(PROVIDER, yfinance_provider)
    if hasattr(provider_module, 'get_historical'):
        data = await provider_module.get_historical(symbol, period)
        if data:
            return {"symbol": symbol.upper(), "period": period, "data": data}
        else:
            raise HTTPException(status_code=404, detail="No historical data found")
    else:
        raise HTTPException(status_code=501, detail="Historical data not supported by current provider")

@app.post("/subscribe")
async def subscribe(req: SubscribeRequest):
    s = req.symbol.strip().upper()
    subs = getattr(app.state, "subscriptions", [])
    if s in subs:
        return {"detail": "already subscribed", "symbol": s}
    subs.append(s)
    app.state.subscriptions = subs
    return {"detail": "subscribed", "symbol": s}

@app.get("/stocks/list", response_model=List[str])
async def get_available_stocks():
    """Get list of all available Indian stocks (for enterprise use)"""
    # In enterprise, load from database or API
    # For now, return subscribed + some popular ones
    subscribed = getattr(app.state, "subscriptions", [])
    popular = ["RELIANCE.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
    all_stocks = list(set(subscribed + popular))
    return all_stocks

@app.get("/crypto/{symbol}")
async def get_crypto_price(symbol: str):
    """Get cryptocurrency price from Binance"""
    try:
        data = await binance_provider.get_crypto_price(symbol.upper())
        if data:
            return data
        else:
            raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    except Exception as e:
        logger.error(f"Error fetching crypto price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crypto price")

@app.get("/crypto-historical/{symbol}")
async def get_crypto_historical(symbol: str, interval: str = "1d", limit: int = 100):
    """Get cryptocurrency historical data from Binance"""
    try:
        data = await binance_provider.get_crypto_historical(symbol.upper(), interval, limit)
        if data:
            return {"symbol": symbol.upper(), "interval": interval, "limit": limit, "data": data}
        else:
            raise HTTPException(status_code=404, detail="No historical data found")
    except Exception as e:
        logger.error(f"Error fetching crypto historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crypto historical data")

@app.get("/crypto-historical-extended/{symbol}")
async def get_crypto_historical_extended(
    symbol: str,
    interval: str = "1d",
    start_str: str = "30 days ago UTC",
    max_records: int = 1000
):
    """Get extended cryptocurrency historical data with pagination (up to 5000 records)"""
    try:
        data = await binance_provider.get_crypto_historical_paginated(
            symbol.upper(), interval, start_str, max_records
        )
        if data:
            return {
                "symbol": symbol.upper(),
                "interval": interval,
                "start_date": start_str,
                "total_records": len(data),
                "data": data
            }
        else:
            raise HTTPException(status_code=404, detail="No historical data found")
    except Exception as e:
        logger.error(f"Error fetching extended crypto historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch extended crypto historical data")

@app.get("/crypto-stats/{symbol}")
async def get_crypto_stats(symbol: str):
    """Get 24hr cryptocurrency statistics from Binance"""
    try:
        data = await binance_provider.get_24hr_ticker_stats(symbol.upper())
        if data:
            return data
        else:
            raise HTTPException(status_code=404, detail="Cryptocurrency stats not found")
    except Exception as e:
        logger.error(f"Error fetching crypto stats for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crypto stats")

@app.get("/crypto-multiple")
async def get_multiple_crypto_prices(symbols: str):
    """Get multiple cryptocurrency prices in a single request"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        if len(symbol_list) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 symbols allowed")

        data = await binance_provider.get_multiple_crypto_prices(symbol_list)
        if data:
            return {
                "symbols_requested": symbol_list,
                "symbols_found": len(data),
                "data": data
            }
        else:
            raise HTTPException(status_code=404, detail="No cryptocurrency data found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching multiple crypto prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch multiple crypto prices")

@app.get("/crypto-comprehensive/{symbol}")
async def get_crypto_comprehensive(symbol: str):
    """Get comprehensive cryptocurrency data (price + 24hr stats)"""
    try:
        price_data = await binance_provider.get_crypto_price(symbol.upper())
        stats_data = await binance_provider.get_24hr_ticker_stats(symbol.upper())

        if not price_data or not stats_data:
            raise HTTPException(status_code=404, detail="Cryptocurrency data not found")

        return {
            "symbol": symbol.upper(),
            "current_price": price_data,
            "statistics_24h": stats_data,
            "timestamp": price_data["timestamp"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching comprehensive crypto data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch comprehensive crypto data")
