# Code Examples

This page provides comprehensive code examples for using the FastAPI Stock & Crypto Data API in different programming languages and frameworks.

## Python Examples

### Basic Usage with requests

```python
import requests
import json
from datetime import datetime

BASE_URL = "https://fastapi-stock-data.onrender.com"

def get_stock_price(symbol):
    """Get current stock price"""
    url = f"{BASE_URL}/api/v1/market/price/stock?symbol={symbol}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"{data['companyName']} ({data['symbol']}): ₹{data['lastPrice']}")
        print(f"Change: {data['pChange']}% (₹{data['change']})")
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_crypto_price(symbol):
    """Get current crypto price"""
    url = f"{BASE_URL}/crypto-price/{symbol}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"{data['symbol']}: ${data['price']}")
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_multiple_crypto_prices(symbols):
    """Get multiple crypto prices"""
    symbol_str = ",".join(symbols)
    url = f"{BASE_URL}/crypto-multiple?symbols={symbol_str}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"Requested: {data['symbols_requested']}")
        print(f"Found: {data['symbols_found']}")

        for symbol, price_data in data['data'].items():
            print(f"{symbol}: ${price_data['price']}")
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Usage examples
if __name__ == "__main__":
    print("=== Stock Price Example ===")
    get_stock_price("RELIANCE.NS")

    print("\n=== Crypto Price Example ===")
    get_crypto_price("BTCUSDT")

    print("\n=== Multiple Crypto Prices Example ===")
    get_multiple_crypto_prices(["BTCUSDT", "ETHUSDT", "ADAUSDT"])
```

### Advanced Python Class

```python
import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class StockCryptoAPI:
    def __init__(self, base_url: str = "https://fastapi-stock-data.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_stock_price(self, symbol: str) -> Optional[Dict]:
        """Get stock price with error handling"""
        try:
            url = f"{self.base_url}/api/v1/market/price/stock?symbol={symbol}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching stock price for {symbol}: {e}")
            return None

    def get_crypto_price(self, symbol: str) -> Optional[Dict]:
        """Get crypto price with error handling"""
        try:
            url = f"{self.base_url}/crypto-price/{symbol}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching crypto price for {symbol}: {e}")
            return None

    def get_crypto_stats(self, symbol: str) -> Optional[Dict]:
        """Get 24h crypto statistics"""
        try:
            url = f"{self.base_url}/crypto-stats/{symbol}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching crypto stats for {symbol}: {e}")
            return None

    def get_historical_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[List]:
        """Get historical data"""
        try:
            if symbol.endswith('.NS') or symbol.startswith('^'):
                # Stock or index
                url = f"{self.base_url}/historical/{symbol}?period={period}&interval={interval}"
            else:
                # Crypto
                url = f"{self.base_url}/crypto-historical/{symbol}?interval={interval}&limit=100"

            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None

    def monitor_prices(self, symbols: List[str], interval_seconds: int = 30):
        """Monitor prices continuously"""
        print(f"Starting price monitor for {symbols} (interval: {interval_seconds}s)")
        print("Press Ctrl+C to stop...")

        try:
            while True:
                print(f"\n--- Price Update at {datetime.now().strftime('%H:%M:%S')} ---")

                for symbol in symbols:
                    if symbol.endswith('.NS'):
                        data = self.get_stock_price(symbol)
                        if data:
                            print(f"{data['symbol']}: ₹{data['lastPrice']} ({data['pChange']}%)")
                    else:
                        data = self.get_crypto_price(symbol)
                        if data:
                            print(f"{data['symbol']}: ${data['price']}")

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

# Usage
api = StockCryptoAPI()

# Get individual prices
stock_data = api.get_stock_price("RELIANCE.NS")
crypto_data = api.get_crypto_price("BTCUSDT")

# Get crypto statistics
stats = api.get_crypto_stats("BTCUSDT")
if stats:
    print(f"BTC 24h Change: {stats['price_change_percent']}%")

# Get historical data
history = api.get_historical_data("BTCUSDT", interval="1d")
if history:
    print(f"Historical data points: {len(history.get('data', []))}")

# Monitor prices
# api.monitor_prices(["RELIANCE.NS", "BTCUSDT", "ETHUSDT"])
```

### Async Python with httpx

