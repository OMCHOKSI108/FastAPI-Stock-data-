import os
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import stocks, crypto, options, analytics, forex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.on_event("startup")
async def startup():
    pass  # Add any startup logic if needed

@app.on_event("shutdown")
async def shutdown():
    pass  # Add any shutdown logic if needed

@app.get("/")
async def root():
    """Welcome to FastStockAPI - A comprehensive stock market data API"""
    return {
        "message": "Welcome to FastStockAPI",
        "description": "A comprehensive FastAPI for stock market data including Indian/US stocks, crypto, options, and indices",
        "version": "1.0.0",
        "endpoints": {
            "stocks": {
                "IND": "/stocks/IND/{symbol} - Indian stock data",
                "US": "/stocks/US/{symbol} - US stock data",
                "IND/quote": "/stocks/IND/quote?symbols=RELIANCE,TCS - Multiple Indian stocks",
                "US/quote": "/stocks/US/quote?symbols=AAPL,GOOGL - Multiple US stocks"
            },
            "crypto": {
                "price": "/crypto/price?symbol=BTC - Cryptocurrency price",
                "historical": "/crypto/historical/{symbol}?period=1d - Historical crypto data"
            },
            "options": {
                "expiries": "/options/expiries?index=NIFTY - Available expiries",
                "index-price": "/options/index-price?index=NIFTY - Index price",
                "stock-price": "/options/stock-price?symbol=RELIANCE - Stock price",
                "fetch": "/options/fetch (POST) - Fetch and save option chain",
                "fetch/expiry": "/options/fetch/expiry (POST) - Fetch specific expiry",
                "analytics": "/options/analytics?index=NIFTY - PCR, max pain, top OI",
                "option-price": "/options/option-price?index=NIFTY&strike=24000&expiry=160925&option_type=CE - Specific option price",
                "direct-data": "/options/direct-data?index=NIFTY&expiry=160925&num_strikes=25 - Direct options data",
                "strike-data": "/options/strike-data?index=NIFTY&strike=24000&expiry=160925&option_type=BOTH - Strike-specific data",
                "historical": "/options/historical/{symbol}?strike=24000&expiry=160925&option_type=CE&period=1d - Historical option data"
            },
            "analytics": {
                "pcr": "/analytics/pcr?index=NIFTY&expiry=160925 - Put-Call Ratio",
                "max-pain": "/analytics/max-pain?index=NIFTY&expiry=160925 - Max Pain calculation",
                "top-oi": "/analytics/top-oi?index=NIFTY&expiry=160925 - Top Open Interest"
            },
            "indices": {
                "US": "/stocks/US/index/{symbol} - US index data (DJI, SPX, IXIC)",
                "BSE": "/stocks/IND/index/{symbol} - BSE index data (SENSEX, BSE100)"
            }
        },
        "documentation": "/docs - Interactive API documentation",
        "health": "/health - API health check"
    }

# Include routers
app.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
app.include_router(crypto.router, prefix="/crypto", tags=["crypto"])
app.include_router(options.router, prefix="/options", tags=["options"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(forex.router, prefix="/forex", tags=["forex"])

@app.get("/health")
async def health():
    return {"status": "ok"}
