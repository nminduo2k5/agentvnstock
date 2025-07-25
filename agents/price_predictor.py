import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PricePredictor:
    def __init__(self, vn_api=None, stock_info=None):
        self.name = "Advanced Price Predictor Agent"
        self.vn_api = vn_api
        self.stock_info = stock_info
        self.prediction_periods = {
            'short_term': [1, 3, 7],      # 1 ngày, 3 ngày, 1 tuần
            'medium_term': [14, 30, 60],   # 2 tuần, 1 tháng, 2 tháng
            'long_term': [90, 180, 365]    # 3 tháng, 6 tháng, 1 năm
        }
    
    def predict_comprehensive(self, symbol: str, vn_api=None, stock_info=None):
        """Dự đoán giá toàn diện theo từng khoảng thời gian
        
        Args:
            symbol: Mã cổ phiếu
            vn_api: Optional VNStockAPI instance
            stock_info: Optional StockInfoDisplay instance
        """
        try:
            # Use provided VN API or initialize new one
            if not vn_api:
                if not self.vn_api:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from src.data.vn_stock_api import VNStockAPI
                    self.vn_api = VNStockAPI()
                vn_api = self.vn_api
            
            # Check if VN stock using real API
            if vn_api and vn_api.is_vn_stock(symbol):
                return self._predict_vn_stock(symbol, vn_api)
            else:
                return self._predict_international_stock(symbol)
                
        except Exception as e:
            return {"error": str(e)}
    
    def _predict_vn_stock(self, symbol: str, vn_api=None):
        """Dự đoán cổ phiếu Việt Nam với thuật toán nâng cao sử dụng real data từ stock_info"""
        try:
            # Use provided VN API or initialize
            if not vn_api:
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from src.data.vn_stock_api import VNStockAPI
                vn_api = VNStockAPI()
            
            # Import StockInfoDisplay để lấy real data
            import asyncio
            from agents.stock_info import StockInfoDisplay
            
            # Khởi tạo StockInfoDisplay với VN API
            stock_info = StockInfoDisplay(vn_api)
            
            # Lấy dữ liệu chi tiết từ stock_info
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            detailed_data = loop.run_until_complete(stock_info.get_detailed_stock_data(symbol))
            loop.close()
            
            if not detailed_data or detailed_data.get('error'):
                # Fallback to traditional method if stock_info fails
                from vnstock import Vnstock
                stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
                hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                current_price = float(hist_data['close'].iloc[-1])
                data_source = "VCI_Fallback"
            else:
                # Use real data from stock_info
                price_history = detailed_data['price_history']
                stock_data = detailed_data['stock_data']
                detailed_metrics = detailed_data['detailed_data']
                
                # Convert price_history to DataFrame for technical analysis
                import pandas as pd
                hist_data = pd.DataFrame(price_history)
                current_price = stock_data.price
                data_source = "StockInfo_Real"
            
            if hist_data.empty:
                return {"error": f"No data found for {symbol}"}
            
            # Tính toán các chỉ báo kỹ thuật nâng cao
            technical_indicators = self._calculate_advanced_indicators(hist_data)
            
            # Enhance technical indicators with detailed metrics if available
            if 'detailed_metrics' in locals() and detailed_metrics:
                # Add real financial ratios to technical indicators
                technical_indicators['pe'] = detailed_metrics.get('pe', technical_indicators.get('pe', 0))
                technical_indicators['pb'] = detailed_metrics.get('pb', technical_indicators.get('pb', 0))
                technical_indicators['dividend_yield'] = detailed_metrics.get('dividend_yield', 0)
                technical_indicators['beta'] = detailed_metrics.get('beta', technical_indicators.get('beta', 1))
            
            # Phân tích xu hướng và pattern
            trend_analysis = self._analyze_market_trend(hist_data)
            
            # Dự đoán giá theo từng khoảng thời gian
            predictions = self._generate_multi_timeframe_predictions(hist_data, technical_indicators)
            
            # Tính toán độ tin cậy
            confidence_scores = self._calculate_confidence_scores(hist_data, technical_indicators)
            
            # Phân tích rủi ro
            risk_analysis = self._analyze_risk_metrics(hist_data)
            
            return {
                "symbol": symbol,
                "current_price": round(float(current_price), 2),
                "market": "Vietnam",
                "data_source": data_source,
                "analysis_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "technical_indicators": technical_indicators,
                "trend_analysis": trend_analysis,
                "predictions": predictions,
                "confidence_scores": confidence_scores,
                "risk_analysis": risk_analysis,
                "recommendations": self._generate_recommendations(predictions, confidence_scores, risk_analysis)
            }
            
        except Exception as e:
            return {"error": f"VN Stock prediction error: {str(e)}"}
    
    def _predict_international_stock(self, symbol: str):
        """Dự đoán cổ phiếu quốc tế"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2y")
            
            if hist.empty:
                return {"error": f"No data found for {symbol}"}
            
            # Convert to lowercase column names for consistency
            hist.columns = [col.lower() for col in hist.columns]
            
            # Tính toán các chỉ báo kỹ thuật nâng cao
            technical_indicators = self._calculate_advanced_indicators(hist)
            
            # Phân tích xu hướng và pattern
            trend_analysis = self._analyze_market_trend(hist)
            
            # Dự đoán giá theo từng khoảng thời gian
            predictions = self._generate_multi_timeframe_predictions(hist, technical_indicators)
            
            # Tính toán độ tin cậy
            confidence_scores = self._calculate_confidence_scores(hist, technical_indicators)
            
            # Phân tích rủi ro
            risk_analysis = self._analyze_risk_metrics(hist)
            
            return {
                "symbol": symbol,
                "current_price": round(float(hist['close'].iloc[-1]), 2),
                "market": "International",
                "data_source": "Yahoo_Finance",
                "analysis_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "technical_indicators": technical_indicators,
                "trend_analysis": trend_analysis,
                "predictions": predictions,
                "confidence_scores": confidence_scores,
                "risk_analysis": risk_analysis,
                "recommendations": self._generate_recommendations(predictions, confidence_scores, risk_analysis)
            }
            
        except Exception as e:
            return {"error": f"International stock prediction error: {str(e)}"}

    def _calculate_advanced_indicators(self, data):
        """Tính toán các chỉ báo kỹ thuật nâng cao"""
        try:
            indicators = {}
            
            # Moving Averages
            indicators['sma_5'] = data['close'].rolling(5).mean().iloc[-1]
            indicators['sma_20'] = data['close'].rolling(20).mean().iloc[-1]
            indicators['sma_50'] = data['close'].rolling(50).mean().iloc[-1]
            indicators['sma_200'] = data['close'].rolling(200).mean().iloc[-1]
            
            # Exponential Moving Averages
            indicators['ema_12'] = data['close'].ewm(span=12).mean().iloc[-1]
            indicators['ema_26'] = data['close'].ewm(span=26).mean().iloc[-1]
            
            # MACD
            macd_line = indicators['ema_12'] - indicators['ema_26']
            signal_line = pd.Series([macd_line]).ewm(span=9).mean().iloc[0]
            indicators['macd'] = macd_line
            indicators['macd_signal'] = signal_line
            indicators['macd_histogram'] = macd_line - signal_line
            
            # RSI
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]
            
            # Bollinger Bands
            sma_20 = data['close'].rolling(20).mean()
            std_20 = data['close'].rolling(20).std()
            indicators['bb_upper'] = (sma_20 + (std_20 * 2)).iloc[-1]
            indicators['bb_middle'] = sma_20.iloc[-1]
            indicators['bb_lower'] = (sma_20 - (std_20 * 2)).iloc[-1]
            indicators['bb_position'] = (data['close'].iloc[-1] - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
            
            # Stochastic Oscillator
            low_14 = data['low'].rolling(14).min()
            high_14 = data['high'].rolling(14).max()
            k_percent = 100 * ((data['close'] - low_14) / (high_14 - low_14))
            indicators['stoch_k'] = k_percent.iloc[-1]
            indicators['stoch_d'] = k_percent.rolling(3).mean().iloc[-1]
            
            # Williams %R
            indicators['williams_r'] = -100 * ((high_14.iloc[-1] - data['close'].iloc[-1]) / (high_14.iloc[-1] - low_14.iloc[-1]))
            
            # Average True Range (ATR)
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            indicators['atr'] = true_range.rolling(14).mean().iloc[-1]
            
            # Volume indicators
            if 'volume' in data.columns:
                indicators['volume_sma'] = data['volume'].rolling(20).mean().iloc[-1]
                indicators['volume_ratio'] = data['volume'].iloc[-1] / indicators['volume_sma']
                
                # On-Balance Volume (OBV)
                obv = (np.sign(data['close'].diff()) * data['volume']).fillna(0).cumsum()
                indicators['obv'] = obv.iloc[-1]
                indicators['obv_trend'] = obv.rolling(10).mean().iloc[-1] - obv.rolling(20).mean().iloc[-1]
            
            # Volatility
            returns = data['close'].pct_change().dropna()
            indicators['volatility'] = returns.std() * np.sqrt(252) * 100
            indicators['volatility_percentile'] = (returns.rolling(252).std().iloc[-1] > returns.rolling(252).std().quantile(0.8))
            
            return {k: round(float(v), 4) if isinstance(v, (int, float, np.number)) else v for k, v in indicators.items()}
            
        except Exception as e:
            return {"error": f"Indicator calculation error: {str(e)}"}
    
    def _analyze_market_trend(self, data):
        """Phân tích xu hướng thị trường"""
        try:
            current_price = data['close'].iloc[-1]
            
            # Trend strength analysis
            sma_5 = data['close'].rolling(5).mean().iloc[-1]
            sma_20 = data['close'].rolling(20).mean().iloc[-1]
            sma_50 = data['close'].rolling(50).mean().iloc[-1]
            
            trend_score = 0
            trend_signals = []
            
            # Price vs Moving Averages
            if current_price > sma_5:
                trend_score += 1
                trend_signals.append("Price > SMA5")
            if current_price > sma_20:
                trend_score += 1
                trend_signals.append("Price > SMA20")
            if current_price > sma_50:
                trend_score += 1
                trend_signals.append("Price > SMA50")
            
            # Moving Average alignment
            if sma_5 > sma_20:
                trend_score += 1
                trend_signals.append("SMA5 > SMA20")
            if sma_20 > sma_50:
                trend_score += 1
                trend_signals.append("SMA20 > SMA50")
            
            # Determine trend strength
            if trend_score >= 4:
                trend_strength = "Strong Bullish"
                trend_direction = "bullish"
            elif trend_score >= 3:
                trend_strength = "Moderate Bullish"
                trend_direction = "bullish"
            elif trend_score >= 2:
                trend_strength = "Neutral"
                trend_direction = "neutral"
            elif trend_score >= 1:
                trend_strength = "Moderate Bearish"
                trend_direction = "bearish"
            else:
                trend_strength = "Strong Bearish"
                trend_direction = "bearish"
            
            # Price momentum
            momentum_5 = (current_price - data['close'].iloc[-6]) / data['close'].iloc[-6] * 100
            momentum_20 = (current_price - data['close'].iloc[-21]) / data['close'].iloc[-21] * 100
            
            return {
                "direction": trend_direction,
                "strength": trend_strength,
                "score": f"{trend_score}/5",
                "signals": trend_signals,
                "momentum_5d": round(momentum_5, 2),
                "momentum_20d": round(momentum_20, 2),
                "support_level": round(data['close'].rolling(20).min().iloc[-1], 2),
                "resistance_level": round(data['close'].rolling(20).max().iloc[-1], 2)
            }
            
        except Exception as e:
            return {"error": f"Trend analysis error: {str(e)}"}
    
    def _generate_multi_timeframe_predictions(self, data, indicators):
        """Tạo dự đoán theo nhiều khung thời gian"""
        try:
            current_price = float(data['close'].iloc[-1])
            predictions = {}
            
            # Lấy các yếu tố dự đoán
            volatility = indicators.get('volatility', 20) / 100
            rsi = indicators.get('rsi', 50)
            macd_signal = 1 if indicators.get('macd', 0) > indicators.get('macd_signal', 0) else -1
            bb_position = indicators.get('bb_position', 0.5)
            
            # Tính toán hệ số điều chỉnh dựa trên các chỉ báo
            trend_multiplier = self._calculate_trend_multiplier(indicators, rsi, bb_position)
            
            for period_type, days_list in self.prediction_periods.items():
                predictions[period_type] = {}
                
                for days in days_list:
                    # Thuật toán dự đoán kết hợp nhiều yếu tố
                    base_change = self._calculate_base_change(days, volatility, trend_multiplier)
                    
                    # Điều chỉnh dựa trên MACD
                    macd_adjustment = macd_signal * min(0.02, volatility * 0.1) * (days / 30)
                    
                    # Điều chỉnh dựa trên RSI
                    rsi_adjustment = self._calculate_rsi_adjustment(rsi, days)
                    
                    # Điều chỉnh dựa trên Bollinger Bands
                    bb_adjustment = self._calculate_bb_adjustment(bb_position, days)
                    
                    # Tổng hợp các điều chỉnh
                    total_change = base_change + macd_adjustment + rsi_adjustment + bb_adjustment
                    
                    # Giới hạn thay đổi tối đa
                    max_change = min(0.3, volatility * 2 * (days / 30))
                    total_change = max(-max_change, min(max_change, total_change))
                    
                    predicted_price = current_price * (1 + total_change)
                    
                    predictions[period_type][f"{days}_days"] = {
                        "price": round(predicted_price, 2),
                        "change_percent": round(total_change * 100, 2),
                        "change_amount": round(predicted_price - current_price, 2)
                    }
            
            return predictions
            
        except Exception as e:
            return {"error": f"Prediction generation error: {str(e)}"}

    def predict_price(self, symbol: str, days: int = 30):
        """Legacy method for backward compatibility with enhanced real data support"""
        # Use the class's vn_api and stock_info if available
        result = self.predict_comprehensive(symbol, self.vn_api, self.stock_info)
        
        if "error" in result:
            return result
        
        # Extract prediction for the requested timeframe
        current_price = result['current_price']
        
        # Find the closest prediction timeframe
        if days <= 7:
            prediction_data = result['predictions']['short_term']['7_days']
        elif days <= 30:
            prediction_data = result['predictions']['medium_term']['30_days']
        elif days <= 90:
            prediction_data = result['predictions']['medium_term']['60_days']
        else:
            prediction_data = result['predictions']['long_term']['180_days']
        
        # Legacy format response
        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": prediction_data['price'],
            "change_percent": prediction_data['change_percent'],
            "timeframe": f"{days} days",
            "confidence": result['confidence_scores'].get('medium_term', 50),
            "trend": result['trend_analysis']['direction'],
            "market": result['market'],
            "data_source": result['data_source'],
            "risk_level": result['risk_analysis']['risk_level'],
            "recommendation": result['recommendations']['medium_term']['recommendation']
        }
    
    def _calculate_trend_multiplier(self, indicators, rsi, bb_position):
        """Tính toán hệ số xu hướng"""
        multiplier = 0
        
        # RSI influence
        if rsi > 70:
            multiplier -= 0.3  # Overbought
        elif rsi < 30:
            multiplier += 0.3  # Oversold
        elif 40 <= rsi <= 60:
            multiplier += 0.1  # Neutral zone
        
        # Bollinger Bands influence
        if bb_position > 0.8:
            multiplier -= 0.2  # Near upper band
        elif bb_position < 0.2:
            multiplier += 0.2  # Near lower band
        
        # MACD influence
        if indicators.get('macd', 0) > indicators.get('macd_signal', 0):
            multiplier += 0.1
        else:
            multiplier -= 0.1
        
        return multiplier
    
    def _calculate_base_change(self, days, volatility, trend_multiplier):
        """Tính toán thay đổi cơ bản"""
        # Base change dựa trên thời gian và volatility
        time_factor = np.sqrt(days / 365)  # Square root of time
        base_change = trend_multiplier * volatility * time_factor
        
        # Thêm yếu tố ngẫu nhiên nhỏ để mô phỏng tính không chắc chắn của thị trường
        random_factor = np.random.normal(0, volatility * 0.1) * time_factor
        
        return base_change + random_factor
    
    def _calculate_rsi_adjustment(self, rsi, days):
        """Điều chỉnh dựa trên RSI"""
        if rsi > 80:
            return -0.05 * (days / 30)  # Strong overbought
        elif rsi > 70:
            return -0.02 * (days / 30)  # Overbought
        elif rsi < 20:
            return 0.05 * (days / 30)   # Strong oversold
        elif rsi < 30:
            return 0.02 * (days / 30)   # Oversold
        else:
            return 0
    
    def _calculate_bb_adjustment(self, bb_position, days):
        """Điều chỉnh dựa trên Bollinger Bands"""
        if bb_position > 0.9:
            return -0.03 * (days / 30)  # Very high
        elif bb_position > 0.8:
            return -0.01 * (days / 30)  # High
        elif bb_position < 0.1:
            return 0.03 * (days / 30)   # Very low
        elif bb_position < 0.2:
            return 0.01 * (days / 30)   # Low
        else:
            return 0
    
    def _calculate_confidence_scores(self, data, indicators):
        """Tính toán độ tin cậy của dự đoán"""
        try:
            scores = {}
            
            # Data quality score
            data_quality = min(100, len(data) / 252 * 100)  # Based on 1 year of data
            
            # Volatility score (lower volatility = higher confidence)
            volatility = indicators.get('volatility', 20)
            volatility_score = max(0, 100 - volatility * 2)
            
            # Trend consistency score
            trend_consistency = self._calculate_trend_consistency(data)
            
            # Volume confirmation score
            volume_score = 50  # Default if no volume data
            if 'volume_ratio' in indicators:
                volume_ratio = indicators['volume_ratio']
                if 0.8 <= volume_ratio <= 1.5:
                    volume_score = 80
                elif 0.5 <= volume_ratio <= 2.0:
                    volume_score = 60
                else:
                    volume_score = 30
            
            # Overall confidence for different timeframes
            scores['short_term'] = round((data_quality * 0.2 + volatility_score * 0.3 + trend_consistency * 0.3 + volume_score * 0.2), 1)
            scores['medium_term'] = round((data_quality * 0.3 + volatility_score * 0.2 + trend_consistency * 0.4 + volume_score * 0.1), 1)
            scores['long_term'] = round((data_quality * 0.4 + volatility_score * 0.1 + trend_consistency * 0.5), 1)
            
            return scores
            
        except Exception as e:
            return {"error": f"Confidence calculation error: {str(e)}"}
    
    def _calculate_trend_consistency(self, data):
        """Tính toán tính nhất quán của xu hướng"""
        try:
            # Calculate moving averages
            sma_5 = data['close'].rolling(5).mean()
            sma_20 = data['close'].rolling(20).mean()
            
            # Count consistent trend days in last 20 days
            recent_data = data.tail(20)
            consistent_days = 0
            
            for i in range(len(recent_data)):
                if i < 5:  # Skip first 5 days due to SMA calculation
                    continue
                    
                price = recent_data['close'].iloc[i]
                sma5 = sma_5.iloc[recent_data.index[i]]
                sma20 = sma_20.iloc[recent_data.index[i]]
                
                # Check if trend is consistent
                if (price > sma5 > sma20) or (price < sma5 < sma20):
                    consistent_days += 1
            
            consistency_score = (consistent_days / 15) * 100  # 15 valid days out of 20
            return min(100, consistency_score)
            
        except Exception as e:
            return 50  # Default score if calculation fails
    
    def _analyze_risk_metrics(self, data):
        """Phân tích các chỉ số rủi ro"""
        try:
            returns = data['close'].pct_change().dropna()
            
            # Value at Risk (VaR) - 95% confidence level
            var_95 = np.percentile(returns, 5) * 100
            
            # Maximum Drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # Sharpe Ratio (assuming risk-free rate of 3%)
            excess_returns = returns - 0.03/252  # Daily risk-free rate
            sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
            
            # Beta (if we have market data, otherwise use volatility as proxy)
            beta = returns.std() / 0.02  # Assuming market volatility of 2%
            
            # Risk level classification
            volatility = returns.std() * np.sqrt(252) * 100
            if volatility < 15:
                risk_level = "Low"
            elif volatility < 25:
                risk_level = "Medium"
            elif volatility < 40:
                risk_level = "High"
            else:
                risk_level = "Very High"
            
            return {
                "risk_level": risk_level,
                "volatility": round(volatility, 2),
                "var_95": round(var_95, 2),
                "max_drawdown": round(max_drawdown, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "beta": round(beta, 2)
            }
            
        except Exception as e:
            return {"error": f"Risk analysis error: {str(e)}"}
    
    def _generate_recommendations(self, predictions, confidence_scores, risk_analysis):
        """Tạo khuyến nghị đầu tư"""
        try:
            recommendations = {}
            
            # Short-term recommendation
            short_term_change = predictions['short_term']['7_days']['change_percent']
            short_confidence = confidence_scores['short_term']
            
            if short_confidence > 70:
                if short_term_change > 5:
                    short_rec = "Strong Buy"
                elif short_term_change > 2:
                    short_rec = "Buy"
                elif short_term_change > -2:
                    short_rec = "Hold"
                elif short_term_change > -5:
                    short_rec = "Sell"
                else:
                    short_rec = "Strong Sell"
            else:
                short_rec = "Hold" if abs(short_term_change) < 3 else "Caution"
            
            # Medium-term recommendation
            medium_term_change = predictions['medium_term']['30_days']['change_percent']
            medium_confidence = confidence_scores['medium_term']
            
            if medium_confidence > 60:
                if medium_term_change > 10:
                    medium_rec = "Strong Buy"
                elif medium_term_change > 5:
                    medium_rec = "Buy"
                elif medium_term_change > -5:
                    medium_rec = "Hold"
                elif medium_term_change > -10:
                    medium_rec = "Sell"
                else:
                    medium_rec = "Strong Sell"
            else:
                medium_rec = "Hold"
            
            # Long-term recommendation
            long_term_change = predictions['long_term']['180_days']['change_percent']
            long_confidence = confidence_scores['long_term']
            
            if long_confidence > 50:
                if long_term_change > 20:
                    long_rec = "Strong Buy"
                elif long_term_change > 10:
                    long_rec = "Buy"
                elif long_term_change > -10:
                    long_rec = "Hold"
                elif long_term_change > -20:
                    long_rec = "Sell"
                else:
                    long_rec = "Strong Sell"
            else:
                long_rec = "Hold"
            
            # Risk-adjusted recommendation
            risk_level = risk_analysis.get('risk_level', 'Medium')
            if risk_level in ['High', 'Very High']:
                risk_note = "⚠️ High risk investment - Consider position sizing"
            elif risk_level == 'Low':
                risk_note = "✅ Low risk investment - Suitable for conservative portfolios"
            else:
                risk_note = "📊 Medium risk investment - Standard due diligence required"
            
            recommendations = {
                "short_term": {
                    "recommendation": short_rec,
                    "confidence": f"{short_confidence}%",
                    "timeframe": "1-7 days"
                },
                "medium_term": {
                    "recommendation": medium_rec,
                    "confidence": f"{medium_confidence}%",
                    "timeframe": "2 weeks - 2 months"
                },
                "long_term": {
                    "recommendation": long_rec,
                    "confidence": f"{long_confidence}%",
                    "timeframe": "3-12 months"
                },
                "risk_note": risk_note,
                "overall_sentiment": self._determine_overall_sentiment(short_rec, medium_rec, long_rec)
            }
            
            return recommendations
            
        except Exception as e:
            return {"error": f"Recommendation generation error: {str(e)}"}
    
    def _determine_overall_sentiment(self, short, medium, long):
        """Xác định sentiment tổng thể"""
        buy_signals = [short, medium, long].count("Strong Buy") + [short, medium, long].count("Buy") * 0.5
        sell_signals = [short, medium, long].count("Strong Sell") + [short, medium, long].count("Sell") * 0.5
        
        if buy_signals > sell_signals + 0.5:
            return "Bullish"
        elif sell_signals > buy_signals + 0.5:
            return "Bearish"
        else:
            return "Neutral"