#!/usr/bin/env python3
"""
Test FastAPI Backend
"""

import requests
import json
import asyncio

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"🏥 Health Check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_vn_symbols():
    """Test VN symbols endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/vn-symbols")
        print(f"📋 VN Symbols: {response.status_code}")
        if response.status_code == 200:
            symbols = response.json()
            print(f"Found {len(symbols)} symbols")
            for symbol in symbols[:3]:
                print(f"  - {symbol['symbol']}: {symbol['name']}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ VN symbols test failed: {e}")
        return False

def test_vn_stock():
    """Test VN stock data endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/vn-stock/VCB")
        print(f"📈 VN Stock (VCB): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Price: {data['price']:,} VND")
            print(f"  Change: {data['change_percent']:+.2f}%")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ VN stock test failed: {e}")
        return False

def test_query():
    """Test query endpoint"""
    try:
        payload = {
            "query": "Phân tích VCB có nên mua không?",
            "symbol": "VCB"
        }
        response = requests.post(f"{BASE_URL}/query", json=payload)
        print(f"💬 Query Test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Expert advice length: {len(data.get('expert_advice', ''))}")
            print(f"  Recommendations: {len(data.get('recommendations', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def test_analyze():
    """Test analyze endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/analyze?symbol=VCB")
        print(f"🔍 Analyze Test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Market type: {data.get('market_type')}")
            print(f"  Has VN stock data: {'vn_stock_data' in data}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Analyze test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing AI Trading Team Vietnam API")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("VN Symbols", test_vn_symbols), 
        ("VN Stock Data", test_vn_stock),
        ("Query Endpoint", test_query),
        ("Analyze Endpoint", test_analyze)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print(f"{'✅ PASS' if result else '❌ FAIL'}")
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the API server.")

if __name__ == "__main__":
    main()