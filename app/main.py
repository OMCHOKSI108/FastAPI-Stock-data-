import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import Dict, List
from .cache import InMemoryCache
from .schemas import Quote, SubscribeRequest
from .fetcher import background_fetcher, load_subscriptions
from .providers import yfinance_provider, finnhub_provider, alphavantage_provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROVIDER = os.getenv("PROVIDER", "YFINANCE").upper()
PROVIDER_MAP = {
    "YFINANCE": yfinance_provider,
    "FINNHUB": finnhub_provider,
    "ALPHAVANTAGE": alphavantage_provider,
}

app = FastAPI(title="FastStockAPI")

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
