# Cryptocurrency API

This section documents all cryptocurrency-related endpoints in the FastAPI Stock & Crypto Data API.

## 📊 Overview

Our cryptocurrency API provides real-time and historical data from Binance, including prices, statistics, and market data for 30+ major cryptocurrencies.

## 🔗 Base URL

```
https://fastapi-stock-data.onrender.com
```

## 📋 Endpoints

### 1. Get Single Crypto Price

Get the current price of a specific cryptocurrency.

**Endpoint:** `GET /crypto-price/{symbol}`

**Parameters:**
- `symbol` (path): Cryptocurrency symbol (e.g., `BTCUSDT`, `ETHUSDT`)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT"
```

**Example Response:**
```json
{
    "symbol": "BTCUSDT",
    "price": "45123.45",
    "timestamp": "1733779200.123"
}
```

**Error Responses:**
- `404`: Symbol not found
- `500`: Server error

---

### 2. Get Multiple Crypto Prices

Get current prices for multiple cryptocurrencies in a single request.

**Endpoint:** `GET /crypto-multiple`

**Parameters:**
- `symbols` (query): Comma-separated list of symbols (max 100)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-multiple?symbols=BTCUSDT,ETHUSDT,ADAUSDT"
```

**Example Response:**
```json
{
    "symbols_requested": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
    "symbols_found": 3,
    "data": {
        "BTCUSDT": {
            "symbol": "BTCUSDT",
            "price": "45123.45",
            "timestamp": "1733779200.123"
        },
        "ETHUSDT": {
            "symbol": "ETHUSDT",
            "price": "2456.78",
            "timestamp": "1733779200.123"
        },
        "ADAUSDT": {
            "symbol": "ADAUSDT",
            "price": "0.5678",
            "timestamp": "1733779200.123"
        }
    }
}
```

---

### 3. Get 24h Crypto Statistics

Get 24-hour statistics for a cryptocurrency including price change, volume, etc.

**Endpoint:** `GET /crypto-stats/{symbol}`

**Parameters:**
- `symbol` (path): Cryptocurrency symbol

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-stats/BTCUSDT"
```

**Example Response:**
```json
{
    "symbol": "BTCUSDT",
    "price_change": 1234.56,
    "price_change_percent": 2.85,
    "weighted_avg_price": 44567.89,
    "prev_close_price": 43889.12,
    "last_price": 45123.68,
    "bid_price": 45120.00,
    "ask_price": 45125.00,
    "open_price": 43889.12,
    "high_price": 45678.90,
    "low_price": 43500.00,
    "volume": 123456.78,
    "quote_asset_volume": 5678901234.56,
    "open_time": 1733692800.0,
    "close_time": 1733779200.0,
    "count": 1234567
}
```

---

### 4. Get Crypto Historical Data

Get historical price data for a cryptocurrency.

**Endpoint:** `GET /crypto-historical/{symbol}`

**Parameters:**
- `symbol` (path): Cryptocurrency symbol
- `interval` (query, optional): Time interval (default: `1d`)
- `limit` (query, optional): Number of data points (default: 100, max: 1000)

**Supported Intervals:**
- `1m`, `3m`, `5m`, `15m`, `30m` - Minutes
- `1h`, `2h`, `4h`, `6h`, `8h`, `12h` - Hours
- `1d`, `3d` - Days
- `1w` - Weeks
- `1M` - Months

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-historical/BTCUSDT?interval=1d&limit=30"
```

**Example Response:**
```json
{
    "symbol": "BTCUSDT",
    "interval": "1d",
    "data": [
        {
            "timestamp": 1733692800000,
            "open": 43889.12,
            "high": 45678.90,
            "low": 43500.00,
            "close": 45123.68,
            "volume": 123456.78
        },
        {
            "timestamp": 1733606400000,
            "open": 43200.00,
            "high": 44123.45,
            "low": 42800.00,
            "close": 43889.12,
            "volume": 98765.43
        }
    ]
}
```

---

### 5. Get Comprehensive Crypto Data

Get both current price and 24h statistics in a single request.

