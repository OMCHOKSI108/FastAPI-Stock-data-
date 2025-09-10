# Options Data API

This section documents the options trading data endpoints in FastStockAPI, providing comprehensive access to NSE options chains, analytics, and historical data.

## Overview

The options API provides complete options trading data including option chains, strike prices, expiry dates, analytics (PCR, Max Pain), and historical option prices for Indian market indices.

## 🔗 Base URL

```
http://localhost:8000  (local development)
https://your-domain.com  (production)
```

## Endpoints

### 1. Get Index Price

Get current price for Indian market indices.

**Endpoint:** `GET /options/index-price`

**Parameters:**
- `index` (query): Index symbol (`NIFTY`, `BANKNIFTY`, `NIFTYIT`, etc.)

**Example Request:**
```bash
curl "http://localhost:8000/options/index-price?index=NIFTY"
```

**Example Response:**
```json
{
    "symbol": "NIFTY",
    "lastPrice": 24500.75,
    "pChange": 0.85,
    "change": 207.50,
    "timestamp": "09-Dec-2024 15:30:00"
}
```

### 2. Get Stock Price

Get current price for individual NSE stocks.

**Endpoint:** `GET /options/stock-price`

**Parameters:**
- `symbol` (query): NSE stock symbol (e.g., `RELIANCE`, `TCS`)

**Example Request:**
```bash
curl "http://localhost:8000/options/stock-price?symbol=RELIANCE"
```

### 3. Get Available Expiries

Get list of available option expiry dates for an index.

**Endpoint:** `GET /options/expiries`

**Parameters:**
- `index` (query): Index symbol

**Example Request:**
```bash
curl "http://localhost:8000/options/expiries?index=NIFTY"
```

**Example Response:**
```json
[
    "26-Dec-2024",
    "30-Jan-2025",
    "27-Feb-2025",
    "27-Mar-2025"
]
```

### 4. Get Option Price

Get price for a specific option contract.

**Endpoint:** `GET /options/option-price`

**Parameters:**
- `index` (query): Index symbol
- `strike` (query): Strike price (e.g., 24000)
- `expiry` (query): Expiry date in DDMMYY format (e.g., `160925` for 16-Sep-2025)
- `option_type` (query): `CE` or `PE`

**Example Request:**
```bash
curl "http://localhost:8000/options/option-price?index=NIFTY&strike=24000&expiry=160925&option_type=CE"
```

**Example Response:**
```json
{
    "symbol": "NIFTY24000CE",
    "strike": 24000,
    "expiry": "16-Sep-2025",
    "option_type": "CE",
    "lastPrice": 125.50,
    "openInterest": 2450000,
    "volume": 125000,
    "bid": 125.25,
    "ask": 125.75,
    "timestamp": "2024-12-09T15:30:00Z"
}
```

### 5. Get Direct Options Data

Get complete options chain data without saving to CSV.

**Endpoint:** `GET /options/direct-data`

**Parameters:**
- `index` (query): Index symbol
- `expiry` (query): Expiry date in DDMMYY format
- `num_strikes` (query, optional): Number of strikes around ATM (default: 25)

**Example Request:**
```bash
curl "http://localhost:8000/options/direct-data?index=NIFTY&expiry=160925&num_strikes=10"
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "expiry": "16-Sep-2025",
    "underlying_value": 24500.75,
    "options": [
        {
            "strikePrice": 23800,
            "expiryDate": "16-Sep-2025",
            "CE": {
                "lastPrice": 725.50,
                "openInterest": 1250000,
                "totalTradedVolume": 75000
            },
            "PE": {
                "lastPrice": 25.75,
                "openInterest": 2450000,
                "totalTradedVolume": 125000
            }
        }
    ],
    "timestamp": "2024-12-09T15:30:00Z"
}
```

### 6. Get Strike-Specific Data

Get option data for a specific strike price.

**Endpoint:** `GET /options/strike-data`

**Parameters:**
- `index` (query): Index symbol
- `strike` (query): Strike price
- `expiry` (query): Expiry date in DDMMYY format
- `option_type` (query): `CE`, `PE`, or `BOTH`

