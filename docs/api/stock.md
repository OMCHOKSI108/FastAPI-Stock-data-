# Stock Data API

This section documents the stock market data endpoints in FastStockAPI, providing comprehensive access to Indian and US stock markets.

## Overview

The stock data API provides real-time and historical stock price information for NSE (National Stock Exchange of India) and US markets, with support for individual stocks, bulk quotes, and market indices.

## 🔗 Base URL

```
http://localhost:8000  (local development)
https://your-domain.com  (production)
```

## Endpoints

### 1. Get Indian Stock Quote

Get current price information for a specific NSE stock.

**Endpoint:** `GET /stocks/IND/{symbol}`

**Parameters:**
- `symbol` (path): NSE stock symbol (e.g., `RELIANCE`, `TCS`, `HDFC`)

**Example Request:**
```bash
curl "http://localhost:8000/stocks/IND/RELIANCE"
```

**Example Response:**
```json
{
    "symbol": "RELIANCE",
    "companyName": "Reliance Industries Ltd",
    "lastPrice": 2456.75,
    "pChange": 1.25,
    "change": 30.50,
    "timestamp": "09-Dec-2024 15:30:00"
}
```

### 2. Get US Stock Quote

Get current price information for a specific US stock.

**Endpoint:** `GET /stocks/US/{symbol}`

**Parameters:**
- `symbol` (path): US stock symbol (e.g., `AAPL`, `GOOGL`, `MSFT`)

**Example Request:**
```bash
curl "http://localhost:8000/stocks/US/AAPL"
```

**Example Response:**
```json
{
    "symbol": "AAPL",
    "companyName": "Apple Inc.",
    "lastPrice": 192.53,
    "pChange": -0.85,
    "change": -1.65,
    "timestamp": "2024-12-09T15:30:00Z"
}
```

### 3. Get Historical Indian Stock Data

Get historical price data for NSE stocks.

**Endpoint:** `GET /stocks/historical/IND/{symbol}`

**Parameters:**
- `symbol` (path): NSE stock symbol
- `period` (query, optional): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

**Example Request:**
```bash
curl "http://localhost:8000/stocks/historical/IND/RELIANCE?period=1mo"
```

### 4. Get Historical US Stock Data

Get historical price data for US stocks.

**Endpoint:** `GET /stocks/historical/US/{symbol}`

**Parameters:**
- `symbol` (path): US stock symbol
- `period` (query, optional): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

**Example Request:**
```bash
curl "http://localhost:8000/stocks/historical/US/AAPL?period=1mo"
```

### 5. Get US Market Index

Get current data for US market indices.

**Endpoint:** `GET /stocks/index/US/{symbol}`

**Parameters:**
- `symbol` (path): US index symbol (`DJI`, `SPX`, `IXIC`)

**Example Request:**
```bash
curl "http://localhost:8000/stocks/index/US/DJI"
```

### 6. Get BSE Market Index

Get current data for BSE market indices.

**Endpoint:** `GET /stocks/index/BSE/{symbol}`

**Parameters:**
- `symbol` (path): BSE index symbol (`SENSEX`, `BSE100`)

**Example Request:**
```bash
curl "http://localhost:8000/stocks/index/BSE/SENSEX"
```

### 7. Get Historical US Index Data

Get historical data for US market indices.

**Endpoint:** `GET /stocks/index/US/{symbol}/historical`

**Parameters:**
- `symbol` (path): US index symbol
- `period` (query, optional): Time period

**Example Request:**
```bash
curl "http://localhost:8000/stocks/index/US/SPX/historical?period=1mo"
```

### 8. Get Historical BSE Index Data

Get historical data for BSE market indices.

**Endpoint:** `GET /stocks/index/BSE/{symbol}/historical`

**Parameters:**
- `symbol` (path): BSE index symbol
- `period` (query, optional): Time period

**Example Request:**
```bash
curl "http://localhost:8000/stocks/index/BSE/SENSEX/historical?period=1mo"
```

### 9. Get Available Indian Stocks

Get list of available Indian stock symbols.

**Endpoint:** `GET /stocks/indian/list`

**Example Request:**
```bash
curl "http://localhost:8000/stocks/indian/list"
```

### 10. Get Available US Stocks

Get list of available US stock symbols.

**Endpoint:** `GET /stocks/us/list`

**Example Request:**
```bash
curl "http://localhost:8000/stocks/us/list"
```

## Response Formats

### Stock Quote Response
```json
{
    "symbol": "RELIANCE",
    "companyName": "Reliance Industries Ltd",
    "lastPrice": 2456.75,
    "pChange": 1.25,
    "change": 30.50,
    "timestamp": "09-Dec-2024 15:30:00"
}
```

### Historical Data Response
```json
{
    "symbol": "RELIANCE",
    "period": "1mo",
    "data": [
        {
            "date": "2024-11-09",
            "open": 2450.00,
            "high": 2470.00,
            "low": 2440.00,
            "close": 2465.50,
            "volume": 1524000
        }
    ]
}
```

## ⚠️ Error Responses

- `404`: Stock symbol not found
- `422`: Invalid parameters
- `500`: Server error or data source unavailable

## 💡 Usage Examples

### Python Example
```python
import requests

# Get Indian stock price
response = requests.get("http://localhost:8000/stocks/IND/RELIANCE")
data = response.json()
print(f"RELIANCE: ₹{data['lastPrice']}")

# Get US stock price
response = requests.get("http://localhost:8000/stocks/US/AAPL")
data = response.json()
print(f"AAPL: ${data['lastPrice']}")
```

