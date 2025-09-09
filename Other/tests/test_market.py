import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestMarketEndpoints:
    """Test cases for market endpoints"""

    @patch('app.routes.market.fetch_index_price')
    def test_get_index_price_success(self, mock_fetch):
        """Test successful index price fetch"""
        mock_fetch.return_value = {
            'symbol': 'NIFTY',
            'lastPrice': 18876.25,
            'pChange': 0.45,
            'change': 85.5,
            'timestamp': '2025-09-09 10:30:00'
        }

        response = client.get("/api/v1/market/price/index?index=NIFTY")

        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'NIFTY'
        assert data['lastPrice'] == 18876.25
        assert data['pChange'] == 0.45

    @patch('app.routes.market.fetch_index_price')
    def test_get_index_price_not_found(self, mock_fetch):
        """Test index price fetch with error"""
        mock_fetch.return_value = {'error': 'Index not found'}

        response = client.get("/api/v1/market/price/index?index=INVALID")

        assert response.status_code == 404
        assert 'error' in response.json()['detail']

    @patch('app.routes.market.fetch_stock_price')
    def test_get_stock_price_success(self, mock_fetch):
        """Test successful stock price fetch"""
        mock_fetch.return_value = {
            'symbol': 'RELIANCE',
            'companyName': 'Reliance Industries Ltd.',
            'lastPrice': 2500.50,
            'pChange': 1.25,
            'change': 31.0,
            'timestamp': '2025-09-09 10:30:00'
        }

        response = client.get("/api/v1/market/price/stock?symbol=RELIANCE")

        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'RELIANCE'
        assert data['companyName'] == 'Reliance Industries Ltd.'
        assert data['lastPrice'] == 2500.50

    @patch('app.routes.market.fetch_stock_price')
    def test_get_stock_price_not_found(self, mock_fetch):
        """Test stock price fetch with error"""
        mock_fetch.return_value = {'error': 'Stock not found'}

        response = client.get("/api/v1/market/price/stock?symbol=INVALID")

        assert response.status_code == 404
        assert 'error' in response.json()['detail']

class TestHistoricalEndpoint:
    """Test cases for historical data endpoint"""

    @patch('app.main.PROVIDER_MAP')
    def test_get_historical_success(self, mock_provider_map):
        """Test successful historical data fetch"""
        # Mock the provider
        mock_provider = MagicMock()
        mock_provider_map.get.return_value = mock_provider
        mock_provider.get_historical = AsyncMock(return_value=[
            {
                "timestamp": "2025-09-09T10:00:00",
                "open": 150.0,
                "high": 155.0,
                "low": 149.0,
                "close": 152.5,
                "volume": 1000000
            }
        ])

        response = client.get("/historical/AAPL?period=1mo&interval=1d")

        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'AAPL'
        assert data['period'] == '1mo'
        assert data['interval'] == '1d'
        assert len(data['data']) == 1

    def test_get_historical_invalid_period(self):
        """Test historical data with invalid period"""
        response = client.get("/historical/AAPL?period=invalid")

        assert response.status_code == 400
        assert 'Invalid period' in response.json()['detail']

    def test_get_historical_invalid_interval(self):
        """Test historical data with invalid interval"""
        response = client.get("/historical/AAPL?interval=invalid")

        assert response.status_code == 400
        assert 'Invalid interval' in response.json()['detail']

    @patch('app.main.PROVIDER_MAP')
    def test_get_historical_no_data(self, mock_provider_map):
        """Test historical data fetch with no data returned"""
        mock_provider = MagicMock()
        mock_provider_map.get.return_value = mock_provider
        mock_provider.get_historical = AsyncMock(return_value=None)

        response = client.get("/historical/AAPL")

        assert response.status_code == 404
        assert 'No historical data found' in response.json()['detail']

    @patch('app.main.PROVIDER_MAP')
    def test_get_historical_provider_no_support(self, mock_provider_map):
        """Test historical data with provider that doesn't support it"""
        mock_provider = MagicMock()
        mock_provider_map.get.return_value = mock_provider
        # Remove get_historical method to simulate no support
        del mock_provider.get_historical

        response = client.get("/historical/AAPL")

        assert response.status_code == 501
        assert 'not supported by current provider' in response.json()['detail']
