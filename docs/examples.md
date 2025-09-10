# FastStockAPI Code Examples

This comprehensive guide provides practical code examples for using FastStockAPI in various programming languages and frameworks. All examples use the current API structure and include error handling, best practices, and real-world use cases.

## Python Examples

### Basic Setup

```python
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your deployed URL
REQUEST_TIMEOUT = 30
RATE_LIMIT_DELAY = 1  # seconds between requests

class FastStockAPI:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.last_request_time = 0

    def _rate_limit_wait(self):
        """Implement rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        self._rate_limit_wait()

        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

# Initialize API client
api = FastStockAPI()
```

### Stock Market Examples

#### 1. Get Individual Stock Prices

```python
def get_stock_price(symbol: str, market: str = "IND") -> Optional[Dict]:
    """Get current price for a specific stock"""
    endpoint = f"/stocks/{market}/{symbol}"
    data = api._make_request(endpoint)

    if data:
        print(f" {data['symbol']}: ₹{data['lastPrice']}")
        print(f"   Change: {data['pChange']}% (₹{data['change']})")
        print(f"   Company: {data['companyName']}")
        return data
    return None

# Usage
reliance_data = get_stock_price("RELIANCE")
apple_data = get_stock_price("AAPL", "US")
```

#### 2. Get Historical Stock Data

```python
def get_historical_stock_data(symbol: str, market: str = "IND", period: str = "1mo") -> Optional[Dict]:
    """Get historical price data for a stock"""
    endpoint = f"/stocks/historical/{market}/{symbol}"
    params = {"period": period}
    data = api._make_request(endpoint, params)

    if data and 'data' in data:
        prices = data['data']
        print(f" {symbol} Historical Data ({len(prices)} points)")
        print(f"   Period: {data['period']}")

        if prices:
            latest = prices[-1]
            oldest = prices[0]
            change = ((latest['close'] - oldest['close']) / oldest['close']) * 100
            print(".2f")
            print(".2f")

        return data
    return None

# Usage
historical_data = get_historical_stock_data("TCS", "IND", "3mo")
```

#### 3. Get Market Index Data

```python
def get_market_index(symbol: str, market: str = "BSE") -> Optional[Dict]:
    """Get market index data"""
    endpoint = f"/stocks/index/{market}/{symbol}"
    data = api._make_request(endpoint)

    if data:
        print(f" {data['symbol']}: {data['lastPrice']}")
        print(f"   Change: {data['pChange']}% (₹{data['change']})")
        return data
    return None

# Usage
nifty_data = get_market_index("SENSEX", "BSE")
dow_data = get_market_index("DJI", "US")
```

#### 4. Portfolio Tracking

```python
class PortfolioTracker:
    def __init__(self):
        self.api = FastStockAPI()
        self.portfolio = {}

    def add_stock(self, symbol: str, quantity: int, market: str = "IND"):
        """Add stock to portfolio"""
        self.portfolio[symbol] = {
            'quantity': quantity,
            'market': market,
            'added_at': datetime.now()
        }

    def get_portfolio_value(self) -> Dict:
        """Calculate current portfolio value"""
        total_value = 0
        positions = []

        for symbol, position in self.portfolio.items():
            try:
                if position['market'] == 'IND':
                    data = self.api._make_request(f"/stocks/IND/{symbol}")
                elif position['market'] == 'US':
                    data = self.api._make_request(f"/stocks/US/{symbol}")

                if data:
                    value = data['lastPrice'] * position['quantity']
                    total_value += value

                    positions.append({
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
            'positions': positions,
            'timestamp': datetime.now()
        }

    def print_portfolio_summary(self):
        """Print portfolio summary"""
        portfolio_data = self.get_portfolio_value()

        print(f"\n Portfolio Summary - {portfolio_data['timestamp']}")
        print(f"💰 Total Value: ₹{portfolio_data['total_value']:,.2f}")
        print("-" * 50)

        for position in portfolio_data['positions']:
            change_symbol = "" if position['change'] >= 0 else ""
            print(f"{position['symbol']}: {position['quantity']} shares @ ₹{position['price']}")
            print(f"  Value: ₹{position['value']:,.2f} {change_symbol} {position['change']}%")

# Usage
tracker = PortfolioTracker()
tracker.add_stock("RELIANCE", 100)
tracker.add_stock("TCS", 50)
tracker.add_stock("AAPL", 10, "US")
tracker.print_portfolio_summary()
```

