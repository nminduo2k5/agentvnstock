#!/usr/bin/env python3
"""
Test script for the improved Investment Expert
"""

from agents.investment_expert import InvestmentExpert
import asyncio

def test_investment_expert():
    """Test the improved investment expert"""
    print("=== Testing Improved Investment Expert ===")
    
    # Test the improved investment expert
    expert = InvestmentExpert()
    
    # Test with VCB
    print("\n--- Testing VCB ---")
    result = expert.analyze_stock('VCB')
    
    print(f"Symbol: {result.get('symbol', 'N/A')}")
    print(f"Recommendation: {result.get('recommendation', 'N/A')}")
    print(f"Reason: {result.get('reason', 'N/A')}")
    print(f"Current Price: {result.get('current_price', 'N/A')}")
    print(f"Target Price: {result.get('target_price', 'N/A')}")
    print(f"PE Ratio: {result.get('pe_ratio', 'N/A')}")
    print(f"PB Ratio: {result.get('pb_ratio', 'N/A')}")
    print(f"ROE: {result.get('roe', 'N/A')}")
    print(f"Market Cap: {result.get('market_cap', 'N/A')}")
    print(f"Dividend Yield: {result.get('dividend_yield', 'N/A')}")
    print(f"Data Source: {result.get('data_source', 'N/A')}")
    print(f"Data Quality: {result.get('data_quality', 'N/A')}")
    
    if 'investment_score' in result:
        print(f"Investment Score: {result['investment_score']}")
    if 'price_position_pct' in result:
        print(f"Price Position: {result['price_position_pct']}%")
    if 'debt_to_equity' in result:
        print(f"Debt to Equity: {result['debt_to_equity']}")
    if 'error' in result:
        print(f"Error: {result['error']}")
    
    # Test with HPG
    print("\n--- Testing HPG ---")
    result2 = expert.analyze_stock('HPG')
    
    print(f"Symbol: {result2.get('symbol', 'N/A')}")
    print(f"Recommendation: {result2.get('recommendation', 'N/A')}")
    print(f"Reason: {result2.get('reason', 'N/A')}")
    print(f"Data Source: {result2.get('data_source', 'N/A')}")
    print(f"Data Quality: {result2.get('data_quality', 'N/A')}")
    
    if 'investment_score' in result2:
        print(f"Investment Score: {result2['investment_score']}")
    if 'error' in result2:
        print(f"Error: {result2['error']}")

if __name__ == "__main__":
    test_investment_expert()