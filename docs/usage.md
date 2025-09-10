# FastStockAPI Usage Guide

This comprehensive guide provides practical examples for using FastStockAPI across different programming languages and use cases.

##  Quick Start

### Base URL
```
http://localhost:8000  (local development)
https://your-domain.com  (production)
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Stock Market Data

### Get Indian Stock Price
```bash
# Using cURL
curl "http://localhost:8000/stocks/IND/RELIANCE"

# Using Python
import requests
response = requests.get("http://localhost:8000/stocks/IND/RELIANCE")
print(response.json())
```

### Get US Stock Price
```bash
# Using cURL
curl "http://localhost:8000/stocks/US/AAPL"

# Using JavaScript
fetch('http://localhost:8000/stocks/US/AAPL')
    .then(res => res.json())
    .then(data => console.log(data));
```

### Get Historical Stock Data
```bash
# Indian Stock - 1 Month
curl "http://localhost:8000/stocks/historical/IND/RELIANCE?period=1mo"

# US Stock - 3 Months
curl "http://localhost:8000/stocks/historical/US/AAPL?period=3mo"
```

### Get Market Index Data
```bash
# US Index
curl "http://localhost:8000/stocks/index/US/DJI"

# BSE Index
curl "http://localhost:8000/stocks/index/BSE/SENSEX"
```

## Cryptocurrency Data

### Get Crypto Price
```bash
# Single cryptocurrency
curl "http://localhost:8000/crypto/quote/BTC"

# Multiple cryptocurrencies
curl "http://localhost:8000/crypto/list"
```

### Get Historical Crypto Data
```bash
curl "http://localhost:8000/crypto/historical/ETH?period=1mo"
```

## Options Trading Data

### Get Index Price for Options
```bash
curl "http://localhost:8000/options/index-price?index=NIFTY"
```

### Get Available Expiries
```bash
curl "http://localhost:8000/options/expiries?index=NIFTY"
```

### Get Options Chain Data
```bash
# Direct data (no CSV saving)
curl "http://localhost:8000/options/direct-data?index=NIFTY&expiry=160925&num_strikes=10"

# Strike-specific data
curl "http://localhost:8000/options/strike-data?index=NIFTY&strike=24000&expiry=160925&option_type=BOTH"
```

### Get Option Price
```bash
curl "http://localhost:8000/options/option-price?index=NIFTY&strike=24000&expiry=160925&option_type=CE"
```

### Get Historical Option Data
```bash
curl "http://localhost:8000/options/historical/NIFTY?strike=24000&expiry=160925&option_type=CE&period=1mo"
```

### Fetch Options Data (JSON Response)
```bash
# Fetch nearest expiry options and return JSON directly
curl -X POST "http://localhost:8000/options/fetch/json" \
     -H "Content-Type: application/json" \
     -d '{"index": "NIFTY", "num_strikes": 25}'

# Fetch specific expiry options and return JSON directly
curl -X POST "http://localhost:8000/options/fetch/expiry/json" \
     -H "Content-Type: application/json" \
     -d '{"index": "NIFTY", "expiry": "160925", "num_strikes": 25}'
```

## Advanced Analytics

### Put-Call Ratio (PCR)
```bash
curl "http://localhost:8000/analytics/pcr?index=NIFTY&expiry=160925"
```

### Maximum Pain Calculation
```bash
curl "http://localhost:8000/analytics/max-pain?index=NIFTY&expiry=160925"
```

### Top Open Interest
```bash
curl "http://localhost:8000/analytics/top-oi?index=NIFTY&expiry=160925&top_n=5"
```

### Complete Analytics Summary
```bash
curl "http://localhost:8000/analytics/summary?index=NIFTY&expiry=160925"
```

## Forex Data

### Get Exchange Rate
```bash
curl "http://localhost:8000/forex/quote?from=USD&to=INR"
```

### Get Multiple Exchange Rates
```bash
curl "http://localhost:8000/forex/quotes?base=USD&symbols=EUR,GBP,JPY"
```

### Get Historical Forex Data
```bash
curl "http://localhost:8000/forex/historical?from=USD&to=INR&period=1mo"
```

## 💻 Programming Examples

### Python - Complete Trading Dashboard

```python
import requests
import pandas as pd
from datetime import datetime

class FastStockAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def get_stock_price(self, symbol, market="IND"):
        """Get stock price for Indian or US market"""
        url = f"{self.base_url}/stocks/{market}/{symbol}"
        response = requests.get(url)
        return response.json()

    def get_options_data(self, index, expiry, num_strikes=10):
        """Get options chain data"""
        url = f"{self.base_url}/options/direct-data"
        params = {
            "index": index,
            "expiry": expiry,
            "num_strikes": num_strikes
        }
        response = requests.get(url, params=params)
        return response.json()

    def get_analytics(self, index, expiry):
        """Get complete analytics"""
        url = f"{self.base_url}/analytics/summary"
        params = {"index": index, "expiry": expiry}
        response = requests.get(url, params=params)
        return response.json()

    def create_options_dashboard(self, index="NIFTY", expiry="160925"):
        """Create a comprehensive options dashboard"""
        print(f"📊 {index} Options Dashboard - Expiry: {expiry}")
        print("=" * 50)

        # Get index price
        index_data = requests.get(f"{self.base_url}/options/index-price?index={index}").json()
        print(f"📈 Index Price: ₹{index_data['lastPrice']}")

        # Get analytics
        analytics = self.get_analytics(index, expiry)
        print(f"📊 PCR: {analytics['pcr']:.2f}")
        print(f"🎯 Max Pain: ₹{analytics['max_pain']['max_pain_strike']}")

        # Get options data
        options_data = self.get_options_data(index, expiry, 5)
        print(f"\n📋 Options Chain (Top 5 strikes around ATM):")
        for option in options_data['options'][:5]:
            strike = option['strikePrice']
            ce_data = option.get('CE', {})
            pe_data = option.get('PE', {})

            ce_price = ce_data.get('lastPrice', 'N/A')
            pe_price = pe_data.get('lastPrice', 'N/A')

            print(f"₹{strike}: CE ₹{ce_price}, PE ₹{pe_price}")

# Usage
api = FastStockAPI()
api.create_options_dashboard()
```

### JavaScript - Real-time Dashboard

```javascript
class FastStockDashboard {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.updateInterval = 30000; // 30 seconds
    }

    async getStockData(symbol, market = 'IND') {
        const response = await fetch(`${this.baseUrl}/stocks/${market}/${symbol}`);
        return await response.json();
    }

    async getOptionsData(index, expiry, numStrikes = 10) {
        const params = new URLSearchParams({
            index,
            expiry,
            num_strikes: numStrikes
        });
        const response = await fetch(`${this.baseUrl}/options/direct-data?${params}`);
        return await response.json();
    }

    async getAnalytics(index, expiry) {
        const params = new URLSearchParams({ index, expiry });
        const response = await fetch(`${this.baseUrl}/analytics/summary?${params}`);
        return await response.json();
    }

    async updateDashboard() {
        try {
            // Update stock prices
            const [reliance, tcs, aapl] = await Promise.all([
                this.getStockData('RELIANCE'),
                this.getStockData('TCS'),
                this.getStockData('AAPL', 'US')
            ]);

            this.updateStockDisplay('reliance', reliance);
            this.updateStockDisplay('tcs', tcs);
            this.updateStockDisplay('aapl', aapl);

            // Update options analytics
            const analytics = await this.getAnalytics('NIFTY', '160925');
            this.updateAnalyticsDisplay(analytics);

            // Update options chain
            const optionsData = await this.getOptionsData('NIFTY', '160925', 5);
            this.updateOptionsTable(optionsData);

        } catch (error) {
            console.error('Dashboard update failed:', error);
        }
    }

    updateStockDisplay(elementId, data) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="stock-card">
                    <h3>${data.symbol}</h3>
                    <p class="price">₹${data.lastPrice}</p>
                    <p class="change ${data.pChange >= 0 ? 'positive' : 'negative'}">
                        ${data.pChange}% (${data.change >= 0 ? '+' : ''}${data.change})
                    </p>
                </div>
            `;
        }
    }

    updateAnalyticsDisplay(analytics) {
        document.getElementById('pcr').textContent = analytics.pcr.toFixed(2);
        document.getElementById('max-pain').textContent = `₹${analytics.max_pain.max_pain_strike}`;
        document.getElementById('atm-strike').textContent = analytics.meta.atmStrike;
    }

    updateOptionsTable(optionsData) {
        const tbody = document.getElementById('options-table-body');
        tbody.innerHTML = optionsData.options.slice(0, 5).map(option => `
            <tr>
                <td>₹${option.strikePrice}</td>
                <td>₹${option.CE?.lastPrice || 'N/A'}</td>
                <td>${option.CE?.openInterest || 'N/A'}</td>
                <td>₹${option.PE?.lastPrice || 'N/A'}</td>
                <td>${option.PE?.openInterest || 'N/A'}</td>
            </tr>
        `).join('');
    }

    startRealTimeUpdates() {
        this.updateDashboard(); // Initial update
        setInterval(() => this.updateDashboard(), this.updateInterval);
    }
}

// Usage
const dashboard = new FastStockDashboard();
dashboard.startRealTimeUpdates();
```