**Example Request:**
```bash
curl "http://localhost:8000/options/strike-data?index=NIFTY&strike=24000&expiry=160925&option_type=BOTH"
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "strike": 24000,
    "expiry": "16-Sep-2025",
    "option_type": "BOTH",
    "ce_data": {
        "lastPrice": 125.50,
        "openInterest": 2450000,
        "volume": 125000
    },
    "pe_data": {
        "lastPrice": 95.25,
        "openInterest": 1850000,
        "volume": 95000
    },
    "underlying_value": 24500.75,
    "timestamp": "2024-12-09T15:30:00Z"
}
```

### 7. Get Historical Option Data

Get historical price data for specific option contracts.

**Endpoint:** `GET /options/historical/{symbol}`

**Parameters:**
- `symbol` (path): Index symbol
- `strike` (query): Strike price
- `expiry` (query): Expiry date in DDMMYY format
- `option_type` (query): `CE` or `PE`
- `period` (query, optional): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

**Example Request:**
```bash
curl "http://localhost:8000/options/historical/NIFTY?strike=24000&expiry=160925&option_type=CE&period=1mo"
```

### 8. Fetch and Save Options Data

Fetch options data and save to CSV file.

**Endpoint:** `POST /options/fetch`

**Request Body:**
```json
{
    "index": "NIFTY",
    "num_strikes": 25
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/options/fetch" \
     -H "Content-Type: application/json" \
     -d '{"index": "NIFTY", "num_strikes": 25}'
```

### 9. Fetch Specific Expiry Options

Fetch options data for a specific expiry date.

**Endpoint:** `POST /options/fetch/expiry`

**Request Body:**
```json
{
    "index": "NIFTY",
    "expiry": "16-Sep-2025",
    "num_strikes": 25
}
```

### 10. Fetch Options Data (JSON Response)

Fetch options data and return JSON directly without saving to CSV.

**Endpoint:** `POST /options/fetch/json`

**Request Body:**
```json
{
    "index": "NIFTY",
    "num_strikes": 25
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/options/fetch/json" \
     -H "Content-Type: application/json" \
     -d '{"index": "NIFTY", "num_strikes": 25}'
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "expiry": "16-Sep-2025",
    "underlying_value": 24500.75,
    "options": [
        {
            "strikePrice": 24000,
            "expiryDate": "16-Sep-2025",
            "CE": {
                "strikePrice": 24000,
                "expiryDate": "16-Sep-2025",
                "underlying": "NIFTY",
                "identifier": "NIFTY16SEP202424000CE",
                "openInterest": 125000,
                "changeinOpenInterest": 15000,
                "pchangeinOpenInterest": 13.64,
                "totalTradedVolume": 250000,
                "impliedVolatility": 15.25,
                "lastPrice": 525.50,
                "change": 25.75,
                "pChange": 5.15,
                "totalBuyQuantity": 50000,
                "totalSellQuantity": 75000,
                "bidQty": 50,
                "bidprice": 525.00,
                "askQty": 75,
                "askPrice": 526.00,
                "underlyingValue": 24500.75
            },
            "PE": {
                "strikePrice": 24000,
                "expiryDate": "16-Sep-2025",
                "underlying": "NIFTY",
                "identifier": "NIFTY16SEP202424000PE",
                "openInterest": 98000,
                "changeinOpenInterest": -5000,
                "pchangeinOpenInterest": -4.85,
                "totalTradedVolume": 180000,
                "impliedVolatility": 14.85,
                "lastPrice": 125.25,
                "change": -5.50,
                "pChange": -4.20,
                "totalBuyQuantity": 35000,
                "totalSellQuantity": 45000,
                "bidQty": 40,
                "bidprice": 125.00,
                "askQty": 60,
                "askPrice": 125.50,
                "underlyingValue": 24500.75
            }
        }
    ],
    "timestamp": "2024-12-09T15:30:00.123456"
}
```

### 11. Fetch Specific Expiry Options (JSON Response)

Fetch options data for a specific expiry date and return JSON directly.

**Endpoint:** `POST /options/fetch/expiry/json`