### Cryptocurrency Examples

#### 1. Get Crypto Prices

```python
def get_crypto_price(symbol: str) -> Optional[Dict]:
    """Get current cryptocurrency price"""
    endpoint = f"/crypto/quote/{symbol}"
    data = api._make_request(endpoint)

    if data:
        print(f" {data['symbol']} ({data['name']}): ${data['price']:,.2f}")
        print(f"   24h Change: {data['changePercent24h']}%")
        print(f"   Market Cap: ${data['marketCap']:,.0f}")
        print(f"   Volume 24h: ${data['volume24h']:,.0f}")
        return data
    return None

def get_multiple_crypto_prices(symbols: List[str]) -> List[Dict]:
    """Get multiple cryptocurrency prices"""
    results = []
    for symbol in symbols:
        data = get_crypto_price(symbol)
        if data:
            results.append(data)
        time.sleep(0.5)  # Rate limiting
    return results

# Usage
btc_data = get_crypto_price("BTC")
crypto_portfolio = get_multiple_crypto_prices(["BTC", "ETH", "ADA", "SOL"])
```

#### 2. Crypto Historical Analysis

```python
def analyze_crypto_performance(symbol: str, period: str = "1mo") -> Optional[Dict]:
    """Analyze cryptocurrency performance over a period"""
    endpoint = f"/crypto/historical/{symbol}"
    params = {"period": period}
    data = api._make_request(endpoint, params)

    if data and 'data' in data:
        prices = data['data']
        if len(prices) < 2:
            return None

        # Calculate performance metrics
        start_price = prices[0]['close']
        end_price = prices[-1]['close']
        total_return = ((end_price - start_price) / start_price) * 100

        # Calculate volatility (standard deviation of returns)
        returns = []
        for i in range(1, len(prices)):
            daily_return = ((prices[i]['close'] - prices[i-1]['close']) / prices[i-1]['close']) * 100
            returns.append(daily_return)

        volatility = sum((r - sum(returns)/len(returns))**2 for r in returns) / len(returns)
        volatility = volatility ** 0.5

        # Find highest and lowest prices
        high_price = max(p['high'] for p in prices)
        low_price = min(p['low'] for p in prices)

        analysis = {
            'symbol': symbol,
            'period': period,
            'start_price': start_price,
            'end_price': end_price,
            'total_return': total_return,
            'volatility': volatility,
            'highest_price': high_price,
            'lowest_price': low_price,
            'data_points': len(prices)
        }

        print(f" {symbol} Performance Analysis ({period})")
        print(f"   Total Return: {total_return:.2f}%")
        print(f"   Volatility: {volatility:.2f}%")
        print(f"   Price Range: ${low_price:.2f} - ${high_price:.2f}")

        return analysis
    return None

# Usage
btc_analysis = analyze_crypto_performance("BTC", "3mo")
eth_analysis = analyze_crypto_performance("ETH", "1mo")
```

### Options Trading Examples

#### 1. Options Chain Analysis

