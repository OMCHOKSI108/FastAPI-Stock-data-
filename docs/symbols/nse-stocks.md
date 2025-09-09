# NSE Stocks

This page lists all supported NSE (National Stock Exchange of India) stock symbols available through our API.

## 📊 Supported NSE Stocks

Our API supports 200+ NSE stocks. Here are the major categories:

### Banking & Financial Services

| Symbol | Company Name |
|--------|--------------|
| `HDFCBANK.NS` | HDFC Bank Ltd |
| `ICICIBANK.NS` | ICICI Bank Ltd |
| `KOTAKBANK.NS` | Kotak Mahindra Bank Ltd |
| `AXISBANK.NS` | Axis Bank Ltd |
| `INDUSINDBK.NS` | IndusInd Bank Ltd |
| `BANDHANBNK.NS` | Bandhan Bank Ltd |
| `IDFCFIRSTB.NS` | IDFC First Bank Ltd |
| `FEDERALBNK.NS` | Federal Bank Ltd |

### IT & Technology

| Symbol | Company Name |
|--------|--------------|
| `TCS.NS` | Tata Consultancy Services Ltd |
| `INFY.NS` | Infosys Ltd |
| `WIPRO.NS` | Wipro Ltd |
| `HCLTECH.NS` | HCL Technologies Ltd |
| `TECHM.NS` | Tech Mahindra Ltd |
| `LTIMINDTREE.NS` | LTIMindtree Ltd |
| `MINDTREE.NS` | Mindtree Ltd |
| `COFORGE.NS` | Coforge Ltd |

### Oil & Gas

| Symbol | Company Name |
|--------|--------------|
| `RELIANCE.NS` | Reliance Industries Ltd |
| `ONGC.NS` | Oil & Natural Gas Corporation Ltd |
| `GAIL.NS` | GAIL (India) Ltd |
| `BPCL.NS` | Bharat Petroleum Corporation Ltd |
| `IOC.NS` | Indian Oil Corporation Ltd |
| `HINDPETRO.NS` | Hindustan Petroleum Corporation Ltd |
| `NTPC.NS` | NTPC Ltd |
| `POWERGRID.NS` | Power Grid Corporation of India Ltd |

### Metals & Mining

| Symbol | Company Name |
|--------|--------------|
| `HINDALCO.NS` | Hindalco Industries Ltd |
| `JSWSTEEL.NS` | JSW Steel Ltd |
| `TATASTEEL.NS` | Tata Steel Ltd |
| `VEDL.NS` | Vedanta Ltd |
| `NMDC.NS` | NMDC Ltd |
| `COALINDIA.NS` | Coal India Ltd |

### Cement

| Symbol | Company Name |
|--------|--------------|
| `ULTRACEMCO.NS` | UltraTech Cement Ltd |
| `GRASIM.NS` | Grasim Industries Ltd |
| `SHREECEM.NS` | Shree Cement Ltd |
| `AMBUJACEM.NS` | Ambuja Cements Ltd |
| `ACC.NS` | ACC Ltd |
| `DALBHARAT.NS` | Dalmia Bharat Ltd |

### Pharmaceuticals

| Symbol | Company Name |
|--------|--------------|
| `DRREDDY.NS` | Dr. Reddy's Laboratories Ltd |
| `SUNPHARMA.NS` | Sun Pharmaceutical Industries Ltd |
| `CIPLA.NS` | Cipla Ltd |
| `DIVISLAB.NS` | Divi's Laboratories Ltd |
| `LUPIN.NS` | Lupin Ltd |
| `AUROPHARMA.NS` | Aurobindo Pharma Ltd |
| `BIOCON.NS` | Biocon Ltd |
| `ZYDUSLIFE.NS` | Zydus Lifesciences Ltd |

### Healthcare

| Symbol | Company Name |
|--------|--------------|
| `APOLLOHOSP.NS` | Apollo Hospitals Enterprise Ltd |
| `MAXHEALTH.NS` | Max Healthcare Institute Ltd |
| `FORTIS.NS` | Fortis Healthcare Ltd |
| `NH.NS` | Narayana Hrudayalaya Ltd |

## 🔍 Symbol Format

All NSE stock symbols must include the `.NS` suffix:

!!! example "Correct Format"
    - `RELIANCE.NS` ✅
    - `TCS.NS` ✅
    - `HDFCBANK.NS` ✅

!!! danger "Incorrect Format"
    - `RELIANCE` ❌
    - `TCS` ❌
    - `HDFCBANK` ❌

## 📈 Available Endpoints

### Stock Data Endpoints

```bash
# Get stock price
GET /api/v1/market/price/stock?symbol=RELIANCE.NS

# Get historical data
GET /historical/RELIANCE.NS?period=1d&interval=1d

# Legacy endpoints
GET /quote/RELIANCE.NS
GET /fetch/RELIANCE.NS
```

### Examples

#### Get Stock Price
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=RELIANCE.NS"
```

Response:
```json
{
    "symbol": "RELIANCE.NS",
    "companyName": "Reliance Industries Ltd",
    "lastPrice": 2456.75,
    "pChange": 1.25,
    "change": 30.50,
    "timestamp": "09-Dec-2024 15:30:00"
}
```

#### Get Historical Data
```bash
curl "https://fastapi-stock-data.onrender.com/historical/RELIANCE.NS?period=5d&interval=1d"
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
- `90m` - 90 minutes
- `1h` - 1 hour
- `1d` - 1 day
- `5d` - 5 days
- `1wk` - 1 week
- `1mo` - 1 month
- `3mo` - 3 months

## 🏛️ Market Indices

In addition to individual stocks, we support major NSE indices:

| Symbol | Index Name |
|--------|------------|
| `NIFTY` | NIFTY 50 |
| `BANKNIFTY` | NIFTY Bank |
| `FINNIFTY` | NIFTY Financial Services |
| `MIDCPNIFTY` | NIFTY Midcap Select |

### Index Endpoints

```bash
# Get index price
GET /api/v1/market/price/index?index=NIFTY

# Get historical index data
GET /historical/^NSENIFTY?period=1d&interval=1d
```

!!! note "Index Symbols"
    For historical data, use the Yahoo Finance format: `^NSENIFTY`, `^NSEBANK`

## 📱 Integration Examples

### Python

```python
import requests

def get_stock_price(symbol):
    url = f"https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol={symbol}"
    response = requests.get(url)
    return response.json()

# Usage
price_data = get_stock_price("RELIANCE.NS")
print(f"{price_data['companyName']}: ₹{price_data['lastPrice']}")
```

### JavaScript

```javascript
async function getStockPrice(symbol) {
    const response = await fetch(
        `https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=${symbol}`
    );
    const data = await response.json();
    return data;
}

// Usage
getStockPrice("TCS.NS").then(data => {
    console.log(`${data.companyName}: ₹${data.lastPrice}`);
});
```

## ⚠️ Important Notes

### Market Hours
- **Pre-market**: 9:00 AM - 9:15 AM IST
- **Regular session**: 9:15 AM - 3:30 PM IST
- **Post-market**: 3:30 PM - 4:00 PM IST

### Data Availability
- Real-time data during market hours
- Historical data available for past periods
- Some stocks may have limited historical data

### Symbol Changes
- Company symbols may change due to mergers, acquisitions, etc.
- Always verify the current symbol on NSE website
- Our API may not reflect real-time symbol changes

## 🔄 Real-time Updates

For real-time stock updates:

1. **Polling**: Call endpoints every 30-60 seconds during market hours
2. **WebSocket**: Use NSE WebSocket API directly
3. **Caching**: Implement client-side caching

## 🆘 Troubleshooting

### Common Issues

**404 Not Found**
- Check symbol format (must include `.NS`)
- Verify symbol exists on NSE

**No Data Available**
- Stock may be suspended or delisted
- Check during market hours

**Historical Data Issues**
- Some stocks have limited historical data
- Try shorter time periods

### Getting Help

- Check the [API Reference](../api/stock.md) for detailed documentation
- Report issues on [GitHub](https://github.com/OMCHOKSI108/FastAPI-Stock-data-)
- Visit NSE website for official symbol verification
