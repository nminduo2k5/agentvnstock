#!/usr/bin/env python3
"""
Test script for AI-enhanced agents
Demonstrates the improved advice and reasoning capabilities
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.price_predictor import PricePredictor
from agents.risk_expert import RiskExpert
from agents.investment_expert import InvestmentExpert
from src.data.vn_stock_api import VNStockAPI
from gemini_agent import GeminiAgent

async def test_ai_enhanced_agents():
    """Test all AI-enhanced agents with VCB stock"""
    
    print("🚀 Testing AI-Enhanced Agents with VCB")
    print("=" * 50)
    
    # Initialize components
    vn_api = VNStockAPI()
    
    # Initialize Gemini AI (you need to set your API key)
    gemini_key = "your_gemini_api_key_here"  # Replace with actual key
    gemini_agent = GeminiAgent(api_key=gemini_key) if gemini_key != "your_gemini_api_key_here" else None
    
    # Initialize agents
    price_predictor = PricePredictor(vn_api)
    risk_expert = RiskExpert(vn_api)
    investment_expert = InvestmentExpert(vn_api)
    
    # Set AI agents if available
    if gemini_agent:
        price_predictor.set_ai_agent(gemini_agent)
        risk_expert.set_ai_agent(gemini_agent)
        investment_expert.set_ai_agent(gemini_agent)
        print("✅ Gemini AI agents configured")
    else:
        print("⚠️ No AI agent configured - will show basic analysis only")
    
    symbol = "VCB"
    
    # Test 1: Price Prediction with AI Advice
    print(f"\n📈 Testing Price Prediction for {symbol}")
    print("-" * 30)
    
    try:
        prediction = price_predictor.predict_price_enhanced(
            symbol=symbol,
            days=30,
            risk_tolerance=60,
            time_horizon="Trung hạn",
            investment_amount=100_000_000
        )
        
        if prediction.get('error'):
            print(f"❌ Error: {prediction['error']}")
        else:
            print(f"Current Price: {prediction.get('current_price', 0):,.0f} VND")
            print(f"Predicted Price: {prediction.get('predicted_price', 0):,.0f} VND")
            print(f"Trend: {prediction.get('trend', 'neutral')}")
            print(f"Confidence: {prediction.get('confidence', 50)}%")
            
            # Show AI advice if available
            if prediction.get('ai_advice'):
                print(f"\n🤖 AI Advice: {prediction['ai_advice']}")
                if prediction.get('ai_reasoning'):
                    print(f"💡 Reasoning: {prediction['ai_reasoning']}")
            
            if prediction.get('ai_enhanced'):
                print(f"✅ Enhanced by AI: {prediction.get('ai_model_used', 'Unknown')}")
            else:
                print("⚠️ No AI enhancement available")
                
    except Exception as e:
        print(f"❌ Price prediction failed: {e}")
    
    # Test 2: Risk Assessment with AI Advice
    print(f"\n⚠️ Testing Risk Assessment for {symbol}")
    print("-" * 30)
    
    try:
        risk_analysis = risk_expert.assess_risk(symbol)
        
        if risk_analysis.get('error'):
            print(f"❌ Error: {risk_analysis['error']}")
        else:
            print(f"Risk Level: {risk_analysis.get('risk_level', 'MEDIUM')}")
            print(f"Volatility: {risk_analysis.get('volatility', 25)}%")
            print(f"Beta: {risk_analysis.get('beta', 1.0)}")
            print(f"Risk Score: {risk_analysis.get('risk_score', 5)}/10")
            
            # Show AI advice if available
            if risk_analysis.get('ai_advice'):
                print(f"\n🤖 AI Risk Advice: {risk_analysis['ai_advice']}")
                if risk_analysis.get('ai_reasoning'):
                    print(f"💡 Reasoning: {risk_analysis['ai_reasoning']}")
            
            if risk_analysis.get('ai_enhanced'):
                print(f"✅ Enhanced by AI: {risk_analysis.get('ai_model_used', 'Unknown')}")
            else:
                print("⚠️ No AI enhancement available")
                
    except Exception as e:
        print(f"❌ Risk assessment failed: {e}")
    
    # Test 3: Investment Analysis with AI Advice
    print(f"\n💼 Testing Investment Analysis for {symbol}")
    print("-" * 30)
    
    try:
        investment_analysis = investment_expert.analyze_stock(symbol)
        
        if investment_analysis.get('error'):
            print(f"❌ Error: {investment_analysis['error']}")
        else:
            print(f"Recommendation: {investment_analysis.get('recommendation', 'HOLD')}")
            print(f"Score: {investment_analysis.get('score', 50)}/100")
            print(f"Confidence: {investment_analysis.get('confidence', 0.5)}")
            print(f"Reason: {investment_analysis.get('reason', 'No reason provided')}")
            
            # Show AI advice if available
            if investment_analysis.get('ai_advice'):
                print(f"\n🤖 AI Investment Advice: {investment_analysis['ai_advice']}")
                if investment_analysis.get('ai_reasoning'):
                    print(f"💡 Reasoning: {investment_analysis['ai_reasoning']}")
            
            if investment_analysis.get('ai_enhanced'):
                print(f"✅ Enhanced by AI: {investment_analysis.get('ai_model_used', 'Unknown')}")
            else:
                print("⚠️ No AI enhancement available")
                
    except Exception as e:
        print(f"❌ Investment analysis failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Agent Testing Complete!")
    print("\nTo enable AI features:")
    print("1. Get Gemini API key from: https://aistudio.google.com/apikey")
    print("2. Replace 'your_gemini_api_key_here' in this script")
    print("3. Run the test again to see AI-enhanced advice")

def test_ai_advice_parsing():
    """Test AI advice parsing functionality"""
    
    print("\n🧪 Testing AI Advice Parsing")
    print("-" * 30)
    
    # Mock AI responses to test parsing
    test_responses = [
        "ADVICE: Nên mua cổ phiếu này vì có tiềm năng tăng trưởng tốt\nREASONING: P/E ratio thấp và xu hướng tăng mạnh",
        "Khuyến nghị mua với tỷ trọng 5-10% danh mục\nLý do: RSI oversold và support mạnh tại 26,000",
        "ADVICE: Giữ cổ phiếu hiện tại\nREASONING: Thị trường đang biến động, chờ tín hiệu rõ ràng hơn"
    ]
    
    # Test with PricePredictor parsing method
    price_predictor = PricePredictor()
    
    for i, response in enumerate(test_responses, 1):
        print(f"\nTest {i}:")
        print(f"Input: {response}")
        
        try:
            advice, reasoning = price_predictor._parse_ai_advice(response)
            print(f"✅ Advice: {advice}")
            print(f"✅ Reasoning: {reasoning}")
        except Exception as e:
            print(f"❌ Parsing failed: {e}")

if __name__ == "__main__":
    print("🇻🇳 DUONG AI TRADING - AI Agents Test")
    print("Testing improved agents with AI advice capabilities")
    
    # Test AI advice parsing first
    test_ai_advice_parsing()
    
    # Test full AI-enhanced agents
    asyncio.run(test_ai_enhanced_agents())