# FastAPI Stock & Crypto Data API

Welcome to the **FastAPI Stock & Crypto Data API** documentation! This API provides comprehensive financial data including stock prices, cryptocurrency prices, market indices, and advanced analytics.

## 🚀 Features

- **Real-time Stock Data**: NSE stock prices and historical data
- **Cryptocurrency Data**: Live crypto prices, stats, and historical data from Binance
- **Market Indices**: NIFTY, BANKNIFTY, and other Indian market indices
- **Advanced Analytics**: PCR, Open Interest, Max Pain calculations
- **Options Data**: Expiries, option chains, and analytics
- **RESTful API**: FastAPI-powered with automatic OpenAPI documentation

## 📊 Quick Start

### Health Check
```bash
curl https://fastapi-stock-data.onrender.com/health
```

### Get Stock Price
```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=RELIANCE"
```

### Get Crypto Price
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT"
```

### Get Multiple Crypto Prices
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-multiple?symbols=BTCUSDT,ETHUSDT,ADAUSDT"
```

## 📚 Documentation Sections

- **[Getting Started](getting-started.md)**: Installation and setup
- **[API Reference](api/)**: Complete endpoint documentation
- **[Symbol Reference](symbols/)**: Available symbols and tickers
- **[Examples](examples.md)**: Code examples in Python, cURL, and JavaScript
- **[Deployment](deployment.md)**: Production deployment guide

## 🔗 Live Demo

Try our interactive demo: **[Crypto API Demo](crypto_demo.html)**

## 📈 Supported Markets

### Indian Stock Market (NSE)
- 200+ NSE stocks with `.NS` suffix
- Major indices: NIFTY, BANKNIFTY
- Options data and analytics

### Cryptocurrency (Binance)
- 30+ major cryptocurrencies
- Real-time prices and 24h statistics
- Historical data with multiple intervals

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Data Sources**: NSE (nsepython), Binance API, Yahoo Finance
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Deployment**: Render.com
- **Documentation**: MkDocs with Material theme

## 📞 Support

- **GitHub**: [OMCHOKSI108/FastAPI-Stock-data-](https://github.com/OMCHOKSI108/FastAPI-Stock-data-)
- **API Base URL**: `https://fastapi-stock-data.onrender.com`
- **Interactive Docs**: [API Documentation](https://fastapi-stock-data.onrender.com/docs)

---

!!! info "Production Deployment"
    This API is deployed on Render.com and available 24/7. Check the [deployment guide](deployment.md) for details.