```python
def analyze_options_chain(index: str, expiry: str, num_strikes: int = 10) -> Optional[Dict]:
    """Analyze complete options chain"""
    endpoint = "/options/direct-data"
    params = {
        "index": index,
        "expiry": expiry,
        "num_strikes": num_strikes
    }
    data = api._make_request(endpoint, params)

    if data:
        print(f" {index} Options Chain - Expiry: {data['expiry']}")
        print(f"   Underlying: ₹{data['underlying_value']}")
        print(f"   Strikes Available: {len(data['options'])}")

        # Analyze call/put ratio
        total_calls = sum(1 for opt in data['options'] if 'CE' in opt and opt['CE'].get('lastPrice'))
        total_puts = sum(1 for opt in data['options'] if 'PE' in opt and opt['PE'].get('lastPrice'))

        print(f"   Calls: {total_calls}, Puts: {total_puts}")

        # Find ATM strike
        atm_strike = min(data['options'],
                        key=lambda x: abs(x['strikePrice'] - data['underlying_value']))
        print(f"   ATM Strike: ₹{atm_strike['strikePrice']}")

        return data
    return None

# Usage
nifty_options = analyze_options_chain("NIFTY", "160925", 15)
```

#### 2. Strike-Specific Analysis

```python
def analyze_specific_strike(index: str, strike: float, expiry: str) -> Optional[Dict]:
    """Analyze specific strike price"""
    endpoint = "/options/strike-data"
    params = {
        "index": index,
        "strike": strike,
        "expiry": expiry,
        "option_type": "BOTH"
    }
    data = api._make_request(endpoint, params)

    if data:
        print(f" {index} {strike} Strike Analysis")
        print(f"   Expiry: {data['expiry']}")
        print(f"   Underlying: ₹{data['underlying_value']}")

        if data.get('ce_data'):
            ce = data['ce_data']
            print(f"   CE: ₹{ce.get('lastPrice', 'N/A')} (OI: {ce.get('openInterest', 'N/A')})")

        if data.get('pe_data'):
            pe = data['pe_data']
            print(f"   PE: ₹{pe.get('lastPrice', 'N/A')} (OI: {pe.get('openInterest', 'N/A')})")

        return data
    return None

# Usage
strike_analysis = analyze_specific_strike("NIFTY", 24000, "160925")
```

#### 3. Fetch Options Data (JSON Response)

```python
def fetch_options_json(index: str, num_strikes: int = 25) -> Optional[Dict]:
    """Fetch options data and return JSON directly (no CSV saving)"""
    import requests
    
    url = f"{BASE_URL}/options/fetch/json"
    payload = {
        "index": index,
        "num_strikes": num_strikes
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f" Fetched {len(data['options'])} strikes for {data['index']} expiry {data['expiry']}")
            print(f"   Underlying: ₹{data['underlying_value']}")
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def fetch_options_expiry_json(index: str, expiry: str, num_strikes: int = 25) -> Optional[Dict]:
    """Fetch options data for specific expiry and return JSON directly"""
    import requests
    
    url = f"{BASE_URL}/options/fetch/expiry/json"
    payload = {
        "index": index,
        "expiry": expiry,
        "num_strikes": num_strikes
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f" Fetched {len(data['options'])} strikes for {data['index']} expiry {data['expiry']}")
            print(f"   Underlying: ₹{data['underlying_value']}")
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

# Usage
# Fetch nearest expiry options
nifty_options = fetch_options_json("NIFTY", 25)

# Fetch specific expiry options
nifty_expiry_options = fetch_options_expiry_json("NIFTY", "160925", 25)
```

#### 4. Options Analytics Dashboard