**Request Body:**
```json
{
    "index": "NIFTY",
    "expiry": "160925",
    "num_strikes": 25
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/options/fetch/expiry/json" \
     -H "Content-Type: application/json" \
     -d '{"index": "NIFTY", "expiry": "160925", "num_strikes": 25}'
```

**Note:** The expiry date can be provided in DDMMYY format (e.g., "160925" for 16-Sep-2025) or DD-MMM-YYYY format.

### 12. Get Options Analytics

Get analytics for saved options data.

**Endpoint:** `GET /options/analytics`

**Parameters:**
- `index` (query): Index symbol
- `limit` (query, optional): Number of records to analyze

**Example Request:**
```bash
curl "http://localhost:8000/options/analytics?index=NIFTY&limit=500"
```

## Response Formats

### Fetch Result Metadata
```json
{
    "createdAtUTC": "2024-12-09T15:30:00Z",
    "indexName": "NIFTY",
    "nearestExpiry": "16-Sep-2025",
    "underlyingValue": 24500.75,
    "atmStrike": 24500,
    "selectedStrikesRange": [23500, 25500],
    "totalStrikesFetched": 41
}
```

### Analytics Response
```json
{
    "meta": {
        "createdAtUTC": "2024-12-09T15:30:00Z",
        "indexName": "NIFTY",
        "underlyingValue": 24500.75
    },
    "pcr": 1.25,
    "top_oi": [
        {
            "strike": 24000,
            "oi_ce": 2450000,
            "oi_pe": 1850000,
            "total_oi": 4300000
        }
    ],
    "max_pain": {
        "max_pain_strike": 24500,
        "total_ce_oi": 125000000,
        "total_pe_oi": 100000000
    }
}
```

## ⚠️ Error Responses

- `400`: Invalid parameters or expiry date format
- `404`: Index not found or no data available
- `422`: Invalid expiry date or strike price
- `500`: Server error or NSE data unavailable

## 💡 Usage Examples

### Python Example - Get Options Chain
```python
import requests

# Get options data
response = requests.get(
    "http://localhost:8000/options/direct-data",
    params={
        "index": "NIFTY",
        "expiry": "160925",
        "num_strikes": 10
    }
)
data = response.json()

print(f"Underlying: {data['underlying_value']}")
for option in data['options'][:5]:
    print(f"Strike: {option['strikePrice']}")
    if 'CE' in option:
        print(f"  CE: ₹{option['CE']['lastPrice']}")
    if 'PE' in option:
        print(f"  PE: ₹{option['PE']['lastPrice']}")
```

### JavaScript Example - Get Option Price
```javascript
// Get specific option price
const params = new URLSearchParams({
    index: 'NIFTY',
    strike: 24000,
    expiry: '160925',
    option_type: 'CE'
});

fetch(`http://localhost:8000/options/option-price?${params}`)
    .then(response => response.json())
    .then(data => {
        console.log(`NIFTY 24000 CE: ₹${data.lastPrice}`);
        console.log(`Open Interest: ${data.openInterest}`);
    });
```

## 🔄 Rate Limits

- Index price requests: 100 per minute
- Options data requests: 50 per minute
- Historical data: 30 per minute
- Analytics requests: 20 per minute

## Data Sources

- **Options Data**: NSE (National Stock Exchange of India)
- **Historical Options**: Yahoo Finance
- **Index Prices**: NSE real-time data

## Best Practices

1. Use DDMMYY format for expiry dates (e.g., `160925` for 16-Sep-2025)
2. Validate expiry dates before making requests
3. Use appropriate strike ranges for your analysis
4. Cache frequently requested data
5. Handle NSE data unavailability gracefully
6. Use the direct-data endpoint for real-time analysis
7. Use fetch endpoints for bulk data processing

## Supported Indices

- **NIFTY**: Primary Indian index
- **BANKNIFTY**: Banking sector index
- **NIFTYIT**: IT sector index
- **NIFTYPHARMA**: Pharma sector index
- **NIFTYAUTO**: Auto sector index
- **NIFTYFINANCE**: Finance sector index

## Date Format Conversion

The API accepts expiry dates in DDMMYY format for user convenience:
- `160925` → `16-Sep-2025`
- `301225` → `30-Dec-2025`
- `280225` → `28-Feb-2025`
