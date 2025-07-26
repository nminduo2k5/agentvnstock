#!/usr/bin/env python3
"""
Test CrewAI Stock Symbols Integration
Kiểm tra xem CrewAI có lấy được danh sách cổ phiếu real không
"""

import asyncio
import os
from dotenv import load_dotenv
from src.data.crewai_collector import get_crewai_collector

load_dotenv()

async def test_crewai_symbols():
    """Test CrewAI symbols collection"""
    print("🧪 Testing CrewAI Stock Symbols Collection...")
    
    # Get API keys
    gemini_key = os.getenv("GOOGLE_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    
    if not gemini_key:
        print("❌ No Gemini API key found in .env")
        return False
    
    print(f"✅ Gemini API key: {'*' * 20}{gemini_key[-4:]}")
    print(f"📡 Serper API key: {'Available' if serper_key else 'Not available'}")
    
    # Initialize CrewAI collector
    collector = get_crewai_collector(gemini_key, serper_key)
    
    if not collector.enabled:
        print("❌ CrewAI collector not enabled")
        return False
    
    print("✅ CrewAI collector initialized successfully")
    
    # Test symbols collection
    try:
        print("\n🔄 Fetching stock symbols from CrewAI...")
        symbols = await collector.get_available_symbols()
        
        if not symbols:
            print("❌ No symbols returned")
            return False
        
        print(f"✅ Got {len(symbols)} symbols from CrewAI")
        
        # Check data quality
        real_symbols = [s for s in symbols if s.get('data_source') != 'Static']
        static_symbols = [s for s in symbols if s.get('data_source') == 'Static']
        
        print(f"📊 Real symbols: {len(real_symbols)}")
        print(f"📋 Static symbols: {len(static_symbols)}")
        
        # Show first 10 symbols
        print("\n📈 First 10 symbols:")
        for i, symbol in enumerate(symbols[:10], 1):
            print(f"  {i:2d}. {symbol['symbol']:4s} - {symbol['name'][:40]:<40} [{symbol['sector']}]")
        
        # Test by sector
        sectors = {}
        for symbol in symbols:
            sector = symbol.get('sector', 'Unknown')
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(symbol['symbol'])
        
        print(f"\n🏢 Sectors found: {len(sectors)}")
        for sector, syms in sectors.items():
            print(f"  {sector}: {len(syms)} stocks ({', '.join(syms[:5])}{'...' if len(syms) > 5 else ''})")
        
        # Check if we got real data from Gemini
        if len(symbols) >= 40 and len(sectors) >= 5:
            print("\n✅ CrewAI symbols collection PASSED")
            print("   - Sufficient symbols count")
            print("   - Good sector diversity")
            return True
        else:
            print("\n⚠️ CrewAI symbols collection PARTIAL")
            print(f"   - Got {len(symbols)} symbols (need ≥40)")
            print(f"   - Got {len(sectors)} sectors (need ≥5)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CrewAI symbols: {e}")
        return False

async def test_fallback_symbols():
    """Test fallback static symbols"""
    print("\n🧪 Testing Fallback Static Symbols...")
    
    from src.data.vn_stock_api import VNStockAPI
    
    api = VNStockAPI()
    static_symbols = api._get_static_symbols()
    
    print(f"📋 Static symbols count: {len(static_symbols)}")
    
    # Group by sector
    sectors = {}
    for symbol in static_symbols:
        sector = symbol.get('sector', 'Unknown')
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(symbol['symbol'])
    
    print(f"🏢 Static sectors: {len(sectors)}")
    for sector, syms in sectors.items():
        print(f"  {sector}: {len(syms)} stocks")
    
    return len(static_symbols) >= 30

async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 CREWAI STOCK SYMBOLS TEST")
    print("=" * 60)
    
    # Test CrewAI
    crewai_success = await test_crewai_symbols()
    
    # Test fallback
    fallback_success = await test_fallback_symbols()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"CrewAI Symbols:  {'✅ PASS' if crewai_success else '❌ FAIL'}")
    print(f"Fallback Symbols: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    
    if crewai_success:
        print("\n🎉 CrewAI integration hoạt động tốt!")
        print("   App sẽ hiển thị danh sách cổ phiếu real-time")
    elif fallback_success:
        print("\n⚠️ CrewAI không hoạt động, sử dụng fallback")
        print("   App sẽ hiển thị 37 mã cổ phiếu tĩnh")
    else:
        print("\n❌ Cả CrewAI và fallback đều fail")
    
    print("\n💡 Để cải thiện:")
    print("   1. Đảm bảo GOOGLE_API_KEY trong .env")
    print("   2. Thêm SERPER_API_KEY để tăng độ chính xác")
    print("   3. Kiểm tra kết nối internet")

if __name__ == "__main__":
    asyncio.run(main())