# Getting Started

This guide will help you get started with the FastAPI Stock & Crypto Data API.

## Quick Start

### 1. API Base URL

```
https://fastapi-stock-data.onrender.com
```

### 2. Health Check

First, let's verify the API is running:

```bash
curl https://fastapi-stock-data.onrender.com/health
```

Response:
```json
{"status": "ok"}
```

## Basic Endpoints

### Get Stock Price

```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=RELIANCE"
```

### Get Index Price

```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index=NIFTY"
```

### Get Crypto Price

```bash
curl "https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT"
```

### Get Crypto Statistics

```bash
curl "https://fastapi-stock-data.onrender.com/crypto-stats/BTCUSDT"
```

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