```python
import httpx
import asyncio
from typing import List, Dict, Optional
import json

class AsyncStockCryptoAPI:
    def __init__(self, base_url: str = "https://fastapi-stock-data.onrender.com"):
        self.base_url = base_url

    async def get_stock_price(self, symbol: str) -> Optional[Dict]:
        """Async get stock price"""
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                url = f"{self.base_url}/api/v1/market/price/stock?symbol={symbol}"
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error: {e}")
                return None

    async def get_multiple_crypto_prices(self, symbols: List[str]) -> Optional[Dict]:
        """Async get multiple crypto prices"""
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                symbol_str = ",".join(symbols)
                url = f"{self.base_url}/crypto-multiple?symbols={symbol_str}"
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error: {e}")
                return None

    async def batch_requests(self, symbols: List[str]):
        """Batch multiple requests concurrently"""
        async with httpx.AsyncClient(timeout=10) as client:
            tasks = []

            for symbol in symbols:
                if symbol.endswith('.NS'):
                    url = f"{self.base_url}/api/v1/market/price/stock?symbol={symbol}"
                else:
                    url = f"{self.base_url}/crypto-price/{symbol}"

                tasks.append(client.get(url))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            results = {}
            for i, response in enumerate(responses):
                symbol = symbols[i]
                if isinstance(response, Exception):
                    results[symbol] = {"error": str(response)}
                elif response.status_code == 200:
                    results[symbol] = response.json()
                else:
                    results[symbol] = {"error": f"HTTP {response.status_code}"}

            return results

# Usage
async def main():
    api = AsyncStockCryptoAPI()

    # Single requests
    stock_price = await api.get_stock_price("TCS.NS")
    print(f"TCS: ₹{stock_price['lastPrice']}")

    # Multiple crypto prices
    crypto_prices = await api.get_multiple_crypto_prices(["BTCUSDT", "ETHUSDT"])
    print(f"Found {crypto_prices['symbols_found']} symbols")

    # Batch requests
    symbols = ["RELIANCE.NS", "TCS.NS", "BTCUSDT", "ETHUSDT"]
    batch_results = await api.batch_requests(symbols)

    for symbol, data in batch_results.items():
        if "error" in data:
            print(f"{symbol}: Error - {data['error']}")
        else:
            if symbol.endswith('.NS'):
                print(f"{symbol}: ₹{data.get('lastPrice', 'N/A')}")
            else:
                print(f"{symbol}: ${data.get('price', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())
```

## JavaScript Examples

### Browser JavaScript (ES6+)

```javascript
// api-client.js
class StockCryptoAPI {
    constructor(baseURL = 'https://fastapi-stock-data.onrender.com') {
        this.baseURL = baseURL;
    }

    async getStockPrice(symbol) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/market/price/stock?symbol=${symbol}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching stock price for ${symbol}:`, error);
            return null;
        }
    }

    async getCryptoPrice(symbol) {
        try {
            const response = await fetch(`${this.baseURL}/crypto-price/${symbol}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching crypto price for ${symbol}:`, error);
            return null;
        }
    }

    async getMultipleCryptoPrices(symbols) {
        try {
            const symbolStr = symbols.join(',');
            const response = await fetch(`${this.baseURL}/crypto-multiple?symbols=${symbolStr}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching multiple crypto prices:', error);
            return null;
        }
    }

    async getCryptoStats(symbol) {
        try {
            const response = await fetch(`${this.baseURL}/crypto-stats/${symbol}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching crypto stats for ${symbol}:`, error);
            return null;
        }
    }

    async getHistoricalData(symbol, period = '1mo', interval = '1d') {
        try {
            let url;
            if (symbol.endsWith('.NS') || symbol.startsWith('^')) {
                // Stock or index
                url = `${this.baseURL}/historical/${symbol}?period=${period}&interval=${interval}`;
            } else {
                // Crypto
                url = `${this.baseURL}/crypto-historical/${symbol}?interval=${interval}&limit=100`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching historical data for ${symbol}:`, error);
            return null;
        }
    }
}

// Usage in browser
const api = new StockCryptoAPI();

// Get stock price
api.getStockPrice('RELIANCE.NS').then(data => {
    if (data) {
        document.getElementById('stock-price').textContent =
            `${data.companyName}: ₹${data.lastPrice} (${data.pChange}%)`;
    }
});

// Get crypto price
api.getCryptoPrice('BTCUSDT').then(data => {
    if (data) {
        document.getElementById('crypto-price').textContent =
            `BTC: $${data.price}`;
    }
});

