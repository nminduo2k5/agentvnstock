import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import LSTM enhancement
try:
    from agents.lstm_price_predictor import LSTMPricePredictor
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    print("⚠️ LSTM predictor not available. Using traditional methods only.")

class PricePredictor:
    def __init__(self, vn_api=None, stock_info=None):
        self.name = "Advanced Price Predictor Agent with LSTM"
        self.vn_api = vn_api
        self.stock_info = stock_info
        self.ai_agent = None  # Will be set by main_agent
        self.crewai_collector = None  # Will be set from vn_api
        self.prediction_periods = {
            'short_term': [1, 3, 7],      # 1 ngày, 3 ngày, 1 tuần
            'medium_term': [14, 30, 60],   # 2 tuần, 1 tháng, 2 tháng
            'long_term': [90, 180, 365]    # 3 tháng, 6 tháng, 1 năm
        }
        
        # Initialize LSTM predictor if available
        if LSTM_AVAILABLE:
            self.lstm_predictor = LSTMPricePredictor(vn_api)
            print("✅ LSTM Price Predictor initialized")
        else:
            self.lstm_predictor = None
    
    def set_ai_agent(self, ai_agent):
        """Set AI agent for enhanced predictions"""
        self.ai_agent = ai_agent
        # Also set AI agent for LSTM predictor
        if self.lstm_predictor:
            self.lstm_predictor.set_ai_agent(ai_agent)
    
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
        """Dự đoán cổ phiếu Việt Nam với real data từ CrewAI + VNStock"""
        try:
            # Use provided VN API or initialize
            if not vn_api:
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from src.data.vn_stock_api import VNStockAPI
                vn_api = VNStockAPI()
            
            # Get CrewAI collector for real data
            self.crewai_collector = getattr(vn_api, 'crewai_collector', None)
            
            # Try to get real stock data from CrewAI first
            real_stock_data = None
            if self.crewai_collector and self.crewai_collector.enabled:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Get real stock news and data from CrewAI
                    stock_news = loop.run_until_complete(self.crewai_collector.get_stock_news(symbol, limit=5))
                    
                    # Get available symbols to find company info
                    symbols = loop.run_until_complete(self.crewai_collector.get_available_symbols())
                    company_info = next((s for s in symbols if s['symbol'] == symbol), {})
                    
                    loop.close()
                    
                    real_stock_data = {
                        'news': stock_news,
                        'company_info': company_info,
                        'data_source': 'CrewAI_Real'
                    }
                    print(f"✅ Got real data for {symbol} from CrewAI")
                    
                except Exception as e:
                    print(f"⚠️ CrewAI data failed for {symbol}: {e}")
            
            # Get VNStock data as primary source
            import asyncio
            from agents.stock_info import StockInfoDisplay
            
            stock_info = StockInfoDisplay(vn_api)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            detailed_data = loop.run_until_complete(stock_info.get_detailed_stock_data(symbol))
            loop.close()
            
            if not detailed_data or detailed_data.get('error'):
                # Fallback to VNStock direct call
                from vnstock import Vnstock
                stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
                hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                current_price = float(hist_data['close'].iloc[-1])
                data_source = "VCI_Direct" + ("_with_CrewAI" if real_stock_data else "")
            else:
                # Use real data from stock_info + CrewAI
                price_history = detailed_data['price_history']
                stock_data = detailed_data['stock_data']
                detailed_metrics = detailed_data['detailed_data']
                
                # Convert price_history to DataFrame for technical analysis
                import pandas as pd
                hist_data = pd.DataFrame(price_history)
                current_price = stock_data.price
                data_source = "VNStock_Real" + ("_with_CrewAI" if real_stock_data else "")
            
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
            
            # Apply machine learning enhancements
            ml_predictions = self._apply_ml_predictions(hist_data, technical_indicators)
            
            # Dự đoán giá theo từng khoảng thời gian với ML enhancement
            predictions = self._generate_multi_timeframe_predictions(hist_data, technical_indicators, ml_predictions)
            
            # Phân tích xu hướng dựa trên predictions (AFTER predictions)
            trend_analysis = self._analyze_market_trend(hist_data, predictions)
            
            # Tính toán độ tin cậy với ML validation
            confidence_scores = self._calculate_confidence_scores(hist_data, technical_indicators, ml_predictions)
            
            # Phân tích rủi ro
            risk_analysis = self._analyze_risk_metrics(hist_data)
            
            result = {
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
            
            # Add CrewAI real data if available
            if real_stock_data:
                result['crewai_news'] = real_stock_data['news']
                result['company_info'] = real_stock_data['company_info']
                result['news_sentiment'] = real_stock_data['news'].get('sentiment', 'Neutral')
                
                # Enhance predictions with news sentiment
                sentiment_score = real_stock_data['news'].get('sentiment_score', 0.5)
                if sentiment_score > 0.6:
                    result['sentiment_boost'] = 'Positive news may support higher prices'
                elif sentiment_score < 0.4:
                    result['sentiment_boost'] = 'Negative news may pressure prices'
            
            return result
            
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
            
            # Dự đoán giá theo từng khoảng thời gian
            predictions = self._generate_multi_timeframe_predictions(hist, technical_indicators)
            
            # Phân tích xu hướng dựa trên predictions (AFTER predictions)
            trend_analysis = self._analyze_market_trend(hist, predictions)
            
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
            
            return {k: round(float(v), 4) if isinstance(v, (int, float, np.number)) and not (np.isnan(float(v)) if isinstance(v, (int, float, np.number)) else False) else v for k, v in indicators.items()}
            
        except Exception as e:
            return {"error": f"Indicator calculation error: {str(e)}"}
    
    def _analyze_market_trend(self, data, predictions=None):
        """Phân tích xu hướng thị trường dựa trên dự đoán giá thực tế"""
        try:
            current_price = data['close'].iloc[-1]
            
            # Calculate technical indicators
            sma_5 = data['close'].rolling(5).mean().iloc[-1]
            sma_20 = data['close'].rolling(20).mean().iloc[-1]
            sma_50 = data['close'].rolling(50).mean().iloc[-1]
            ema_12 = data['close'].ewm(span=12).mean().iloc[-1]
            ema_26 = data['close'].ewm(span=26).mean().iloc[-1]
            
            # RSI calculation
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            macd = ema_12 - ema_26
            macd_signal = pd.Series([macd]).ewm(span=9).mean().iloc[0]
            
            # Volume analysis
            volume_trend = 0
            if 'volume' in data.columns and len(data) > 20:
                recent_vol = data['volume'].iloc[-5:].mean()
                avg_vol = data['volume'].iloc[-20:].mean()
                volume_trend = recent_vol / avg_vol if avg_vol > 0 else 1
            
            # Price momentum
            momentum_5 = (current_price - data['close'].iloc[-6]) / data['close'].iloc[-6] * 100
            momentum_20 = (current_price - data['close'].iloc[-21]) / data['close'].iloc[-21] * 100
            
            # Technical scoring (0-100)
            tech_score = 50  # Base neutral
            signals = []
            
            # Price vs MA (30 points)
            if current_price > sma_50:
                tech_score += 15
                signals.append("Above SMA50")
            if current_price > sma_20:
                tech_score += 10
                signals.append("Above SMA20")
            if current_price > sma_5:
                tech_score += 5
                signals.append("Above SMA5")
            
            # MA alignment (20 points)
            if sma_5 > sma_20 > sma_50:
                tech_score += 20
                signals.append("Bullish MA alignment")
            elif sma_5 < sma_20 < sma_50:
                tech_score -= 20
                signals.append("Bearish MA alignment")
            
            # MACD (15 points)
            if macd > macd_signal:
                tech_score += 15
                signals.append("MACD bullish")
            else:
                tech_score -= 15
                signals.append("MACD bearish")
            
            # RSI (15 points)
            if 30 < rsi < 70:
                tech_score += 10
                signals.append("RSI healthy")
            elif rsi < 30:
                tech_score += 15
                signals.append("RSI oversold")
            elif rsi > 70:
                tech_score -= 10
                signals.append("RSI overbought")
            
            # Momentum (20 points)
            if momentum_5 > 2:
                tech_score += 10
                signals.append("Strong 5d momentum")
            if momentum_20 > 5:
                tech_score += 10
                signals.append("Strong 20d momentum")
            
            # Volume confirmation (10 points)
            if volume_trend > 1.2:
                tech_score += 10
                signals.append("Volume supporting")
            
            # PRIORITY: Use actual price predictions to determine trend
            final_direction = "neutral"
            final_strength = "Neutral"
            
            if predictions:
                try:
                    # Get predictions and calculate changes from current price
                    pred_1d = predictions.get('short_term', {}).get('1_days', {})
                    pred_7d = predictions.get('short_term', {}).get('7_days', {})
                    pred_30d = predictions.get('medium_term', {}).get('30_days', {})
                    
                    # Calculate changes from ACTUAL prices vs current price
                    change_1d = 0
                    change_7d = 0
                    change_30d = 0
                    
                    if pred_1d.get('price'):
                        change_1d = ((float(pred_1d['price']) - float(current_price)) / float(current_price)) * 100
                    elif pred_1d.get('change_percent'):
                        change_1d = float(pred_1d['change_percent'])
                    
                    if pred_7d.get('price'):
                        change_7d = ((float(pred_7d['price']) - float(current_price)) / float(current_price)) * 100
                    elif pred_7d.get('change_percent'):
                        change_7d = float(pred_7d['change_percent'])
                    
                    if pred_30d.get('price'):
                        change_30d = ((float(pred_30d['price']) - float(current_price)) / float(current_price)) * 100
                    elif pred_30d.get('change_percent'):
                        change_30d = float(pred_30d['change_percent'])
                    
                    # Weighted average: 1d (30%), 7d (40%), 30d (30%)
                    avg_change = (change_1d * 0.3 + change_7d * 0.4 + change_30d * 0.3)
                    
                    # Primary logic: Use average change with thresholds
                    if avg_change > 3:  # Strong positive
                        final_direction = "bullish"
                        if avg_change > 8:
                            final_strength = "Strong Bullish"
                        elif avg_change > 5:
                            final_strength = "Moderate Bullish"
                        else:
                            final_strength = "Weak Bullish"
                        signals.append(f"Positive trend: 1d={change_1d:.1f}%, 7d={change_7d:.1f}%, 30d={change_30d:.1f}%, avg={avg_change:.1f}%")
                        
                    elif avg_change < -3:  # Strong negative
                        final_direction = "bearish"
                        if avg_change < -8:
                            final_strength = "Strong Bearish"
                        elif avg_change < -5:
                            final_strength = "Moderate Bearish"
                        else:
                            final_strength = "Weak Bearish"
                        signals.append(f"Negative trend: 1d={change_1d:.1f}%, 7d={change_7d:.1f}%, 30d={change_30d:.1f}%, avg={avg_change:.1f}%")
                        
                    elif abs(avg_change) <= 1.5:  # Very small changes
                        final_direction = "neutral"
                        final_strength = "Neutral"
                        signals.append(f"Sideways trend: 1d={change_1d:.1f}%, 7d={change_7d:.1f}%, 30d={change_30d:.1f}%, avg={avg_change:.1f}%")
                        
                    else:  # Weak signals - check consistency
                        # Check majority direction for weak signals
                        positive_count = sum(1 for x in [change_1d, change_7d, change_30d] if x > 0)
                        if positive_count >= 2:  # Majority positive
                            final_direction = "bullish"
                            final_strength = "Weak Bullish"
                            signals.append(f"Weak bullish: 1d={change_1d:.1f}%, 7d={change_7d:.1f}%, 30d={change_30d:.1f}%")
                        elif positive_count <= 1:  # Majority negative
                            final_direction = "bearish"
                            final_strength = "Weak Bearish"
                            signals.append(f"Weak bearish: 1d={change_1d:.1f}%, 7d={change_7d:.1f}%, 30d={change_30d:.1f}%")
                        else:  # Exactly mixed
                            final_direction = "neutral"
                            final_strength = "Neutral"
                            signals.append(f"Mixed signals: 1d={change_1d:.1f}%, 7d={change_7d:.1f}%, 30d={change_30d:.1f}%")
                    

                        
                except Exception as e:
                    print(f"⚠️ Prediction-based trend analysis failed: {e}")
                    # Fallback to technical analysis
                    if tech_score >= 65:
                        final_direction = "bullish"
                        final_strength = "Moderate Bullish"
                    elif tech_score <= 35:
                        final_direction = "bearish"
                        final_strength = "Moderate Bearish"
                    else:
                        final_direction = "neutral"
                        final_strength = "Neutral"
                    signals.append(f"Exception fallback to technical analysis (score: {tech_score})")
                    # Reset changes for fallback display
                    change_1d = change_7d = change_30d = 0
            else:
                # No predictions available - use technical analysis only
                if tech_score >= 75:
                    final_direction = "bullish"
                    final_strength = "Strong Bullish"
                elif tech_score >= 60:
                    final_direction = "bullish"
                    final_strength = "Moderate Bullish"
                elif tech_score >= 40:
                    final_direction = "neutral"
                    final_strength = "Neutral"
                elif tech_score >= 25:
                    final_direction = "bearish"
                    final_strength = "Moderate Bearish"
                else:
                    final_direction = "bearish"
                    final_strength = "Strong Bearish"
                signals.append(f"Technical analysis fallback (score: {tech_score})")
            
            # AI can provide additional insight but NOT override clear price trends
            ai_insight = ""
            if self.ai_agent:
                try:
                    ai_analysis = self._get_gemini_trend_analysis(
                        current_price, tech_score, rsi, macd, momentum_5, momentum_20, volume_trend
                    )
                    
                    if ai_analysis.get('ai_direction'):
                        ai_direction = ai_analysis['ai_direction']
                        # AI can enhance weak signals but not override strong price trends
                        if final_strength in ["Neutral", "Weak Bullish", "Weak Bearish"]:
                            # Allow AI to enhance weak signals
                            final_direction = ai_direction
                            final_strength = ai_analysis.get('ai_strength', final_strength)
                            signals.append(f"AI enhanced: {ai_direction}")
                        else:
                            # Strong price trends take priority
                            ai_insight = f" (AI suggests {ai_direction})"
                            signals.append(f"AI insight: {ai_direction} (price trend priority)")
                        
                except Exception as e:
                    print(f"⚠️ Gemini trend analysis failed: {e}")
            

            
            result = {
                "direction": final_direction,
                "strength": final_strength,
                "score": f"{tech_score}/100",
                "signals": signals,
                "rsi": round(rsi, 1),
                "macd": round(macd, 4),
                "momentum_5d": round(momentum_5, 2),
                "momentum_20d": round(momentum_20, 2),
                "volume_trend": round(volume_trend, 2),
                "support_level": round(data['close'].rolling(20).min().iloc[-1], 2),
                "resistance_level": round(data['close'].rolling(20).max().iloc[-1], 2),
                "prediction_based": True if predictions else False
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Trend analysis error: {str(e)}"}
    
    def _get_gemini_trend_analysis(self, price, tech_score, rsi, macd, momentum_5, momentum_20, volume_trend):
        """Get Gemini AI trend analysis"""
        try:
            context = f"""
Phân tích xu hướng kỹ thuật cho quyết định đầu tư:
- Điểm kỹ thuật: {tech_score}/100
- RSI: {rsi:.1f} ({'Quá mua' if rsi > 70 else 'Quá bán' if rsi < 30 else 'Bình thường'})
- MACD: {macd:.4f} ({'Tích cực' if macd > 0 else 'Tiêu cực'})
- Momentum 5 ngày: {momentum_5:.1f}%
- Momentum 20 ngày: {momentum_20:.1f}%
- Volume trend: {volume_trend:.2f}x

Hãy đưa ra quyết định xu hướng rõ ràng:
- Điểm ≥65: Xu hướng TĂNG mạnh
- Điểm ≤35: Xu hướng GIẢM mạnh  
- Điểm 36-64: Phân tích kỹ các chỉ báo

TREND: [BULLISH/BEARISH/NEUTRAL - phải chọn 1 trong 3]
STRENGTH: [Strong/Moderate/Weak]
REASON: [lý do cụ thể dựa trên chỉ báo]
"""
            
            ai_result = self.ai_agent.generate_with_fallback(context, 'trend_analysis', max_tokens=200)
            
            if ai_result['success']:
                response = ai_result['response']
                
                # Parse AI response
                ai_direction = None
                ai_strength = None
                
                if 'TREND: BULLISH' in response.upper() or 'XU HƯỚNG TĂNG' in response.upper():
                    ai_direction = 'bullish'
                elif 'TREND: BEARISH' in response.upper() or 'XU HƯỚNG GIẢM' in response.upper():
                    ai_direction = 'bearish'
                elif 'TREND: NEUTRAL' in response.upper() or 'TRUNG TÍNH' in response.upper():
                    ai_direction = 'neutral'
                # Additional patterns for stronger detection
                elif 'TĂNG MẠNH' in response.upper() or 'BULLISH' in response.upper():
                    ai_direction = 'bullish'
                elif 'GIẢM MẠNH' in response.upper() or 'BEARISH' in response.upper():
                    ai_direction = 'bearish'
                
                if 'STRENGTH: STRONG' in response.upper():
                    ai_strength = f"Strong {ai_direction.title()}" if ai_direction else "Strong"
                elif 'STRENGTH: MODERATE' in response.upper():
                    ai_strength = f"Moderate {ai_direction.title()}" if ai_direction else "Moderate"
                elif 'STRENGTH: WEAK' in response.upper():
                    ai_strength = f"Weak {ai_direction.title()}" if ai_direction else "Weak"
                
                return {
                    'ai_direction': ai_direction,
                    'ai_strength': ai_strength,
                    'ai_analysis': response
                }
            
            return {}
            
        except Exception as e:
            return {}
    
    def _apply_ml_predictions(self, data, indicators):
        """Apply machine learning-based predictions using simple models"""
        try:
            # Prepare features for ML
            features = self._prepare_ml_features(data, indicators)
            
            # Simple linear regression for trend prediction
            linear_prediction = self._linear_trend_prediction(data)
            
            # Moving average convergence prediction
            ma_prediction = self._moving_average_prediction(data)
            
            # Momentum-based prediction
            momentum_prediction = self._momentum_prediction(data, indicators)
            
            # Ensemble prediction (weighted average)
            ensemble_weights = [0.4, 0.3, 0.3]  # Linear, MA, Momentum
            ensemble_prediction = (
                linear_prediction * ensemble_weights[0] +
                ma_prediction * ensemble_weights[1] +
                momentum_prediction * ensemble_weights[2]
            )
            
            return {
                'linear_prediction': linear_prediction,
                'ma_prediction': ma_prediction,
                'momentum_prediction': momentum_prediction,
                'ensemble_prediction': ensemble_prediction,
                'ml_confidence': self._calculate_ml_confidence(data, [linear_prediction, ma_prediction, momentum_prediction]),
                'features_used': len(features)
            }
            
        except Exception as e:
            return {'error': f"ML prediction error: {str(e)}"}
    
    def _prepare_ml_features(self, data, indicators):
        """Prepare features for machine learning models"""
        try:
            features = []
            
            # Price-based features
            features.extend([
                indicators.get('sma_5', 0),
                indicators.get('sma_20', 0),
                indicators.get('sma_50', 0),
                indicators.get('ema_12', 0),
                indicators.get('ema_26', 0)
            ])
            
            # Technical indicator features
            features.extend([
                indicators.get('rsi', 50),
                indicators.get('macd', 0),
                indicators.get('bb_position', 0.5),
                indicators.get('stoch_k', 50),
                indicators.get('williams_r', -50)
            ])
            
            # Volume features (if available)
            if 'volume' in data.columns:
                features.extend([
                    indicators.get('volume_ratio', 1),
                    indicators.get('obv_trend', 0)
                ])
            
            # Volatility features
            features.extend([
                indicators.get('volatility', 20),
                indicators.get('atr', 0)
            ])
            
            return [f for f in features if f is not None and not np.isnan(f)]
            
        except Exception as e:
            return []
    
    def _linear_trend_prediction(self, data, days_ahead=30):
        """Simple linear regression trend prediction"""
        try:
            prices = data['close'].values[-60:]  # Use last 60 days
            if len(prices) < 10:
                return data['close'].iloc[-1]
            
            # Create time series
            x = np.arange(len(prices))
            
            # Simple linear regression
            slope = np.polyfit(x, prices, 1)[0]
            
            # Predict future price
            future_price = prices[-1] + (slope * days_ahead)
            
            return max(0, future_price)  # Ensure non-negative price
            
        except Exception as e:
            return data['close'].iloc[-1]
    
    def _moving_average_prediction(self, data):
        """Moving average convergence prediction"""
        try:
            sma_5 = data['close'].rolling(5).mean().iloc[-1]
            sma_20 = data['close'].rolling(20).mean().iloc[-1]
            sma_50 = data['close'].rolling(50).mean().iloc[-1]
            
            # Weighted prediction based on MA convergence
            if sma_5 > sma_20 > sma_50:  # Strong uptrend
                prediction = sma_5 * 1.05
            elif sma_5 < sma_20 < sma_50:  # Strong downtrend
                prediction = sma_5 * 0.95
            else:  # Neutral/mixed signals
                prediction = (sma_5 + sma_20 + sma_50) / 3
            
            return prediction
            
        except Exception as e:
            return data['close'].iloc[-1]
    
    def _momentum_prediction(self, data, indicators):
        """Momentum-based prediction using RSI and MACD"""
        try:
            current_price = data['close'].iloc[-1]
            rsi = indicators.get('rsi', 50)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            
            # RSI-based adjustment
            if rsi > 70:  # Overbought
                rsi_factor = 0.98
            elif rsi < 30:  # Oversold
                rsi_factor = 1.02
            else:
                rsi_factor = 1.0
            
            # MACD-based adjustment
            if macd > macd_signal:  # Bullish
                macd_factor = 1.01
            else:  # Bearish
                macd_factor = 0.99
            
            prediction = current_price * rsi_factor * macd_factor
            
            return prediction
            
        except Exception as e:
            return data['close'].iloc[-1]
    
    def _calculate_ml_confidence(self, data, predictions):
        """Calculate confidence based on ML model agreement"""
        try:
            if len(predictions) < 2:
                return 50
            
            current_price = data['close'].iloc[-1]
            
            # Calculate prediction variance
            pred_array = np.array(predictions)
            variance = np.var(pred_array) / (current_price ** 2)  # Normalized variance
            
            # Lower variance = higher confidence
            confidence = max(30, min(90, 80 - (variance * 1000)))
            
            return round(confidence, 1)
            
        except Exception as e:
            return 50
    
    def _generate_multi_timeframe_predictions(self, data, indicators, ml_predictions=None):
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
            
            # Use ML ensemble prediction if available
            ml_adjustment = 0
            if ml_predictions and not ml_predictions.get('error'):
                ensemble_pred = ml_predictions.get('ensemble_prediction', current_price)
                ml_adjustment = (ensemble_pred - current_price) / current_price
                # Limit ML adjustment to reasonable range
                ml_adjustment = max(-0.15, min(0.15, ml_adjustment))
            
            for period_type, days_list in self.prediction_periods.items():
                predictions[period_type] = {}
                
                for days in days_list:
                    # Thuật toán dự đoán kết hợp nhiều yếu tố + ML
                    base_change = self._calculate_base_change(days, volatility, trend_multiplier)
                    
                    # Apply ML adjustment with time decay
                    time_decay = max(0.1, 1 - (days / 365))  # ML more relevant for shorter periods
                    ml_contribution = ml_adjustment * time_decay * 0.3  # 30% weight for ML
                    
                    # Điều chỉnh dựa trên MACD
                    macd_adjustment = macd_signal * min(0.02, volatility * 0.1) * (days / 30)
                    
                    # Điều chỉnh dựa trên RSI
                    rsi_adjustment = self._calculate_rsi_adjustment(rsi, days)
                    
                    # Điều chỉnh dựa trên Bollinger Bands
                    bb_adjustment = self._calculate_bb_adjustment(bb_position, days)
                    
                    # Tổng hợp các điều chỉnh bao gồm ML
                    total_change = base_change + ml_contribution + macd_adjustment + rsi_adjustment + bb_adjustment
                    
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

    def predict_price(self, symbol: str):
        """Simple price prediction for backward compatibility"""
        return self.predict_comprehensive(symbol, self.vn_api, self.stock_info)
    
    def predict_price_enhanced(self, symbol: str, days: int = 30, risk_tolerance: int = 50, time_horizon: str = "Trung hạn", investment_amount: int = 10000000):
        """Enhanced price prediction with LSTM priority and AI analysis"""
        # Try LSTM first if available and prioritize it
        if self.lstm_predictor:
            try:
                lstm_result = self.lstm_predictor.predict_with_ai_enhancement(symbol, days)
                if not lstm_result.get('error') and lstm_result['model_performance']['confidence'] > 20:
                    # LSTM successful with acceptable confidence - use it as primary
                    combined_result = self._combine_lstm_with_traditional(lstm_result, symbol)
                    
                    # Add investment profile analysis
                    combined_result['risk_adjusted_analysis'] = self._get_risk_adjusted_analysis(
                        combined_result, risk_tolerance, time_horizon, investment_amount
                    )
                    
                    # Set main prediction values from LSTM
                    lstm_30d = lstm_result['predictions'].get('medium_term', {}).get('30_days', {})
                    if lstm_30d:
                        combined_result['predicted_price'] = lstm_30d['price']
                        combined_result['change_percent'] = ((lstm_30d['price'] - combined_result['current_price']) / combined_result['current_price']) * 100
                        combined_result['timeframe'] = f"{days} days"
                        combined_result['confidence'] = lstm_result['model_performance']['confidence']
                        combined_result['trend'] = combined_result.get('trend_analysis', {}).get('direction', 'neutral')
                        combined_result['method_used'] = 'LSTM Primary'
                    
                    return combined_result
                else:
                    print(f"⚠️ LSTM confidence too low ({lstm_result.get('model_performance', {}).get('confidence', 0)}%) or error, falling back to traditional")
            except Exception as e:
                print(f"⚠️ LSTM prediction failed: {e}, falling back to traditional")
        
        # Fallback to traditional comprehensive prediction
        result = self.predict_comprehensive(symbol, self.vn_api, self.stock_info)
        
        if "error" in result:
            return result
        
        # Find the closest prediction timeframe for main predicted_price
        if days <= 7:
            prediction_data = result['predictions']['short_term']['7_days']
        elif days <= 30:
            prediction_data = result['predictions']['medium_term']['30_days']
        elif days <= 90:
            prediction_data = result['predictions']['medium_term']['60_days']
        else:
            prediction_data = result['predictions']['long_term']['180_days']
        
        # Return COMPLETE result with predicted_price for the specific timeframe
        result['predicted_price'] = prediction_data['price']
        result['change_percent'] = prediction_data['change_percent']
        result['timeframe'] = f"{days} days"
        result['confidence'] = result['confidence_scores'].get('medium_term', 50)
        result['trend'] = result['trend_analysis']['direction']
        
        # Add risk-adjusted analysis
        result['risk_adjusted_analysis'] = self._get_risk_adjusted_analysis(
            result, risk_tolerance, time_horizon, investment_amount
        )
        
        # Add AI enhancement if available - ALWAYS try to get AI advice
        if self.ai_agent:
            try:
                ai_analysis = self._get_ai_price_analysis(symbol, result, days, risk_tolerance, time_horizon)
                result.update(ai_analysis)
                
                # Use AI-adjusted predictions if available
                if ai_analysis.get('ai_adjusted_predictions'):
                    result['predictions'] = ai_analysis['ai_adjusted_predictions']
                    result['predicted_price'] = ai_analysis['ai_adjusted_predictions']['medium_term']['30_days']['price']
                    result['change_percent'] = ai_analysis['ai_adjusted_predictions']['medium_term']['30_days']['change_percent']
                    
                # Update trend analysis with AI insights
                if ai_analysis.get('ai_trend'):
                    result['trend_analysis']['ai_direction'] = ai_analysis['ai_trend']
                    result['trend_analysis']['ai_support'] = ai_analysis.get('ai_support', result['trend_analysis']['support_level'])
                    result['trend_analysis']['ai_resistance'] = ai_analysis.get('ai_resistance', result['trend_analysis']['resistance_level'])
                    
            except Exception as e:
                print(f"⚠️ AI analysis failed: {e}")
                result['ai_enhanced'] = False
                result['ai_error'] = str(e)
        else:
            # No AI agent available
            result['ai_enhanced'] = False
            result['ai_error'] = 'AI agent not configured'
        
        return result
    
    def _combine_lstm_with_traditional(self, lstm_result: dict, symbol: str):
        """Combine LSTM predictions with traditional technical analysis"""
        try:
            # Get traditional analysis for technical indicators and risk metrics
            traditional_result = self.predict_comprehensive(symbol, self.vn_api, self.stock_info)
            
            if traditional_result.get('error'):
                # If traditional fails, return LSTM only
                return lstm_result
            
            # Create combined result
            combined_result = {
                'symbol': symbol,
                'current_price': lstm_result['current_price'],
                'market': traditional_result.get('market', 'Unknown'),
                'data_source': f"LSTM + {traditional_result.get('data_source', 'Technical')}",
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                
                # Use traditional technical indicators
                'technical_indicators': traditional_result.get('technical_indicators', {}),
                'trend_analysis': traditional_result.get('trend_analysis', {}),
                'risk_analysis': traditional_result.get('risk_analysis', {}),
                
                # Use LSTM predictions as primary
                'predictions': lstm_result['predictions'],
                'lstm_confidence': lstm_result['model_performance']['confidence'],
                'lstm_method': lstm_result['method'],
                
                # Combine confidence scores
                'confidence_scores': self._combine_confidence_scores(
                    lstm_result['model_performance']['confidence'],
                    traditional_result.get('confidence_scores', {})
                ),
                
                # Enhanced recommendations
                'recommendations': self._generate_combined_recommendations(
                    lstm_result, traditional_result
                ),
                
                # Method tracking
                'prediction_methods': ['LSTM Neural Network', 'Technical Analysis'],
                'primary_method': 'LSTM Enhanced'
            }
            
            # Add AI enhancements if available
            if lstm_result.get('ai_enhanced'):
                combined_result['ai_enhanced'] = True
                combined_result['ai_lstm_analysis'] = lstm_result.get('ai_lstm_analysis', '')
                combined_result['ai_model_used'] = lstm_result.get('ai_model_used', 'Gemini')
            
            return combined_result
            
        except Exception as e:
            print(f"⚠️ Failed to combine LSTM with traditional: {e}")
            return lstm_result
    
    def _combine_confidence_scores(self, lstm_confidence: float, traditional_scores: dict):
        """Combine LSTM and traditional confidence scores"""
        try:
            # Weight LSTM higher for short/medium term, traditional for long term
            combined_scores = {
                'short_term': round(lstm_confidence * 0.7 + traditional_scores.get('short_term', 50) * 0.3, 1),
                'medium_term': round(lstm_confidence * 0.6 + traditional_scores.get('medium_term', 50) * 0.4, 1),
                'long_term': round(lstm_confidence * 0.3 + traditional_scores.get('long_term', 50) * 0.7, 1),
                'lstm_confidence': lstm_confidence,
                'combined_method': True
            }
            
            return combined_scores
            
        except Exception as e:
            return {'short_term': 50, 'medium_term': 50, 'long_term': 50, 'error': str(e)}
    
    def _generate_combined_recommendations(self, lstm_result: dict, traditional_result: dict):
        """Generate recommendations combining LSTM and traditional analysis"""
        try:
            lstm_predictions = lstm_result.get('predictions', {})
            traditional_recs = traditional_result.get('recommendations', {})
            current_price = lstm_result['current_price']
            
            recommendations = {}
            
            # Short-term: Use LSTM primarily
            lstm_7d = lstm_predictions.get('short_term', {}).get('7_days', {})
            if lstm_7d:
                change_7d = ((lstm_7d['price'] - current_price) / current_price) * 100
                if change_7d > 3:
                    short_rec = "Buy (LSTM)"
                elif change_7d > 1:
                    short_rec = "Weak Buy (LSTM)"
                elif change_7d > -1:
                    short_rec = "Hold (LSTM)"
                elif change_7d > -3:
                    short_rec = "Weak Sell (LSTM)"
                else:
                    short_rec = "Sell (LSTM)"
            else:
                short_rec = traditional_recs.get('short_term', {}).get('recommendation', 'Hold')
            
            # Medium-term: Combine LSTM and traditional
            lstm_30d = lstm_predictions.get('medium_term', {}).get('30_days', {})
            traditional_medium = traditional_recs.get('medium_term', {}).get('recommendation', 'Hold')
            
            if lstm_30d:
                change_30d = ((lstm_30d['price'] - current_price) / current_price) * 100
                if change_30d > 5 and 'Buy' in traditional_medium:
                    medium_rec = "Strong Buy (Combined)"
                elif change_30d > 2:
                    medium_rec = f"Buy (LSTM + {traditional_medium})"
                elif change_30d > -2:
                    medium_rec = f"Hold (LSTM + {traditional_medium})"
                else:
                    medium_rec = f"Sell (LSTM + {traditional_medium})"
            else:
                medium_rec = traditional_medium
            
            # Long-term: Use traditional primarily
            long_rec = traditional_recs.get('long_term', {}).get('recommendation', 'Hold')
            
            recommendations = {
                'short_term': {
                    'recommendation': short_rec,
                    'confidence': f"{lstm_result['model_performance']['confidence']:.1f}%",
                    'timeframe': '1-7 days',
                    'method': 'LSTM Primary'
                },
                'medium_term': {
                    'recommendation': medium_rec,
                    'confidence': f"{(lstm_result['model_performance']['confidence'] + traditional_result.get('confidence_scores', {}).get('medium_term', 50)) / 2:.1f}%",
                    'timeframe': '2 weeks - 2 months',
                    'method': 'LSTM + Technical'
                },
                'long_term': {
                    'recommendation': long_rec,
                    'confidence': traditional_recs.get('long_term', {}).get('confidence', '50%'),
                    'timeframe': '3-12 months',
                    'method': 'Technical Analysis'
                },
                'overall_sentiment': self._determine_combined_sentiment(short_rec, medium_rec, long_rec),
                'risk_note': traditional_recs.get('risk_note', '📊 Combined LSTM + Technical Analysis')
            }
            
            return recommendations
            
        except Exception as e:
            return {'error': f'Combined recommendation error: {str(e)}'}
    
    def _determine_combined_sentiment(self, short: str, medium: str, long: str):
        """Determine overall sentiment from combined recommendations"""
        try:
            buy_count = sum(1 for rec in [short, medium, long] if 'Buy' in rec)
            sell_count = sum(1 for rec in [short, medium, long] if 'Sell' in rec)
            
            if buy_count >= 2:
                return "Bullish (LSTM Enhanced)"
            elif sell_count >= 2:
                return "Bearish (LSTM Enhanced)"
            else:
                return "Neutral (Mixed Signals)"
                
        except Exception as e:
            return "Neutral"
    
    def _get_risk_adjusted_analysis(self, result: dict, risk_tolerance: int, time_horizon: str, investment_amount: int):
        """Generate risk-adjusted analysis based on user profile"""
        try:
            current_price = result['current_price']
            volatility = result.get('technical_indicators', {}).get('volatility', 20)
            
            # Determine risk profile
            if risk_tolerance <= 30:
                risk_profile = "Conservative"
                max_position_size = 0.05  # 5% max position
                stop_loss_pct = 5  # 5% stop loss
                target_return = 8  # 8% annual target
            elif risk_tolerance <= 70:
                risk_profile = "Moderate"
                max_position_size = 0.10  # 10% max position
                stop_loss_pct = 8  # 8% stop loss
                target_return = 15  # 15% annual target
            else:
                risk_profile = "Aggressive"
                max_position_size = 0.20  # 20% max position
                stop_loss_pct = 12  # 12% stop loss
                target_return = 25  # 25% annual target
            
            # Calculate position sizing
            max_investment = investment_amount * max_position_size
            shares_to_buy = int(max_investment / current_price)
            actual_investment = shares_to_buy * current_price
            
            # Calculate stop loss and take profit levels
            stop_loss_price = current_price * (1 - stop_loss_pct / 100)
            
            # Adjust target based on time horizon
            time_multiplier = {"Ngắn hạn": 0.5, "Trung hạn": 1.0, "Dài hạn": 1.5}.get(time_horizon, 1.0)
            adjusted_target_return = target_return * time_multiplier
            take_profit_price = current_price * (1 + adjusted_target_return / 100)
            
            # Risk assessment
            risk_score = min(10, max(1, (volatility / 5) + (10 - risk_tolerance / 10)))
            
            # Generate recommendations
            recommendations = []
            if risk_profile == "Conservative":
                recommendations.extend([
                    "Ưu tiên cổ phiếu blue-chip với cổ tức ổn định",
                    "Đầu tư định kỳ (DCA) để giảm rủi ro thời điểm",
                    "Không nên đầu tư quá 5% tổng tài sản vào 1 cổ phiếu"
                ])
            elif risk_profile == "Moderate":
                recommendations.extend([
                    "Cân bằng giữa tăng trưởng và ổn định",
                    "Có thể chấp nhận biến động ngắn hạn",
                    "Đa dạng hóa danh mục với 8-12 cổ phiếu"
                ])
            else:
                recommendations.extend([
                    "Tập trung vào cổ phiếu tăng trưởng cao",
                    "Có thể sử dụng margin với thận trọng",
                    "Chấp nhận biến động mạnh để đạt lợi nhuận cao"
                ])
            
            # Add volatility-based recommendations
            if volatility > 30:
                recommendations.append("⚠️ Cổ phiếu có độ biến động cao - cân nhắc giảm tỷ trọng")
            elif volatility < 15:
                recommendations.append("✅ Cổ phiếu ổn định - phù hợp với chiến lược dài hạn")
            
            return {
                'risk_profile': risk_profile,
                'risk_tolerance': risk_tolerance,
                'risk_score': round(risk_score, 1),
                'position_sizing': {
                    'max_investment': max_investment,
                    'recommended_shares': shares_to_buy,
                    'actual_investment': actual_investment,
                    'position_percentage': round(actual_investment / investment_amount * 100, 2)
                },
                'risk_management': {
                    'stop_loss_price': round(stop_loss_price, 2),
                    'stop_loss_pct': stop_loss_pct,
                    'take_profit_price': round(take_profit_price, 2),
                    'target_return_pct': adjusted_target_return
                },
                'recommendations': recommendations,
                'time_horizon': time_horizon,
                'suitability_score': self._calculate_suitability_score(result, risk_tolerance, volatility)
            }
            
        except Exception as e:
            return {'error': f"Risk analysis error: {str(e)}"}
    
    def _calculate_suitability_score(self, result: dict, risk_tolerance: int, volatility: float):
        """Calculate how suitable this stock is for the user's risk profile"""
        try:
            score = 50  # Base score
            
            # Adjust based on volatility vs risk tolerance
            vol_risk_match = 100 - abs(volatility - risk_tolerance)
            score += (vol_risk_match - 50) * 0.3
            
            # Adjust based on trend strength
            trend_direction = result.get('trend_analysis', {}).get('direction', 'neutral')
            if trend_direction == 'bullish':
                score += 15
            elif trend_direction == 'bearish':
                score -= 15
            
            # Adjust based on technical indicators
            rsi = result.get('technical_indicators', {}).get('rsi', 50)
            if 30 <= rsi <= 70:  # Good RSI range
                score += 10
            elif rsi > 80 or rsi < 20:  # Extreme RSI
                score -= 10
            
            # Adjust based on confidence
            confidence = result.get('confidence_scores', {}).get('medium_term', 50)
            score += (confidence - 50) * 0.2
            
            return max(0, min(100, round(score, 1)))
            
        except Exception as e:
            return 50  # Default neutral score
    
    def _get_ai_price_analysis(self, symbol: str, technical_data: dict, days: int, risk_tolerance: int = 50, time_horizon: str = "Trung hạn"):
        """Get AI-enhanced price analysis with REAL prediction adjustments and risk-aware recommendations"""
        try:
            # Determine risk profile for AI context
            risk_profile = "Conservative" if risk_tolerance <= 30 else "Moderate" if risk_tolerance <= 70 else "Aggressive"
            
            # Get technical indicators safely
            tech_indicators = technical_data.get('technical_indicators', {})
            trend_analysis = technical_data.get('trend_analysis', {})
            current_price = technical_data.get('current_price', 0)
            rsi = tech_indicators.get('rsi', 50)
            volatility = tech_indicators.get('volatility', 25)
            trend_direction = trend_analysis.get('direction', 'neutral')
            
            # Generate detailed fallback advice based on real data from sidebar
            fallback_advice = self._generate_detailed_fallback_advice(
                symbol, current_price, rsi, volatility, trend_direction, 
                risk_profile, risk_tolerance, time_horizon
            )
            
            # Try AI analysis with shorter timeout and simpler prompt
            if self.ai_agent:
                try:
                    # Simplified context to avoid timeout
                    context = f"""
Phân tích {symbol}:
- Giá: {current_price:,.0f} VND
- RSI: {rsi:.1f}
- Xu hướng: {trend_direction}
- Nhà đầu tư: {risk_profile} ({risk_tolerance}%)
- Thời gian: {time_horizon}

Đưa ra lời khuyên ngắn gọn:
ADVICE: [mua/bán/giữ và lý do]
REASONING: [giải thích ngắn]
"""
                    
                    # Use shorter timeout to avoid 503 errors
                    ai_result = self.ai_agent.generate_with_fallback(context, 'price_prediction', max_tokens=300)
                    
                    if ai_result.get('success') and ai_result.get('response'):
                        # Parse AI response for advice and reasoning
                        ai_advice, ai_reasoning = self._parse_ai_advice(ai_result['response'])
                        
                        # Use AI advice if valid, otherwise use fallback
                        final_advice = ai_advice if ai_advice and len(ai_advice) > 10 else fallback_advice['advice']
                        final_reasoning = ai_reasoning if ai_reasoning and len(ai_reasoning) > 10 else fallback_advice['reasoning']
                        
                        return {
                            'ai_analysis': ai_result['response'],
                            'ai_model_used': ai_result.get('model_used', 'Gemini'),
                            'ai_enhanced': True,
                            'ai_advice': final_advice,
                            'ai_reasoning': final_reasoning,
                            'enhanced_confidence': max(10, min(95, 
                                technical_data.get('confidence_scores', {}).get('medium_term', 50) + 5
                            ))
                        }
                    else:
                        # AI failed, use detailed fallback
                        return {
                            'ai_enhanced': False,
                            'ai_error': ai_result.get('error', 'AI response invalid'),
                            'ai_advice': fallback_advice['advice'],
                            'ai_reasoning': fallback_advice['reasoning']
                        }
                        
                except Exception as ai_error:
                    # AI completely failed, use detailed fallback
                    error_msg = str(ai_error)
                    if "503" in error_msg or "overloaded" in error_msg.lower():
                        error_msg = "AI đang quá tải, vui lòng thử lại sau"
                    elif "timeout" in error_msg.lower():
                        error_msg = "AI phản hồi chậm, sử dụng phân tích kỹ thuật"
                    
                    return {
                        'ai_enhanced': False,
                        'ai_error': error_msg,
                        'ai_advice': fallback_advice['advice'],
                        'ai_reasoning': fallback_advice['reasoning']
                    }
            else:
                # No AI agent, use detailed fallback
                return {
                    'ai_enhanced': False,
                    'ai_error': 'AI chưa được cấu hình',
                    'ai_advice': fallback_advice['advice'],
                    'ai_reasoning': fallback_advice['reasoning']
                }
                
        except Exception as e:
            # Fallback for any other errors
            return {
                'ai_enhanced': False, 
                'ai_error': f'Lỗi hệ thống: {str(e)}',
                'ai_advice': f"Theo dõi {symbol} với RSI {rsi:.1f} và xu hướng {trend_direction}",
                'ai_reasoning': "Sử dụng phân tích kỹ thuật cơ bản do lỗi hệ thống"
            }
    
    def _parse_ai_price_adjustments(self, ai_response: str):
        """Parse AI response for numerical adjustments"""
        import re
        adjustments = {
            'price_adj': 0,
            'confidence_adj': 0, 
            'trend': 'neutral',
            'support_adj': 0,
            'resistance_adj': 0,
            'reason': ai_response
        }
        
        try:
            # Extract price adjustment
            price_match = re.search(r'PRICE_ADJUSTMENT:\s*([+-]?\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if price_match:
                adjustments['price_adj'] = float(price_match.group(1))
            
            # Extract confidence adjustment  
            conf_match = re.search(r'CONFIDENCE_ADJUSTMENT:\s*([+-]?\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if conf_match:
                adjustments['confidence_adj'] = float(conf_match.group(1))
            
            # Extract AI trend
            trend_match = re.search(r'AI_TREND:\s*(BULLISH|BEARISH|NEUTRAL)', ai_response, re.IGNORECASE)
            if trend_match:
                adjustments['trend'] = trend_match.group(1).lower()
            
            # Extract support/resistance adjustments
            support_match = re.search(r'SUPPORT_ADJUSTMENT:\s*([+-]?\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if support_match:
                adjustments['support_adj'] = float(support_match.group(1))
                
            resistance_match = re.search(r'RESISTANCE_ADJUSTMENT:\s*([+-]?\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if resistance_match:
                adjustments['resistance_adj'] = float(resistance_match.group(1))
                
        except Exception as e:
            print(f"⚠️ AI adjustment parsing failed: {e}")
            
        return adjustments
    
    def _generate_detailed_fallback_advice(self, symbol: str, current_price: float, rsi: float, 
                                          volatility: float, trend_direction: str, risk_profile: str, 
                                          risk_tolerance: int, time_horizon: str):
        """Generate detailed fallback advice using real data from sidebar"""
        try:
            # Analyze RSI signals
            if rsi > 70:
                rsi_signal = "quá mua"
                rsi_action = "cân nhắc chốt lời hoặc chờ điều chỉnh"
            elif rsi < 30:
                rsi_signal = "quá bán"
                rsi_action = "có thể tìm cơ hội mua vào"
            else:
                rsi_signal = "trung tính"
                rsi_action = "theo dõi thêm tín hiệu khác"
            
            # Analyze volatility
            if volatility > 30:
                vol_assessment = "biến động cao"
                vol_advice = "cần quản lý rủi ro chặt chẽ"
            elif volatility < 15:
                vol_assessment = "ổn định"
                vol_advice = "phù hợp đầu tư dài hạn"
            else:
                vol_assessment = "biến động vừa phải"
                vol_advice = "cần theo dõi xu hướng"
            
            # Generate advice based on risk profile and data
            if risk_profile == "Conservative":
                if trend_direction == "bullish" and rsi < 60 and volatility < 25:
                    advice = f"Có thể cân nhắc mua {symbol} với tỷ trọng nhỏ (5-10% danh mục)"
                    reasoning = f"Xu hướng tăng, RSI {rsi:.1f} chưa quá mua, volatility {volatility:.1f}% chấp nhận được cho nhà đầu tư thận trọng"
                elif rsi > 70:
                    advice = f"Nên chờ {symbol} điều chỉnh trước khi mua"
                    reasoning = f"RSI {rsi:.1f} cho thấy {rsi_signal}, không phù hợp với chiến lược thận trọng"
                else:
                    advice = f"Giữ quan sát {symbol}, chưa có tín hiệu rõ ràng"
                    reasoning = f"Với hồ sơ thận trọng, cần tín hiệu mạnh hơn. Hiện tại RSI {rsi:.1f}, xu hướng {trend_direction}"
                    
            elif risk_profile == "Moderate":
                if trend_direction == "bullish" and rsi < 70:
                    advice = f"Có thể mua {symbol} với tỷ trọng 10-15% danh mục"
                    reasoning = f"Xu hướng {trend_direction}, RSI {rsi:.1f} còn dư địa, phù hợp với chiến lược cân bằng"
                elif trend_direction == "bearish" and rsi > 50:
                    advice = f"Cân nhắc giảm tỷ trọng {symbol} hoặc chờ tín hiệu phục hồi"
                    reasoning = f"Xu hướng giảm, RSI {rsi:.1f} chưa oversold, nên thận trọng"
                else:
                    advice = f"Có thể DCA {symbol} với khối lượng nhỏ định kỳ"
                    reasoning = f"Chiến lược trung bình hóa chi phí phù hợp khi thị trường {trend_direction}, RSI {rsi:.1f}"
                    
            else:  # Aggressive
                if trend_direction == "bullish":
                    advice = f"Có thể tăng tỷ trọng {symbol} lên 15-20% danh mục"
                    reasoning = f"Xu hướng tăng mạnh, RSI {rsi:.1f}, nhà đầu tư mạo hiểm có thể tận dụng momentum"
                elif rsi < 30:
                    advice = f"Cơ hội mua {symbol} khi RSI oversold"
                    reasoning = f"RSI {rsi:.1f} {rsi_signal}, có thể là cơ hội tốt cho nhà đầu tư mạo hiểm"
                else:
                    advice = f"Có thể swing trade {symbol} dựa trên biến động"
                    reasoning = f"Volatility {volatility:.1f}% tạo cơ hội giao dịch ngắn hạn cho nhà đầu tư mạo hiểm"
            
            # Add time horizon consideration
            if time_horizon == "Ngắn hạn":
                advice += " trong 1-3 tháng tới"
                reasoning += f". Khung thời gian ngắn phù hợp với {vol_assessment}"
            elif time_horizon == "Dài hạn":
                advice += " và giữ dài hạn"
                reasoning += f". Đầu tư dài hạn giúp giảm thiểu rủi ro từ {vol_assessment}"
            
            return {
                'advice': advice,
                'reasoning': reasoning
            }
            
        except Exception as e:
            return {
                'advice': f"Theo dõi {symbol} với RSI {rsi:.1f} và xu hướng {trend_direction}",
                'reasoning': f"Phân tích kỹ thuật cơ bản cho nhà đầu tư {risk_profile.lower()}"
            }
    
    def _parse_ai_advice(self, ai_response: str):
        """Parse AI response for advice and reasoning"""
        import re
        
        advice = ""
        reasoning = ""
        
        try:
            # Extract advice
            advice_match = re.search(r'ADVICE:\s*(.+?)(?=\n|REASONING:|$)', ai_response, re.IGNORECASE | re.DOTALL)
            if advice_match:
                advice = advice_match.group(1).strip()
            
            # Extract reasoning
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?=\n\n|$)', ai_response, re.IGNORECASE | re.DOTALL)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
            
            # Fallback: use entire response if no structured format
            if not advice and not reasoning:
                lines = ai_response.strip().split('\n')
                if len(lines) >= 2:
                    advice = lines[0]
                    reasoning = ' '.join(lines[1:])
                elif ai_response.strip():
                    # Use entire response as advice if it's meaningful
                    advice = ai_response[:150] + "..." if len(ai_response) > 150 else ai_response
                    reasoning = "Phân tích tổng hợp từ AI"
                    
        except Exception as e:
            print(f"⚠️ AI advice parsing failed: {e}")
            
        return advice, reasoning
    
    def _apply_ai_price_adjustments(self, base_predictions: dict, current_price: float, ai_adjustments: dict):
        """Apply AI adjustments to base predictions"""
        try:
            adjusted_predictions = {}
            price_adj_factor = 1 + (ai_adjustments.get('price_adj', 0) / 100)
            
            for timeframe, predictions in base_predictions.items():
                adjusted_predictions[timeframe] = {}
                for period, data in predictions.items():
                    original_price = data['price']
                    adjusted_price = original_price * price_adj_factor
                    
                    # Ensure reasonable bounds
                    max_change = 0.3  # 30% max change
                    min_price = current_price * (1 - max_change)
                    max_price = current_price * (1 + max_change)
                    adjusted_price = max(min_price, min(max_price, adjusted_price))
                    
                    adjusted_predictions[timeframe][period] = {
                        'price': round(adjusted_price, 2),
                        'change_percent': round(((adjusted_price - current_price) / current_price) * 100, 2),
                        'change_amount': round(adjusted_price - current_price, 2),
                        'ai_adjusted': True
                    }
            
            return adjusted_predictions
            
        except Exception as e:
            print(f"⚠️ AI adjustment application failed: {e}")
            return base_predictions
    
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
    
    def _calculate_confidence_scores(self, data, indicators, ml_predictions=None):
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
            
            # ML confidence boost if available
            ml_confidence_boost = 0
            if ml_predictions and not ml_predictions.get('error'):
                ml_confidence = ml_predictions.get('ml_confidence', 50)
                ml_confidence_boost = (ml_confidence - 50) * 0.2  # 20% weight for ML confidence
            
            # Overall confidence for different timeframes with ML enhancement
            base_short = data_quality * 0.2 + volatility_score * 0.3 + trend_consistency * 0.3 + volume_score * 0.2
            base_medium = data_quality * 0.3 + volatility_score * 0.2 + trend_consistency * 0.4 + volume_score * 0.1
            base_long = data_quality * 0.4 + volatility_score * 0.1 + trend_consistency * 0.5
            
            scores['short_term'] = round(max(10, min(95, base_short + ml_confidence_boost)), 1)
            scores['medium_term'] = round(max(10, min(95, base_medium + ml_confidence_boost * 0.8)), 1)
            scores['long_term'] = round(max(10, min(95, base_long + ml_confidence_boost * 0.5)), 1)
            
            # Add ML-specific metrics if available
            if ml_predictions and not ml_predictions.get('error'):
                scores['ml_enhanced'] = True
                scores['ml_confidence'] = ml_predictions.get('ml_confidence', 50)
                scores['features_used'] = ml_predictions.get('features_used', 0)
            
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