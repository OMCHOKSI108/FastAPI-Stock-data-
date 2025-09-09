# NSE Indices

This page lists all supported NSE (National Stock Exchange of India) indices available through our API.

## 🏛️ Supported NSE Indices

### Major Broad Market Indices

| Symbol | Index Name | Description |
|--------|------------|-------------|
| `NIFTY` | NIFTY 50 | India's benchmark stock market index |
| `BANKNIFTY` | NIFTY Bank | Banking sector index |
| `FINNIFTY` | NIFTY Financial Services | Financial services sector index |
| `MIDCPNIFTY` | NIFTY Midcap Select | Mid-cap companies index |

### Sectoral Indices

| Symbol | Index Name | Description |
|--------|------------|-------------|
| `NIFTYAUTO` | NIFTY Auto | Automobile sector index |
| `NIFTYIT` | NIFTY IT | Information Technology sector index |
| `NIFTYPHARMA` | NIFTY Pharma | Pharmaceutical sector index |
| `NIFTYFMCG` | NIFTY FMCG | Fast Moving Consumer Goods sector index |
| `NIFTYMEDIA` | NIFTY Media | Media & Entertainment sector index |
| `NIFTYMETAL` | NIFTY Metal | Metal sector index |
| `NIFTYREALTY` | NIFTY Realty | Real Estate sector index |
| `NIFTYENERGY` | NIFTY Energy | Energy sector index |
| `NIFTYPSE` | NIFTY PSE | Public Sector Enterprises index |

### Thematic Indices

| Symbol | Index Name | Description |
|--------|------------|-------------|
| `NIFTYNEXT50` | NIFTY Next 50 | Next 50 companies after NIFTY 50 |
| `NIFTYSMALLCAP` | NIFTY Smallcap 250 | Small-cap companies index |
| `NIFTYMIDCAP` | NIFTY Midcap 150 | Mid-cap companies index |
| `NIFTYMICROCAP` | NIFTY Microcap 250 | Micro-cap companies index |

## 🔍 Symbol Formats

### For Index Price Endpoint
Use the simple format without any prefix/suffix:

!!! example "Index Price Format"
    - `NIFTY` ✅
    - `BANKNIFTY` ✅
    - `FINNIFTY` ✅

### For Historical Data Endpoint
Use the Yahoo Finance format with `^` prefix:

!!! example "Historical Data Format"
    - `^NSENIFTY` ✅
    - `^NSEBANK` ✅
    - `^NSENEXT50` ✅

## 📈 Available Endpoints

### Index Data Endpoints

```bash
# Get current index price
GET /api/v1/market/price/index?index=NIFTY

# Get historical index data
GET /historical/^NSENIFTY?period=1d&interval=1d
```

### Examples

#### Get NIFTY Index Price
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index=NIFTY"
```

Response:
```json
{
    "symbol": "NIFTY",
    "lastPrice": 23456.75,
    "pChange": 0.85,
    "change": 198.50,
    "timestamp": "09-Dec-2024 15:30:00"
}
```

#### Get Historical NIFTY Data
```bash
curl "https://fastapi-stock-data.onrender.com/historical/^NSENIFTY?period=5d&interval=1d"
```

#### Get BANKNIFTY Price
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index=BANKNIFTY"
```

## 📊 Historical Data Parameters

### Periods
- `1d` - 1 day
- `5d` - 5 days
- `1mo` - 1 month
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year
- `2y` - 2 years
- `5y` - 5 years
- `10y` - 10 years
- `ytd` - Year to date
- `max` - Maximum available

### Intervals
- `1m` - 1 minute
- `2m` - 2 minutes
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `60m` - 60 minutes
- `1h` - 1 hour
- `1d` - 1 day
- `5d` - 5 days
- `1wk` - 1 week
- `1mo` - 1 month

## 📱 Integration Examples

### Python

```python
import requests

def get_index_price(index_name):
    url = f"https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index={index_name}"
    response = requests.get(url)
    return response.json()

def get_index_history(index_symbol, period="1mo", interval="1d"):
    url = f"https://fastapi-stock-data.onrender.com/historical/{index_symbol}?period={period}&interval={interval}"
    response = requests.get(url)
    return response.json()

# Usage
nifty_price = get_index_price("NIFTY")
print(f"NIFTY: {nifty_price['lastPrice']}")

nifty_history = get_index_history("^NSENIFTY", "1mo", "1d")
print(f"Historical data points: {len(nifty_history)}")
```

### JavaScript

```javascript
async function getIndexPrice(indexName) {
    const response = await fetch(
        `https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index=${indexName}`
    );
    const data = await response.json();
    return data;
}

async function getIndexHistory(indexSymbol, period = "1mo", interval = "1d") {
    const response = await fetch(
        `https://fastapi-stock-data.onrender.com/historical/${indexSymbol}?period=${period}&interval=${interval}`
    );
    const data = await response.json();
    return data;
}

// Usage
getIndexPrice("NIFTY").then(data => {
    console.log(`NIFTY: ${data.lastPrice}`);
});

getIndexHistory("^NSENIFTY").then(data => {
    console.log(`Data points: ${data.length}`);
});
```

## 📊 Index Components

### NIFTY 50 Components
The NIFTY 50 index consists of 50 large-cap companies:

**Banking & Financial Services (12)**
- HDFC Bank, ICICI Bank, Kotak Mahindra Bank, Axis Bank, IndusInd Bank, etc.

**IT & Technology (9)**
- TCS, Infosys, Wipro, HCL Technologies, Tech Mahindra, etc.

**Oil & Gas (3)**
- Reliance Industries, ONGC, Coal India

**Automobiles (4)**
- Maruti Suzuki, Mahindra & Mahindra, Tata Motors, Bajaj Auto

**And many more sectors...**

### BANKNIFTY Components
BANKNIFTY consists of the most liquid and large-cap banking stocks:
- HDFC Bank, ICICI Bank, Kotak Mahindra Bank, Axis Bank
- State Bank of India, Bank of Baroda, Punjab National Bank
- And other major banking stocks

## ⚠️ Important Notes

### Market Hours
- **Pre-open**: 9:00 AM - 9:15 AM IST
- **Regular session**: 9:15 AM - 3:30 PM IST
- **Closing**: 3:30 PM - 3:32 PM IST
- **Post-close**: 3:32 PM - 4:00 PM IST

### Index Calculation
- NIFTY indices are calculated using the free-float market capitalization method
- Base value: 1000 (NIFTY 50)
- Updated every 6 seconds during market hours

### Data Availability
- Real-time data during market hours
- Historical data available from index inception
- Some indices have limited historical data

## 🔄 Real-time Updates

For real-time index updates:

1. **Polling**: Call endpoints every 30 seconds during market hours
2. **WebSocket**: Use NSE WebSocket API directly
3. **Caching**: Implement client-side caching

## 📈 Index Performance

### NIFTY 50 Historical Performance
- **2024**: ~25-30% growth expected
- **2023**: ~18% growth
- **2022**: ~4% growth
- **2021**: ~24% growth

### Volatility Measures
- **VIX**: India VIX measures market volatility
- **Beta**: Measures stock/index volatility relative to market

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

- Check the [API Reference](../api/market.md) for detailed documentation
- Visit NSE website for official index information
- Report issues on [GitHub](https://github.com/OMCHOKSI108/FastAPI-Stock-data-)
