import pytest
from unittest.mock import patch, MagicMock
import os
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestOptionsEndpoints:
    """Test cases for options endpoints"""

    @patch('app.routes.options.get_available_expiries')
    def test_get_expiries_success(self, mock_get_expiries):
        """Test successful expiries fetch"""
        mock_get_expiries.return_value = ['11-Sep-2025', '18-Sep-2025', '25-Sep-2025']

        response = client.get("/api/v1/options/expiries?index=NIFTY")

        assert response.status_code == 200
        data = response.json()
        assert data['index'] == 'NIFTY'
        assert len(data['expiries']) == 3
        assert '11-Sep-2025' in data['expiries']

    @patch('app.routes.options.get_available_expiries')
    def test_get_expiries_not_found(self, mock_get_expiries):
        """Test expiries fetch with no data"""
        mock_get_expiries.return_value = []

        response = client.get("/api/v1/options/expiries?index=INVALID")

        assert response.status_code == 404
        assert 'No expiries found' in response.json()['detail']

    def test_fetch_options_background_task(self):
        """Test options fetch endpoint creates background task"""
        request_data = {
            "index": "NIFTY",
            "num_strikes": 50
        }

        # Mock auth by patching the dependency
        with patch('app.routes.options.get_current_user'):
            response = client.post(
                "/api/v1/options/fetch",
                json=request_data,
                headers={"Authorization": "Bearer test-token"}
            )

        assert response.status_code == 200
        data = response.json()
        assert 'job_id' in data
        assert data['status'] == 'accepted'
        assert 'queued successfully' in data['message']

    def test_fetch_options_expiry_background_task(self):
        """Test options fetch for specific expiry creates background task"""
        request_data = {
            "index": "NIFTY",
            "expiry": "11-Sep-2025",
            "num_strikes": 30
        }

        # Mock auth by patching the dependency
        with patch('app.routes.options.get_current_user'):
            response = client.post(
                "/api/v1/options/fetch/expiry",
                json=request_data,
                headers={"Authorization": "Bearer test-token"}
            )

        assert response.status_code == 200
        data = response.json()
        assert 'job_id' in data
        assert data['status'] == 'accepted'
        assert 'queued successfully' in data['message']

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('pandas.read_csv')
    def test_get_latest_options_success(self, mock_read_csv, mock_listdir, mock_exists):
        """Test successful latest options fetch"""
        # Mock file system
        mock_exists.return_value = True
        mock_listdir.return_value = ['nifty_option_chain_11-Sep-2025_2025-09-09_10-30-00.csv']

        # Mock DataFrame
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {
                'strikePrice': 18800,
                'expiryDate': '11-Sep-2025',
                'CE_openInterest': 1000,
                'CE_lastPrice': 150.5,
                'PE_openInterest': 800,
                'PE_lastPrice': 120.3
            })
        ]
        mock_read_csv.return_value = mock_df

        # Mock auth
        with patch('app.routes.options.get_current_user'):
            response = client.get(
                "/api/v1/options/latest?index=NIFTY",
                headers={"Authorization": "Bearer test-token"}
            )

        assert response.status_code == 200
        data = response.json()
        assert 'meta' in data
        assert 'rows' in data
        assert data['meta']['index'] == 'NIFTY'

    @patch('os.path.exists')
    def test_get_latest_options_no_data(self, mock_exists):
        """Test latest options fetch with no data"""
        mock_exists.return_value = False

        # Mock auth
        with patch('app.routes.options.get_current_user'):
            response = client.get(
                "/api/v1/options/latest?index=NIFTY",
                headers={"Authorization": "Bearer test-token"}
            )

        assert response.status_code == 404
        assert 'No option data available' in response.json()['detail']
