#!/usr/bin/env python3
"""
Debug script để kiểm tra CrewAI integration
"""

import asyncio
import os
from src.data.vn_stock_api import VNStockAPI
from main_agent import MainAgent

async def debug_crewai():
    print("🔍 DEBUGGING CREWAI INTEGRATION")
    print("=" * 50)
    
    # 1. Check environment
    print("1. Environment Check:")
    gemini_key = os.getenv("GOOGLE_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    print(f"   - GOOGLE_API_KEY: {'✅ Set' if gemini_key else '❌ Not set'}")
    print(f"   - SERPER_API_KEY: {'✅ Set' if serper_key else '❌ Not set'}")
    
    # 2. Initialize VN API
    print("\n2. VN API Initialization:")
    vn_api = VNStockAPI()
    print(f"   - VN API created: ✅")
    print(f"   - CrewAI collector exists: {'✅' if vn_api.crewai_collector else '❌'}")
    if vn_api.crewai_collector:
        print(f"   - CrewAI collector enabled: {'✅' if vn_api.crewai_collector.enabled else '❌'}")
    
    # 3. Initialize Main Agent
    print("\n3. Main Agent Initialization:")
    main_agent = MainAgent(vn_api)
    print(f"   - Main agent created: ✅")
    print(f"   - Gemini agent exists: {'✅' if main_agent.gemini_agent else '❌'}")
    
    # 4. Test symbols loading
    print("\n4. Testing Symbols Loading:")
    try:
        symbols = await vn_api.get_available_symbols()
        print(f"   - Symbols loaded: ✅ ({len(symbols)} symbols)")
        
        if symbols:
            first_symbol = symbols[0]
            data_source = first_symbol.get('data_source', 'Unknown')
            print(f"   - Data source: {data_source}")
            
            if data_source == 'CrewAI':
                print("   - 🎉 SUCCESS: Using CrewAI real data!")
            else:
                print("   - ⚠️ FALLBACK: Using static data")
                
                # Debug why CrewAI failed
                print("\n5. CrewAI Debug:")
                if not vn_api.crewai_collector:
                    print("   - ❌ CrewAI collector not initialized")
                elif not vn_api.crewai_collector.enabled:
                    print("   - ❌ CrewAI collector not enabled")
                    print(f"   - Gemini API key: {'✅' if vn_api.crewai_collector.gemini_api_key else '❌'}")
                else:
                    print("   - ✅ CrewAI collector should work, testing...")
                    try:
                        crewai_symbols = await vn_api.crewai_collector.get_available_symbols()
                        print(f"   - CrewAI symbols: {len(crewai_symbols) if crewai_symbols else 0}")
                    except Exception as e:
                        print(f"   - CrewAI error: {e}")
        
    except Exception as e:
        print(f"   - ❌ Error loading symbols: {e}")
    
    # 5. Test with manual API key
    print("\n6. Testing with Manual API Key:")
    test_key = input("Enter Gemini API key for testing (or press Enter to skip): ").strip()
    if test_key:
        try:
            # Set API key manually
            success = main_agent.set_gemini_api_key(test_key)
            print(f"   - API key set: {'✅' if success else '❌'}")
            
            if success:
                # Test symbols again
                symbols = await vn_api.get_available_symbols()
                if symbols:
                    data_source = symbols[0].get('data_source', 'Unknown')
                    print(f"   - New data source: {data_source}")
                    
                    if data_source == 'CrewAI':
                        print("   - 🎉 SUCCESS: CrewAI now working!")
                    else:
                        print("   - ⚠️ Still using fallback")
        except Exception as e:
            print(f"   - ❌ Error with manual key: {e}")
    
    print("\n" + "=" * 50)
    print("Debug completed!")

if __name__ == "__main__":
    asyncio.run(debug_crewai())