// Get multiple crypto prices
api.getMultipleCryptoPrices(['BTCUSDT', 'ETHUSDT', 'ADAUSDT']).then(data => {
    if (data) {
        const container = document.getElementById('crypto-list');
        container.innerHTML = '';

        Object.entries(data.data).forEach(([symbol, priceData]) => {
            const div = document.createElement('div');
            div.textContent = `${symbol}: $${priceData.price}`;
            container.appendChild(div);
        });
    }
});

// Get crypto statistics
api.getCryptoStats('BTCUSDT').then(stats => {
    if (stats) {
        const changeClass = stats.price_change_percent >= 0 ? 'positive' : 'negative';
        document.getElementById('crypto-stats').innerHTML = `
            <div class="stat">
                <strong>BTC 24h Change:</strong>
                <span class="${changeClass}">${stats.price_change_percent.toFixed(2)}%</span>
            </div>
            <div class="stat">
                <strong>Volume:</strong> ${stats.volume.toLocaleString()}
            </div>
            <div class="stat">
                <strong>High:</strong> $${stats.high_price}
            </div>
            <div class="stat">
                <strong>Low:</strong> $${stats.low_price}
            </div>
        `;
    }
});
```

### Node.js with axios

```javascript
const axios = require('axios');

class StockCryptoAPI {
    constructor(baseURL = 'https://fastapi-stock-data.onrender.com') {
        this.baseURL = baseURL;
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 10000,
        });
    }

    async getStockPrice(symbol) {
        try {
            const response = await this.client.get(`/api/v1/market/price/stock?symbol=${symbol}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching stock price for ${symbol}:`, error.message);
            return null;
        }
    }

    async getCryptoPrice(symbol) {
        try {
            const response = await this.client.get(`/crypto-price/${symbol}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching crypto price for ${symbol}:`, error.message);
            return null;
        }
    }

    async getMultipleCryptoPrices(symbols) {
        try {
            const symbolStr = symbols.join(',');
            const response = await this.client.get(`/crypto-multiple?symbols=${symbolStr}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching multiple crypto prices:', error.message);
            return null;
        }
    }

    async getHistoricalData(symbol, params = {}) {
        try {
            let endpoint;
            if (symbol.endsWith('.NS') || symbol.startsWith('^')) {
                endpoint = `/historical/${symbol}`;
            } else {
                endpoint = `/crypto-historical/${symbol}`;
            }

            const response = await this.client.get(endpoint, { params });
            return response.data;
        } catch (error) {
            console.error(`Error fetching historical data for ${symbol}:`, error.message);
            return null;
        }
    }

    async monitorPrices(symbols, intervalMs = 30000) {
        console.log(`Starting price monitor for ${symbols.join(', ')}`);

        const monitor = async () => {
            console.log(`\n--- Price Update at ${new Date().toLocaleTimeString()} ---`);

            for (const symbol of symbols) {
                try {
                    let data;
                    if (symbol.endsWith('.NS')) {
                        data = await this.getStockPrice(symbol);
                        if (data) {
                            console.log(`${data.symbol}: ₹${data.lastPrice} (${data.pChange}%)`);
                        }
                    } else {
                        data = await this.getCryptoPrice(symbol);
                        if (data) {
                            console.log(`${data.symbol}: $${data.price}`);
                        }
                    }
                } catch (error) {
                    console.error(`Error monitoring ${symbol}:`, error.message);
                }
            }
        };

        // Initial call
        await monitor();

        // Set up interval
        return setInterval(monitor, intervalMs);
    }
}

// Usage
async function main() {
    const api = new StockCryptoAPI();

    // Get individual prices
    const stockData = await api.getStockPrice('RELIANCE.NS');
    const cryptoData = await api.getCryptoPrice('BTCUSDT');

    console.log('Stock:', stockData);
    console.log('Crypto:', cryptoData);

    // Get multiple crypto prices
    const multiCrypto = await api.getMultipleCryptoPrices(['BTCUSDT', 'ETHUSDT', 'ADAUSDT']);
    console.log('Multiple crypto:', multiCrypto);

    // Get historical data
    const history = await api.getHistoricalData('BTCUSDT', { interval: '1d', limit: 30 });
    console.log('Historical data points:', history ? history.data.length : 0);

    // Start monitoring (commented out to avoid infinite loop)
    // const monitorId = api.monitorPrices(['RELIANCE.NS', 'BTCUSDT'], 30000);

    // Stop monitoring after some time
    // setTimeout(() => clearInterval(monitorId), 300000); // 5 minutes
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = StockCryptoAPI;
```

## 📱 React Example

```jsx
import React, { useState, useEffect } from 'react';

function CryptoDashboard() {
    const [prices, setPrices] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const BASE_URL = 'https://fastapi-stock-data.onrender.com';

    useEffect(() => {
        fetchPrices();
        // Set up auto-refresh every 30 seconds
        const interval = setInterval(fetchPrices, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchPrices = async () => {
        try {
            setLoading(true);
            const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT'];
            const symbolStr = symbols.join(',');

            const response = await fetch(`${BASE_URL}/crypto-multiple?symbols=${symbolStr}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            setPrices(data.data);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading && Object.keys(prices).length === 0) {
        return <div className="loading">Loading cryptocurrency prices...</div>;
    }

    if (error) {
        return <div className="error">Error: {error}</div>;
    }

    return (
        <div className="crypto-dashboard">
            <h1>Cryptocurrency Prices</h1>
            <button onClick={fetchPrices} disabled={loading}>
                {loading ? 'Refreshing...' : 'Refresh Prices'}
            </button>

            <div className="price-grid">
                {Object.entries(prices).map(([symbol, data]) => (
                    <div key={symbol} className="price-card">
                        <h3>{symbol.replace('USDT', '')}/USD</h3>
                        <div className="price">${parseFloat(data.price).toLocaleString()}</div>
                        <small>Last updated: {new Date(data.timestamp * 1000).toLocaleTimeString()}</small>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default CryptoDashboard;
```

## 📊 cURL Examples

```bash
# Health check
curl https://fastapi-stock-data.onrender.com/health

# Get stock price
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=RELIANCE.NS"

# Get crypto price
curl "https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT"

# Get multiple crypto prices
curl "https://fastapi-stock-data.onrender.com/crypto-multiple?symbols=BTCUSDT,ETHUSDT,ADAUSDT"

# Get crypto statistics
curl "https://fastapi-stock-data.onrender.com/crypto-stats/BTCUSDT"

# Get historical crypto data
curl "https://fastapi-stock-data.onrender.com/crypto-historical/BTCUSDT?interval=1d&limit=30"

# Get historical stock data
curl "https://fastapi-stock-data.onrender.com/historical/RELIANCE.NS?period=1mo&interval=1d"

# Get index price
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index=NIFTY"

# Pretty print JSON responses
curl "https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT" | jq .
```

## 🐚 Shell Script Examples

```bash
#!/bin/bash

BASE_URL="https://fastapi-stock-data.onrender.com"

# Function to get stock price
get_stock_price() {
    local symbol=$1
    echo "Getting price for $symbol..."
    curl -s "$BASE_URL/api/v1/market/price/stock?symbol=$symbol" | jq .
}

# Function to get crypto price
get_crypto_price() {
    local symbol=$1
    echo "Getting price for $symbol..."
    curl -s "$BASE_URL/crypto-price/$symbol" | jq .
}

# Function to monitor prices
monitor_prices() {
    local symbols=("$@")
    echo "Monitoring prices for ${symbols[*]}"

    while true; do
        echo "=== $(date '+%H:%M:%S') ==="

        for symbol in "${symbols[@]}"; do
            if [[ $symbol == *".NS" ]]; then
                # Stock
                price=$(curl -s "$BASE_URL/api/v1/market/price/stock?symbol=$symbol" | jq -r '.lastPrice')
                echo "$symbol: ₹$price"
            else
                # Crypto
                price=$(curl -s "$BASE_URL/crypto-price/$symbol" | jq -r '.price')
                echo "$symbol: $$price"
            fi
        done

        sleep 30
    done
}

# Usage examples
get_stock_price "RELIANCE.NS"
get_crypto_price "BTCUSDT"

# Monitor prices (uncomment to use)
# monitor_prices "RELIANCE.NS" "BTCUSDT" "ETHUSDT"
```

## 🔧 Error Handling Examples

### Python Error Handling

```python
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

def safe_api_call(url, max_retries=3):
    """Make API call with retry logic and error handling"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()

        except Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue

        except ConnectionError:
            print(f"Connection error on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("Rate limited, waiting...")
                time.sleep(60)
                continue
            elif response.status_code >= 500:
                print(f"Server error: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
            else:
                print(f"HTTP error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    return None

# Usage
data = safe_api_call("https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT")
if data:
    print(f"BTC: ${data['price']}")
else:
    print("Failed to fetch data after retries")
```

### JavaScript Error Handling

```javascript
async function safeApiCall(url, options = {}) {
    const maxRetries = options.maxRetries || 3;
    const timeout = options.timeout || 10000;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                if (response.status === 429) {
                    // Rate limited
                    const retryAfter = response.headers.get('Retry-After') || 60;
                    console.log(`Rate limited, waiting ${retryAfter} seconds...`);
                    await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
                    continue;
                } else if (response.status >= 500) {
                    // Server error, retry
                    console.log(`Server error ${response.status}, retrying...`);
                    await new Promise(resolve => setTimeout(resolve, 1000 * (2 ** attempt)));
                    continue;
                } else {
                    // Client error, don't retry
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            }

            return await response.json();

        } catch (error) {
            if (error.name === 'AbortError') {
                console.log(`Timeout on attempt ${attempt + 1}`);
            } else {
                console.log(`Error on attempt ${attempt + 1}: ${error.message}`);
            }

            if (attempt < maxRetries - 1) {
                const delay = 1000 * (2 ** attempt);
                console.log(`Waiting ${delay}ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    throw new Error(`Failed after ${maxRetries} attempts`);
}

// Usage
try {
    const data = await safeApiCall('https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT');
    console.log(`BTC: $${data.price}`);
} catch (error) {
    console.error('Failed to fetch BTC price:', error.message);
}
```

## 📈 Advanced Examples

### Price Alert System

```python
import requests
import time
from typing import Dict, Callable

class PriceAlertSystem:
    def __init__(self, base_url: str = "https://fastapi-stock-data.onrender.com"):
        self.base_url = base_url
        self.alerts = {}  # symbol -> (target_price, condition, callback)

    def add_alert(self, symbol: str, target_price: float, condition: str, callback: Callable):
        """Add price alert"""
        self.alerts[symbol] = (target_price, condition, callback)

    def check_alerts(self):
        """Check all alerts"""
        if not self.alerts:
            return

        symbols = list(self.alerts.keys())

        # Get current prices
        try:
            if symbols[0].endswith('.NS'):
                # Stocks
                prices = {}
                for symbol in symbols:
                    response = requests.get(f"{self.base_url}/api/v1/market/price/stock?symbol={symbol}")
                    if response.status_code == 200:
                        data = response.json()
                        prices[symbol] = float(data['lastPrice'])
            else:
                # Crypto
                symbol_str = ",".join(symbols)
                response = requests.get(f"{self.base_url}/crypto-multiple?symbols={symbol_str}")
                if response.status_code == 200:
                    data = response.json()
                    prices = {symbol: float(info['price']) for symbol, info in data['data'].items()}

            # Check alerts
            triggered = []
            for symbol, (target_price, condition, callback) in self.alerts.items():
                if symbol in prices:
                    current_price = prices[symbol]

                    if condition == 'above' and current_price >= target_price:
                        callback(symbol, current_price, 'above', target_price)
                        triggered.append(symbol)
                    elif condition == 'below' and current_price <= target_price:
                        callback(symbol, current_price, 'below', target_price)
                        triggered.append(symbol)

            # Remove triggered alerts
            for symbol in triggered:
                del self.alerts[symbol]

        except Exception as e:
            print(f"Error checking alerts: {e}")

    def monitor_alerts(self, interval_seconds: int = 30):
        """Monitor alerts continuously"""
        print(f"Monitoring {len(self.alerts)} alerts...")

        try:
            while self.alerts:
                self.check_alerts()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("Alert monitoring stopped.")

# Usage
def price_alert_callback(symbol, current_price, condition, target_price):
    print(f"🚨 ALERT: {symbol} is {condition} ₹{target_price} (current: ₹{current_price})")

alert_system = PriceAlertSystem()

# Add alerts
alert_system.add_alert("RELIANCE.NS", 2500, "above", price_alert_callback)
alert_system.add_alert("BTCUSDT", 50000, "below", price_alert_callback)

# Monitor alerts
alert_system.monitor_alerts()
```

This comprehensive examples page provides code samples for various use cases and programming languages. All examples include proper error handling and best practices for production use.