```python
def create_options_analytics_dashboard(index: str, expiry: str) -> Dict:
    """Create comprehensive options analytics dashboard"""
    dashboard = {
        'index': index,
        'expiry': expiry,
        'timestamp': datetime.now(),
        'analytics': {}
    }

    # Get PCR
    pcr_data = api._make_request("/analytics/pcr", {"index": index, "expiry": expiry})
    if pcr_data:
        dashboard['analytics']['pcr'] = pcr_data
        print(f" PCR: {pcr_data['pcr']:.2f}")

    # Get Max Pain
    max_pain_data = api._make_request("/analytics/max-pain", {"index": index, "expiry": expiry})
    if max_pain_data:
        dashboard['analytics']['max_pain'] = max_pain_data
        print(f" Max Pain: ₹{max_pain_data['max_pain_strike']}")

    # Get Top OI
    top_oi_data = api._make_request("/analytics/top-oi", {"index": index, "expiry": expiry, "top_n": 5})
    if top_oi_data:
        dashboard['analytics']['top_oi'] = top_oi_data
        print(" Top OI Strikes:")
        for strike in top_oi_data.get('top_strikes', []):
            print(f"   ₹{strike['strike']}: {strike['total_oi']:,} contracts")

    # Get complete summary
    summary_data = api._make_request("/analytics/summary", {"index": index, "expiry": expiry})
    if summary_data:
        dashboard['analytics']['summary'] = summary_data

    return dashboard

# Usage
dashboard = create_options_analytics_dashboard("NIFTY", "160925")
```

### Forex Examples

#### 1. Currency Exchange Rates

```python
def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[Dict]:
    """Get currency exchange rate"""
    endpoint = "/forex/quote"
    params = {"from": from_currency, "to": to_currency}
    data = api._make_request(endpoint, params)

    if data:
        print(f" {from_currency} to {to_currency}: {data.get('rate', 'N/A')}")
        return data
    return None

def get_multiple_exchange_rates(base_currency: str, target_currencies: List[str]) -> Optional[Dict]:
    """Get multiple exchange rates"""
    endpoint = "/forex/quotes"
    params = {"base": base_currency, "symbols": ",".join(target_currencies)}
    data = api._make_request(endpoint, params)

    if data:
        print(f" {base_currency} Exchange Rates:")
        for currency, rate in data.get('rates', {}).items():
            print(f"   {base_currency}/{currency}: {rate}")
        return data
    return None

# Usage
usd_inr = get_exchange_rate("USD", "INR")
multiple_rates = get_multiple_exchange_rates("USD", ["EUR", "GBP", "JPY", "CAD"])
```

## JavaScript Examples

### Node.js API Client

```javascript
const axios = require('axios');

class FastStockAPIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 30000,
        });

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            response => response,
            error => {
                console.error('API Error:', error.response?.status, error.response?.data);
                return Promise.reject(error);
            }
        );
    }

    async getStockPrice(symbol, market = 'IND') {
        try {
            const response = await this.client.get(`/stocks/${market}/${symbol}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching ${symbol}:`, error.message);
            return null;
        }
    }

    async getCryptoPrice(symbol) {
        try {
            const response = await this.client.get(`/crypto/quote/${symbol}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching ${symbol}:`, error.message);
            return null;
        }
    }

    async getOptionsAnalytics(index, expiry) {
        try {
            const [pcrRes, maxPainRes] = await Promise.all([
                this.client.get('/analytics/pcr', { params: { index, expiry } }),
                this.client.get('/analytics/max-pain', { params: { index, expiry } })
            ]);

            return {
                pcr: pcrRes.data,
                maxPain: maxPainRes.data
            };
        } catch (error) {
            console.error('Error fetching analytics:', error.message);
            return null;
        }
    }

    async getPortfolioValue(stocks) {
        const portfolio = [];
        let totalValue = 0;

        for (const stock of stocks) {
            const data = await this.getStockPrice(stock.symbol, stock.market);
            if (data) {
                const value = data.lastPrice * stock.quantity;
                totalValue += value;
                portfolio.push({
                    ...stock,
                    currentPrice: data.lastPrice,
                    value: value,
                    change: data.pChange
                });
            }
        }

        return {
            totalValue,
            positions: portfolio,
            timestamp: new Date().toISOString()
        };
    }
}

// Usage
async function main() {
    const api = new FastStockAPIClient();

    // Get individual prices
    const reliance = await api.getStockPrice('RELIANCE');
    const btc = await api.getCryptoPrice('BTC');

    console.log('RELIANCE:', reliance);
    console.log('BTC:', btc);

    // Get analytics
    const analytics = await api.getOptionsAnalytics('NIFTY', '160925');
    console.log('Analytics:', analytics);

    // Portfolio tracking
    const portfolio = await api.getPortfolioValue([
        { symbol: 'RELIANCE', quantity: 100, market: 'IND' },
        { symbol: 'TCS', quantity: 50, market: 'IND' },
        { symbol: 'AAPL', quantity: 10, market: 'US' }
    ]);

    console.log('Portfolio Value:', portfolio.totalValue);
}

main().catch(console.error);
```

### Browser JavaScript (Frontend Integration)

```javascript
// api-client.js
class FastStockAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    async makeRequest(endpoint, params = {}) {
        const url = new URL(`${this.baseURL}${endpoint}`);

        // Add query parameters
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.append(key, params[key]);
            }
        });

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Stock methods
    async getStockPrice(symbol, market = 'IND') {
        return this.makeRequest(`/stocks/${market}/${symbol}`);
    }

    async getHistoricalStockData(symbol, market = 'IND', period = '1mo') {
        return this.makeRequest(`/stocks/historical/${market}/${symbol}`, { period });
    }

    // Crypto methods
    async getCryptoPrice(symbol) {
        return this.makeRequest(`/crypto/quote/${symbol}`);
    }

    async getHistoricalCryptoData(symbol, period = '1mo') {
        return this.makeRequest(`/crypto/historical/${symbol}`, { period });
    }

    // Options methods
    async getOptionsChain(index, expiry, numStrikes = 10) {
        return this.makeRequest('/options/direct-data', {
            index,
            expiry,
            num_strikes: numStrikes
        });
    }

    async getOptionsAnalytics(index, expiry) {
        const [pcr, maxPain, topOi] = await Promise.all([
            this.makeRequest('/analytics/pcr', { index, expiry }),
            this.makeRequest('/analytics/max-pain', { index, expiry }),
            this.makeRequest('/analytics/top-oi', { index, expiry, top_n: 5 })
        ]);

        return { pcr, maxPain, topOi };
    }

    // Forex methods
    async getExchangeRate(fromCurrency, toCurrency) {
        return this.makeRequest('/forex/quote', { from: fromCurrency, to: toCurrency });
    }
}

// Initialize API client
const api = new FastStockAPI();

// React component example
function StockDashboard() {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(false);

    const loadStockData = async () => {
        setLoading(true);
        try {
            const [reliance, tcs, aapl] = await Promise.all([
                api.getStockPrice('RELIANCE'),
                api.getStockPrice('TCS'),
                api.getStockPrice('AAPL', 'US')
            ]);

            setStocks([reliance, tcs, aapl].filter(Boolean));
        } catch (error) {
            console.error('Error loading stock data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadStockData();
        // Refresh every 30 seconds
        const interval = setInterval(loadStockData, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="stock-dashboard">
            <h2>Stock Dashboard</h2>
            {loading ? (
                <p>Loading...</p>
            ) : (
                <div className="stock-grid">
                    {stocks.map(stock => (
                        <div key={stock.symbol} className="stock-card">
                            <h3>{stock.symbol}</h3>
                            <p className="price">₹{stock.lastPrice}</p>
                            <p className={`change ${stock.pChange >= 0 ? 'positive' : 'negative'}`}>
                                {stock.pChange}% ({stock.change >= 0 ? '+' : ''}{stock.change})
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

// Vue.js component example
const StockDashboard = {
    template: `
        <div class="stock-dashboard">
            <h2>Stock Dashboard</h2>
            <div v-if="loading" class="loading">Loading...</div>
            <div v-else class="stock-grid">
                <div v-for="stock in stocks" :key="stock.symbol" class="stock-card">
                    <h3>{{ stock.symbol }}</h3>
                    <p class="price">₹{{ stock.lastPrice }}</p>
                    <p :class="['change', stock.pChange >= 0 ? 'positive' : 'negative']">
                        {{ stock.pChange }}% ({{ stock.change >= 0 ? '+' : '' }}{{ stock.change }})
                    </p>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            stocks: [],
            loading: false
        };
    },
    async created() {
        await this.loadStockData();
        // Auto-refresh every 30 seconds
        setInterval(this.loadStockData, 30000);
    },
    methods: {
        async loadStockData() {
            this.loading = true;
            try {
                const [reliance, tcs] = await Promise.all([
                    api.getStockPrice('RELIANCE'),
                    api.getStockPrice('TCS')
                ]);
                this.stocks = [reliance, tcs].filter(Boolean);
            } catch (error) {
                console.error('Error loading stock data:', error);
            } finally {
                this.loading = false;
            }
        }
    }
};
```

## Mobile App Examples

### React Native

```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, RefreshControl } from 'react-native';

