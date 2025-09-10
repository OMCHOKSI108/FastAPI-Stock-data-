# Analytics API

This section documents the advanced analytics endpoints in FastStockAPI, providing sophisticated options trading analytics including PCR, Max Pain, and Open Interest analysis.

## Overview

The analytics API provides powerful trading analytics tools for options data, helping traders make informed decisions with data-driven insights.

## 🔗 Base URL

```
http://localhost:8000  (local development)
https://your-domain.com  (production)
```

## Endpoints

### 1. Get Put-Call Ratio (PCR)

Calculate the Put-Call Ratio for options data.

**Endpoint:** `GET /analytics/pcr`

**Parameters:**
- `index` (query): Index symbol (e.g., `NIFTY`, `BANKNIFTY`)
- `expiry` (query, optional): Expiry date in DDMMYY format

**Example Request:**
```bash
curl "http://localhost:8000/analytics/pcr?index=NIFTY&expiry=160925"
```

**Example Response:**
```json
{
    "pcr": 1.25,
    "total_ce_oi": 125000000,
    "total_pe_oi": 100000000,
    "index": "NIFTY",
    "expiry": "16-Sep-2025"
}
```

### 2. Calculate Max Pain

Find the maximum pain strike price for options.

**Endpoint:** `GET /analytics/max-pain`

**Parameters:**
- `index` (query): Index symbol
- `expiry` (query, optional): Expiry date in DDMMYY format

**Example Request:**
```bash
curl "http://localhost:8000/analytics/max-pain?index=NIFTY&expiry=160925"
```

**Example Response:**
```json
{
    "max_pain_strike": 24500,
    "total_ce_oi": 125000000,
    "total_pe_oi": 100000000,
    "total_oi": 225000000,
    "index": "NIFTY",
    "expiry": "16-Sep-2025"
}
```

### 3. Get Top Open Interest

Find strikes with highest open interest.

**Endpoint:** `GET /analytics/top-oi`

**Parameters:**
- `index` (query): Index symbol
- `expiry` (query, optional): Expiry date in DDMMYY format
- `top_n` (query, optional): Number of top strikes to return (default: 5)

**Example Request:**
```bash
curl "http://localhost:8000/analytics/top-oi?index=NIFTY&expiry=160925&top_n=5"
```

**Example Response:**
```json
{
    "top_strikes": [
        {
            "strike": 24000,
            "oi_ce": 2450000,
            "oi_pe": 1850000,
            "total_oi": 4300000,
            "oi_ce_percentage": 12.5,
            "oi_pe_percentage": 9.2
        },
        {
            "strike": 24500,
            "oi_ce": 2100000,
            "oi_pe": 1950000,
            "total_oi": 4050000,
            "oi_ce_percentage": 10.7,
            "oi_pe_percentage": 9.8
        }
    ],
    "index": "NIFTY",
    "expiry": "16-Sep-2025"
}
```

### 4. Get Complete Analytics Summary

Get comprehensive analytics for options data.

**Endpoint:** `GET /analytics/summary`

**Parameters:**
- `index` (query): Index symbol
- `expiry` (query, optional): Expiry date in DDMMYY format
- `limit` (query, optional): Number of records to analyze

**Example Request:**
```bash
curl "http://localhost:8000/analytics/summary?index=NIFTY&expiry=160925&limit=500"
```

**Example Response:**
```json
{
    "meta": {
        "createdAtUTC": "2024-12-09T15:30:00Z",
        "indexName": "NIFTY",
        "nearestExpiry": "16-Sep-2025",
        "underlyingValue": 24500.75,
        "atmStrike": 24500,
        "selectedStrikesRange": [23500, 25500],
        "totalStrikesFetched": 41
    },
    "pcr": 1.25,
    "max_pain": {
        "max_pain_strike": 24500,
        "total_ce_oi": 125000000,
        "total_pe_oi": 100000000,
        "total_oi": 225000000
    },
    "top_oi": [
        {
            "strike": 24000,
            "oi_ce": 2450000,
            "oi_pe": 1850000,
            "total_oi": 4300000
        }
    ],
    "atm_analysis": {
        "atm_strike": 24500,
        "atm_ce_price": 125.50,
        "atm_pe_price": 95.25,
        "atm_ce_oi": 2100000,
        "atm_pe_oi": 1950000
    }
}
```

## Analytics Explained

### Put-Call Ratio (PCR)
- **Formula**: Total PE Open Interest / Total CE Open Interest
- **Interpretation**:
  - PCR > 1: Bearish sentiment (more puts)
  - PCR < 1: Bullish sentiment (more calls)
  - PCR = 1: Neutral sentiment

### Maximum Pain
- **Definition**: Strike price where the total value of expiring options is minimized
- **Calculation**: Sums open interest for calls above and puts below each strike
- **Significance**: Price level where option writers (market makers) suffer least loss

### Open Interest Analysis
- **Top OI Strikes**: Most actively traded strike prices
- **OI Distribution**: Shows where market participants have positioned
- **Volume vs OI**: Fresh positions vs existing positions

## 💡 Usage Examples

