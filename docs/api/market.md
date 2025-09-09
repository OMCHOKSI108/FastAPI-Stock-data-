# Market Data API

This section documents market and index data endpoints in the FastAPI Stock & Crypto Data API.

## 📊 Overview

The market data API provides real-time and historical data for NSE indices and broader market information.

## 🔗 Base URL

```
https://fastapi-stock-data.onrender.com
```

## 📋 Endpoints

### 1. Get Index Price

Get current price information for NSE market indices.

**Endpoint:** `GET /api/v1/market/price/index?index={index_name}`

**Parameters:**
- `index` (query): NSE index name (e.g., `NIFTY`, `BANKNIFTY`)

**Supported Indices:**
- `NIFTY` - NIFTY 50
- `BANKNIFTY` - NIFTY Bank
- `FINNIFTY` - NIFTY Financial Services
- `MIDCPNIFTY` - NIFTY Midcap Select

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index=NIFTY"
```

**Example Response:**
```json
{
    "symbol": "NIFTY",
    "lastPrice": 23456.75,
    "pChange": 0.85,
    "change": 198.50,
    "timestamp": "09-Dec-2024 15:30:00"
}
```

**Error Responses:**
- `404`: Index not found
- `500`: Server error

---

### 2. Get Historical Index Data

Get historical price data for market indices.

**Endpoint:** `GET /historical/{index_symbol}`

**Parameters:**
- `index_symbol` (path): Index symbol with Yahoo Finance format (e.g., `^NSENIFTY`)
- `period` (query, optional): Time period (default: `1d`)
- `interval` (query, optional): Data interval (default: `1d`)

**Supported Index Symbols:**
- `^NSENIFTY` - NIFTY 50
- `^NSEBANK` - NIFTY Bank
- `^NSENEXT50` - NIFTY Next 50
- `^NSEMIDCAP` - NIFTY Midcap 150

**Supported Periods:**
- `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

**Supported Intervals:**
- `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/historical/^NSENIFTY?period=1mo&interval=1d"
```

**Example Response:**
```json
[
    {
        "Date": "2024-11-09",
        "Open": 23400.0,
        "High": 23500.0,
        "Low": 23350.0,
        "Close": 23456.75,
        "Volume": 234567890
    },
    {
        "Date": "2024-11-10",
        "Open": 23456.75,
        "High": 23600.0,
        "Low": 23400.0,
        "Close": 23567.25,
        "Volume": 245678901
    }
]
```

## 📊 Response Formats

### Index Price Response

```json
{
    "symbol": "string",
    "lastPrice": "number",
    "pChange": "number",
    "change": "number",
    "timestamp": "string"
}
```

### Historical Index Data Response

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

### Index Symbol Formats

**For Index Price Endpoint:**
- Use simple names: `NIFTY`, `BANKNIFTY`
- No special characters or prefixes needed

**For Historical Data Endpoint:**
- Use Yahoo Finance format: `^NSENIFTY`, `^NSEBANK`
- Must include `^` prefix and `NSE` in the name

### Market Hours
- **Pre-market**: 9:00 AM - 9:15 AM IST
- **Regular session**: 9:15 AM - 3:30 PM IST
- **Post-market**: 3:30 PM - 4:00 PM IST

### Index Calculation
- NIFTY indices use free-float market capitalization method
- Base value: 1000 for NIFTY 50
- Updated every 6 seconds during market hours

### Data Sources
- Primary: NSE direct APIs
- Fallback: Yahoo Finance for historical data

## 📱 Integration Examples

### Python

```python
import requests

def get_index_price(index_name):
    url = f"https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index={index_name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def get_index_history(index_symbol, period="1mo", interval="1d"):
    url = f"https://fastapi-stock-data.onrender.com/historical/{index_symbol}?period={period}&interval={interval}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
nifty_price = get_index_price("NIFTY")
if nifty_price:
    print(f"NIFTY: {nifty_price['lastPrice']} ({nifty_price['pChange']}%)")

nifty_history = get_index_history("^NSENIFTY", "1mo", "1d")
if nifty_history:
    print(f"Historical data points: {len(nifty_history)}")
```

### JavaScript

```javascript
async function getIndexPrice(indexName) {
    const response = await fetch(
        `https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index=${indexName}`
    );

    if (response.ok) {
        const data = await response.json();
        return data;
    } else {
        console.error(`Error: ${response.status}`);
        return null;
    }
}

async function getIndexHistory(indexSymbol, period = "1mo", interval = "1d") {
    const response = await fetch(
        `https://fastapi-stock-data.onrender.com/historical/${indexSymbol}?period=${period}&interval=${interval}`
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
getIndexPrice('NIFTY').then(data => {
    if (data) {
        console.log(`NIFTY: ${data.lastPrice} (${data.pChange}%)`);
    }
});

getIndexHistory('^NSENIFTY').then(data => {
    if (data) {
        console.log(`Historical data points: ${data.length}`);
    }
});
```

## 📊 Index Components

### NIFTY 50 Components
The NIFTY 50 index consists of 50 large-cap companies representing various sectors:

**Banking & Financial Services (12 companies)**
- HDFC Bank, ICICI Bank, Kotak Mahindra Bank, Axis Bank, IndusInd Bank, etc.

**IT & Technology (9 companies)**
- TCS, Infosys, Wipro, HCL Technologies, Tech Mahindra, etc.

**Oil & Gas (3 companies)**
- Reliance Industries, ONGC, Coal India

**Automobiles (4 companies)**
- Maruti Suzuki, Mahindra & Mahindra, Tata Motors, Bajaj Auto

**And other sectors...**

### BANKNIFTY Components
BANKNIFTY consists of the most liquid and large-cap banking stocks:
- HDFC Bank, ICICI Bank, Kotak Mahindra Bank, Axis Bank
- State Bank of India, Bank of Baroda, Punjab National Bank
- And other major banking stocks

## 🔍 Error Handling

### Common HTTP Status Codes

- **200**: Success
- **404**: Index not found
- **500**: Server error or data source unavailable

### Error Response Format

```json
{
    "detail": "Error description message"
}
```

## 📊 Data Fields Explanation

| Field | Description | Type |
|-------|-------------|------|
| `symbol` | Index symbol | string |
| `lastPrice` | Last traded value | number |
| `pChange` | Percentage change from previous close | number |
| `change` | Absolute change from previous close | number |
| `timestamp` | Data timestamp | string |

## 🆘 Troubleshooting

### Common Issues

**404 Not Found**
- Check index name spelling
- Verify index exists on NSE

**No Data Available**
- Check during market hours
- Some indices may be under maintenance

**Historical Data Issues**
- Try shorter time periods
- Some indices have limited historical data

### Getting Help

- Check the [Indices](../symbols/indices.md) page for supported indices
- Report issues on [GitHub](https://github.com/OMCHOKSI108/FastAPI-Stock-data-)
- Visit NSE website for official index information