### Java - Enterprise Integration

```java
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import com.fasterxml.jackson.databind.ObjectMapper;

public class FastStockClient {
    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    public FastStockClient(String baseUrl) {
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }

    public StockQuote getIndianStock(String symbol) throws Exception {
        String url = baseUrl + "/stocks/IND/" + symbol;
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() == 200) {
            return objectMapper.readValue(response.body(), StockQuote.class);
        } else {
            throw new RuntimeException("API request failed: " + response.statusCode());
        }
    }

    public OptionsData getOptionsData(String index, String expiry) throws Exception {
        String url = String.format("%s/options/direct-data?index=%s&expiry=%s&num_strikes=10",
                                 baseUrl, index, expiry);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() == 200) {
            return objectMapper.readValue(response.body(), OptionsData.class);
        } else {
            throw new RuntimeException("API request failed: " + response.statusCode());
        }
    }

    public AnalyticsData getAnalytics(String index, String expiry) throws Exception {
        String url = String.format("%s/analytics/summary?index=%s&expiry=%s",
                                 baseUrl, index, expiry);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() == 200) {
            return objectMapper.readValue(response.body(), AnalyticsData.class);
        } else {
            throw new RuntimeException("API request failed: " + response.statusCode());
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        FastStockClient client = new FastStockClient("http://localhost:8000");

        try {
            // Get stock data
            StockQuote reliance = client.getIndianStock("RELIANCE");
            System.out.println("RELIANCE Price: ₹" + reliance.getLastPrice());

            // Get options data
            OptionsData options = client.getOptionsData("NIFTY", "160925");
            System.out.println("Options loaded: " + options.getOptions().size());

            // Get analytics
            AnalyticsData analytics = client.getAnalytics("NIFTY", "160925");
            System.out.println("PCR: " + analytics.getPcr());

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
```

## Advanced Use Cases

### Algorithmic Trading Bot

```python
import time
import logging
from fastapi_client import FastStockAPI

class OptionsTradingBot:
    def __init__(self):
        self.api = FastStockAPI()
        self.logger = logging.getLogger(__name__)

    def monitor_pcr_divergence(self, index="NIFTY", threshold=0.3):
        """Monitor PCR divergence for trading signals"""
        expiries = self.api.get_expiries(index)

        for expiry in expiries[:2]:  # Check near-term expiries
            analytics = self.api.get_analytics(index, expiry)

            if analytics['pcr'] > 1.5:  # Extreme bearish sentiment
                self.logger.info(f"🐻 Bearish signal: PCR {analytics['pcr']} for {expiry}")
                # Implement bearish strategy

            elif analytics['pcr'] < 0.7:  # Extreme bullish sentiment
                self.logger.info(f"🐂 Bullish signal: PCR {analytics['pcr']} for {expiry}")
                # Implement bullish strategy

    def max_pain_levels(self, index="NIFTY"):
        """Track max pain levels for position management"""
        expiries = self.api.get_expiries(index)

        for expiry in expiries[:3]:
            analytics = self.api.get_analytics(index, expiry)
            max_pain = analytics['max_pain']['max_pain_strike']

            # Check if current price is near max pain
            index_price = self.api.get_index_price(index)['lastPrice']
            distance = abs(index_price - max_pain) / index_price * 100

            if distance < 2:  # Within 2% of max pain
                self.logger.warning(f"⚠️ Near max pain: ₹{max_pain} for {expiry}")

    def run(self):
        """Main bot loop"""
        while True:
            try:
                self.monitor_pcr_divergence()
                self.max_pain_levels()
                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Bot error: {e}")
                time.sleep(60)  # Wait before retry

# Usage
if __name__ == "__main__":
    bot = OptionsTradingBot()
    bot.run()
```

