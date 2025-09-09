import pytest
from unittest.mock import patch, MagicMock
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
