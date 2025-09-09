# Analytics API

This section documents analytics and options data endpoints in the FastAPI Stock & Crypto Data API.

## 📊 Overview

The analytics API provides advanced market analysis including Put-Call Ratio (PCR), Open Interest analysis, Max Pain calculations, and options data.

## 🔗 Base URL

```
https://fastapi-stock-data.onrender.com
```

## 📋 Endpoints

### 1. Put-Call Ratio (PCR)

Get the Put-Call Ratio for NIFTY options.

**Endpoint:** `GET /api/v1/analytics/pcr?index=NIFTY`

**Parameters:**
- `index` (query, optional): Index name (default: `NIFTY`)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/analytics/pcr?index=NIFTY"
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "pcr": 1.25,
    "put_oi": 12500000,
    "call_oi": 10000000,
    "timestamp": "2024-12-09T15:30:00Z",
    "interpretation": "Bullish (PCR > 1.0)"
}
```

---

### 2. Top Open Interest Strikes

Get strikes with highest open interest for options.

**Endpoint:** `GET /api/v1/analytics/top-oi?index=NIFTY`

**Parameters:**
- `index` (query, optional): Index name (default: `NIFTY`)
- `limit` (query, optional): Number of strikes to return (default: 10)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/analytics/top-oi?index=NIFTY&limit=5"
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "top_strikes": [
        {
            "strike_price": 23500,
            "total_oi": 2500000,
            "put_oi": 1500000,
            "call_oi": 1000000,
            "oi_change": 125000
        },
        {
            "strike_price": 24000,
            "total_oi": 2200000,
            "put_oi": 1200000,
            "call_oi": 1000000,
            "oi_change": 98000
        }
    ],
    "timestamp": "2024-12-09T15:30:00Z"
}
```

---

### 3. Max Pain Calculation

Get the Max Pain strike price for options expiry.

**Endpoint:** `GET /api/v1/analytics/max-pain?index=NIFTY`

**Parameters:**
- `index` (query, optional): Index name (default: `NIFTY`)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/analytics/max-pain?index=NIFTY"
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "max_pain_strike": 23800,
    "total_oi_at_max_pain": 3500000,
    "put_oi_at_max_pain": 1800000,
    "call_oi_at_max_pain": 1700000,
    "calculation_method": "Total OI at strike price",
    "timestamp": "2024-12-09T15:30:00Z"
}
```

---

### 4. Analytics Summary

Get comprehensive analytics summary for an index.

**Endpoint:** `GET /api/v1/analytics/summary?index=NIFTY`

**Parameters:**
- `index` (query, optional): Index name (default: `NIFTY`)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/analytics/summary?index=NIFTY"
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "current_price": 23456.75,
    "pcr": 1.25,
    "max_pain": 23800,
    "top_strikes": [
        {
            "strike_price": 23500,
            "total_oi": 2500000
        }
    ],
    "market_sentiment": "Bullish",
    "volatility_indicator": "Moderate",
    "timestamp": "2024-12-09T15:30:00Z"
}
```

---

### 5. Options Expiries

Get available expiry dates for options.

**Endpoint:** `GET /api/v1/options/expiries?index=NIFTY`

**Parameters:**
- `index` (query, optional): Index name (default: `NIFTY`)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/options/expiries?index=NIFTY"
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "expiries": [
        "14-Dec-2024",
        "21-Dec-2024",
        "28-Dec-2024",
        "25-Jan-2025"
    ],
    "current_expiry": "14-Dec-2024",
    "timestamp": "2024-12-09T15:30:00Z"
}
```

---

### 6. Latest Options Chain

Get the latest options chain data.

**Endpoint:** `GET /api/v1/options/latest?index=NIFTY`

**Parameters:**
- `index` (query, optional): Index name (default: `NIFTY`)
- `limit` (query, optional): Number of strikes to return (default: 20)

**Example Request:**
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/options/latest?index=NIFTY&limit=10"
```

**Example Response:**
```json
{
    "index": "NIFTY",
    "spot_price": 23456.75,
    "expiry": "14-Dec-2024",
    "options_chain": [
        {
            "strike_price": 23000,
            "put": {
                "oi": 1250000,
                "change_in_oi": 25000,
                "volume": 50000,
                "iv": 15.5,
                "ltp": 45.25,
                "net_change": 2.15
            },
            "call": {
                "oi": 980000,
                "change_in_oi": 15000,
                "volume": 35000,
                "iv": 14.2,
                "ltp": 456.75,
                "net_change": 25.50
            }
        }
    ],
    "timestamp": "2024-12-09T15:30:00Z"
}
```

---

### 7. Fetch Options Chain (Background)

Fetch and cache options chain data asynchronously.

**Endpoint:** `POST /api/v1/options/fetch`

**Parameters:**
- `index` (body): Index name
- `expiry` (body, optional): Specific expiry date

**Example Request:**
```bash
curl -X POST "https://fastapi-stock-data.onrender.com/api/v1/options/fetch" \
     -H "Content-Type: application/json" \
     -d '{"index": "NIFTY"}'
```

**Example Response:**
```json
{
    "job_id": "abc123-def456-ghi789",
    "status": "processing",
    "message": "Options data fetch initiated",
    "estimated_time": "30-60 seconds"
}
```

---