### Portfolio Tracker

```python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class PortfolioTracker:
    def __init__(self, api_client):
        self.api = api_client
        self.portfolio = {}

    def add_position(self, symbol, quantity, market="IND"):
        """Add a position to the portfolio"""
        self.portfolio[symbol] = {
            'quantity': quantity,
            'market': market,
            'entry_date': datetime.now()
        }

    def get_portfolio_value(self):
        """Calculate current portfolio value"""
        total_value = 0
        positions_data = []

        for symbol, position in self.portfolio.items():
            try:
                if position['market'] == 'IND':
                    data = self.api.get_stock_price(symbol, 'IND')
                elif position['market'] == 'US':
                    data = self.api.get_stock_price(symbol, 'US')
                else:
                    continue

                value = data['lastPrice'] * position['quantity']
                total_value += value

                positions_data.append({
                    'symbol': symbol,
                    'quantity': position['quantity'],
                    'price': data['lastPrice'],
                    'value': value,
                    'change': data['pChange']
                })

            except Exception as e:
                print(f"Error getting data for {symbol}: {e}")

        return {
            'total_value': total_value,
            'positions': positions_data,
            'timestamp': datetime.now()
        }

    def generate_report(self):
        """Generate portfolio performance report"""
        portfolio_data = self.get_portfolio_value()

        print(f"📊 Portfolio Report - {portfolio_data['timestamp']}")
        print(f"💰 Total Value: ₹{portfolio_data['total_value']:,.2f}")
        print("-" * 50)

        for position in portfolio_data['positions']:
            change_symbol = "📈" if position['change'] >= 0 else "📉"
            print(f"{position['symbol']}: {position['quantity']} shares @ ₹{position['price']}")
            print(f"  Value: ₹{position['value']:,.2f} {change_symbol} {position['change']}%")
            print()

# Usage
tracker = PortfolioTracker(FastStockAPI())
tracker.add_position('RELIANCE', 100)
tracker.add_position('TCS', 50)
tracker.add_position('AAPL', 10, 'US')

tracker.generate_report()
```

## Error Handling

### Common Error Patterns

```python
def robust_api_call(func, *args, **kwargs):
    """Robust API call with error handling and retries"""
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)

            # Check for API-specific errors
            if isinstance(result, dict) and 'error' in result:
                raise ValueError(result['error'])

            return result

        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                continue
            raise

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise

        except ValueError as e:
            # API returned an error
            print(f"API Error: {e}")
            raise

# Usage
@robust_api_call
def get_stock_with_retry(symbol):
    return requests.get(f"http://localhost:8000/stocks/IND/{symbol}").json()
```

## Best Practices

### 1. Rate Limiting
```python
import time

class RateLimiter:
    def __init__(self, calls_per_minute=50):
        self.calls_per_minute = calls_per_minute
        self.calls = []

    def can_make_call(self):
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [call for call in self.calls if now - call < 60]

        return len(self.calls) < self.calls_per_minute

    def record_call(self):
        self.calls.append(time.time())

# Usage
limiter = RateLimiter()

if limiter.can_make_call():
    # Make API call
    limiter.record_call()
else:
    time.sleep(1)  # Wait before retry
```

### 2. Data Caching
```python
from cachetools import TTLCache

class DataCache:
    def __init__(self, ttl_seconds=300):  # 5 minutes default
        self.cache = TTLCache(maxsize=100, ttl=ttl_seconds)

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

    def get_or_fetch(self, key, fetch_func):
        """Get from cache or fetch and cache"""
        if key in self.cache:
            return self.cache[key]

        value = fetch_func()
        self.cache[key] = value
        return value

# Usage
cache = DataCache()

def get_cached_stock_price(symbol):
    return cache.get_or_fetch(
        f"stock_{symbol}",
        lambda: requests.get(f"http://localhost:8000/stocks/IND/{symbol}").json()
    )
```

