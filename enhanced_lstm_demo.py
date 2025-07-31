#!/usr/bin/env python3
"""
Enhanced LSTM Demo - Showcasing improvements from reference code
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.lstm_price_predictor import LSTMPricePredictor
from src.data.vn_stock_api import VNStockAPI

def demo_enhanced_lstm():
    """Demo enhanced LSTM features"""
    print("🚀 Enhanced LSTM Price Predictor Demo")
    print("=" * 50)
    
    # Initialize
    vn_api = VNStockAPI()
    lstm_predictor = LSTMPricePredictor(vn_api)
    
    print(f"📊 LSTM Configuration:")
    print(f"   - Look-back period: {lstm_predictor.look_back} days")
    print(f"   - Architecture: Enhanced 2-layer LSTM")
    print(f"   - Features: Confidence intervals, rolling predictions")
    print()
    
    # Test with Vietnamese stock
    symbol = "VCB"
    print(f"🔍 Testing enhanced prediction for {symbol}...")
    
    try:
        result = lstm_predictor.predict_with_ai_enhancement(symbol, 90)
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            return
        
        print("✅ Enhanced LSTM Prediction Results:")
        print(f"   - Current Price: {result['current_price']:,.0f} VND")
        print(f"   - Method: {result['method']}")
        print(f"   - Confidence: {result['model_performance']['confidence']:.1f}%")
        print(f"   - Data Points: {result['data_points_used']}")
        print()
        
        # Display predictions with confidence intervals
        predictions = result.get('predictions', {})
        
        if 'short_term' in predictions:
            print("📈 Short-term Predictions (with confidence intervals):")
            for period, data in predictions['short_term'].items():
                price = data['price']
                ci = data.get('confidence_interval', {})
                if ci:
                    print(f"   - {period}: {price:,.0f} VND [{ci['lower']:,.0f} - {ci['upper']:,.0f}] (±{ci['uncertainty']}%)")
                else:
                    print(f"   - {period}: {price:,.0f} VND")
        
        if 'medium_term' in predictions:
            print("\n📊 Medium-term Predictions:")
            for period, data in predictions['medium_term'].items():
                price = data['price']
                ci = data.get('confidence_interval', {})
                if ci:
                    print(f"   - {period}: {price:,.0f} VND [{ci['lower']:,.0f} - {ci['upper']:,.0f}] (±{ci['uncertainty']}%)")
                else:
                    print(f"   - {period}: {price:,.0f} VND")
        
        if 'long_term' in predictions:
            print("\n📉 Long-term Predictions:")
            for period, data in predictions['long_term'].items():
                price = data['price']
                ci = data.get('confidence_interval', {})
                if ci:
                    print(f"   - {period}: {price:,.0f} VND [{ci['lower']:,.0f} - {ci['upper']:,.0f}] (±{ci['uncertainty']}%)")
                else:
                    print(f"   - {period}: {price:,.0f} VND")
        
        # AI Enhancement info
        if result.get('ai_enhanced'):
            print(f"\n🤖 AI Enhancement: {result['ai_model_used']}")
            if result.get('ai_lstm_analysis'):
                print("   - Analysis available ✅")
        else:
            print(f"\n⚠️ AI Enhancement: {result.get('ai_error', 'Not available')}")
        
        print("\n🎯 Key Improvements:")
        print("   ✅ Enhanced 2-layer LSTM architecture (50+50 neurons)")
        print("   ✅ Confidence intervals for all predictions")
        print("   ✅ Rolling window prediction approach")
        print("   ✅ Optimized training parameters (60-day lookback)")
        print("   ✅ 80/20 train/test split for better generalization")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    demo_enhanced_lstm()