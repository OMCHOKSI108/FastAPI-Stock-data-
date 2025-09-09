#!/usr/bin/env python3
"""
Test script to verify the fixes for the deployed FastAPI application.
This script tests the crypto API and market endpoints.
"""

import requests
import json
import time

# Production URL
BASE_URL = "https://fastapi-stock-data.onrender.com"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_crypto_price():
    """Test crypto price endpoint"""
    print("\n🪙 Testing crypto price endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/crypto/BTCUSDT")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ BTC Price: ${data.get('price', 'N/A')}")
            return True
        else:
            print(f"❌ Crypto price failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Crypto price error: {e}")
        return False

def test_crypto_stats():
    """Test crypto stats endpoint"""
    print("\n📊 Testing crypto stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/crypto-stats/BTCUSDT")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ BTC Stats - Price: ${data.get('last_price', 'N/A')}, Change: {data.get('price_change_percent', 'N/A')}%")
            return True
        else:
            print(f"❌ Crypto stats failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Crypto stats error: {e}")
        return False

def test_crypto_multiple():
    """Test multiple crypto prices endpoint"""
    print("\n📈 Testing multiple crypto prices...")
    try:
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        response = requests.get(f"{BASE_URL}/crypto-multiple?symbols={','.join(symbols)}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Multiple prices - Found {data.get('symbols_found', 0)} symbols")
            return True
        else:
            print(f"❌ Multiple crypto prices failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Multiple crypto prices error: {e}")
        return False

def test_crypto_historical():
    """Test crypto historical data endpoint"""
    print("\n📊 Testing crypto historical data...")
    try:
        response = requests.get(f"{BASE_URL}/crypto-historical/BTCUSDT?interval=1d&limit=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Historical data - {len(data.get('data', []))} data points")
            return True
        else:
            print(f"❌ Crypto historical failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Crypto historical error: {e}")
        return False

def test_market_index():
    """Test market index price endpoint"""
    print("\n🏛️ Testing market index endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/market/price/index/NIFTY")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ NIFTY Index - Price: {data.get('lastPrice', 'N/A')}")
            return True
        else:
            print(f"❌ Market index failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Market index error: {e}")
        return False

def test_stock_price():
    """Test stock price endpoint"""
    print("\n📈 Testing stock price endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/market/price/stock/RELIANCE.NS")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stock Price - {data.get('companyName', 'N/A')}: ₹{data.get('lastPrice', 'N/A')}")
            return True
        else:
            print(f"❌ Stock price failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Stock price error: {e}")
        return False

def test_historical_stock():
    """Test historical stock data endpoint"""
    print("\n📊 Testing historical stock data...")
    try:
        response = requests.get(f"{BASE_URL}/historical/RELIANCE.NS?period=5d&interval=1d")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Historical stock data - {len(data)} data points")
            return True
        else:
            print(f"❌ Historical stock failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Historical stock error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing FastAPI Stock Data API")
    print("=" * 50)

    tests = [
        test_health,
        test_crypto_price,
        test_crypto_stats,
        test_crypto_multiple,
        test_crypto_historical,
        test_market_index,
        test_stock_price,
        test_historical_stock
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Be nice to the API

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
