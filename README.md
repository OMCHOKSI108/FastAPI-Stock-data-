# FastAPI Stock Data API

This is a FastAPI-based microservice for fetching real-time Indian stock market data with options analytics. It provides RESTful endpoints to access stock quotes, historical data, market indices, options chains, and comprehensive analytics using NSE data and various providers.

## Features

The API includes:
- **Stock & Index Data**: Real-time quotes for NSE stocks and indices
- **Options Analytics**: PCR, Max Pain, Top OI strikes, complete options chains
- **Background Processing**: Asynchronous data fetching with job tracking
- **Authentication**: JWT-based auth system (stub implementation)
- **Caching**: In-memory caching for performance
- **Multiple Providers**: Yahoo Finance, Finnhub, Alpha Vantage, Binance for crypto
- **Database Models**: SQLAlchemy models for snapshots, alerts, and jobs
- **Comprehensive Testing**: Unit tests with mocked external dependencies

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd FastAPI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Server will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_market.py

# Run with coverage
pytest --cov=app --cov-report=html
```

## API Endpoints

### Market Data
- `GET /api/v1/market/price/index` - Get index price (NIFTY, BANKNIFTY)
- `GET /api/v1/market/price/stock` - Get stock price (RELIANCE, INFY, etc.)

### Options Data
- `GET /api/v1/options/expiries` - Get available expiry dates
- `POST /api/v1/options/fetch` - Fetch options for nearest expiry (background)
- `POST /api/v1/options/fetch/expiry` - Fetch options for specific expiry (background)
- `GET /api/v1/options/latest` - Get latest options snapshot

### Analytics
- `GET /api/v1/analytics/pcr` - Put-Call Ratio analysis
- `GET /api/v1/analytics/top-oi` - Top Open Interest strikes
- `GET /api/v1/analytics/max-pain` - Maximum Pain calculation
- `GET /api/v1/analytics/summary` - Combined analytics summary

### Historical Data (Enhanced)
- `GET /historical/{symbol}?period=1d&interval=1d&start=2025-01-01&end=2025-09-09`

**Supported Periods:** 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
**Supported Intervals:** 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

**Examples:**
- `/historical/AAPL?period=1mo&interval=1d` - 1 month of daily data
- `/historical/AAPL?period=1y&interval=1wk` - 1 year of weekly data
- `/historical/AAPL?period=5d&interval=1h` - 5 days of hourly data
- `/historical/AAPL?start=2025-01-01&end=2025-09-09&interval=1d` - Custom date range

### Legacy Endpoints
- `GET /health` - Health check
- `GET /quotes` - All cached quotes
- `GET /quote/{symbol}` - Individual stock quote
- `GET /crypto/{symbol}` - Cryptocurrency price

## Configuration

### Environment Variables

```bash
# Data provider (YFINANCE, FINNHUB, ALPHAVANTAGE)
PROVIDER=YFINANCE

# Background fetch interval in seconds
FETCH_INTERVAL=60

# API Keys for providers
FINNHUB_API_KEY=your_key_here
ALPHAVANTAGE_API_KEY=your_key_here

# Database (for production)
DATABASE_URL=sqlite:///./app.db
```

### Authentication

The API uses JWT-based authentication. For development, use the header:
```
Authorization: Bearer test-token
```

TODO: Implement proper JWT token generation and validation for production.

## Project Structure

```
app/
├── main.py              # FastAPI application and legacy endpoints
├── auth.py              # Authentication dependencies
├── cache.py             # In-memory caching
├── schemas.py           # Pydantic models
├── fetcher.py           # Background data fetching
├── providers/           # Data provider modules
├── routes/              # New modular routes
│   ├── market.py        # Market data endpoints
│   ├── options.py       # Options endpoint
│   ├── analytics.py     # Analytics endpoints
├── models/              # Database models
│   └── models.py        # SQLAlchemy models
tests/                   # Unit tests
├── test_market.py       # Market endpoint tests
├── test_options.py      # Options endpoint tests
data_gather_stocks.py    # NSE data fetching utilities
```

## Database Models

The project includes SQLAlchemy models for:
- **Snapshots**: Store options chain data
- **Alerts**: User alert configurations
- **Jobs**: Background job tracking

TODO: Set up database connection and migrations for production use.

## Deployment

### Docker

```bash
# Build the image
docker build -t fastapi-stock-api .

# Run the container
docker run -p 8000:8000 fastapi-stock-api
```

### Render Deployment

The project includes `render.yaml` for easy deployment to Render. Push to GitHub and connect to Render web service.

## Development Notes

### TODO Items for Production
- Implement proper JWT authentication with token refresh
- Add database connection and migrations
- Implement rate limiting for NSE API calls
- Add retry logic for failed API requests
- Set up proper logging and monitoring
- Add input validation and sanitization
- Implement caching layer (Redis)
- Add API versioning strategy
- Set up CI/CD pipeline

### Testing Strategy
- Unit tests mock external NSE API calls
- Integration tests can be added for full API testing
- Use `pytest` with `pytest-asyncio` for async endpoint testing

## License

This project is open source and available under the MIT License.