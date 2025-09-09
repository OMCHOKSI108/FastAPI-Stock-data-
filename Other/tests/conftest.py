import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Mock auth headers for testing"""
    return {"Authorization": "Bearer test-token"}
