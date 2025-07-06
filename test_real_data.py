# test_real_data.py
"""
Test Real Data API Calls
Kiểm tra khả năng gọi API dữ liệu thật
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_vnstock_real_data():
    """Test VNStock real data calls"""
    print("Testing VNStock Real Data API...")
    
    try:
        from src.data.vnstock_real_data import VNStockRealData
        
        vn_data = VNStockRealData()
        
        # Test 1: Stock price data
        print("\n1. Testing stock price data...")
        price_data = vn_data.get_stock_price_data('VCB', days=5)
        if price_data:
            print(f"OK VCB Price: {price_data['current_price']:,.0f} VND")
            print(f"   Change: {price_data['change']:+,.0f} ({price_data['change_percent']:+.2f}%)")
            print(f"   Volume: {price_data['volume']:,}")
        else:
            print("No price data")
        
        # Test 2: Company info
        print("\n2. Testing company info...")
        company_info = vn_data.get_company_info('VCB')
        if company_info:
            print(f"OK Company: {company_info['company_name']}")
            print(f"   Sector: {company_info['sector']}")
        else:
            print("No company info")
        
        # Test 3: VN-Index
        print("\n3. Testing VN-Index...")
        vnindex = vn_data.get_vnindex_data()
        if vnindex:
            print(f"OK VN-Index: {vnindex['value']:,.2f}")
            print(f"   Change: {vnindex['change']:+,.2f} ({vnindex['change_percent']:+.2f}%)")
        else:
            print("No VN-Index data")
        
        return True
    except Exception as e:
        print(f"VNStock error: {e}")
        return False

async def test_vn_stock_api():
    """Test VN Stock API wrapper"""
    print("\nTesting VN Stock API Wrapper...")
    
    try:
        from src.data.vn_stock_api import VNStockAPI
        
        api = VNStockAPI()
        
        # Test stock data
        print("\n1. Testing VN Stock API...")
        stock_data = await api.get_stock_data('VCB')
        if stock_data:
            print(f"OK VCB via API: {stock_data.price:,.0f} VND")
            print(f"   Market Cap: {stock_data.market_cap:,.0f}B VND")
            print(f"   P/E: {stock_data.pe_ratio}, P/B: {stock_data.pb_ratio}")
        else:
            print("No API data")
        
        # Test market overview
        print("\n2. Testing market overview...")
        market = await api.get_market_overview()
        if market and market.get('vn_index'):
            vn_index = market['vn_index']
            print(f"OK Market Overview - VN-Index: {vn_index['value']:,.2f}")
        else:
            print("No market data")
        
        return True
    except Exception as e:
        print(f"API error: {e}")
        return False

async def test_main_agent_real_data():
    """Test MainAgent with real data"""
    print("\nTesting MainAgent Real Data...")
    
    try:
        from main_agent import MainAgent
        from src.data.vn_stock_api import VNStockAPI
        
        vn_api = VNStockAPI()
        main_agent = MainAgent(vn_api)
        
        # Test comprehensive analysis
        print("\n1. Testing comprehensive analysis...")
        result = await main_agent.analyze_stock('VCB')
        
        if result and not result.get('error'):
            print("OK MainAgent analysis successful")
            
            # Check VN stock data
            if result.get('vn_stock_data'):
                stock_data = result['vn_stock_data']
                if hasattr(stock_data, 'price'):
                    print(f"   VCB Price: {stock_data.price:,.0f} VND")
                else:
                    print("   Using mock data")
            
            # Check predictions
            if result.get('price_prediction'):
                pred = result['price_prediction']
                print(f"   Prediction: {pred.get('trend', 'N/A')}")
            
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        
        return True
    except Exception as e:
        print(f"MainAgent error: {e}")
        return False

def test_yfinance_international():
    """Test international data via yfinance"""
    print("\nTesting International Data (yfinance)...")
    
    try:
        import yfinance as yf
        
        # Test US stock
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            print(f"OK AAPL Price: ${current_price:.2f}")
            print(f"   Market Cap: ${info.get('marketCap', 0):,}")
        else:
            print("No yfinance data")
        
        return True
    except Exception as e:
        print(f"yfinance error: {e}")
        return False

async def run_real_data_tests():
    """Run all real data tests"""
    print("REAL DATA API TEST")
    print("=" * 40)
    
    tests = [
        ("VNStock Real Data", test_vnstock_real_data),
        ("VN Stock API", test_vn_stock_api), 
        ("MainAgent Real Data", test_main_agent_real_data),
        ("International Data", test_yfinance_international),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"{test_name} failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("REAL DATA TEST SUMMARY")
    print("=" * 40)
    
    for test_name, result in results.items():
        status = "OK WORKING" if result else "FAILED"
        print(f"{test_name:<20}: {status}")
    
    working = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\nReal Data APIs: {working}/{total} working")
    
    if working > 0:
        print("SUCCESS: Your system CAN call real data APIs!")
    else:
        print("WARNING: No real data APIs working - using mock data")

if __name__ == "__main__":
    asyncio.run(run_real_data_tests())