**Endpoint:** `GET /crypto-comprehensive/{symbol}`

**Parameters:**
- `symbol` (path): Cryptocurrency symbol

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-comprehensive/BTCUSDT"
```

**Example Response:**
```json
{
    "symbol": "BTCUSDT",
    "current_price": {
        "symbol": "BTCUSDT",
        "price": "45123.45",
        "timestamp": "1733779200.123"
    },
    "statistics_24h": {
        "symbol": "BTCUSDT",
        "price_change": 1234.56,
        "price_change_percent": 2.85,
        "last_price": 45123.68,
        "volume": 123456.78,
        "high_price": 45678.90,
        "low_price": 43500.00
    },
    "timestamp": "1733779200.123"
}
```

---

### 6. Get Extended Historical Data

Get historical data with pagination support.

**Endpoint:** `GET /crypto-historical-extended/{symbol}`

**Parameters:**
- `symbol` (path): Cryptocurrency symbol
- `interval` (query, optional): Time interval (default: `1d`)
- `start_date` (query, optional): Start date (YYYY-MM-DD)
- `end_date` (query, optional): End date (YYYY-MM-DD)
- `limit` (query, optional): Number of data points (default: 100)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-historical-extended/BTCUSDT?interval=1d&start_date=2024-01-01&end_date=2024-01-31"
```

## 📊 Response Formats

### Success Response Structure

All successful responses follow this general structure:

```json
{
    "status": "success",
    "data": { ... },
    "timestamp": "2024-12-09T15:30:00Z"
}
```

### Error Response Structure

```json
{
    "detail": "Error description",
    "status_code": 404,
    "timestamp": "2024-12-09T15:30:00Z"
}
```

## ⚠️ Rate Limiting

- **Production**: No rate limiting currently
- **Best Practice**: Implement client-side caching
- **Fair Use**: Please don't abuse the API

## 🔧 Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Symbol not found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 502 | Bad Gateway (Binance API issues) |
| 503 | Service Unavailable |

## 📱 SDKs and Libraries

### Python

```python
import requests

class CryptoAPI:
    def __init__(self, base_url="https://fastapi-stock-data.onrender.com"):
        self.base_url = base_url

    def get_price(self, symbol):
        response = requests.get(f"{self.base_url}/crypto-price/{symbol}")
        return response.json()

    def get_multiple_prices(self, symbols):
        symbol_str = ",".join(symbols)
        response = requests.get(f"{self.base_url}/crypto-multiple?symbols={symbol_str}")
        return response.json()

    def get_stats(self, symbol):
        response = requests.get(f"{self.base_url}/crypto-stats/{symbol}")
        return response.json()

# Usage
api = CryptoAPI()
btc_price = api.get_price("BTCUSDT")
print(f"BTC: ${btc_price['price']}")
```

### JavaScript/Node.js

```javascript
class CryptoAPI {
    constructor(baseURL = 'https://fastapi-stock-data.onrender.com') {
        this.baseURL = baseURL;
    }

    async getPrice(symbol) {
        const response = await fetch(`${this.baseURL}/crypto-price/${symbol}`);
        return await response.json();
    }

    async getMultiplePrices(symbols) {
        const symbolStr = symbols.join(',');
        const response = await fetch(`${this.baseURL}/crypto-multiple?symbols=${symbolStr}`);
        return await response.json();
    }

    async getStats(symbol) {
        const response = await fetch(`${this.baseURL}/crypto-stats/${symbol}`);
        return await response.json();
    }
}

// Usage
const api = new CryptoAPI();
const btcPrice = await api.getPrice('BTCUSDT');
console.log(`BTC: $${btcPrice.price}`);
```

## 🔍 Testing

Use our test script to verify all endpoints:

```bash
python test_api_fixes.py
```

## 📚 Related Documentation

- [Cryptocurrency Symbols](../symbols/cryptocurrencies.md) - List of supported symbols
- [Getting Started](../getting-started.md) - Quick start guide
- [Examples](../examples.md) - Code examples
- [Interactive Demo](../crypto_demo.html) - Live testing
