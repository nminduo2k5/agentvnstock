# test_crewai_integration.py
"""
Test CrewAI Integration for Real News Collection
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_crewai_integration():
    """Test CrewAI integration"""
    print("🧪 Testing CrewAI Integration...")
    
    # Test imports
    try:
        from src.data.crewai_collector import get_crewai_collector
        print("✅ CrewAI collector import successful")
    except ImportError as e:
        print(f"❌ CrewAI import failed: {e}")
        return False
    
    # Test API keys
    gemini_key = os.getenv("GOOGLE_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    
    if not gemini_key:
        print("⚠️ No Gemini API key found in .env")
        return False
    
    if not serper_key:
        print("⚠️ No Serper API key found in .env - using fallback")
    
    # Test collector initialization
    try:
        collector = get_crewai_collector(gemini_key, serper_key)
        print(f"✅ CrewAI collector initialized - Enabled: {collector.enabled}")
        
        if not collector.enabled:
            print("⚠️ CrewAI collector disabled - check API keys")
            return False
            
    except Exception as e:
        print(f"❌ CrewAI collector initialization failed: {e}")
        return False
    
    # Test stock news collection
    try:
        print("\n📰 Testing stock news collection for VCB...")
        news_result = await collector.get_stock_news("VCB", limit=3)
        
        print(f"✅ News collection successful:")
        print(f"   - Headlines: {len(news_result.get('headlines', []))}")
        print(f"   - Sentiment: {news_result.get('sentiment', 'N/A')}")
        print(f"   - Source: {news_result.get('source', 'N/A')}")
        
        if news_result.get('headlines'):
            print(f"   - Sample headline: {news_result['headlines'][0]}")
            
    except Exception as e:
        print(f"❌ Stock news collection failed: {e}")
        return False
    
    # Test market overview
    try:
        print("\n📈 Testing market overview collection...")
        market_result = await collector.get_market_overview_news()
        
        print(f"✅ Market overview successful:")
        print(f"   - Overview length: {len(market_result.get('overview', ''))}")
        print(f"   - Key points: {len(market_result.get('key_points', []))}")
        print(f"   - Source: {market_result.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Market overview collection failed: {e}")
        return False
    
    return True

async def test_vn_api_integration():
    """Test VN API with CrewAI integration"""
    print("\n🔗 Testing VN API + CrewAI Integration...")
    
    try:
        from src.data.vn_stock_api import VNStockAPI
        
        # Initialize with API keys
        gemini_key = os.getenv("GOOGLE_API_KEY")
        serper_key = os.getenv("SERPER_API_KEY")
        
        vn_api = VNStockAPI(gemini_key, serper_key)
        print("✅ VN API with CrewAI initialized")
        
        # Test news sentiment with CrewAI
        print("\n📊 Testing enhanced news sentiment for HPG...")
        news_sentiment = await vn_api.get_news_sentiment("HPG")
        
        print(f"✅ Enhanced news sentiment:")
        print(f"   - Symbol: {news_sentiment.get('symbol', 'N/A')}")
        print(f"   - Sentiment: {news_sentiment.get('sentiment', 'N/A')}")
        print(f"   - Score: {news_sentiment.get('sentiment_score', 'N/A')}")
        print(f"   - Headlines: {len(news_sentiment.get('headlines', []))}")
        print(f"   - Source: {news_sentiment.get('source', 'N/A')}")
        
        # Test market overview with CrewAI
        print("\n🏢 Testing enhanced market overview...")
        market_overview = await vn_api.get_market_overview()
        
        print(f"✅ Enhanced market overview:")
        print(f"   - VN-Index: {market_overview.get('vn_index', {}).get('value', 'N/A')}")
        print(f"   - Market news available: {'market_news' in market_overview}")
        
        if 'market_news' in market_overview:
            market_news = market_overview['market_news']
            print(f"   - News source: {market_news.get('source', 'N/A')}")
            print(f"   - Overview length: {len(market_news.get('overview', ''))}")
        
        return True
        
    except Exception as e:
        print(f"❌ VN API + CrewAI integration failed: {e}")
        return False

async def test_main_agent_integration():
    """Test Main Agent with CrewAI"""
    print("\n🤖 Testing Main Agent + CrewAI Integration...")
    
    try:
        from main_agent import MainAgent
        from src.data.vn_stock_api import VNStockAPI
        
        # Initialize with API keys
        gemini_key = os.getenv("GOOGLE_API_KEY")
        serper_key = os.getenv("SERPER_API_KEY")
        
        vn_api = VNStockAPI(gemini_key, serper_key)
        main_agent = MainAgent(vn_api, gemini_key, serper_key)
        
        print("✅ Main Agent with CrewAI initialized")
        
        # Test comprehensive analysis
        print("\n🔍 Testing comprehensive analysis for FPT...")
        analysis_result = await main_agent.analyze_stock("FPT")
        
        print(f"✅ Comprehensive analysis:")
        print(f"   - Symbol: {analysis_result.get('symbol', 'N/A')}")
        print(f"   - Market type: {analysis_result.get('market_type', 'N/A')}")
        print(f"   - VN stock data: {'vn_stock_data' in analysis_result}")
        print(f"   - Ticker news: {'ticker_news' in analysis_result}")
        print(f"   - Price prediction: {'price_prediction' in analysis_result}")
        print(f"   - Risk assessment: {'risk_assessment' in analysis_result}")
        
        # Check if news has CrewAI enhancement
        if 'ticker_news' in analysis_result:
            ticker_news = analysis_result['ticker_news']
            if isinstance(ticker_news, dict):
                print(f"   - News source: {ticker_news.get('source', 'N/A')}")
                print(f"   - Enhanced: {'CrewAI' in str(ticker_news.get('source', ''))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Main Agent + CrewAI integration failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting CrewAI Integration Tests...\n")
    
    # Check environment
    if not os.path.exists('.env'):
        print("❌ No .env file found. Please create one with API keys.")
        return
    
    # Run tests
    tests = [
        ("CrewAI Integration", test_crewai_integration),
        ("VN API Integration", test_vn_api_integration), 
        ("Main Agent Integration", test_main_agent_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
        
        print("\n" + "="*50)
    
    # Summary
    print("\n📋 Test Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! CrewAI integration is ready.")
        print("\n📝 Next steps:")
        print("1. Run: streamlit run src/ui/dashboard.py")
        print("2. Enter your API keys in the sidebar")
        print("3. Click 'Cài đặt CrewAI' to enable real news")
    else:
        print("⚠️ Some tests failed. Check your API keys and dependencies.")

if __name__ == "__main__":
    asyncio.run(main())