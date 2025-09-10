# Cryptocurrency API

This section documents the cryptocurrency data endpoints in FastStockAPI, providing real-time and historical crypto market data.

## Overview

The crypto API provides comprehensive cryptocurrency data including real-time prices, historical data, and market statistics from multiple exchanges.

## 🔗 Base URL

```
http://localhost:8000  (local development)
https://your-domain.com  (production)
```

## Endpoints

### 1. Get Cryptocurrency Quote

Get current price and market data for a specific cryptocurrency.

**Endpoint:** `GET /crypto/quote/{symbol}`

**Parameters:**
- `symbol` (path): Cryptocurrency symbol (e.g., `BTC`, `ETH`, `ADA`)

**Example Request:**
```bash
curl "http://localhost:8000/crypto/quote/BTC"
```

**Example Response:**
```json
{
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": 45123.45,
    "change24h": 2.5,
    "changePercent24h": 2.5,
    "volume24h": 28500000000,
    "marketCap": 890000000000,
    "lastUpdated": "2024-12-09T15:30:00Z"
}
```

### 2. Get Historical Cryptocurrency Data

Get historical price data for cryptocurrencies.

**Endpoint:** `GET /crypto/historical/{symbol}`

**Parameters:**
- `symbol` (path): Cryptocurrency symbol
- `period` (query, optional): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

**Example Request:**
```bash
curl "http://localhost:8000/crypto/historical/BTC?period=1mo"
```

**Example Response:**
```json
{
    "symbol": "BTC",
    "period": "1mo",
    "data": [
        {
            "date": "2024-11-09",
            "open": 45000.00,
            "high": 46000.00,
            "low": 44500.00,
            "close": 45500.00,
            "volume": 28500000000
        }
    ]
}
```

### 3. Get Available Cryptocurrencies

Get list of available cryptocurrency symbols.

**Endpoint:** `GET /crypto/list`

**Example Request:**
```bash
curl "http://localhost:8000/crypto/list"
```

**Example Response:**
```json
[
    "BTC",
    "ETH",
    "ADA",
    "SOL",
    "DOT",
    "LINK",
    "UNI",
    "AAVE"
]
```

## Response Formats

### Crypto Quote Response
```json
{
    "symbol": "string",
    "name": "string",
    "price": "number",
    "change24h": "number",
    "changePercent24h": "number",
    "volume24h": "number",
    "marketCap": "number",
    "lastUpdated": "string"
}
```

### Historical Data Response
```json
{
    "symbol": "string",
    "period": "string",
    "data": [
        {
            "date": "string",
            "open": "number",
            "high": "number",
            "low": "number",
            "close": "number",
            "volume": "number"
        }
    ]
}
```

## 💡 Usage Examples

### Python Example - Get Crypto Prices
```python
import requests

# Get single crypto price
response = requests.get("http://localhost:8000/crypto/quote/BTC")
btc_data = response.json()
print(f"BTC Price: ${btc_data['price']}")

# Get historical data
response = requests.get("http://localhost:8000/crypto/historical/ETH?period=1mo")
eth_history = response.json()
print(f"ETH Historical Data Points: {len(eth_history['data'])}")

# Get available symbols
response = requests.get("http://localhost:8000/crypto/list")
symbols = response.json()
print(f"Available Symbols: {symbols[:5]}")
```

### JavaScript Example - Crypto Dashboard
```javascript
async function getCryptoData() {
    try {
        // Get multiple crypto prices
        const symbols = ['BTC', 'ETH', 'ADA'];
        const promises = symbols.map(symbol =>
            fetch(`http://localhost:8000/crypto/quote/${symbol}`)
                .then(res => res.json())
        );

        const results = await Promise.all(promises);

        results.forEach(crypto => {
            console.log(`${crypto.symbol}: $${crypto.price} (${crypto.changePercent24h}%)`);
        });

    } catch (error) {
        console.error('Error fetching crypto data:', error);
    }
}

