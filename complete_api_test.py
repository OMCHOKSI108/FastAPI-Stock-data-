#!/usr/bin/env python3
"""
Complete FastStockAPI Test Suite
Tests ALL endpoints with proper authentication
"""

import requests
import json
import time
from typing import Dict, List, Optional

# Test configuration
BASE_URL = "http://localhost:8000"
API_KEYS = {
    "full_access": "demo-api-key-123",
    "read_only": "test-key-456", 
    "invalid": "invalid-key-999"
}

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def test_endpoint(self, method: str, endpoint: str, api_key: Optional[str] = None, 
                     data: Optional[dict] = None, params: Optional[dict] = None,
                     description: str = "", expected_status: int = 200):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if api_key:
            headers["X-API-Key"] = api_key
            
        print(f"\n{'='*80}")
        print(f"🧪 Testing: {description}")
        print(f"📍 {method.upper()} {url}")
        print(f"🔑 API Key: {api_key or 'None'}")
        print(f"📊 Expected Status: {expected_status}")
        print(f"{'='*80}")
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data, params=params, timeout=30)
            else:
                print(f"❌ Unsupported method: {method}")
                return
                
            print(f"📈 Status Code: {response.status_code}")
            
            # Check if status matches expectation
            status_match = response.status_code == expected_status
            
            if status_match and response.status_code == 200:
                print("✅ SUCCESS")
                try:
                    data = response.json()
                    preview = json.dumps(data, indent=2)
                    if len(preview) > 500:
                        preview = preview[:500] + "..."
                    print(f"📋 Response: {preview}")
                except:
                    print(f"📋 Response (text): {response.text[:200]}...")
            elif status_match:
                print(f"✅ EXPECTED STATUS {expected_status}")
                try:
                    error_data = response.json()
                    print(f"📋 Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Error (text): {response.text}")
            else:
                print(f"❌ UNEXPECTED STATUS (got {response.status_code}, expected {expected_status})")
                try:
                    error_data = response.json()
                    print(f"📋 Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Response (text): {response.text}")
                    
            # Store result
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'api_key': api_key,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'success': status_match
            })
            
        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST FAILED: {e}")
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'api_key': api_key,
                'expected_status': expected_status,
                'actual_status': 'ERROR',
                'success': False
            })
            
        time.sleep(1)  # Rate limiting courtesy
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print(" Starting Complete FastStockAPI Test Suite")
        print(f"🌐 Base URL: {self.base_url}")
        
        # Test 1: Health Check / Root
        print("\n" + "="*80)
        print("📊 SECTION 1: HEALTH & INFO ENDPOINTS")
        print("="*80)
        
        self.test_endpoint("GET", "/", description="Root endpoint")
        self.test_endpoint("GET", "/health", description="Health check endpoint")
        
        # Test 2: Market Data Endpoints
        print("\n" + "="*80) 
        print("📈 SECTION 2: MARKET DATA ENDPOINTS")
        print("="*80)
        
        # Quote endpoints
        self.test_endpoint("GET", "/api/v1/market/quote/YESBANK.NS", 
                          description="Get YESBANK.NS quote (no auth)", expected_status=401)
        
        self.test_endpoint("GET", "/api/v1/market/quote/YESBANK.NS", 
                          api_key=API_KEYS["full_access"],
                          description="Get YESBANK.NS quote (valid auth)")
                          
        self.test_endpoint("GET", "/api/v1/market/quote/RELIANCE.NS", 
                          api_key=API_KEYS["full_access"],
                          description="Get RELIANCE quote (NSE)")
                          
        self.test_endpoint("GET", "/api/v1/market/quote/INVALID_SYMBOL", 
                          api_key=API_KEYS["full_access"],
                          description="Invalid symbol test", expected_status=404)
        
        # Search endpoints
        self.test_endpoint("GET", "/api/v1/market/search", 
                          api_key=API_KEYS["full_access"],
                          params={"query": "Apple"},
                          description="Search for Apple")
                          
        self.test_endpoint("GET", "/api/v1/market/search", 
                          api_key=API_KEYS["full_access"],
                          params={"query": "Reliance", "exchange": "NSE"},
                          description="Search Reliance on NSE")
        
        # Historical data
        self.test_endpoint("GET", "/api/v1/market/historical/YESBANK.NS", 
                          api_key=API_KEYS["full_access"],
                          params={"period": "1mo", "interval": "1d"},
                          description="YESBANK.NS historical data")
        
        # Test 3: Options Endpoints
        print("\n" + "="*80)
        print("📊 SECTION 3: OPTIONS ENDPOINTS") 
        print("="*80)
        
        self.test_endpoint("GET", "/api/v1/options/expiries", 
                          api_key=API_KEYS["full_access"],
                          params={"index": "NIFTY"},
                          description="Get NIFTY option expiries")
                          
        self.test_endpoint("GET", "/api/v1/options/chain", 
                          api_key=API_KEYS["full_access"],
                          params={"index": "NIFTY", "expiry": "2025-09-12"},
                          description="Get NIFTY option chain")
                          
        self.test_endpoint("POST", "/api/v1/options/fetch", 
                          api_key=API_KEYS["full_access"],
                          data={"index": "NIFTY", "num_strikes": 10},
                          description="Fetch NIFTY options (background)")
        
        # Test 4: Analytics Endpoints
        print("\n" + "="*80)
        print("📊 SECTION 4: ANALYTICS ENDPOINTS")
        print("="*80)
        
        self.test_endpoint("GET", "/api/v1/analytics/volatility", 
                          api_key=API_KEYS["full_access"],
                          params={"index": "NIFTY", "expiry": "2025-09-12"},
                          description="Get volatility analysis")
                          
        self.test_endpoint("GET", "/api/v1/analytics/pcr", 
                          api_key=API_KEYS["full_access"],
                          params={"index": "NIFTY", "expiry": "2025-09-12"},
                          description="Get Put-Call Ratio")
                          
        self.test_endpoint("GET", "/api/v1/analytics/max-pain", 
                          api_key=API_KEYS["full_access"],
                          params={"index": "NIFTY", "expiry": "2025-09-12"},
                          description="Get Max Pain analysis")
        
        # Test 5: Authentication Tests
        print("\n" + "="*80)
        print("🔐 SECTION 5: AUTHENTICATION TESTS")
        print("="*80)
        
        # Test invalid API key
        self.test_endpoint("GET", "/api/v1/market/quote/YESBANK.NS", 
                          api_key=API_KEYS["invalid"],
                          description="Invalid API key test", expected_status=401)
        
        # Test read-only key on write operation
        self.test_endpoint("POST", "/api/v1/options/fetch", 
                          api_key=API_KEYS["read_only"],
                          data={"index": "NIFTY", "num_strikes": 5},
                          description="Read-only key on write operation", expected_status=403)
        
        # Test 6: Error Handling
        print("\n" + "="*80)
        print("❌ SECTION 6: ERROR HANDLING TESTS")
        print("="*80)
        
        self.test_endpoint("GET", "/api/v1/market/nonexistent", 
                          api_key=API_KEYS["full_access"],
                          description="Non-existent endpoint", expected_status=404)
                          
        self.test_endpoint("GET", "/api/v1/market/quote/", 
                          api_key=API_KEYS["full_access"],
                          description="Missing symbol parameter", expected_status=404)
        
        # Test 7: Rate Limiting (if enabled)
        print("\n" + "="*80)
        print("⏱️ SECTION 7: RATE LIMITING TESTS") 
        print("="*80)
        
        print("🔄 Testing rate limits with 5 rapid requests...")
        for i in range(5):
            self.test_endpoint("GET", "/api/v1/market/quote/YESBANK.NS", 
                              api_key=API_KEYS["full_access"],
                              description=f"Rate limit test {i+1}/5")
        
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['method']} {result['endpoint']} - {result['description']}")
                    print(f"     Expected: {result['expected_status']}, Got: {result['actual_status']}")
        
        print(f"\n🔑 CREDENTIALS USED:")
        print(f"   • Full Access: {API_KEYS['full_access']}")
        print(f"   • Read Only: {API_KEYS['read_only']}")
        print(f"   • Invalid: {API_KEYS['invalid']}")
        
        print(f"\n🌐 API BASE URL: {self.base_url}")
        print("="*80)

def main():
    """Main test runner"""
    print("🧪 FastStockAPI Complete Test Suite")
    print("Make sure your server is running on http://localhost:8000")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
    except:
        print("❌ Server is not responding! Please start your FastAPI server first.")
        print("   Run: uvicorn app.main:app --reload --port 8000")
        return
    
    # Run tests
    tester = APITester()
    tester.run_all_tests()
    tester.print_summary()

if __name__ == "__main__":
    main()
