#!/usr/bin/env python3
"""
Quick test for enhanced features
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_basic():
    """Basic test"""
    print("Testing basic functionality...")
    
    try:
        # Test imports
        from src.data.company_search_api import get_company_search_api
        from agents.enhanced_news_agent import create_enhanced_news_agent
        from agents.report_generator import ReportGenerator
        
        print("All imports successful")
        
        # Test company search
        company_api = get_company_search_api()
        result = await company_api.search_company("VCB")
        print(f"Company search: {result.get('found', False)}")
        
        # Test enhanced news
        news_agent = create_enhanced_news_agent()
        news_result = await news_agent.get_stock_news("VCB")
        print(f"Enhanced news: {news_result.get('news_count', 0)} news items")
        
        # Test report generator
        report_gen = ReportGenerator()
        print("Report generator initialized")
        
        print("All basic tests passed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic())