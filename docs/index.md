# FastStockAPI - Comprehensive Financial Data API

Welcome to **FastStockAPI**, a powerful and comprehensive FastAPI-based financial data service that provides real-time and historical data for stocks, cryptocurrencies, options, indices, and forex markets.

## Features

- **Stock Data**: Indian (NSE) and US stock prices with historical data
- **Cryptocurrency**: Live crypto prices and historical data from multiple exchanges
- **Options Trading**: Complete options chain data, analytics, and historical options data
- **Market Indices**: US and BSE index data with historical trends
- **Forex Data**: Real-time forex rates and historical data
- **Advanced Analytics**: PCR, Max Pain, Open Interest analysis
- **High Performance**: Async FastAPI with automatic OpenAPI documentation
- **Production Ready**: CORS enabled, health checks, error handling

## API Endpoints Overview

### Stocks
- **Indian Stocks**: `/stocks/IND/{symbol}` - Individual NSE stock data
- **US Stocks**: `/stocks/US/{symbol}` - Individual US stock data
- **Bulk Quotes**: `/stocks/IND/quote?symbols=RELIANCE,TCS` - Multiple stocks
- **Historical Data**: `/stocks/historical/IND/{symbol}?period=1mo` - Historical prices

### Cryptocurrency
- **Price Data**: `/crypto/quote/{symbol}` - BTC, ETH, ADA, etc.
- **Historical Data**: `/crypto/historical/{symbol}?period=1d` - Historical crypto data
- **Symbol List**: `/crypto/list` - Available cryptocurrencies

### Options & Derivatives
- **Index Prices**: `/options/index-price?index=NIFTY` - NIFTY, BANKNIFTY prices
- **Available Expiries**: `/options/expiries?index=NIFTY` - Option expiries
- **Option Chains**: `/options/direct-data?index=NIFTY&expiry=160925` - Complete option data
- **Strike Data**: `/options/strike-data?index=NIFTY&strike=24000&expiry=160925` - Specific strike data
- **Historical Options**: `/options/historical/NIFTY?strike=24000&expiry=160925&option_type=CE` - Historical option prices

### Market Indices
- **US Indices**: `/stocks/index/US/{symbol}` - DJI, SPX, IXIC
- **BSE Indices**: `/stocks/index/BSE/{symbol}` - SENSEX, BSE100
- **Historical Indices**: `/stocks/index/US/{symbol}/historical?period=1mo`

### Forex
- **Exchange Rates**: `/forex/quote?from=USD&to=INR` - Currency conversion
- **Multiple Rates**: `/forex/quotes?base=USD&symbols=EUR,GBP,JPY` - Bulk forex rates
- **Historical Forex**: `/forex/historical?from=USD&to=INR&period=1mo` - Historical rates

### Analytics
- **Put-Call Ratio**: `/analytics/pcr?index=NIFTY&expiry=160925` - PCR calculation
- **Max Pain**: `/analytics/max-pain?index=NIFTY&expiry=160925` - Max pain analysis
- **Top OI**: `/analytics/top-oi?index=NIFTY&expiry=160925` - Top open interest
- **Summary**: `/analytics/summary?index=NIFTY&expiry=160925` - Complete analytics

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

### Get Stock Price
```bash
# Indian Stock
curl "http://localhost:8000/stocks/IND/RELIANCE"

# US Stock
curl "http://localhost:8000/stocks/US/AAPL"
```

### Get Crypto Price
```bash
curl "http://localhost:8000/crypto/quote/BTC"
```

### Get Option Data
```bash
# Index Price
curl "http://localhost:8000/options/index-price?index=NIFTY"

# Option Chain
curl "http://localhost:8000/options/direct-data?index=NIFTY&expiry=160925&num_strikes=10"
```

##  Documentation

- **[Getting Started](getting-started.md)**: Installation and setup guide
- **[API Reference](api/)**: Complete endpoint documentation
  - [Stock API](api/stock.md)
  - [Crypto API](api/crypto.md)
  - [Options API](api/options.md)
  - [Analytics API](api/analytics.md)
- **[Symbol Reference](symbols/)**: Available symbols and tickers
- **[Examples](examples.md)**: Code examples in Python, JavaScript, cURL
- **[Deployment](deployment.md)**: Production deployment guide

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation with live API testing.

## Supported Markets

### Indian Markets (NSE)
- **Stocks**: RELIANCE, TCS, HDFC, ICICIBANK, INFY, etc.
- **Indices**: NIFTY, BANKNIFTY, NIFTYIT, NIFTYPHARMA, etc.

### US Markets
- **Stocks**: AAPL, GOOGL, MSFT, TSLA, AMZN, etc.
- **Indices**: DJI (Dow Jones), SPX (S&P 500), IXIC (Nasdaq)

### Cryptocurrency
- **Major Coins**: BTC, ETH, ADA, SOL, DOT, etc.
- **Exchanges**: Binance, Coinbase, Kraken integration

### Forex
- **Major Pairs**: USD/INR, EUR/USD, GBP/USD, USD/JPY, etc.
- **Real-time Rates**: Updated every minute

##  Deployment

### Local Development
```bash
git clone <repository-url>
cd FastAPI
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker Deployment
```bash
docker build -t faststockapi .
docker run -p 8000:8000 faststockapi
```

### Cloud Deployment
- **Railway**: Connect GitHub repo for automatic deployment
- **Render**: Deploy from GitHub with Docker support
- **Heroku**: Traditional PaaS deployment
- **AWS/GCP/Azure**: Container orchestration with Kubernetes

## Data Sources

- **Indian Stocks**: NSE via nsepython library
- **US Stocks**: Yahoo Finance (yfinance)
- **Cryptocurrency**: Binance API and other exchanges
- **Options Data**: NSE option chains
- **Forex**: Real-time forex APIs
- **Indices**: Yahoo Finance and NSE data

## Technical Stack

- **Framework**: FastAPI (Python async web framework)
- **Data Processing**: Pandas for data manipulation
- **Caching**: Redis for performance optimization
- **Rate Limiting**: SlowAPI for request throttling
- **Documentation**: MkDocs with Material theme
- **Containerization**: Docker for easy deployment

## Performance Features

- **Async Operations**: Non-blocking I/O for high concurrency
- **Data Caching**: Redis caching for frequently requested data
- **Rate Limiting**: Prevents API abuse and ensures fair usage
- **Error Handling**: Comprehensive error responses with helpful messages
- **Health Monitoring**: Built-in health checks and metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Support

For support and questions:
- 📧 Email: support@faststockapi.com
- 💬 GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- 📖 Documentation: [Full API Docs](api/)

---

**FastStockAPI** - Your comprehensive solution for financial market data!
- 200+ NSE stocks with `.NS` suffix
- Major indices: NIFTY, BANKNIFTY
- Options data and analytics

### Cryptocurrency (Binance)
- 30+ major cryptocurrencies
- Real-time prices and 24h statistics
- Historical data with multiple intervals

## Technology Stack

- **Backend**: FastAPI (Python)
- **Data Sources**: NSE (nsepython), Binance API, Yahoo Finance
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Deployment**: Render.com
- **Documentation**: MkDocs with Material theme

## Support

- **GitHub**: [OMCHOKSI108/FastAPI-Stock-data-](https://github.com/OMCHOKSI108/FastAPI-Stock-data-)
- **API Base URL**: `https://fastapi-stock-data.onrender.com`
- **Interactive Docs**: [API Documentation](https://fastapi-stock-data.onrender.com/docs)

---

!!! info "Production Deployment"
    This API is deployed on Render.com and available 24/7. Check the [deployment guide](deployment.md) for details.
