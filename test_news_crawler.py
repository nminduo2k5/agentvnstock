#!/usr/bin/env python3
"""
Test script for the improved news crawler
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ticker_news import TickerNews

async def test_news_crawler():
    """Test the news crawler with real data"""
    
    print("🚀 Testing Enhanced News Crawler")
    print("=" * 50)
    
    # Initialize news agent
    news_agent = TickerNews()
    
    # Test symbols
    test_symbols = ['VCB', 'VIC', 'FPT', 'HPG', 'MSN']
    
    for symbol in test_symbols:
        print(f"\n📰 Testing news for {symbol}:")
        print("-" * 30)
        
        try:
            # Get news
            news_data = news_agent.get_ticker_news(symbol, limit=3)
            
            if 'error' in news_data:
                print(f"❌ Error: {news_data['error']}")
                continue
            
            print(f"✅ Found {news_data.get('news_count', 0)} news items")
            print(f"📊 Data source: {news_data.get('data_source', 'Unknown')}")
            print(f"🏢 Company: {news_data.get('company_name', 'N/A')}")
            print(f"🏭 Sector: {news_data.get('sector', 'N/A')}")
            
            # Show news items
            for i, news in enumerate(news_data.get('news', []), 1):
                print(f"\n  {i}. {news.get('title', 'No title')}")
                print(f"     📅 {news.get('published', 'No date')}")
                print(f"     🔗 {news.get('link', 'No link')}")
                print(f"     📝 {news.get('summary', 'No summary')[:100]}...")
            
            # Show AI analysis if available
            if news_data.get('ai_enhanced'):
                print(f"\n🤖 AI Analysis Available:")
                print(f"   Sentiment: {news_data.get('news_sentiment', 'N/A')}")
                print(f"   Impact Score: {news_data.get('impact_score', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ News crawler test completed!")

def test_news_stats():
    """Test news summary statistics"""
    
    print("\n🔍 Testing News Statistics")
    print("=" * 50)
    
    news_agent = TickerNews()
    
    test_symbol = 'VCB'
    stats = news_agent.get_news_summary_stats(test_symbol)
    
    if 'error' in stats:
        print(f"❌ Error: {stats['error']}")
        return
    
    print(f"📊 News Statistics for {test_symbol}:")
    print(f"   Total News: {stats.get('total_news', 0)}")
    print(f"   Data Source: {stats.get('data_source', 'Unknown')}")
    print(f"   Market: {stats.get('market', 'Unknown')}")
    print(f"   AI Enhanced: {stats.get('ai_enhanced', False)}")
    print(f"   Sentiment: {stats.get('news_sentiment', 'NEUTRAL')}")
    print(f"   Impact Score: {stats.get('impact_score', 5.0)}")
    print(f"   Last Updated: {stats.get('last_updated', 'N/A')}")
    
    publishers = stats.get('publishers', {})
    if publishers:
        print(f"   Publishers:")
        for pub, count in publishers.items():
            print(f"     - {pub}: {count} articles")

if __name__ == "__main__":
    print("🧪 VN Stock News Crawler Test Suite")
    print("=" * 60)
    
    # Test basic news crawling
    asyncio.run(test_news_crawler())
    
    # Test news statistics
    test_news_stats()
    
    print("\n🎉 All tests completed!")