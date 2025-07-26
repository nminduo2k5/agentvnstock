#!/usr/bin/env python3
"""
Simple test for stock symbols (without CrewAI dependency)
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_symbols():
    """Test stock symbols loading"""
    print("Testing stock symbols loading...")
    
    try:
        from src.data.vn_stock_api import VNStockAPI
        
        # Initialize API
        api = VNStockAPI()
        
        # Test get_available_symbols
        print("Getting available symbols...")
        symbols = await api.get_available_symbols()
        
        print(f"Total symbols: {len(symbols)}")
        
        # Check data source
        data_sources = {}
        for symbol in symbols:
            source = symbol.get('data_source', 'Unknown')
            if source not in data_sources:
                data_sources[source] = 0
            data_sources[source] += 1
        
        print("Data sources:")
        for source, count in data_sources.items():
            print(f"  {source}: {count} symbols")
        
        # Group by sector
        sectors = {}
        for symbol in symbols:
            sector = symbol.get('sector', 'Unknown')
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(symbol['symbol'])
        
        print(f"\nSectors ({len(sectors)}):")
        for sector, syms in sectors.items():
            print(f"  {sector}: {len(syms)} stocks")
            print(f"    Examples: {', '.join(syms[:3])}")
        
        # Show first 10 symbols
        print(f"\nFirst 10 symbols:")
        for i, symbol in enumerate(symbols[:10], 1):
            try:
                name = symbol['name'][:40]
                print(f"  {i:2d}. {symbol['symbol']:4s} - {name}")
            except UnicodeEncodeError:
                print(f"  {i:2d}. {symbol['symbol']:4s} - [Vietnamese name]")
        
        # Check if CrewAI is working
        if 'CrewAI' in data_sources:
            print(f"\nSUCCESS: CrewAI is working! Got {data_sources['CrewAI']} real symbols")
        else:
            print(f"\nINFO: Using static symbols ({data_sources.get('Static', 0)} symbols)")
            print("   To enable CrewAI:")
            print("   1. pip install crewai[tools]")
            print("   2. Set GOOGLE_API_KEY in .env")
            print("   3. Optionally set SERPER_API_KEY")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_symbols())
    if success:
        print("\nSUCCESS: Symbols test PASSED")
    else:
        print("\nFAILED: Symbols test FAILED")