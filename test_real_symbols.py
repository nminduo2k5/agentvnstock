#!/usr/bin/env python3
"""
Quick test to verify CrewAI symbols are working with real data indicators
"""

import asyncio
import os
from src.data.vn_stock_api import VNStockAPI

async def test_real_symbols():
    print("🧪 Testing Real CrewAI Symbols")
    print("=" * 40)
    
    # Test with API key
    gemini_key = input("Enter Gemini API key (or press Enter to skip): ").strip()
    
    if gemini_key:
        print("\n🔑 Testing with Gemini API key...")
        vn_api = VNStockAPI()
        vn_api.set_crewai_keys(gemini_key)
        
        symbols = await vn_api.get_available_symbols()
        
        print(f"📊 Loaded {len(symbols)} symbols")
        
        if symbols and symbols[0].get('data_source') == 'CrewAI':
            print("✅ SUCCESS: Using CrewAI real data!")
            print("🎯 First 5 symbols from CrewAI:")
            for i, symbol in enumerate(symbols[:5]):
                print(f"   {i+1}. {symbol['symbol']} - {symbol['name']} ({symbol['sector']})")
        else:
            print("⚠️ Using static data (CrewAI may have failed)")
            print("🎯 First 5 symbols:")
            for i, symbol in enumerate(symbols[:5]):
                print(f"   {i+1}. {symbol['symbol']} - {symbol['name']} ({symbol['sector']})")
    else:
        print("\n📋 Testing without API key (static data)...")
        vn_api = VNStockAPI()
        symbols = await vn_api.get_available_symbols()
        
        print(f"📊 Loaded {len(symbols)} symbols")
        print("🎯 First 5 symbols (static):")
        for i, symbol in enumerate(symbols[:5]):
            print(f"   {i+1}. {symbol['symbol']} - {symbol['name']} ({symbol['sector']})")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_real_symbols())