### 8. Fetch Specific Expiry Options

Fetch options data for a specific expiry date.

**Endpoint:** `POST /api/v1/options/fetch-expiry`

**Parameters:**
- `index` (body): Index name
- `expiry` (body): Expiry date

**Example Request:**
```bash
curl -X POST "https://fastapi-stock-data.onrender.com/api/v1/options/fetch-expiry" \
     -H "Content-Type: application/json" \
     -d '{"index": "NIFTY", "expiry": "14-Dec-2024"}'
```

**Example Response:**
```json
{
    "job_id": "def456-ghi789-jkl012",
    "status": "processing",
    "message": "Expiry-specific options data fetch initiated",
    "expiry_date": "14-Dec-2024"
}
```

## 📊 Response Formats

### PCR Response

```json
{
    "index": "string",
    "pcr": "number",
    "put_oi": "number",
    "call_oi": "number",
    "timestamp": "string",
    "interpretation": "string"
}
```

### Top OI Response

```json
{
    "index": "string",
    "top_strikes": [
        {
            "strike_price": "number",
            "total_oi": "number",
            "put_oi": "number",
            "call_oi": "number",
            "oi_change": "number"
        }
    ],
    "timestamp": "string"
}
```

### Max Pain Response

```json
{
    "index": "string",
    "max_pain_strike": "number",
    "total_oi_at_max_pain": "number",
    "put_oi_at_max_pain": "number",
    "call_oi_at_max_pain": "number",
    "calculation_method": "string",
    "timestamp": "string"
}
```

## ⚠️ Important Notes

### Data Availability
- Options data is updated during market hours
- Historical options data may be limited
- Some calculations require sufficient market data

### Calculation Methods

**PCR Calculation:**
- PCR = Total Put OI / Total Call OI
- Values > 1.0 indicate bullish sentiment
- Values < 1.0 indicate bearish sentiment

**Max Pain Calculation:**
- Strike price with maximum total open interest
- Used to predict market movement at expiry
- Based on current open interest distribution

### Background Processing
- Large options data fetches run in background
- Use job IDs to track progress
- Results are cached for faster subsequent access

## 📱 Integration Examples

### Python

```python
import requests

def get_pcr(index="NIFTY"):
    url = f"https://fastapi-stock-data.onrender.com/api/v1/analytics/pcr?index={index}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def get_max_pain(index="NIFTY"):
    url = f"https://fastapi-stock-data.onrender.com/api/v1/analytics/max-pain?index={index}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
pcr_data = get_pcr("NIFTY")
if pcr_data:
    print(f"NIFTY PCR: {pcr_data['pcr']} ({pcr_data['interpretation']})")

max_pain = get_max_pain("NIFTY")
if max_pain:
    print(f"Max Pain Strike: {max_pain['max_pain_strike']}")
```

### JavaScript

```javascript
async function getAnalytics(index = 'NIFTY') {
    const baseURL = 'https://fastapi-stock-data.onrender.com';

    try {
        // Get PCR
        const pcrResponse = await fetch(`${baseURL}/api/v1/analytics/pcr?index=${index}`);
        const pcrData = await pcrResponse.json();

        // Get Max Pain
        const maxPainResponse = await fetch(`${baseURL}/api/v1/analytics/max-pain?index=${index}`);
        const maxPainData = await maxPainResponse.json();

        // Get Top OI
        const topOIResponse = await fetch(`${baseURL}/api/v1/analytics/top-oi?index=${index}&limit=5`);
        const topOIData = await topOIResponse.json();

        return {
            pcr: pcrData,
            maxPain: maxPainData,
            topOI: topOIData
        };
    } catch (error) {
        console.error('Error fetching analytics:', error);
        return null;
    }
}

// Usage
getAnalytics('NIFTY').then(data => {
    if (data) {
        console.log(`PCR: ${data.pcr.pcr}`);
        console.log(`Max Pain: ${data.maxPain.max_pain_strike}`);
        console.log(`Top OI Strikes: ${data.topOI.top_strikes.length}`);
    }
});
```

## 🔍 Error Handling

### Common HTTP Status Codes

- **200**: Success
- **404**: Index not found or no data available
- **500**: Server error or calculation error

### Error Response Format

```json
{
    "detail": "Error description message"
}
```

## 📊 Analytics Interpretation

### PCR Values
- **> 1.0**: Bullish sentiment (more puts being bought)
- **< 1.0**: Bearish sentiment (more calls being bought)
- **= 1.0**: Neutral sentiment

### Max Pain
- The strike price where maximum options would expire worthless
- Market makers may hedge around this level
- Not a guaranteed prediction but a useful indicator

### Open Interest
- High OI indicates strong interest at that strike
- Increasing OI suggests new positions being opened
- Decreasing OI suggests positions being closed

## 🆘 Troubleshooting

### Common Issues

**No Data Available**
- Check during market hours
- Options data may not be available for all indices

**Calculation Errors**
- Insufficient data for calculations
- Try different time periods or indices

**Background Job Issues**
- Large datasets take time to process
- Check job status after some time

### Getting Help

- Check the [API Reference](../api/stock.md) for basic endpoints
- Report issues on [GitHub](https://github.com/OMCHOKSI108/FastAPI-Stock-data-)
- Visit NSE website for official options data