// Get historical data for chart
async function getCryptoHistory(symbol, period = '1mo') {
    try {
        const response = await fetch(`http://localhost:8000/crypto/historical/${symbol}?period=${period}`);
        const data = await response.json();

        // Process data for charting
        const chartData = data.data.map(item => ({
            x: new Date(item.date),
            y: item.close
        }));

        return chartData;
    } catch (error) {
        console.error('Error fetching historical data:', error);
        return [];
    }
}
```

## Supported Cryptocurrencies

### Major Cryptocurrencies
- **BTC**: Bitcoin
- **ETH**: Ethereum
- **ADA**: Cardano
- **SOL**: Solana
- **DOT**: Polkadot
- **LINK**: Chainlink
- **UNI**: Uniswap
- **AAVE**: Aave

### DeFi Tokens
- **COMP**: Compound
- **MKR**: MakerDAO
- **SUSHI**: SushiSwap
- **YFI**: Yearn Finance

### Layer 1 Blockchains
- **AVAX**: Avalanche
- **MATIC**: Polygon
- **FTM**: Fantom
- **NEAR**: Near Protocol

## ⚠️ Error Responses

- `404`: Cryptocurrency symbol not found
- `422`: Invalid parameters
- `500`: Server error or exchange API unavailable

## 🔄 Rate Limits

- Individual crypto requests: 100 per minute
- Historical data requests: 50 per minute
- Bulk requests: 30 per minute

## Data Sources

- **Primary**: Binance API
- **Secondary**: CoinGecko, CoinMarketCap
- **Real-time**: WebSocket connections for live updates

## Best Practices

1. **Use appropriate time periods** for historical data
2. **Cache frequently requested data** to reduce API calls
3. **Handle rate limits gracefully** with exponential backoff
4. **Validate symbols** before making requests
5. **Use bulk endpoints** when fetching multiple cryptocurrencies
6. **Monitor API health** with the health endpoint

## Advanced Usage

### Price Change Analysis
```python
def analyze_price_changes(symbol, period='1mo'):
    """Analyze price changes over a period"""
    response = requests.get(f"http://localhost:8000/crypto/historical/{symbol}?period={period}")
    data = response.json()

    if data['data']:
        first_price = data['data'][0]['close']
        last_price = data['data'][-1]['close']
        change_percent = ((last_price - first_price) / first_price) * 100

        return {
            'symbol': symbol,
            'period': period,
            'start_price': first_price,
            'end_price': last_price,
            'change_percent': change_percent,
            'trend': 'bullish' if change_percent > 0 else 'bearish'
        }
    return None
```

### Volume Analysis
```python
def analyze_volume(symbol, period='1mo'):
    """Analyze trading volume patterns"""
    response = requests.get(f"http://localhost:8000/crypto/historical/{symbol}?period={period}")
    data = response.json()

    volumes = [item['volume'] for item in data['data']]
    avg_volume = sum(volumes) / len(volumes)
    max_volume = max(volumes)
    min_volume = min(volumes)

    return {
        'symbol': symbol,
        'avg_volume': avg_volume,
        'max_volume': max_volume,
        'min_volume': min_volume,
        'volume_variability': (max_volume - min_volume) / avg_volume
    }
```

### Multi-Asset Portfolio Tracking
```python
def track_portfolio(holdings):
    """Track portfolio value across multiple cryptocurrencies"""
    total_value = 0
    portfolio_data = []

    for symbol, amount in holdings.items():
        response = requests.get(f"http://localhost:8000/crypto/quote/{symbol}")
        if response.status_code == 200:
            data = response.json()
            value = data['price'] * amount
            total_value += value

            portfolio_data.append({
                'symbol': symbol,
                'amount': amount,
                'price': data['price'],
                'value': value,
                'change_24h': data['changePercent24h']
            })

    return {
        'total_value': total_value,
        'holdings': portfolio_data,
        'timestamp': datetime.now().isoformat()
    }
```

## Market Insights

### Volatility Analysis
```javascript
function calculateVolatility(prices) {
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
        returns.push((prices[i] - prices[i-1]) / prices[i-1]);
    }

    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length;
    const volatility = Math.sqrt(variance) * Math.sqrt(252); // Annualized

    return volatility;
}
```

### Support and Resistance Levels
```javascript
function findSupportResistance(prices, window = 20) {
    const highs = prices.map(p => p.high);
    const lows = prices.map(p => p.low);

    const resistance = Math.max(...highs.slice(-window));
    const support = Math.min(...lows.slice(-window));

    return { support, resistance };
}
```

## Real-time Updates

For real-time price updates, consider implementing WebSocket connections:

```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@ticker');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`BTC Price: ${data.c}`);
};
```

## API Limits and Quotas

- **Free Tier**: 1000 requests per day
- **Premium Tier**: 100,000 requests per day
- **Enterprise**: Unlimited requests

Contact support for premium access and higher rate limits.

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

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Symbol not found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 502 | Bad Gateway (Binance API issues) |
| 503 | Service Unavailable |

## SDKs and Libraries

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

##  Related Documentation

- [Cryptocurrency Symbols](../symbols/cryptocurrencies.md) - List of supported symbols
- [Getting Started](../getting-started.md) - Quick start guide
- [Examples](../examples.md) - Code examples
- [Interactive Demo](../crypto_demo.html) - Live testing