### JavaScript Example
```javascript
// Get stock data
fetch('http://localhost:8000/stocks/IND/TCS')
    .then(response => response.json())
    .then(data => {
        console.log(`TCS Price: ₹${data.lastPrice}`);
    });
```

## 🔄 Rate Limits

- Individual stock requests: 100 per minute
- Bulk requests: 50 per minute
- Historical data: 30 per minute

## Data Sources

- **Indian Stocks**: NSE (National Stock Exchange)
- **US Stocks**: Yahoo Finance
- **Indices**: Yahoo Finance and NSE

## Best Practices

1. Use appropriate time periods for historical data
2. Cache frequently requested data
3. Handle rate limits gracefully
4. Validate stock symbols before requests
5. Use bulk endpoints for multiple symbols when possible

Get historical price data for a stock.

**Endpoint:** `GET /historical/{symbol}`

**Parameters:**
- `symbol` (path): Stock symbol with `.NS` suffix
- `period` (query, optional): Time period (default: `1d`)
- `interval` (query, optional): Data interval (default: `1d`)

**Supported Periods:**
- `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

**Supported Intervals:**
- `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/historical/RELIANCE.NS?period=1mo&interval=1d"
```

**Example Response:**
```json
[
    {
        "Date": "2024-11-09",
        "Open": 2450.0,
        "High": 2470.0,
        "Low": 2440.0,
        "Close": 2456.75,
        "Volume": 1234567
    },
    {
        "Date": "2024-11-10",
        "Open": 2456.75,
        "High": 2480.0,
        "Low": 2450.0,
        "Close": 2465.25,
        "Volume": 1456789
    }
]
```

---

### 3. Legacy Stock Endpoints

**Get Quote:** `GET /quote/{symbol}`
**Fetch Quote:** `GET /fetch/{symbol}`

These endpoints provide basic stock information and are maintained for backward compatibility.

**Example:**
```bash
curl "https://fastapi-stock-data.onrender.com/quote/RELIANCE.NS"
```

---

### 4. Get All Quotes

Get all cached stock quotes.

**Endpoint:** `GET /quotes`

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/quotes"
```

**Example Response:**
```json
{
    "RELIANCE.NS": {
        "symbol": "RELIANCE.NS",
        "price": 2456.75,
        "timestamp": "2024-12-09T15:30:00Z"
    },
    "TCS.NS": {
        "symbol": "TCS.NS",
        "price": 3456.25,
        "timestamp": "2024-12-09T15:30:00Z"
    }
}
```

## 📊 Response Formats

### Stock Price Response

```json
{
    "symbol": "string",
    "companyName": "string",
    "lastPrice": "number",
    "pChange": "number",
    "change": "number",
    "timestamp": "string"
}
```

### Historical Data Response

```json
[
    {
        "Date": "string",
        "Open": "number",
        "High": "number",
        "Low": "number",
        "Close": "number",
        "Volume": "number"
    }
]
```

## ⚠️ Important Notes

### Symbol Format
- All NSE stock symbols must include the `.NS` suffix
- Example: `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`

### Market Hours
- **Pre-market**: 9:00 AM - 9:15 AM IST
- **Regular session**: 9:15 AM - 3:30 PM IST
- **Post-market**: 3:30 PM - 4:00 PM IST

### Data Sources
- Primary: Yahoo Finance (yfinance library)
- Fallback: NSE direct APIs when available

### Rate Limits
- No explicit rate limits for stock endpoints
- Respectful usage recommended
- Consider implementing client-side caching

## Integration Examples

### Python

```python
import requests

def get_stock_price(symbol):
    url = f"https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol={symbol}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
stock_data = get_stock_price("RELIANCE.NS")
if stock_data:
    print(f"{stock_data['companyName']}: ₹{stock_data['lastPrice']}")
```

### JavaScript

```javascript
async function getStockPrice(symbol) {
    const response = await fetch(
        `https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=${symbol}`
    );

    if (response.ok) {
        const data = await response.json();
        return data;
    } else {
        console.error(`Error: ${response.status}`);
        return null;
    }
}

// Usage
getStockPrice('RELIANCE.NS').then(data => {
    if (data) {
        console.log(`${data.companyName}: ₹${data.lastPrice}`);
    }
});
```

## 🔍 Error Handling

### Common HTTP Status Codes

- **200**: Success
- **404**: Stock symbol not found or delisted
- **500**: Server error or data source unavailable

### Error Response Format

```json
{
    "detail": "Error description message"
}
```

## Data Fields Explanation

| Field | Description | Type |
|-------|-------------|------|
| `symbol` | Stock symbol with exchange suffix | string |
| `companyName` | Full company name | string |
| `lastPrice` | Last traded price | number |
| `pChange` | Percentage change from previous close | number |
| `change` | Absolute change from previous close | number |
| `timestamp` | Data timestamp | string |

## 🆘 Troubleshooting

### Common Issues

**404 Not Found**
- Check symbol format (must include `.NS`)
- Verify symbol exists on NSE
- Stock may be delisted or suspended

**No Data Available**
- Check during market hours
- Some stocks may have limited historical data

**Slow Response**
- Historical data requests may take longer
- Consider using shorter time periods

### Getting Help

- Check the [NSE Stocks](../symbols/nse-stocks.md) page for supported symbols
- Report issues on [GitHub](https://github.com/OMCHOKSI108/FastAPI-Stock-data-)
- Visit NSE website for official symbol verification