const API_BASE_URL = 'http://localhost:8000';

const StockList = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [refreshing, setRefreshing] = useState(false);

    const fetchStocks = async () => {
        setLoading(true);
        try {
            const stockSymbols = ['RELIANCE', 'TCS', 'HDFC', 'ICICIBANK'];
            const promises = stockSymbols.map(symbol =>
                fetch(`${API_BASE_URL}/stocks/IND/${symbol}`)
                    .then(res => res.json())
            );

            const results = await Promise.all(promises);
            setStocks(results.filter(stock => stock.symbol));
        } catch (error) {
            console.error('Error fetching stocks:', error);
        } finally {
            setLoading(false);
        }
    };

    const onRefresh = async () => {
        setRefreshing(true);
        await fetchStocks();
        setRefreshing(false);
    };

    useEffect(() => {
        fetchStocks();
    }, []);

    const renderStock = ({ item }) => (
        <View style={styles.stockCard}>
            <Text style={styles.symbol}>{item.symbol}</Text>
            <Text style={styles.price}>₹{item.lastPrice}</Text>
            <Text style={[
                styles.change,
                item.pChange >= 0 ? styles.positive : styles.negative
            ]}>
                {item.pChange}% ({item.change >= 0 ? '+' : ''}{item.change})
            </Text>
        </View>
    );

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Indian Stocks</Text>
            <FlatList
                data={stocks}
                renderItem={renderStock}
                keyExtractor={item => item.symbol}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
                ListEmptyComponent={
                    <Text style={styles.empty}>No stocks loaded</Text>
                }
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#f5f5f5',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center',
    },
    stockCard: {
        backgroundColor: 'white',
        padding: 15,
        marginVertical: 5,
        borderRadius: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    symbol: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    price: {
        fontSize: 16,
        color: '#666',
        marginTop: 5,
    },
    change: {
        fontSize: 14,
        marginTop: 5,
    },
    positive: {
        color: '#4CAF50',
    },
    negative: {
        color: '#F44336',
    },
    empty: {
        textAlign: 'center',
        fontSize: 16,
        color: '#666',
        marginTop: 50,
    },
});

export default StockList;
```

### Flutter (Dart)

```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
    runApp(MyApp());
}

class MyApp extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return MaterialApp(
            title: 'FastStockAPI Demo',
            theme: ThemeData(primarySwatch: Colors.blue),
            home: StockDashboard(),
        );
    }
}

class StockDashboard extends StatefulWidget {
    @override
    _StockDashboardState createState() => _StockDashboardState();
}

class _StockDashboardState extends State<StockDashboard> {
    List<dynamic> stocks = [];
    bool loading = false;

    @override
    void initState() {
        super.initState();
        fetchStocks();
    }