### 3. Logging and Monitoring
```python
import logging
import json

class APIMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.error_count = 0

    def log_request(self, endpoint, params=None, response_time=None):
        self.request_count += 1
        log_data = {
            'endpoint': endpoint,
            'params': params,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.info(f"API Request: {json.dumps(log_data)}")

    def log_error(self, endpoint, error):
        self.error_count += 1
        self.logger.error(f"API Error - {endpoint}: {error}")

    def get_stats(self):
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': self.error_count / max(self.request_count, 1)
        }

# Usage
monitor = APIMonitor()

def monitored_api_call(endpoint, **kwargs):
    start_time = time.time()

    try:
        response = requests.get(f"http://localhost:8000{endpoint}", **kwargs)
        response_time = time.time() - start_time

        monitor.log_request(endpoint, kwargs, response_time)
        return response.json()

    except Exception as e:
        monitor.log_error(endpoint, str(e))
        raise
```

##  Production Deployment

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose for Full Stack
```yaml
version: '3.8'
services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

This comprehensive guide covers everything from basic API calls to advanced trading strategies and production deployment. Use the examples as starting points and adapt them to your specific use cases.
```

Example response:

```json
{
  "symbol": "NIFTY",
  "lastPrice": 23456.75,
  "pChange": 0.85,
  "change": 198.50,
  "timestamp": "09-Dec-2024 15:30:00"
}
```

Errors
- 400 Bad Request: missing or malformed query parameter
- 404 Not Found: index not found or no data returned from source
- 500 Server Error: unexpected internal error (rare — please check logs and upstream data source)

2) Get Stock Price

Description: Returns the latest price data for an NSE stock.

Endpoint (path):

```
GET /api/v1/market/price/stock/{symbol}
```

Example (path form):

```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/stock/RELIANCE.NS"
```

Endpoint (query):

```
GET /api/v1/market/price/stock?symbol={symbol}
```

Example (query form). The API will try the exact symbol and then fall back to appending `.NS` if needed:

```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=RELIANCE"
```

Example response:

```json
{
  "symbol": "RELIANCE.NS",
  "companyName": "Reliance Industries Ltd",
  "lastPrice": 2456.75,
  "pChange": 1.25,
  "change": 30.5,
  "timestamp": "09-Dec-2024 15:30:00"
}
```

Errors
- 400 Bad Request: missing required parameter `symbol`
- 404 Not Found: symbol not supported or delisted
- 500 Server Error: unexpected internal error

Client examples

Python (requests)

```python
import requests

BASE = "https://fastapi-stock-data.onrender.com"

# Index
r = requests.get(f"{BASE}/api/v1/market/price/index/NIFTY")
if r.ok:
    print(r.json())
else:
    print("Error", r.status_code, r.text)

# Stock (query form)
r = requests.get(f"{BASE}/api/v1/market/price/stock", params={"symbol": "RELIANCE"})
if r.ok:
    print(r.json())
else:
    print("Error", r.status_code, r.text)
```

JavaScript (fetch)

```javascript
const base = 'https://fastapi-stock-data.onrender.com';

// Index
fetch(`${base}/api/v1/market/price/index?index=NIFTY`)
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);

// Stock
fetch(`${base}/api/v1/market/price/stock?symbol=RELIANCE`)
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

Tips & Troubleshooting

- If you get `404` with message like "No lastPrice found... Available keys: [...]", the upstream NSE response shape changed for that symbol or the symbol is not available. Try:
  - Verify the symbol on the NSE website
  - Use the alternative form (path vs query)
  - Try the `.NS` suffix for stocks
- For indices use the simple names (`NIFTY`, `BANKNIFTY`). Historical endpoints require Yahoo-style symbols like `^NSENIFTY`.
- For crypto and other parts of the API, refer to the corresponding API docs pages under `docs/api`.

Best practices

- Cache responses where suitable (indices do not change every millisecond for most use cases).
- Respect upstream rate limits (NSE, Binance). Add client-side throttling.
- Prefer the path form in server-to-server calls (stable, easier to log), use the query form if your client framework builds query params more conveniently.

Further reading

- Full API reference: `docs/api/market.md`
- Symbol reference: `docs/symbols/nse-stocks.md`

---

If you want, I can add this file to the navigation (`mkdocs.yml`) and update examples across the docs so both URL styles are shown consistently.
