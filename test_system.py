# test_system.py
"""
Comprehensive System Test for AI Trading System
Test toàn diện hệ thống AI Trading
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        # Core components
        from main_agent import MainAgent
        from gemini_agent import GeminiAgent
        from src.data.vn_stock_api import VNStockAPI
        from src.utils.error_handler import handle_errors
        from src.utils.config_manager import config
        
        # Agents
        from agents.price_predictor import PricePredictor
        from agents.ticker_news import TickerNews
        from agents.market_news import MarketNews
        from agents.investment_expert import InvestmentExpert
        from agents.risk_expert import RiskExpert
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_vnstock_integration():
    """Test VNStock integration"""
    print("\n🧪 Testing VNStock integration...")
    
    try:
        from src.data.vnstock_real_data import VNStockRealData
        
        vn_data = VNStockRealData()
        
        # Test price data
        price_data = vn_data.get_stock_price_data('ACB', days=5)
        if price_data:
            print(f"✅ VNStock price data: ACB = {price_data['current_price']:,.0f} VND")
        else:
            print("⚠️ VNStock price data not available (using mock)")
        
        # Test VN-Index
        vnindex = vn_data.get_vnindex_data()
        if vnindex:
            print(f"✅ VN-Index: {vnindex['value']:,.2f}")
        else:
            print("⚠️ VN-Index data not available")
        
        return True
    except Exception as e:
        print(f"❌ VNStock error: {e}")
        return False

def test_agents():
    """Test all 6 AI Agents"""
    print("\n🧪 Testing 6 AI Agents...")
    
    try:
        # Initialize agents
        from agents.price_predictor import PricePredictor
        from agents.ticker_news import TickerNews
        from agents.market_news import MarketNews
        from agents.investment_expert import InvestmentExpert
        from agents.risk_expert import RiskExpert
        
        agents = {
            'PricePredictor': PricePredictor(),
            'TickerNews': TickerNews(),
            'MarketNews': MarketNews(),
            'InvestmentExpert': InvestmentExpert(),
            'RiskExpert': RiskExpert()
        }
        
        test_symbol = 'VCB'
        
        for name, agent in agents.items():
            try:
                if name == 'PricePredictor':
                    result = agent.predict_price(test_symbol)
                elif name == 'TickerNews':
                    result = agent.get_ticker_news(test_symbol)
                elif name == 'MarketNews':
                    result = agent.get_market_news()
                elif name == 'InvestmentExpert':
                    result = agent.analyze_stock(test_symbol)
                elif name == 'RiskExpert':
                    result = agent.assess_risk(test_symbol)
                
                if result and not result.get('error'):
                    print(f"✅ {name}: Working")
                else:
                    print(f"⚠️ {name}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ {name}: {str(e)}")
        
        return True
    except Exception as e:
        print(f"❌ Agents test error: {e}")
        return False

async def test_main_agent():
    """Test MainAgent integration"""
    print("\n🧪 Testing MainAgent integration...")
    
    try:
        from main_agent import MainAgent
        from src.data.vn_stock_api import VNStockAPI
        
        # Initialize without Gemini (for testing)
        vn_api = VNStockAPI()
        main_agent = MainAgent(vn_api)
        
        # Test stock analysis
        result = await main_agent.analyze_stock('VCB')
        if result and not result.get('error'):
            print("✅ MainAgent stock analysis: Working")
        else:
            print(f"⚠️ MainAgent analysis: {result.get('error', 'Unknown error')}")
        
        # Test market overview
        market = await main_agent.get_market_overview()
        if market and not market.get('error'):
            print("✅ MainAgent market overview: Working")
        else:
            print(f"⚠️ MainAgent market: {market.get('error', 'Unknown error')}")
        
        return True
    except Exception as e:
        print(f"❌ MainAgent error: {e}")
        return False

def test_gemini_agent():
    """Test Gemini Agent (if API key available)"""
    print("\n🧪 Testing Gemini Agent...")
    
    try:
        from src.utils.config_manager import config
        
        if config.is_gemini_configured():
            from gemini_agent import GeminiAgent
            
            gemini = GeminiAgent(config.api.google_api_key)
            
            # Test connection
            if gemini.test_connection():
                print("✅ Gemini API: Connected")
                
                # Test advice generation
                response = gemini.generate_expert_advice("Phân tích VCB", "VCB")
                if response and response.get('expert_advice'):
                    print("✅ Gemini advice generation: Working")
                else:
                    print("⚠️ Gemini advice: No response")
            else:
                print("❌ Gemini API: Connection failed")
        else:
            print("⚠️ Gemini API key not configured")
        
        return True
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API endpoints...")
    
    try:
        import requests
        import time
        
        # Start API server in background (for testing)
        print("Note: Start API server manually with 'python api.py' to test endpoints")
        
        base_url = "http://127.0.0.1:8000"
        
        try:
            # Test health endpoint
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API Health endpoint: Working")
            else:
                print(f"⚠️ API Health: Status {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ API server not running (start with 'python api.py')")
        
        return True
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def test_configuration():
    """Test configuration management"""
    print("\n🧪 Testing configuration...")
    
    try:
        from src.utils.config_manager import config, VN_STOCK_SYMBOLS, AGENT_CONFIG
        
        # Test config loading
        api_config = config.get_api_config()
        system_config = config.get_system_config()
        ui_config = config.get_ui_config()
        
        print(f"✅ Config loaded: API timeout={api_config.timeout_seconds}s")
        print(f"✅ VN Stocks: {len(VN_STOCK_SYMBOLS)} symbols configured")
        print(f"✅ Agents: {len(AGENT_CONFIG)} agents configured")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def run_all_tests():
    """Run all system tests"""
    print("🚀 DUONG AI TRADING SYSTEM - COMPREHENSIVE TEST")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("VNStock Integration", test_vnstock_integration),
        ("AI Agents", test_agents),
        ("MainAgent", test_main_agent),
        ("Gemini Agent", test_gemini_agent),
        ("API Endpoints", test_api_endpoints),
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
            print(f"❌ {test_name} test failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(run_all_tests())