#!/usr/bin/env python3
"""
Test script for improved price prediction AI advice
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.price_predictor import PricePredictor
from src.data.vn_stock_api import VNStockAPI

def test_fallback_advice():
    """Test the detailed fallback advice generation"""
    print("🧪 Testing detailed fallback advice generation...")
    
    # Initialize predictor
    vn_api = VNStockAPI()
    predictor = PricePredictor(vn_api)
    
    # Test different risk profiles and scenarios
    test_cases = [
        {
            'symbol': 'VCB',
            'current_price': 85000,
            'rsi': 45,
            'volatility': 20,
            'trend_direction': 'bullish',
            'risk_profile': 'Conservative',
            'risk_tolerance': 25,
            'time_horizon': 'Dài hạn'
        },
        {
            'symbol': 'HPG',
            'current_price': 26000,
            'rsi': 75,
            'volatility': 35,
            'trend_direction': 'bullish',
            'risk_profile': 'Moderate',
            'risk_tolerance': 60,
            'time_horizon': 'Trung hạn'
        },
        {
            'symbol': 'VIC',
            'current_price': 45000,
            'rsi': 25,
            'volatility': 40,
            'trend_direction': 'bearish',
            'risk_profile': 'Aggressive',
            'risk_tolerance': 85,
            'time_horizon': 'Ngắn hạn'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📊 Test Case {i}: {case['symbol']} - {case['risk_profile']}")
        print(f"   RSI: {case['rsi']}, Volatility: {case['volatility']}%, Trend: {case['trend_direction']}")
        
        # Generate fallback advice
        advice_data = predictor._generate_detailed_fallback_advice(
            case['symbol'],
            case['current_price'],
            case['rsi'],
            case['volatility'],
            case['trend_direction'],
            case['risk_profile'],
            case['risk_tolerance'],
            case['time_horizon']
        )
        
        print(f"   💡 Advice: {advice_data['advice']}")
        print(f"   🔍 Reasoning: {advice_data['reasoning']}")
        print("   " + "="*80)

def test_ai_analysis_with_fallback():
    """Test AI analysis with improved fallback"""
    print("\n🤖 Testing AI analysis with improved fallback...")
    
    # Initialize predictor without AI agent (to test fallback)
    vn_api = VNStockAPI()
    predictor = PricePredictor(vn_api)
    
    # Mock technical data
    technical_data = {
        'current_price': 75000,
        'technical_indicators': {
            'rsi': 55,
            'volatility': 25,
            'macd': 0.5
        },
        'trend_analysis': {
            'direction': 'bullish',
            'support_level': 70000,
            'resistance_level': 80000
        },
        'confidence_scores': {
            'medium_term': 65
        }
    }
    
    # Test AI analysis (should use fallback since no AI agent)
    result = predictor._get_ai_price_analysis(
        'VCB', 
        technical_data, 
        90, 
        risk_tolerance=50, 
        time_horizon='Trung hạn'
    )
    
    print(f"✅ AI Enhanced: {result.get('ai_enhanced', False)}")
    print(f"⚠️ AI Error: {result.get('ai_error', 'None')}")
    print(f"💡 AI Advice: {result.get('ai_advice', 'None')}")
    print(f"🔍 AI Reasoning: {result.get('ai_reasoning', 'None')}")

def test_comprehensive_prediction():
    """Test comprehensive prediction with improvements"""
    print("\n📈 Testing comprehensive prediction...")
    
    try:
        # Initialize predictor
        vn_api = VNStockAPI()
        predictor = PricePredictor(vn_api)
        
        # Test prediction for VCB
        result = predictor.predict_price_enhanced(
            'VCB', 
            days=90, 
            risk_tolerance=60, 
            time_horizon='Trung hạn',
            investment_amount=100_000_000
        )
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Symbol: {result.get('symbol', 'N/A')}")
            print(f"💰 Current Price: {result.get('current_price', 0):,.0f} VND")
            print(f"🎯 Predicted Price: {result.get('predicted_price', 0):,.0f} VND")
            print(f"📊 Change: {result.get('change_percent', 0):+.1f}%")
            print(f"🤖 AI Enhanced: {result.get('ai_enhanced', False)}")
            print(f"💡 AI Advice: {result.get('ai_advice', 'None')}")
            print(f"🔍 AI Reasoning: {result.get('ai_reasoning', 'None')}")
            
            if result.get('risk_adjusted_analysis'):
                risk_analysis = result['risk_adjusted_analysis']
                print(f"⚖️ Risk Profile: {risk_analysis.get('risk_profile', 'N/A')}")
                print(f"📈 Suitability Score: {risk_analysis.get('suitability_score', 0)}/100")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Price Prediction Improvements")
    print("="*60)
    
    # Run tests
    test_fallback_advice()
    test_ai_analysis_with_fallback()
    test_comprehensive_prediction()
    
    print("\n✅ All tests completed!")
    print("\n📝 Summary of improvements:")
    print("   • Enhanced fallback advice using real sidebar data")
    print("   • Better error handling for AI timeouts (503 errors)")
    print("   • Risk-aware recommendations based on user profile")
    print("   • Detailed reasoning for all advice scenarios")
    print("   • Graceful degradation when AI is unavailable")