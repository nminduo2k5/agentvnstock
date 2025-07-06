#!/usr/bin/env python3
"""
Test script for CrewAI stock symbols integration
"""

import asyncio
import os
from src.data.vn_stock_api import VNStockAPI
from src.data.crewai_collector import get_crewai_collector

async def test_crewai_symbols():
    """Test CrewAI symbols collection"""
    print("🧪 Testing CrewAI Stock Symbols Integration")
    print("=" * 50)
    
    # Test 1: Without API keys (should use static symbols)
    print("\n1️⃣ Test without API keys (static symbols):")
    vn_api = VNStockAPI()
    symbols = await vn_api.get_available_symbols()
    print(f"   📊 Loaded {len(symbols)} symbols")
    print(f"   🏦 First 3 symbols: {[s['symbol'] for s in symbols[:3]]}")
    
    # Test 2: With API keys (if available)
    gemini_key = os.getenv("GOOGLE_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    
    if gemini_key:
        print(f"\n2️⃣ Test with API keys (CrewAI real data):")
        vn_api_with_keys = VNStockAPI(gemini_key, serper_key)
        
        if vn_api_with_keys.crewai_collector and vn_api_with_keys.crewai_collector.enabled:
            print("   ✅ CrewAI collector enabled")
            try:
                symbols_crewai = await vn_api_with_keys.get_available_symbols()
                print(f"   📊 Loaded {len(symbols_crewai)} symbols from CrewAI")
                print(f"   🏦 First 3 symbols: {[s['symbol'] for s in symbols_crewai[:3]]}")
            except Exception as e:
                print(f"   ❌ CrewAI failed: {e}")
                print("   📋 Falling back to static symbols")
        else:
            print("   ⚠️ CrewAI collector not enabled")
    else:
        print(f"\n2️⃣ No API keys found in environment")
        print("   💡 Set GOOGLE_API_KEY to test CrewAI integration")
    
    # Test 3: Enhanced static symbols
    print(f"\n3️⃣ Enhanced static symbols list:")
    static_symbols = vn_api._get_static_symbols()
    print(f"   📊 Total symbols: {len(static_symbols)}")
    
    # Group by sector
    sectors = {}
    for symbol in static_symbols:
        sector = symbol['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(symbol['symbol'])
    
    for sector, symbols_list in sectors.items():
        print(f"   🏢 {sector}: {len(symbols_list)} symbols ({', '.join(symbols_list[:3])}...)")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_crewai_symbols())