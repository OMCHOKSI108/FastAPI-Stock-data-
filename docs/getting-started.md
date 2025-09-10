# Getting Started with FastStockAPI

Welcome to **FastStockAPI**! This comprehensive guide will help you get started with our powerful financial data API that provides real-time and historical data for stocks, cryptocurrencies, options, indices, and forex markets.

## 🚀 What is FastStockAPI?

FastStockAPI is a high-performance FastAPI-based service that aggregates financial market data from multiple sources:

- **Indian Stocks**: NSE (National Stock Exchange) data
- **Cryptocurrencies**: Real-time crypto prices and historical data
- **Options Trading**: Complete options chains, analytics, and historical data
- **Market Indices**: US and BSE index data
- **Forex**: Real-time currency exchange rates
- **Advanced Analytics**: PCR, Max Pain, Open Interest analysis

## Prerequisites

Before you start, make sure you have:

- **Python 3.9+** (for local development)
- **cURL** or **Postman** (for API testing)
- **Git** (for cloning the repository)
- Basic knowledge of REST APIs

## 🛠️ Installation & Setup

### Option 1: Use the Live API (Recommended)

The easiest way to get started is to use our hosted API:

```
Base URL: http://localhost:8000 (local) or https://your-deployed-url.com (production)
```

### Option 2: Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/fastapi-project.git
   cd fastapi-project
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Verify Installation**
   ```bash
   curl http://localhost:8000/health
   ```

## 🧪 Your First API Calls

### 1. Health Check

Let's start by checking if the API is running:

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
    "status": "ok"
}
```

### 2. Get API Information

Get a complete overview of all available endpoints:

```bash
curl http://localhost:8000/
```

This will return a comprehensive list of all endpoints with examples.

### 3. Get Stock Price

Let's get the current price of a popular Indian stock:

```bash
curl "http://localhost:8000/stocks/IND/RELIANCE"
```

**Response:**
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

### 4. Get US Stock Price

Now let's try a US stock:

```bash
curl "http://localhost:8000/stocks/US/AAPL"
```

**Response:**
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

### 5. Get Cryptocurrency Price

Let's get Bitcoin's current price:

```bash
curl "http://localhost:8000/crypto/quote/BTC"
```

**Response:**
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

### 6. Get Options Data

Get current NIFTY index price for options trading:

```bash
curl "http://localhost:8000/options/index-price?index=NIFTY"
```

**Response:**
```json
{
    "symbol": "NIFTY",
    "lastPrice": 24500.75,
    "pChange": 0.85,
    "change": 207.50,
    "timestamp": "09-Dec-2024 15:30:00"
}
```

### 7. Get Options Analytics

Get Put-Call Ratio for NIFTY:

```bash
curl "http://localhost:8000/analytics/pcr?index=NIFTY&expiry=160925"
```

**Response:**
```json
{
    "pcr": 1.25,
    "total_ce_oi": 125000000,
    "total_pe_oi": 100000000,
    "index": "NIFTY",
    "expiry": "16-Sep-2025"
}
```

## 💻 Programming Examples

### Python - Basic Usage

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{BASE_URL}/health")
print("API Status:", response.json())

# 2. Get stock price
response = requests.get(f"{BASE_URL}/stocks/IND/RELIANCE")
reliance_data = response.json()
print(f"RELIANCE: ₹{reliance_data['lastPrice']}")

# 3. Get crypto price
response = requests.get(f"{BASE_URL}/crypto/quote/BTC")
btc_data = response.json()
print(f"BTC: ${btc_data['price']}")

# 4. Get options analytics
response = requests.get(f"{BASE_URL}/analytics/pcr?index=NIFTY&expiry=160925")
pcr_data = response.json()
print(f"NIFTY PCR: {pcr_data['pcr']}")
```

### JavaScript - Web Integration

```javascript
// Using fetch API
const BASE_URL = 'http://localhost:8000';

// Get stock data
async function getStockData(symbol) {
    try {
        const response = await fetch(`${BASE_URL}/stocks/IND/${symbol}`);
        const data = await response.json();
        console.log(`${data.symbol}: ₹${data.lastPrice}`);
        return data;
    } catch (error) {
        console.error('Error fetching stock data:', error);
    }
}

// Get crypto data
async function getCryptoData(symbol) {
    try {
        const response = await fetch(`${BASE_URL}/crypto/quote/${symbol}`);
        const data = await response.json();
        console.log(`${data.symbol}: $${data.price}`);
        return data;
    } catch (error) {
        console.error('Error fetching crypto data:', error);
    }
}

// Usage
getStockData('TCS');
getCryptoData('ETH');
```

### Java - Enterprise Integration

```java
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import com.fasterxml.jackson.databind.ObjectMapper;

public class FastStockAPIClient {
    private static final String BASE_URL = "http://localhost:8000";
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    public FastStockAPIClient() {
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }

    public void getStockPrice(String symbol) throws Exception {
        String url = BASE_URL + "/stocks/IND/" + symbol;
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() == 200) {
            // Parse and use the data
            System.out.println("Stock data: " + response.body());
        } else {
            System.out.println("Error: " + response.statusCode());
        }
    }

    public void getCryptoPrice(String symbol) throws Exception {
        String url = BASE_URL + "/crypto/quote/" + symbol;
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() == 200) {
            System.out.println("Crypto data: " + response.body());
        } else {
            System.out.println("Error: " + response.statusCode());
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        FastStockAPIClient client = new FastStockAPIClient();

        try {
            client.getStockPrice("RELIANCE");
            client.getCryptoPrice("BTC");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

## Understanding the Data

### Stock Data Fields
- **symbol**: Stock ticker symbol
- **companyName**: Full company name
- **lastPrice**: Current stock price
- **pChange**: Percentage change
- **change**: Absolute price change
- **timestamp**: Data timestamp

### Crypto Data Fields
- **symbol**: Cryptocurrency symbol
- **name**: Full cryptocurrency name
- **price**: Current price in USD
- **change24h**: 24-hour price change
- **changePercent24h**: 24-hour percentage change
- **volume24h**: 24-hour trading volume
- **marketCap**: Market capitalization
- **lastUpdated**: Last update timestamp

### Options Data Fields
- **pcr**: Put-Call Ratio
- **total_ce_oi**: Total Call Open Interest
- **total_pe_oi**: Total Put Open Interest
- **max_pain_strike**: Maximum pain strike price
- **underlying_value**: Current index value

## 🔧 Advanced Features

### Historical Data

Get historical price data for analysis:

```bash
# Stock historical data
curl "http://localhost:8000/stocks/historical/IND/RELIANCE?period=1mo"

# Crypto historical data
curl "http://localhost:8000/crypto/historical/BTC?period=1mo"

# Options historical data
curl "http://localhost:8000/options/historical/NIFTY?strike=24000&expiry=160925&option_type=CE&period=1mo"
```

### Bulk Requests

Get multiple stocks at once:

```bash
# Multiple stocks (if endpoint available)
curl "http://localhost:8000/stocks/IND/RELIANCE,TCS,HDFC"
```

### Options Chain Analysis

Get complete options data for trading decisions:

```bash
# Get options chain
curl "http://localhost:8000/options/direct-data?index=NIFTY&expiry=160925&num_strikes=10"

# Get specific strike data
curl "http://localhost:8000/options/strike-data?index=NIFTY&strike=24000&expiry=160925&option_type=BOTH"
```

## 🎯 Common Use Cases

### 1. Portfolio Tracking
```python
def track_portfolio(stocks, cryptos):
    portfolio = {}

    # Get stock prices
    for stock in stocks:
        response = requests.get(f"{BASE_URL}/stocks/IND/{stock}")
        portfolio[stock] = response.json()

    # Get crypto prices
    for crypto in cryptos:
        response = requests.get(f"{BASE_URL}/crypto/quote/{crypto}")
        portfolio[crypto] = response.json()

    return portfolio
```

### 2. Options Strategy Analysis
```python
def analyze_options_strategy(index, expiry, strikes):
    analysis = {}

    # Get PCR
    pcr_response = requests.get(f"{BASE_URL}/analytics/pcr?index={index}&expiry={expiry}")
    analysis['pcr'] = pcr_response.json()

    # Get Max Pain
    max_pain_response = requests.get(f"{BASE_URL}/analytics/max-pain?index={index}&expiry={expiry}")
    analysis['max_pain'] = max_pain_response.json()

    # Get strike data
    for strike in strikes:
        strike_response = requests.get(
            f"{BASE_URL}/options/strike-data?index={index}&strike={strike}&expiry={expiry}&option_type=BOTH"
        )
        analysis[f'strike_{strike}'] = strike_response.json()

    return analysis
