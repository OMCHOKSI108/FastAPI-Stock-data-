# FastAPI Stock Data API

This is a FastAPI-based microservice for fetching real-time Indian stock market data. It provides RESTful endpoints to access stock quotes, historical data, and market indices using various data providers like Yahoo Finance, Finnhub, and Alpha Vantage.

## Features

The API includes background data fetching for subscribed stocks, in-memory caching for performance, and support for multiple data providers. It offers endpoints for health checks, retrieving all quotes, individual stock quotes, on-demand fetching, subscription management, historical data retrieval, and cryptocurrency price data from Binance.

## Installation

To run locally, create a virtual environment and install dependencies from requirements.txt. Use uvicorn to start the server on localhost port 8000.

## Usage

Access the interactive API documentation at /docs. The main endpoints include /health for status checks, /quotes for all cached quotes, /quote/{symbol} for individual stocks, /fetch/{symbol} for on-demand data, /historical/{symbol} for price history, /crypto/{symbol} for cryptocurrency prices, and /crypto-historical/{symbol} for crypto price history.

## Configuration

Configure the data provider using environment variables. Set PROVIDER to YFINANCE, FINNHUB, or ALPHAVANTAGE. Adjust FETCH_INTERVAL for update frequency. Add API keys for paid providers as needed.

## Deployment

The project includes Docker support and a render.yaml file for easy deployment to Render. Push the code to GitHub and connect it to a Render web service for production hosting.

## License

This project is open source and available under the MIT License.