import yfinance as yf
import pandas as pd
import numpy as np

class PricePredictor:
    def __init__(self):
        self.name = "Price Predictor Agent"
    
    def predict_price(self, symbol: str, days: int = 30):
        try:
            # Import VN API to check if VN stock
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.data.vn_stock_api import VNStockAPI
            
            vn_api = VNStockAPI()
            
            if vn_api.is_vn_stock(symbol):
                from vnstock import Vnstock
                from datetime import datetime, timedelta
                
                stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
                
                # Lấy dữ liệu lịch sử 1 năm
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                
                hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                
                if hist_data.empty:
                    return {"error": f"No data found for {symbol}"}
                
                # Tính toán technical indicators
                current_price = hist_data['close'].iloc[-1]
                ma_20 = hist_data['close'].rolling(20).mean().iloc[-1]
                ma_50 = hist_data['close'].rolling(50).mean().iloc[-1]
                
                # Phân tích xu hướng
                if ma_20 > ma_50:
                    trend = "bullish"
                    predicted_price = current_price * 1.05
                    confidence = "high"
                elif ma_20 < ma_50:
                    trend = "bearish"
                    predicted_price = current_price * 0.95
                    confidence = "high"
                else:
                    trend = "neutral"
                    predicted_price = current_price * 1.01
                    confidence = "medium"
                
                return {
                    "symbol": symbol,
                    "current_price": round(current_price, -2),
                    "predicted_price": round(predicted_price, -2),
                    "trend": trend,
                    "confidence": confidence,
                    "timeframe": f"{days} days",
                    "market": "Vietnam",
                    "data_source": "VCI_Real"
                }
            
            # Kiểm tra xem có phải mã hợp lệ không
            if not self._is_valid_symbol(symbol):
                return {"error": f"Invalid symbol: {symbol}"}
            
            # US/International stocks
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {"error": f"No data found for {symbol} - may be delisted or invalid"}
            
            # Simple moving average prediction
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]
            
            # Basic trend analysis
            trend = "bullish" if ma_20 > ma_50 else "bearish"
            
            # Simple prediction based on trend
            if trend == "bullish":
                predicted_price = current_price * 1.05
            else:
                predicted_price = current_price * 0.95
            
            return {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "predicted_price": round(predicted_price, 2),
                "trend": trend,
                "confidence": "medium",
                "timeframe": f"{days} days",
                "market": "International"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _is_valid_symbol(self, symbol: str) -> bool:
        """Kiểm tra symbol hợp lệ"""
        if not symbol or len(symbol) < 1:
            return False
        
        # Loại bỏ các mã biết là không hợp lệ
        invalid_symbols = ['X20', 'X21', 'X22', 'X23', 'X24', 'X25', 'TEST', 'DEMO']
        if symbol.upper() in invalid_symbols:
            return False
        
        return True