```

### 3. Market Sentiment Analysis
```python
def get_market_sentiment():
    sentiment = {}

    # Get major indices
    indices = ['NIFTY', 'BANKNIFTY']
    for index in indices:
        response = requests.get(f"{BASE_URL}/options/index-price?index={index}")
        sentiment[index] = response.json()

        # Get PCR for sentiment
        pcr_response = requests.get(f"{BASE_URL}/analytics/pcr?index={index}&expiry=160925")
        sentiment[f'{index}_pcr'] = pcr_response.json()

    return sentiment
```

## 🆘 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Make sure the API server is running
   - Check if the port (8000) is available
   - Verify the BASE_URL is correct

2. **404 Not Found**
   - Check the endpoint URL
   - Verify symbol names are correct
   - Ensure expiry dates are in DDMMYY format

3. **500 Internal Server Error**
   - The API might be having issues with external data sources
   - Check the server logs for more details
   - Try again in a few minutes

4. **Rate Limiting**
   - Free tier has request limits
   - Implement delays between requests
   - Consider upgrading to premium plans

### Getting Help

- **API Documentation**: Visit `/docs` for interactive documentation
- **Health Check**: Use `/health` to verify API status
- **Logs**: Check server logs for detailed error information
- **GitHub Issues**: Report bugs and request features

## 🚀 Next Steps

Now that you know the basics, explore these advanced topics:

1. **[API Reference](api/)**: Complete endpoint documentation
2. **[Usage Examples](usage.md)**: Advanced code examples
3. **[Deployment Guide](deployment.md)**: Production deployment
4. **[Analytics](api/analytics.md)**: Advanced trading analytics

## 📞 Support

- **📧 Email**: support@faststockapi.com
- **💬 GitHub**: [Create an issue](https://github.com/your-repo/issues)
- **📖 Docs**: [Full Documentation](https://your-docs-site.com)

---

**Happy coding with FastStockAPI! 🚀📈**

## Python Examples

### Using requests library

```python
import requests

# Get stock price
response = requests.get("https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=RELIANCE")
data = response.json()
print(f"RELIANCE: ₹{data['lastPrice']}")

# Get crypto price
response = requests.get("https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT")
data = response.json()
print(f"BTC: ${data['price']}")
```

### Using httpx (async)

```python
import httpx
import asyncio

async def get_data():
    async with httpx.AsyncClient() as client:
        # Get multiple crypto prices
        response = await client.get(
            "https://fastapi-stock-data.onrender.com/crypto-multiple?symbols=BTCUSDT,ETHUSDT,ADAUSDT"
        )
        data = response.json()
        print(data)

asyncio.run(get_data())
```

## JavaScript Examples

### Fetch API

```javascript
// Get crypto price
fetch('https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT')
    .then(response => response.json())
    .then(data => {
        console.log(`BTC Price: $${data.price}`);
    });

// Get multiple prices
fetch('https://fastapi-stock-data.onrender.com/crypto-multiple?symbols=BTCUSDT,ETHUSDT')
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
```

### Axios

```javascript
const axios = require('axios');

// Get stock price
axios.get('https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=TCS')
    .then(response => {
        console.log(response.data);
    });
```

## Mobile Applications

### React Native

```javascript
import React, { useEffect, useState } from 'react';

function CryptoPrice() {
    const [price, setPrice] = useState(null);

    useEffect(() => {
        fetch('https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT')
            .then(response => response.json())
            .then(data => setPrice(data.price));
    }, []);

    return (
        <div>
            <h2>BTC Price: ${price}</h2>
        </div>
    );
}
```

## Error Handling

### Common HTTP Status Codes

- **200**: Success
- **404**: Symbol not found
- **500**: Server error

### Error Response Format

```json
{
    "detail": "Error message description"
}
```

### Best Practices

```python
def safe_api_call(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return None
```

## Rate Limiting

- **Production**: No rate limiting (for now)
- **Development**: Test responsibly
- **Best Practice**: Implement caching on your end

## Testing

Use our test script to verify all endpoints:

```bash
python test_api_fixes.py
```

## Next Steps

- [API Reference](api/stock.md) - Complete endpoint documentation
- [Symbol Reference](symbols/nse-stocks.md) - Available symbols
- [Examples](examples.md) - More code examples
- [Interactive Demo](crypto_demo.html) - Try the API live
