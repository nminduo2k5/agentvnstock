#!/usr/bin/env python3
"""
Test script to verify trend_analysis integration between price_predictor and app.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.price_predictor import PricePredictor
from src.data.vn_stock_api import VNStockAPI

def test_trend_analysis_structure():
    """Test if trend_analysis returns expected structure"""
    print("🧪 Testing trend_analysis structure...")
    
    try:
        # Initialize components
        vn_api = VNStockAPI()
        predictor = PricePredictor(vn_api)
        
        # Test with a VN stock
        test_symbol = "VCB"
        print(f"📊 Testing with symbol: {test_symbol}")
        
        result = predictor.predict_comprehensive(test_symbol, vn_api)
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            return False
        
        # Check if trend_analysis exists
        trend_analysis = result.get('trend_analysis', {})
        if not trend_analysis:
            print("❌ trend_analysis not found in result")
            return False
        
        # Check expected fields
        expected_fields = [
            'direction', 'strength', 'score', 'signals', 
            'rsi', 'macd', 'momentum_5d', 'momentum_20d', 
            'volume_trend', 'support_level', 'resistance_level', 
            'prediction_based'
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in trend_analysis:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields in trend_analysis: {missing_fields}")
            return False
        
        # Print structure for verification
        print("✅ trend_analysis structure is correct!")
        print("\n📋 trend_analysis content:")
        for key, value in trend_analysis.items():
            print(f"  {key}: {value}")
        
        # Test app.py compatibility
        print("\n🔍 Testing app.py compatibility...")
        
        # Simulate what app.py does
        trend = trend_analysis.get('direction', 'neutral')
        trend_strength = trend_analysis.get('strength', 'Medium')
        tech_score = trend_analysis.get('score', '50/100')
        signals = trend_analysis.get('signals', [])
        momentum_5d = trend_analysis.get('momentum_5d', 0)
        momentum_20d = trend_analysis.get('momentum_20d', 0)
        volume_trend = trend_analysis.get('volume_trend', 0)
        prediction_based = trend_analysis.get('prediction_based', False)
        support = trend_analysis.get('support_level', 0)
        resistance = trend_analysis.get('resistance_level', 0)
        trend_rsi = trend_analysis.get('rsi', 50)
        trend_macd = trend_analysis.get('macd', 0)
        
        print(f"  ✅ trend: {trend}")
        print(f"  ✅ trend_strength: {trend_strength}")
        print(f"  ✅ tech_score: {tech_score}")
        print(f"  ✅ signals count: {len(signals)}")
        print(f"  ✅ momentum_5d: {momentum_5d}")
        print(f"  ✅ momentum_20d: {momentum_20d}")
        print(f"  ✅ volume_trend: {volume_trend}")
        print(f"  ✅ prediction_based: {prediction_based}")
        print(f"  ✅ support: {support}")
        print(f"  ✅ resistance: {resistance}")
        print(f"  ✅ trend_rsi: {trend_rsi}")
        print(f"  ✅ trend_macd: {trend_macd}")
        
        print("\n🎉 All tests passed! Integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting trend_analysis integration test...")
    success = test_trend_analysis_structure()
    
    if success:
        print("\n✅ Integration test completed successfully!")
        print("📱 App.py should now display all trend_analysis data correctly.")
    else:
        print("\n❌ Integration test failed!")
        print("🔧 Please check the implementation.")