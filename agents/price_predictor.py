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
        """Phân tích xu hướng thị trường với logic tối ưu"""
        try:
            current_price = data['close'].iloc[-1]
            
            # 1. Tính toán chỉ báo kỹ thuật
            indicators = self._calculate_technical_indicators(data)
            
            # 2. Tính điểm kỹ thuật (0-100)
            tech_score, tech_signals = self._calculate_technical_score(current_price, indicators)
            
            # 3. Phân tích dự đoán giá (ưu tiên cao nhất)
            if predictions:
                direction, strength, pred_signals = self._analyze_price_predictions(current_price, predictions)
            else:
                direction, strength, pred_signals = self._analyze_technical_only(tech_score)
            
            # 4. Kết quả cuối cùng
            return {
                "direction": direction,
                "strength": strength,
                "score": f"{tech_score}/100",
                "signals": tech_signals + pred_signals,
                "rsi": round(indicators['rsi'], 1),
                "macd": round(indicators['macd'], 4),
                "momentum_5d": round(indicators['momentum_5'], 2),
                "momentum_20d": round(indicators['momentum_20'], 2),
                "volume_trend": round(indicators['volume_trend'], 2),
                "support_level": round(data['close'].rolling(20).min().iloc[-1], 2),
                "resistance_level": round(data['close'].rolling(20).max().iloc[-1], 2),
                "prediction_based": bool(predictions)
            }
            
        except Exception as e:
            return {"error": f"Trend analysis error: {str(e)}"}
    
    def _calculate_technical_indicators(self, data):
        """Tính toán các chỉ báo kỹ thuật"""
        current_price = data['close'].iloc[-1]
        
        # Moving averages
        sma_5 = data['close'].rolling(5).mean().iloc[-1]
        sma_20 = data['close'].rolling(20).mean().iloc[-1]
        sma_50 = data['close'].rolling(50).mean().iloc[-1]
        ema_12 = data['close'].ewm(span=12).mean().iloc[-1]
        ema_26 = data['close'].ewm(span=26).mean().iloc[-1]
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD
        macd = ema_12 - ema_26
        macd_signal = pd.Series([macd]).ewm(span=9).mean().iloc[0]
        
        # Volume
        volume_trend = 1
        if 'volume' in data.columns and len(data) > 20:
            recent_vol = data['volume'].iloc[-5:].mean()
            avg_vol = data['volume'].iloc[-20:].mean()
            volume_trend = recent_vol / avg_vol if avg_vol > 0 else 1
        
        # Momentum
        momentum_5 = (current_price - data['close'].iloc[-6]) / data['close'].iloc[-6] * 100 if len(data) > 5 else 0
        momentum_20 = (current_price - data['close'].iloc[-21]) / data['close'].iloc[-21] * 100 if len(data) > 20 else 0
        
        return {
            'sma_5': sma_5, 'sma_20': sma_20, 'sma_50': sma_50,
            'rsi': rsi, 'macd': macd, 'macd_signal': macd_signal,
            'volume_trend': volume_trend, 'momentum_5': momentum_5, 'momentum_20': momentum_20
        }
    
    def _calculate_technical_score(self, current_price, indicators):
        """Tính điểm kỹ thuật và tín hiệu"""
        score = 50  # Base neutral
        signals = []
        
        # Price vs MA (30 points)
        if current_price > indicators['sma_50']:
            score += 15
            signals.append("Above SMA50")
        if current_price > indicators['sma_20']:
            score += 10
            signals.append("Above SMA20")
        if current_price > indicators['sma_5']:
            score += 5
            signals.append("Above SMA5")
        
        # MA alignment (20 points)
        if indicators['sma_5'] > indicators['sma_20'] > indicators['sma_50']:
            score += 20
            signals.append("Bullish MA alignment")
        elif indicators['sma_5'] < indicators['sma_20'] < indicators['sma_50']:
            score -= 20
            signals.append("Bearish MA alignment")
        
        # MACD (15 points)
        if indicators['macd'] > indicators['macd_signal']:
            score += 15
            signals.append("MACD bullish")
        else:
            score -= 15
            signals.append("MACD bearish")
        
        # RSI (15 points)
        rsi = indicators['rsi']
        if 30 < rsi < 70:
            score += 10
            signals.append("RSI healthy")
        elif rsi < 30:
            score += 15
            signals.append("RSI oversold")
        elif rsi > 70:
            score -= 10
            signals.append("RSI overbought")
        
        # Momentum (20 points)
        if indicators['momentum_5'] > 2:
            score += 10
            signals.append("Strong 5d momentum")
        if indicators['momentum_20'] > 5:
            score += 10
            signals.append("Strong 20d momentum")
        
        # Volume (10 points)
        if indicators['volume_trend'] > 1.2:
            score += 10
            signals.append("Volume supporting")
        
        return max(0, min(100, score)), signals
    
    def _analyze_price_predictions(self, current_price, predictions):
        """Phân tích dự đoán giá - logic chính với validation"""
        try:
            # Lấy dự đoán
            pred_1d = predictions.get('short_term', {}).get('1_days', {})
            pred_7d = predictions.get('short_term', {}).get('7_days', {})
            pred_30d = predictions.get('medium_term', {}).get('30_days', {})
            
            # Tính % thay đổi với validation
            changes = []
            for pred, name in [(pred_1d, '1d'), (pred_7d, '7d'), (pred_30d, '30d')]:
                if pred.get('price'):
                    predicted_price = float(pred['price'])
                    # CRITICAL: Validate predicted price is reasonable
                    if predicted_price <= 0 or predicted_price > current_price * 3:
                        print(f"⚠️ Invalid prediction for {name}: {predicted_price} (current: {current_price})")
                        change = 0  # Use 0 for invalid predictions
                    else:
                        change = ((predicted_price - float(current_price)) / float(current_price)) * 100
                elif pred.get('change_percent'):
                    change = float(pred['change_percent'])
                    # Validate change_percent is reasonable
                    if abs(change) > 50:  # More than 50% change is suspicious
                        print(f"⚠️ Extreme change_percent for {name}: {change}%")
                        change = max(-30, min(30, change))  # Cap at ±30%
                else:
                    change = 0
                changes.append((change, name))
            
            change_1d, change_7d, change_30d = [c[0] for c in changes]
            
            # Trọng số: 7d quan trọng nhất (50%), 30d (30%), 1d (20%)
            weighted_avg = change_1d * 0.2 + change_7d * 0.5 + change_30d * 0.3
            
            # CORRECTED Logic quyết định dựa trên weighted average
            if weighted_avg > 2:  # Tăng mạnh
                direction = "bullish"
                strength = "Strong Bullish" if weighted_avg > 5 else "Moderate Bullish"
            elif weighted_avg < -2:  # Giảm mạnh - FIXED: This should be bearish!
                direction = "bearish"
                strength = "Strong Bearish" if weighted_avg < -5 else "Moderate Bearish"
            elif abs(weighted_avg) <= 1:  # Sideway
                direction = "neutral"
                strength = "Neutral"
            else:  # Tín hiệu yếu - kiểm tra consensus
                positive_count = sum(1 for c, _ in changes if c > 0.5)
                negative_count = sum(1 for c, _ in changes if c < -0.5)
                
                if positive_count >= 2 and negative_count == 0:
                    direction = "bullish"
                    strength = "Weak Bullish"
                elif negative_count >= 2 and positive_count == 0:
                    direction = "bearish"
                    strength = "Weak Bearish"
                else:
                    direction = "neutral"
                    strength = "Neutral"
            
            # CRITICAL FIX: Debug logging to catch inconsistencies
            print(f"🔍 MSN Analysis: 1d={change_1d:.1f}%, 7d={change_7d:.1f}%, 30d={change_30d:.1f}%, weighted_avg={weighted_avg:.1f}% -> {direction} {strength}")
            

            
            signals = [f"Price trend: 1d={change_1d:.1f}%, 7d={change_7d:.1f}%, 30d={change_30d:.1f}%, avg={weighted_avg:.1f}%"]
            return direction, strength, signals
            
        except Exception as e:
            print(f"⚠️ Prediction analysis error: {e}")
            return "neutral", "Neutral", [f"Prediction error: {str(e)}"]
    
    def _analyze_technical_only(self, tech_score):
        """Phân tích chỉ dựa trên kỹ thuật với logic chính xác"""
        # FIXED: Technical score should align with actual trend direction
        if tech_score >= 70:
            return "bullish", "Strong Bullish", [f"Strong technical signals (score: {tech_score})"]
        elif tech_score >= 55:
            return "bullish", "Moderate Bullish", [f"Positive technical signals (score: {tech_score})"]
        elif tech_score >= 45:
            return "neutral", "Neutral", [f"Mixed technical signals (score: {tech_score})"]
        elif tech_score >= 30:
            return "bearish", "Moderate Bearish", [f"Negative technical signals (score: {tech_score})"]
        else:
            return "bearish", "Strong Bearish", [f"Weak technical signals (score: {tech_score})"]
        
        # Debug logging
        print(f"🔍 Technical Analysis: score={tech_score} -> direction determined")

    
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
    
    def predict_price_for_date(self, symbol: str, target_date, risk_tolerance: int = 50, time_horizon: str = "Trung hạn", investment_amount: int = 10000000):
        """Dự đoán giá cổ phiếu cho một ngày cụ thể - LSTM PRIORITY
        
        Args:
            symbol: Mã cổ phiếu
            target_date: Ngày cần dự đoán (datetime object hoặc string)
            risk_tolerance: Mức độ rủi ro (0-100)
            time_horizon: Khung thời gian đầu tư
            investment_amount: Số tiền đầu tư
        """
        try:
            from datetime import date
            
            # Convert target_date to date object
            if isinstance(target_date, str):
                target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
            elif isinstance(target_date, datetime):
                target_date_obj = target_date.date()
            elif isinstance(target_date, date):
                target_date_obj = target_date
            else:
                target_date_obj = target_date.date() if hasattr(target_date, 'date') else target_date
            
            # Calculate days from now to target date - both are now date objects
            current_date = datetime.now().date()
            days_ahead = (target_date_obj - current_date).days
            
            # Validate target date
            if days_ahead < 0:
                return {"error": "Không thể dự đoán cho ngày trong quá khứ"}
            elif days_ahead == 0:
                # Special handling for today's prediction
                return self._predict_today_close_price(symbol, risk_tolerance, time_horizon, investment_amount)
            elif days_ahead > 365:
                return {"error": "Chỉ có thể dự đoán tối đa 1 năm trong tương lai"}
            
            # 🧠 LSTM PRIORITY: Always try LSTM first for calendar predictions
            if self.lstm_predictor and days_ahead > 0:
                try:
                    print(f"🧠 Using LSTM for calendar prediction: {symbol} - {days_ahead} days")
                    lstm_result = self.lstm_predictor.predict_with_ai_enhancement(symbol, days_ahead)
                    
                    # LOWERED threshold for LSTM acceptance (was 15, now 10)
                    if not lstm_result.get('error') and lstm_result['model_performance']['confidence'] > 10:
                        print(f"✅ LSTM successful with {lstm_result['model_performance']['confidence']:.1f}% confidence")
                        
                        # LSTM successful - use it as primary method
                        result = self._combine_lstm_with_traditional(lstm_result, symbol)
                        result['method_used'] = 'LSTM Neural Network (Calendar)'
                        result['lstm_confidence'] = lstm_result['model_performance']['confidence']
                        result['primary_method'] = 'LSTM'
                        
                        # Set main prediction values from LSTM with enhanced interpolation
                        interpolated_price = self._interpolate_price_for_date_lstm(result['predictions'], days_ahead, result['current_price'])
                        if interpolated_price:
                            result['predicted_price'] = interpolated_price['price']
                            result['change_percent'] = interpolated_price['change_percent']
                            result['interpolation_method'] = 'LSTM Enhanced'
                        
                        # Add LSTM-specific calendar insights
                        result['lstm_calendar_analysis'] = self._get_lstm_calendar_analysis(lstm_result, days_ahead, target_date_obj)
                        
                        # Add risk analysis
                        result['risk_adjusted_analysis'] = self._get_risk_adjusted_analysis(
                            result, risk_tolerance, time_horizon, investment_amount
                        )
                        
                        # Add AI enhancement
                        if self.ai_agent:
                            try:
                                ai_analysis = self._get_ai_price_analysis(symbol, result, days_ahead, risk_tolerance, time_horizon)
                                result.update(ai_analysis)
                            except Exception as e:
                                result['ai_error'] = str(e)
                        
                        # Add date-specific information
                        result['target_date'] = target_date.strftime('%Y-%m-%d')
                        result['days_ahead'] = days_ahead
                        result['prediction_type'] = 'lstm_calendar'
                        
                        # Calculate interpolated price for exact date if not already done
                        if not result.get('interpolated_price'):
                            interpolated_price = self._interpolate_price_for_date_lstm(result['predictions'], days_ahead, result['current_price'])
                            if interpolated_price:
                                result['interpolated_price'] = interpolated_price
                                result['predicted_price'] = interpolated_price['price']
                                result['change_percent'] = interpolated_price['change_percent']
                        
                        # Add calendar-specific insights
                        result['calendar_insights'] = self._get_calendar_insights(target_date, days_ahead)
                        
                        return result
                        
                    else:
                        # LSTM failed or low confidence, fallback to traditional
                        print(f"⚠️ LSTM failed or low confidence ({lstm_result.get('model_performance', {}).get('confidence', 0):.1f}%), using traditional")
                        result = self.predict_price_enhanced(symbol, days_ahead, risk_tolerance, time_horizon, investment_amount)
                        result['method_used'] = 'Traditional (LSTM low confidence)'
                        result['lstm_fallback_reason'] = f"LSTM confidence {lstm_result.get('model_performance', {}).get('confidence', 0):.1f}% < 10%"
                        
                except Exception as e:
                    # LSTM error, fallback to traditional
                    print(f"❌ LSTM error: {e}, using traditional")
                    result = self.predict_price_enhanced(symbol, days_ahead, risk_tolerance, time_horizon, investment_amount)
                    result['method_used'] = f'Traditional (LSTM error)'
                    result['lstm_error'] = str(e)
            else:
                # No LSTM available, use traditional
                print(f"📊 No LSTM available, using traditional for {symbol}")
                result = self.predict_price_enhanced(symbol, days_ahead, risk_tolerance, time_horizon, investment_amount)
                result['method_used'] = 'Traditional (No LSTM)'
            
            if "error" in result:
                return result
            
            # Add date-specific information for traditional methods
            result['target_date'] = target_date.strftime('%Y-%m-%d')
            result['days_ahead'] = days_ahead
            result['prediction_type'] = 'traditional_calendar'
            
            # Calculate interpolated price for exact date if needed
            if not result.get('interpolated_price'):
                interpolated_price = self._interpolate_price_for_date(result['predictions'], days_ahead, result['current_price'])
                if interpolated_price:
                    result['interpolated_price'] = interpolated_price
                    result['predicted_price'] = interpolated_price['price']
                    result['change_percent'] = interpolated_price['change_percent']
            
            # Add calendar-specific insights
            result['calendar_insights'] = self._get_calendar_insights(target_date, days_ahead)
            
            return result
            
        except Exception as e:
            return {"error": f"Date prediction error: {str(e)}"}
    
    def _interpolate_price_for_date(self, predictions: dict, days_ahead: int, current_price: float):
        """Nội suy giá cho ngày cụ thể dựa trên các dự đoán có sẵn"""
        try:
            # Collect all prediction points
            prediction_points = []
            
            for timeframe, preds in predictions.items():
                for period, data in preds.items():
                    if 'days' in period:
                        days = int(period.split('_')[0])
                        price = data['price']
                        prediction_points.append((days, price))
            
            # Add current price as day 0
            prediction_points.append((0, current_price))
            
            # Sort by days
            prediction_points.sort(key=lambda x: x[0])
            
            # Find surrounding points for interpolation
            lower_point = None
            upper_point = None
            
            for i, (days, price) in enumerate(prediction_points):
                if days <= days_ahead:
                    lower_point = (days, price)
                if days >= days_ahead and upper_point is None:
                    upper_point = (days, price)
                    break
            
            # Interpolate price
            if lower_point and upper_point and lower_point[0] != upper_point[0]:
                # Linear interpolation
                days_diff = upper_point[0] - lower_point[0]
                price_diff = upper_point[1] - lower_point[1]
                target_days_from_lower = days_ahead - lower_point[0]
                
                interpolated_price = lower_point[1] + (price_diff * target_days_from_lower / days_diff)
                
                return {
                    'price': round(interpolated_price, 2),
                    'change_percent': round(((interpolated_price - current_price) / current_price) * 100, 2),
                    'change_amount': round(interpolated_price - current_price, 2),
                    'interpolation_method': 'linear',
                    'based_on_points': f"{lower_point[0]}d-{upper_point[0]}d"
                }
            elif lower_point:
                # Use exact match or closest point
                return {
                    'price': round(lower_point[1], 2),
                    'change_percent': round(((lower_point[1] - current_price) / current_price) * 100, 2),
                    'change_amount': round(lower_point[1] - current_price, 2),
                    'interpolation_method': 'exact_match',
                    'based_on_points': f"{lower_point[0]}d"
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Price interpolation failed: {e}")
            return None
    
    def _get_calendar_insights(self, target_date, days_ahead: int):
        """Tạo insights dựa trên lịch và thời gian"""
        try:
            insights = []
            
            # Day of week analysis
            weekday = target_date.weekday()
            weekday_names = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
            
            if weekday == 0:  # Monday
                insights.append("📈 Thứ 2 thường có volatility cao do tin tức cuối tuần")
            elif weekday == 4:  # Friday
                insights.append("📊 Thứ 6 có thể có profit-taking trước cuối tuần")
            elif weekday in [5, 6]:  # Weekend
                insights.append("⚠️ Thị trường đóng cửa vào cuối tuần")
            
            # Month analysis
            month = target_date.month
            if month in [1, 12]:  # January/December
                insights.append("🎯 Tháng 1/12 thường có hiệu ứng window dressing")
            elif month in [3, 6, 9, 12]:  # Quarter end
                insights.append("📋 Cuối quý có thể có rebalancing từ các quỹ")
            
            # Time horizon insights
            if days_ahead <= 7:
                insights.append("⚡ Dự đoán ngắn hạn - chịu ảnh hưởng mạnh từ tin tức")
            elif days_ahead <= 30:
                insights.append("📊 Dự đoán trung hạn - cân bằng giữa kỹ thuật và cơ bản")
            elif days_ahead <= 90:
                insights.append("📈 Dự đoán dài hạn - tập trung vào fundamentals")
            else:
                insights.append("🔮 Dự đoán rất dài hạn - độ tin cậy giảm theo thời gian")
            
            # Season analysis
            if target_date.month in [12, 1, 2]:
                insights.append("❄️ Mùa đông - thường có rally cuối năm")
            elif target_date.month in [3, 4, 5]:
                insights.append("🌸 Mùa xuân - earnings season Q1")
            elif target_date.month in [6, 7, 8]:
                insights.append("☀️ Mùa hè - thường có volume thấp")
            else:
                insights.append("🍂 Mùa thu - back-to-school effect")
            
            return {
                'target_weekday': weekday_names[weekday],
                'days_ahead': days_ahead,
                'insights': insights,
                'market_open': weekday < 5,  # Monday to Friday
                'quarter': f"Q{(month-1)//3 + 1}",
                'is_month_end': target_date.day > 25
            }
            
        except Exception as e:
            return {'error': f"Calendar insights error: {str(e)}"}
    def _interpolate_price_for_date_lstm(self, predictions: dict, days_ahead: int, current_price: float):
        """Enhanced LSTM-specific interpolation for calendar predictions"""
        try:
            # Collect all LSTM prediction points with confidence intervals
            prediction_points = []
            
            for timeframe, preds in predictions.items():
                for period, data in preds.items():
                    if 'days' in period:
                        days = int(period.split('_')[0])
                        price = data['price']
                        confidence_interval = data.get('confidence_interval', {})
                        prediction_points.append((days, price, confidence_interval))
            
            # Add current price as day 0
            prediction_points.append((0, current_price, {}))
            
            # Sort by days
            prediction_points.sort(key=lambda x: x[0])
            
            # Find surrounding points for LSTM interpolation
            lower_point = None
            upper_point = None
            
            for i, (days, price, conf_int) in enumerate(prediction_points):
                if days <= days_ahead:
                    lower_point = (days, price, conf_int)
                if days >= days_ahead and upper_point is None:
                    upper_point = (days, price, conf_int)
                    break
            
            # Enhanced LSTM interpolation with confidence consideration
            if lower_point and upper_point and lower_point[0] != upper_point[0]:
                # Weighted interpolation considering LSTM confidence
                days_diff = upper_point[0] - lower_point[0]
                price_diff = upper_point[1] - lower_point[1]
                target_days_from_lower = days_ahead - lower_point[0]
                
                # LSTM-enhanced interpolation with non-linear adjustment
                weight = target_days_from_lower / days_diff
                
                # Apply LSTM-specific smoothing (neural networks tend to be smoother)
                smoothed_weight = 0.5 * (1 + np.tanh(2 * (weight - 0.5)))  # Sigmoid-like smoothing
                
                interpolated_price = lower_point[1] + (price_diff * smoothed_weight)
                
                # Calculate confidence interval for interpolated price
                lower_conf = lower_point[2].get('lower', lower_point[1])
                upper_conf = upper_point[2].get('upper', upper_point[1])
                interpolated_lower = lower_conf + ((upper_conf - lower_conf) * smoothed_weight)
                interpolated_upper = interpolated_price + abs(interpolated_price - interpolated_lower)
                
                return {
                    'price': round(interpolated_price, 2),
                    'change_percent': round(((interpolated_price - current_price) / current_price) * 100, 2),
                    'change_amount': round(interpolated_price - current_price, 2),
                    'interpolation_method': 'lstm_enhanced',
                    'based_on_points': f"{lower_point[0]}d-{upper_point[0]}d",
                    'confidence_interval': {
                        'lower': round(interpolated_lower, 2),
                        'upper': round(interpolated_upper, 2),
                        'range': round(abs(interpolated_upper - interpolated_lower), 2)
                    },
                    'lstm_smoothing': True
                }
            elif lower_point:
                # Use exact match or closest LSTM point
                return {
                    'price': round(lower_point[1], 2),
                    'change_percent': round(((lower_point[1] - current_price) / current_price) * 100, 2),
                    'change_amount': round(lower_point[1] - current_price, 2),
                    'interpolation_method': 'lstm_exact',
                    'based_on_points': f"{lower_point[0]}d",
                    'confidence_interval': lower_point[2],
                    'lstm_smoothing': False
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ LSTM interpolation failed: {e}")
            return None
    
    def _get_lstm_calendar_analysis(self, lstm_result: dict, days_ahead: int, target_date):
        """Generate LSTM-specific calendar analysis"""
        try:
            analysis = {
                'lstm_method': lstm_result.get('method', 'LSTM Neural Network'),
                'model_confidence': lstm_result['model_performance']['confidence'],
                'data_points_used': lstm_result.get('data_points_used', 0),
                'look_back_period': lstm_result.get('look_back_period', 60),
                'prediction_horizon': days_ahead
            }
            
            # LSTM trend analysis
            lstm_trend = lstm_result.get('trend', 'neutral')
            analysis['lstm_trend'] = lstm_trend
            
            # Model performance insights
            model_perf = lstm_result['model_performance']
            train_rmse = model_perf.get('train_rmse', 0)
            test_rmse = model_perf.get('test_rmse', 0)
            
            analysis['model_accuracy'] = {
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'overfitting_risk': 'High' if abs(train_rmse - test_rmse) > train_rmse * 0.5 else 'Low'
            }
            
            # Time-specific LSTM insights
            if days_ahead <= 7:
                analysis['lstm_suitability'] = 'Excellent - LSTM excels at short-term patterns'
                analysis['confidence_adjustment'] = 1.1  # Boost confidence for short-term
            elif days_ahead <= 30:
                analysis['lstm_suitability'] = 'Very Good - LSTM captures medium-term trends'
                analysis['confidence_adjustment'] = 1.0
            elif days_ahead <= 90:
                analysis['lstm_suitability'] = 'Good - LSTM with some uncertainty'
                analysis['confidence_adjustment'] = 0.9
            else:
                analysis['lstm_suitability'] = 'Moderate - Long-term predictions less reliable'
                analysis['confidence_adjustment'] = 0.8
            
            # Calendar-specific LSTM considerations
            weekday = target_date.weekday()
            if weekday == 0:  # Monday
                analysis['calendar_note'] = 'LSTM may capture Monday volatility patterns from training data'
            elif weekday == 4:  # Friday
                analysis['calendar_note'] = 'LSTM trained on Friday profit-taking patterns'
            elif weekday in [5, 6]:  # Weekend
                analysis['calendar_note'] = 'Weekend prediction - LSTM extrapolates from Friday close'
            else:
                analysis['calendar_note'] = 'Mid-week prediction - LSTM most reliable'
            
            return analysis
            
        except Exception as e:
            return {'error': f'LSTM calendar analysis error: {str(e)}'}