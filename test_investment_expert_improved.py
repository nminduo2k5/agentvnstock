#!/usr/bin/env python3
"""
Test script for improved InvestmentExpert with real data analysis
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.investment_expert import InvestmentExpert

async def test_investment_analysis():
    """Test the new investment analysis functionality"""
    print("🧪 Testing Improved Investment Expert Analysis")
    print("=" * 60)
    
    # Initialize the expert
    expert = InvestmentExpert()
    
    # Test symbols
    test_symbols = ['VCB', 'HPG', 'VIC', 'MSN', 'BID']
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing {symbol}...")
        print("-" * 40)
        
        try:
            # Test the new investment decision method
            result = await expert.analyze_investment_decision(symbol)
            
            print(f"📊 Symbol: {result['symbol']}")
            print(f"🎯 Recommendation: {result['recommendation']}")
            print(f"📈 Score: {result['score']}/100")
            print(f"🔒 Confidence: {result['confidence']:.1%}")
            print(f"💡 Reason: {result['reason']}")
            
            # Show detailed analysis
            if 'analysis' in result and result['analysis']:
                analysis = result['analysis']
                
                if 'financial' in analysis:
                    fin = analysis['financial']
                    print(f"💰 Financial Score: {fin['total_score']}/100")
                
                if 'technical' in analysis:
                    tech = analysis['technical']
                    print(f"📊 Technical Score: {tech['total_score']}/100")
                
                if 'valuation' in analysis:
                    val = analysis['valuation']
                    print(f"💎 Valuation Score: {val['total_score']}/100")
            
            print(f"⏰ Timestamp: {result['timestamp']}")
            
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")
        
        print()

def test_legacy_method():
    """Test the main analyze_stock method"""
    print("\n🧪 Testing Main analyze_stock Method")
    print("=" * 60)
    
    expert = InvestmentExpert()
    
    # Test a few symbols
    test_symbols = ['VCB', 'HPG']
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing analyze_stock for {symbol}...")
        print("-" * 40)
        
        try:
            result = expert.analyze_stock(symbol)
            
            print(f"📊 Symbol: {result['symbol']}")
            print(f"🎯 Recommendation: {result['recommendation']}")
            print(f"📈 Score: {result['score']}/100")
            print(f"🔒 Confidence: {result['confidence']:.1%}")
            print(f"💡 Analysis: {result['analysis']}")
            print(f"⏰ Timestamp: {result['timestamp']}")
            
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Investment Expert Tests")
    print("=" * 60)
    
    # Test async method
    asyncio.run(test_investment_analysis())
    
    # Test main method
    test_legacy_method()
    
    print("\n✅ All tests completed!")