    Future<void> fetchStocks() async {
        setState(() => loading = true);

        try {
            final stockSymbols = ['RELIANCE', 'TCS', 'HDFC'];
            final futures = stockSymbols.map((symbol) =>
                http.get(Uri.parse('http://localhost:8000/stocks/IND/$symbol'))
            );

            final responses = await Future.wait(futures);
            final results = responses
                .where((response) => response.statusCode == 200)
                .map((response) => json.decode(response.body))
                .toList();

            setState(() => stocks = results);
        } catch (e) {
            print('Error fetching stocks: $e');
        } finally {
            setState(() => loading = false);
        }
    }

    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(
                title: Text('Stock Dashboard'),
                actions: [
                    IconButton(
                        icon: Icon(Icons.refresh),
                        onPressed: fetchStocks,
                    )
                ],
            ),
            body: loading
                ? Center(child: CircularProgressIndicator())
                : ListView.builder(
                    itemCount: stocks.length,
                    itemBuilder: (context, index) {
                        final stock = stocks[index];
                        final isPositive = stock['pChange'] >= 0;

                        return Card(
                            margin: EdgeInsets.all(8),
                            child: ListTile(
                                title: Text(
                                    stock['symbol'],
                                    style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                subtitle: Text(stock['companyName']),
                                trailing: Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                        Text(
                                            '₹${stock['lastPrice']}',
                                            style: TextStyle(
                                                fontSize: 18,
                                                fontWeight: FontWeight.bold,
                                            ),
                                        ),
                                        Text(
                                            '${stock['pChange']}% (${stock['change'] >= 0 ? '+' : ''}${stock['change']})',
                                            style: TextStyle(
                                                color: isPositive ? Colors.green : Colors.red,
                                                fontWeight: FontWeight.w500,
                                            ),
                                        ),
                                    ],
                                ),
                            ),
                        );
                    },
                ),
        );
    }
}
```

## Desktop Application Examples

### Electron (JavaScript)

```javascript
// main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const axios = require('axios');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
    });

    mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

// API handlers
ipcMain.handle('get-stock-price', async (event, symbol, market = 'IND') => {
    try {
        const response = await axios.get(`http://localhost:8000/stocks/${market}/${symbol}`);
        return response.data;
    } catch (error) {
        throw new Error(`Failed to fetch ${symbol}: ${error.message}`);
    }
});

ipcMain.handle('get-portfolio-value', async (event, stocks) => {
    try {
        const promises = stocks.map(stock =>
            axios.get(`http://localhost:8000/stocks/${stock.market}/${stock.symbol}`)
        );

        const responses = await Promise.all(promises);
        const portfolio = responses.map((response, index) => ({
            ...stocks[index],
            ...response.data,
            value: response.data.lastPrice * stocks[index].quantity
        }));

        const totalValue = portfolio.reduce((sum, stock) => sum + stock.value, 0);

        return { portfolio, totalValue };
    } catch (error) {
        throw new Error(`Failed to fetch portfolio: ${error.message}`);
    }
});
```

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>FastStockAPI Desktop</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .stock-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .positive { color: green; }
        .negative { color: red; }
        .portfolio-summary { background: #f0f0f0; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Stock Portfolio Tracker</h1>

    <div class="portfolio-summary">
        <h2>Portfolio Summary</h2>
        <p id="total-value">Loading...</p>
    </div>

    <div id="stocks-container">
        <!-- Stock cards will be inserted here -->
    </div>

    <script>
        const { ipcRenderer } = require('electron');

        // Sample portfolio
        const portfolio = [
            { symbol: 'RELIANCE', quantity: 100, market: 'IND' },
            { symbol: 'TCS', quantity: 50, market: 'IND' },
            { symbol: 'AAPL', quantity: 10, market: 'US' }
        ];

        async function loadPortfolio() {
            try {
                const result = await ipcRenderer.invoke('get-portfolio-value', portfolio);

                // Update total value
                document.getElementById('total-value').textContent =
                    `Total Value: ₹${result.totalValue.toLocaleString()}`;

                // Update stock cards
                const container = document.getElementById('stocks-container');
                container.innerHTML = result.portfolio.map(stock => `
                    <div class="stock-card">
                        <h3>${stock.symbol}</h3>
                        <p>Quantity: ${stock.quantity}</p>
                        <p>Price: ₹${stock.lastPrice}</p>
                        <p class="${stock.pChange >= 0 ? 'positive' : 'negative'}">
                            Change: ${stock.pChange}% (₹${stock.change})
                        </p>
                        <p>Value: ₹${stock.value.toLocaleString()}</p>
                    </div>
                `).join('');

            } catch (error) {
                console.error('Error loading portfolio:', error);
                document.getElementById('total-value').textContent = 'Error loading portfolio';
            }
        }

        // Load portfolio on startup
        loadPortfolio();

        // Refresh every 30 seconds
        setInterval(loadPortfolio, 30000);
    </script>
</body>
</html>
```

