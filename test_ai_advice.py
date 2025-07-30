#!/usr/bin/env python3
"""
Quick test to check if agents return ai_advice and ai_reasoning
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.price_predictor import PricePredictor
from agents.risk_expert import RiskExpert  
from agents.investment_expert import InvestmentExpert
from src.data.vn_stock_api import VNStockAPI

def test_agents_advice():
    """Test if agents return ai_advice and ai_reasoning"""
    
    print("🧪 Testing AI Advice in Agents")
    print("=" * 40)
    
    # Initialize
    vn_api = VNStockAPI()
    symbol = "VCB"
    
    # Test 1: PricePredictor
    print("\n📈 Testing PricePredictor...")
    price_predictor = PricePredictor(vn_api)
    
    try:
        result = price_predictor.predict_price_enhanced(
            symbol=symbol,
            days=30,
            risk_tolerance=60,
            time_horizon="Trung hạn",
            investment_amount=100_000_000
        )
        
        print(f"✅ PricePredictor result keys: {list(result.keys())}")
        
        if 'ai_advice' in result:
            print(f"🤖 AI Advice: {result['ai_advice']}")
        else:
            print("❌ No ai_advice found")
            
        if 'ai_reasoning' in result:
            print(f"💡 AI Reasoning: {result['ai_reasoning']}")
        else:
            print("❌ No ai_reasoning found")
            
    except Exception as e:
        print(f"❌ PricePredictor failed: {e}")
    
    # Test 2: RiskExpert
    print("\n⚠️ Testing RiskExpert...")
    risk_expert = RiskExpert(vn_api)
    
    try:
        result = risk_expert.assess_risk(symbol)
        
        print(f"✅ RiskExpert result keys: {list(result.keys())}")
        
        if 'ai_advice' in result:
            print(f"🤖 AI Advice: {result['ai_advice']}")
        else:
            print("❌ No ai_advice found")
            
        if 'ai_reasoning' in result:
            print(f"💡 AI Reasoning: {result['ai_reasoning']}")
        else:
            print("❌ No ai_reasoning found")
            
    except Exception as e:
        print(f"❌ RiskExpert failed: {e}")
    
    # Test 3: InvestmentExpert
    print("\n💼 Testing InvestmentExpert...")
    investment_expert = InvestmentExpert(vn_api)
    
    try:
        result = investment_expert.analyze_stock(symbol)
        
        print(f"✅ InvestmentExpert result keys: {list(result.keys())}")
        
        if 'ai_advice' in result:
            print(f"🤖 AI Advice: {result['ai_advice']}")
        else:
            print("❌ No ai_advice found")
            
        if 'ai_reasoning' in result:
            print(f"💡 AI Reasoning: {result['ai_reasoning']}")
        else:
            print("❌ No ai_reasoning found")
            
    except Exception as e:
        print(f"❌ InvestmentExpert failed: {e}")
    
    print("\n" + "=" * 40)
    print("📝 Summary:")
    print("- Agents should return 'ai_advice' and 'ai_reasoning' keys")
    print("- If missing, AI agent is not configured or failed")
    print("- Configure Gemini API key in sidebar to enable AI features")

if __name__ == "__main__":
    test_agents_advice()