#!/usr/bin/env python3
"""
Test script for Investment Expert Real Data Integration
"""

from agents.investment_expert import InvestmentExpert
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_investment_expert_real_data():
    """Test investment expert with real data fetching"""
    print("=== Testing Investment Expert Real Data Integration ===")
    
    # Initialize investment expert
    expert = InvestmentExpert()
    
    # Test symbols
    test_symbols = ['VCB', 'HPG', 'FPT', 'VIC', 'BID']
    
    for symbol in test_symbols:
        print(f"\n--- Testing {symbol} ---")
        
        try:
            result = expert.analyze_stock(symbol)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            print(f"Symbol: {result.get('symbol', 'N/A')}")
            print(f"Recommendation: {result.get('recommendation', 'N/A')}")
            print(f"Current Price: {result.get('current_price', 'N/A'):,}")
            print(f"Target Price: {result.get('target_price', 'N/A'):,}")
            print(f"PE Ratio: {result.get('pe_ratio', 'N/A')}")
            print(f"PB Ratio: {result.get('pb_ratio', 'N/A')}")
            print(f"ROE: {result.get('roe', 'N/A')}%")
            print(f"Market Cap: {result.get('market_cap', 'N/A')}")
            print(f"Dividend Yield: {result.get('dividend_yield', 'N/A')}%")
            print(f"Year High/Low: {result.get('year_high', 'N/A'):,}/{result.get('year_low', 'N/A'):,}")
            print(f"Data Source: {result.get('data_source', 'N/A')}")
            print(f"Data Quality: {result.get('data_quality', 'N/A')}")
            
            if 'investment_score' in result:
                print(f"Investment Score: {result['investment_score']}")
            
            if 'price_position_pct' in result:
                print(f"Price Position: {result['price_position_pct']}%")
            
            # Check if we got real data
            data_source = result.get('data_source', '')
            if 'Enhanced_Real' in data_source or 'REAL' in result.get('data_quality', ''):
                print("✅ Successfully got REAL data!")
            elif 'Mock' in data_source:
                print("⚠️ Using mock data fallback")
            else:
                print("ℹ️ Using basic data")
                
            print(f"Reason: {result.get('reason', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Exception testing {symbol}: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_investment_expert_real_data()