## Advanced Integration Patterns

### Webhook Integration

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

FASTSTOCK_API_URL = "http://localhost:8000"

@app.route('/webhook/stock-alert', methods=['POST'])
def stock_alert_webhook():
    """Handle stock price alerts"""
    data = request.json

    # Extract alert data
    symbol = data.get('symbol')
    threshold = data.get('threshold')
    condition = data.get('condition')  # 'above' or 'below'

    # Get current price
    response = requests.get(f"{FASTSTOCK_API_URL}/stocks/IND/{symbol}")
    current_price = response.json()['lastPrice']

    # Check condition
    if condition == 'above' and current_price > threshold:
        send_alert(f"{symbol} is above ₹{threshold}: ₹{current_price}")
    elif condition == 'below' and current_price < threshold:
        send_alert(f"{symbol} is below ₹{threshold}: ₹{current_price}")

    return jsonify({"status": "processed"})

def send_alert(message):
    """Send alert notification"""
    print(f" ALERT: {message}")
    # Implement your notification logic here
    # (email, SMS, push notification, etc.)

if __name__ == '__main__':
    app.run(port=5000)
```

### Database Integration

```python
import sqlite3
from datetime import datetime
import requests

class StockDatabase:
    def __init__(self, db_path='stocks.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    symbol TEXT PRIMARY KEY,
                    name TEXT,
                    price REAL,
                    change REAL,
                    change_percent REAL,
                    last_updated TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT,
                    price REAL,
                    timestamp TEXT,
                    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
                )
            ''')

    def update_stock_price(self, symbol):
        """Update stock price in database"""
        # Get current price from API
        response = requests.get(f"http://localhost:8000/stocks/IND/{symbol}")
        data = response.json()

        with sqlite3.connect(self.db_path) as conn:
            # Update current price
            conn.execute('''
                INSERT OR REPLACE INTO stocks
                (symbol, name, price, change, change_percent, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['symbol'],
                data['companyName'],
                data['lastPrice'],
                data['change'],
                data['pChange'],
                datetime.now().isoformat()
            ))

            # Add to price history
            conn.execute('''
                INSERT INTO price_history (symbol, price, timestamp)
                VALUES (?, ?, ?)
            ''', (symbol, data['lastPrice'], datetime.now().isoformat()))

    def get_stock_history(self, symbol, days=30):
        """Get price history for a stock"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT price, timestamp
                FROM price_history
                WHERE symbol = ?
                AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(days), (symbol,))

            return cursor.fetchall()

# Usage
db = StockDatabase()

# Update stock prices
db.update_stock_price('RELIANCE')
db.update_stock_price('TCS')

# Get price history
history = db.get_stock_history('RELIANCE', days=7)
for price, timestamp in history:
    print(f"RELIANCE: ₹{price} at {timestamp}")
```

These examples demonstrate how to integrate FastStockAPI into various applications and use cases. The API is designed to be flexible and can be adapted to different programming languages and frameworks. Remember to handle errors appropriately and implement rate limiting in production applications.

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
