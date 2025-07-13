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
                
                # Tính toán technical indicators nâng cao
                current_price = float(hist_data['close'].iloc[-1])
                
                # Multiple moving averages
                ma_5 = hist_data['close'].rolling(5).mean().iloc[-1]
                ma_20 = hist_data['close'].rolling(20).mean().iloc[-1]
                ma_50 = hist_data['close'].rolling(50).mean().iloc[-1]
                
                # RSI calculation
                delta = hist_data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                # Volatility
                returns = hist_data['close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) * 100
                
                # Enhanced trend analysis
                trend_score = 0
                if ma_5 > ma_20: trend_score += 1
                if ma_20 > ma_50: trend_score += 1
                if current_price > ma_20: trend_score += 1
                if 30 < rsi < 70: trend_score += 1  # Not overbought/oversold
                
                if trend_score >= 3:
                    trend = "bullish"
                    predicted_price = current_price * (1 + min(0.08, volatility/100))
                    confidence = "high"
                elif trend_score <= 1:
                    trend = "bearish"
                    predicted_price = current_price * (1 - min(0.08, volatility/100))
                    confidence = "high"
                else:
                    trend = "neutral"
                    predicted_price = current_price * (1 + (volatility/1000))
                    confidence = "medium"
                
                return {
                    "symbol": symbol,
                    "current_price": round(current_price, 2),
                    "predicted_price": round(predicted_price, 2),
                    "trend": trend,
                    "confidence": confidence,
                    "rsi": round(rsi, 2),
                    "volatility": round(volatility, 2),
                    "trend_score": f"{trend_score}/4",
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
            
            # Enhanced technical analysis
            current_price = hist['Close'].iloc[-1]
            ma_5 = hist['Close'].rolling(window=5).mean().iloc[-1]
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            # Volume analysis
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            recent_volume = hist['Volume'].iloc[-1]
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Enhanced trend analysis
            trend_signals = 0
            if ma_5 > ma_20: trend_signals += 1
            if ma_20 > ma_50: trend_signals += 1
            if current_price > ma_20: trend_signals += 1
            if volume_ratio > 1.2: trend_signals += 1  # High volume
            
            if trend_signals >= 3:
                trend = "bullish"
                predicted_price = current_price * 1.06
                confidence = "high"
            elif trend_signals <= 1:
                trend = "bearish"
                predicted_price = current_price * 0.94
                confidence = "high"
            else:
                trend = "neutral"
                predicted_price = current_price * 1.01
                confidence = "medium"
            
            return {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "predicted_price": round(predicted_price, 2),
                "trend": trend,
                "confidence": confidence,
                "volume_ratio": round(volume_ratio, 2),
                "trend_signals": f"{trend_signals}/4",
                "timeframe": f"{days} days",
                "market": "International",
                "data_source": "Yahoo_Finance"
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