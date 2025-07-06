#!/usr/bin/env python3
"""
Force test CrewAI symbols generation
"""

import asyncio
import os
from src.data.crewai_collector import get_crewai_collector

async def test_force_crewai():
    print("🧪 Force Testing CrewAI Symbols Generation")
    print("=" * 50)
    
    # Get API key
    api_key = input("Enter Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    print("\n🤖 Creating CrewAI collector...")
    collector = get_crewai_collector(api_key)
    
    print(f"✅ CrewAI enabled: {collector.enabled}")
    
    if collector.enabled:
        print("\n🔄 Generating symbols from CrewAI...")
        try:
            symbols = await collector.get_available_symbols()
            
            print(f"📊 Generated {len(symbols)} symbols")
            
            if symbols and len(symbols) > 20:
                print("✅ SUCCESS: Got real symbols from CrewAI!")
                print("\n🎯 First 10 symbols:")
                for i, symbol in enumerate(symbols[:10]):
                    print(f"   {i+1:2d}. {symbol['symbol']:4s} - {symbol['name'][:40]:40s} ({symbol['sector']})")
                
                # Check data source
                if symbols[0].get('data_source') == 'CrewAI':
                    print("\n✅ Data source correctly marked as 'CrewAI'")
                else:
                    print(f"\n⚠️ Data source: {symbols[0].get('data_source', 'Unknown')}")
            else:
                print("❌ Failed to get sufficient symbols from CrewAI")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ CrewAI not enabled")

if __name__ == "__main__":
    asyncio.run(test_force_crewai())