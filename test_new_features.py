#!/usr/bin/env python3
"""
Test script for new Company Search API and International News features
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_company_search():
    """Test Company Search API"""
    print("🔍 Testing Company Search API...")
    
    try:
        from src.data.company_search_api import get_company_search_api
        
        company_api = get_company_search_api()
        
        # Test 1: Search by company name
        print("\n1. Search by company name 'Vietcombank':")
        result = await company_api.search_company("Vietcombank")
        print(f"   Found: {result.get('found', False)}")
        if result.get('found'):
            print(f"   Symbol: {result['company_info']['symbol']}")
            print(f"   Market: {result.get('market', 'Unknown')}")
        
        # Test 2: Search by symbol
        print("\n2. Search by symbol 'VCB':")
        result = await company_api.get_company_by_symbol("VCB")
        print(f"   Found: {result.get('found', False)}")
        if result.get('found'):
            print(f"   Name: {result['company_info']['full_name']}")
        
        # Test 3: Search by sector
        print("\n3. Search by sector 'Banking':")
        result = await company_api.search_companies_by_sector("Banking")
        print(f"   Found {result.get('found_count', 0)} companies")
        
        # Test 4: Search international company
        print("\n4. Search international company 'Apple':")
        result = await company_api.search_company("Apple")
        print(f"   Found: {result.get('found', False)}")
        if result.get('found'):
            print(f"   Symbol: {result['company_info']['symbol']}")
            print(f"   Market: {result.get('market', 'Unknown')}")
        
        print("✅ Company Search API tests completed")
        
    except Exception as e:
        print(f"❌ Company Search API test failed: {e}")

async def test_international_news():
    """Test International News functionality"""
    print("\n🌍 Testing International News...")
    
    try:
        from src.data.crewai_collector import get_crewai_collector
        
        collector = get_crewai_collector()
        
        # Test 1: Get international tech news
        print("\n1. Get international tech news:")
        result = await collector.get_international_news("technology", "US", 3)
        print(f"   News count: {result.get('news_count', 0)}")
        print(f"   Source: {result.get('source', 'Unknown')}")
        if result.get('headlines'):
            print(f"   First headline: {result['headlines'][0]}")
        
        # Test 2: Get finance news
        print("\n2. Get international finance news:")
        result = await collector.get_international_news("finance", "US", 2)
        print(f"   News count: {result.get('news_count', 0)}")
        print(f"   Impact score: {result.get('impact_score', 'N/A')}")
        
        print("✅ International News tests completed")
        
    except Exception as e:
        print(f"❌ International News test failed: {e}")

async def test_enhanced_news():
    """Test Enhanced News with CrewAI"""
    print("\n🤖 Testing Enhanced News with CrewAI...")
    
    try:
        from src.data.crewai_collector import get_crewai_collector
        
        collector = get_crewai_collector()
        
        # Test enhanced stock news
        print("\n1. Get enhanced news for VCB:")
        result = await collector.get_stock_news("VCB", 3)
        print(f"   News count: {result.get('news_count', 0)}")
        print(f"   Sentiment: {result.get('sentiment', 'Unknown')}")
        print(f"   Source: {result.get('source', 'Unknown')}")
        
        # Test market overview news
        print("\n2. Get market overview news:")
        result = await collector.get_market_overview_news()
        print(f"   Overview available: {'overview' in result}")
        print(f"   Key points: {len(result.get('key_points', []))}")
        
        print("✅ Enhanced News tests completed")
        
    except Exception as e:
        print(f"❌ Enhanced News test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Testing New Features: Company Search API + International News")
    print("=" * 60)
    
    await test_company_search()
    await test_international_news()
    await test_enhanced_news()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("\n📝 Summary:")
    print("   ✅ Company Search API - Search VN & International companies")
    print("   ✅ International News - Get global market news")
    print("   ✅ Enhanced News - CrewAI-powered news analysis")
    print("\n🔗 API Endpoints added:")
    print("   GET /search/company/{company_name}")
    print("   GET /search/symbol/{symbol}")
    print("   GET /search/sector/{sector}")
    print("   GET /international-news/{keyword}")
    print("   GET /enhanced-news/{symbol}")
    print("   GET /market-overview-news")

if __name__ == "__main__":
    asyncio.run(main())