### Python Example - Complete Analysis
```python
import requests

def analyze_options(index, expiry):
    # Get PCR
    pcr_response = requests.get(
        "http://localhost:8000/analytics/pcr",
        params={"index": index, "expiry": expiry}
    )
    pcr_data = pcr_response.json()

    # Get Max Pain
    max_pain_response = requests.get(
        "http://localhost:8000/analytics/max-pain",
        params={"index": index, "expiry": expiry}
    )
    max_pain_data = max_pain_response.json()

    # Get Top OI
    top_oi_response = requests.get(
        "http://localhost:8000/analytics/top-oi",
        params={"index": index, "expiry": expiry, "top_n": 3}
    )
    top_oi_data = top_oi_response.json()

    print(f"📊 {index} Analysis for {expiry}")
    print(f"PCR: {pcr_data['pcr']:.2f}")
    print(f"Max Pain: ₹{max_pain_data['max_pain_strike']}")

    print("\n🏆 Top OI Strikes:")
    for strike in top_oi_data['top_strikes']:
        print(f"₹{strike['strike']}: {strike['total_oi']:,} contracts")

# Usage
analyze_options("NIFTY", "160925")
```

### JavaScript Example - Real-time Dashboard
```javascript
async function updateAnalytics(index, expiry) {
    try {
        // Get all analytics in parallel
        const [pcrRes, maxPainRes, topOiRes] = await Promise.all([
            fetch(`/analytics/pcr?index=${index}&expiry=${expiry}`),
            fetch(`/analytics/max-pain?index=${index}&expiry=${expiry}`),
            fetch(`/analytics/top-oi?index=${index}&expiry=${expiry}&top_n=5`)
        ]);

        const [pcr, maxPain, topOi] = await Promise.all([
            pcrRes.json(),
            maxPainRes.json(),
            topOiRes.json()
        ]);

        // Update UI
        document.getElementById('pcr-value').textContent = pcr.pcr.toFixed(2);
        document.getElementById('max-pain').textContent = `₹${maxPain.max_pain_strike}`;

        // Update top OI table
        const tableBody = document.getElementById('top-oi-table');
        tableBody.innerHTML = topOi.top_strikes.map(strike => `
            <tr>
                <td>₹${strike.strike}</td>
                <td>${strike.total_oi.toLocaleString()}</td>
                <td>${strike.oi_ce_percentage.toFixed(1)}%</td>
                <td>${strike.oi_pe_percentage.toFixed(1)}%</td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error updating analytics:', error);
    }
}

// Update every 30 seconds
setInterval(() => updateAnalytics('NIFTY', '160925'), 30000);
```

## Trading Insights

### PCR Interpretation
```javascript
function interpretPCR(pcr) {
    if (pcr > 1.5) return "🔴 Extremely Bearish";
    if (pcr > 1.2) return "🟠 Bearish";
    if (pcr > 0.8) return "🟡 Neutral";
    if (pcr > 0.5) return "🟢 Bullish";
    return "🟢 Extremely Bullish";
}
```

### Max Pain Strategy
```javascript
function maxPainStrategy(currentPrice, maxPain) {
    const diff = Math.abs(currentPrice - maxPain) / currentPrice * 100;

    if (diff < 1) return "🎯 At Max Pain - High manipulation risk";
    if (diff < 3) return "⚠️ Near Max Pain - Watch closely";
    return "✅ Away from Max Pain - Natural movement";
}
```

## ⚠️ Important Notes

- **Data Freshness**: Analytics are based on last fetched options data
- **Market Hours**: NSE options data available during market hours
- **Expiry Effects**: Analytics most relevant close to expiry
- **Liquidity**: Higher OI strikes provide better liquidity
- **Volatility**: PCR and OI patterns change with market volatility

## 🔄 Rate Limits

- PCR requests: 50 per minute
- Max Pain requests: 50 per minute
- Top OI requests: 30 per minute
- Summary requests: 20 per minute

## Supported Indices

- **NIFTY**: Primary index analytics
- **BANKNIFTY**: Banking sector
- **NIFTYIT**: Information Technology
- **NIFTYPHARMA**: Pharmaceuticals
- **NIFTYAUTO**: Automobile sector

## Best Practices

1. **Use Recent Data**: Fetch fresh options data before analytics
2. **Compare Timeframes**: Analyze PCR trends over time
3. **Combine Metrics**: Use PCR + Max Pain + OI together
4. **Context Matters**: Consider overall market sentiment
5. **Risk Management**: Don't rely solely on technical indicators
6. **Multiple Expiries**: Compare near-term vs far-term analytics

## Advanced Usage

### Custom PCR Calculation
```python
def custom_pcr(ce_oi, pe_oi, min_strike=None, max_strike=None):
    """Calculate PCR for specific strike range"""
    if min_strike and max_strike:
        # Filter strikes within range
        filtered_ce = sum(oi for strike, oi in ce_oi.items()
                         if min_strike <= strike <= max_strike)
        filtered_pe = sum(oi for strike, oi in pe_oi.items()
                         if min_strike <= strike <= max_strike)
        return filtered_pe / filtered_ce if filtered_ce > 0 else 0
    return sum(pe_oi.values()) / sum(ce_oi.values()) if sum(ce_oi.values()) > 0 else 0
```

### OI Concentration Analysis
```python
def oi_concentration(top_oi_strikes, total_oi):
    """Calculate OI concentration in top strikes"""
    top_total = sum(strike['total_oi'] for strike in top_oi_strikes)
    return (top_total / total_oi) * 100 if total_oi > 0 else 0
```

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

## Response Formats

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

## Integration Examples

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

## Analytics Interpretation

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
