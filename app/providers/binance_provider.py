# app/providers/binance_provider.py
import os
import httpx
import asyncio
import time
import hmac
import hashlib
from urllib.parse import urlencode
from typing import Optional, List, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://api.binance.com"
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

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

async def get_crypto_historical_paginated(symbol: str, interval: str = "1d", start_str: str = "30 days ago UTC", max_records: int = 5000) -> Optional[List[dict]]:
    """Fetch large historical datasets with pagination and rate limiting."""
    url = f"{BASE_URL}/api/v3/klines"

    # Convert start_str to timestamp
    if start_str == "30 days ago UTC":
        start_time = int((datetime.now().timestamp() - 30 * 24 * 60 * 60) * 1000)
    else:
        start_time = int(datetime.strptime(start_str, "%Y-%m-%d").timestamp() * 1000)

    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": 1000,
        "startTime": start_time
    }

    all_data = []
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            while len(all_data) < max_records:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                for kline in data:
                    all_data.append({
                        "timestamp": kline[0] / 1000,  # Keep as float for easier processing
                        "open": float(kline[1]),
                        "high": float(kline[2]),
                        "low": float(kline[3]),
                        "close": float(kline[4]),
                        "volume": float(kline[5]),
                        "close_time": kline[6] / 1000,
                        "quote_asset_volume": float(kline[7]),
                        "number_of_trades": int(kline[8]),
                        "taker_buy_base_asset_volume": float(kline[9]),
                        "taker_buy_quote_asset_volume": float(kline[10])
                    })

                # Update startTime for next batch
                last_time = data[-1][0]
                params["startTime"] = last_time + 1

                # Rate limiting
                await asyncio.sleep(0.5)

                # Break if we got less than 1000 records (last batch)
                if len(data) < 1000:
                    break

            return all_data[:max_records]  # Return only requested amount

        except Exception as e:
            logger.error(f"Binance paginated historical error for {symbol}: {e}")
            return None

async def get_24hr_ticker_stats(symbol: str) -> Optional[dict]:
    """Get 24hr ticker statistics including price change, volume, etc."""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    params = {"symbol": symbol.upper()}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return {
                "symbol": data["symbol"],
                "price_change": float(data["priceChange"]),
                "price_change_percent": float(data["priceChangePercent"]),
                "weighted_avg_price": float(data["weightedAvgPrice"]),
                "prev_close_price": float(data["prevClosePrice"]),
                "last_price": float(data["lastPrice"]),
                "bid_price": float(data["bidPrice"]),
                "ask_price": float(data["askPrice"]),
                "open_price": float(data["openPrice"]),
                "high_price": float(data["highPrice"]),
                "low_price": float(data["lowPrice"]),
                "volume": float(data["volume"]),
                "quote_asset_volume": float(data["quoteAssetVolume"]),
                "open_time": data["openTime"] / 1000,
                "close_time": data["closeTime"] / 1000,
                "count": int(data["count"])
            }
        except Exception as e:
            logger.error(f"Binance 24hr stats error for {symbol}: {e}")
            return None

async def get_multiple_crypto_prices(symbols: List[str]) -> Dict[str, dict]:
    """Fetch multiple crypto prices in a single request."""
    url = f"{BASE_URL}/api/v3/ticker/price"
    symbols_param = ",".join([f'"{s.upper()}"' for s in symbols])

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(url, params={"symbols": f"[{symbols_param}]"})
            response.raise_for_status()
            data = response.json()

            result = {}
            for item in data:
                result[item["symbol"]] = {
                    "symbol": item["symbol"],
                    "price": float(item["price"]),
                    "timestamp": str(asyncio.get_event_loop().time())
                }
            return result
        except Exception as e:
            logger.error(f"Binance multiple prices error: {e}")
            return {}

def _signed_request(http_method: str, url_path: str, payload: dict = None) -> dict:
    """Create signed request for authenticated endpoints."""
    if not API_KEY or not API_SECRET:
        raise ValueError("API_KEY and API_SECRET must be set for signed requests")

    if payload is None:
        payload = {}

    query_string = urlencode(payload)
    timestamp = int(time.time() * 1000)

    if query_string:
        query_string = f"{query_string}&timestamp={timestamp}"
    else:
        query_string = f"timestamp={timestamp}"

    # Create signature
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    query_string += f"&signature={signature}"

    url = f"{BASE_URL}{url_path}?{query_string}"
    headers = {"X-MBX-APIKEY": API_KEY}

    # Note: This is a synchronous function for signed requests
    # In production, you might want to make it async
    import requests
    if http_method.upper() == "GET":
        return requests.get(url, headers=headers).json()
    elif http_method.upper() == "POST":
        return requests.post(url, headers=headers).json()
    else:
        raise ValueError(f"HTTP method {http_method} not implemented")
