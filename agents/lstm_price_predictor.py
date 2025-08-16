import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, LSTM, Dropout
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("⚠️ TensorFlow/Keras not available. LSTM predictions will use fallback methods.")

class LSTMPricePredictor:
    def __init__(self, vn_api=None):
        self.name = "LSTM Price Predictor Agent"
        self.vn_api = vn_api
        self.ai_agent = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.look_back = 60  # Use 60 days for better performance (modern approach)
        self.model_cache = {}  # Cache trained models
        self.model_cache_time = {}  # Track model training time
        
    def set_ai_agent(self, ai_agent):
        """Set AI agent for enhanced predictions"""
        self.ai_agent = ai_agent
    
    def create_dataset(self, dataset, look_back=60):
        """Convert time series to supervised learning format"""
        dataX, dataY = [], []
        for i in range(len(dataset) - look_back - 1):
            a = dataset[i:(i + look_back), 0]
            dataX.append(a)
            dataY.append(dataset[i + look_back, 0])
        return np.array(dataX), np.array(dataY)
    
    def prepare_data(self, price_data):
        """Prepare data for LSTM training"""
        try:
            # Convert to numpy array and reshape
            if isinstance(price_data, pd.Series):
                dataset = price_data.values.reshape(-1, 1)
            else:
                dataset = np.array(price_data).reshape(-1, 1)
            
            # Normalize data
            dataset = self.scaler.fit_transform(dataset.astype('float32'))
            
            # Split into train/test (80/20 - modern approach)
            train_size = int(len(dataset) * 0.8)
            train, test = dataset[0:train_size, :], dataset[train_size:len(dataset), :]
            
            # Create datasets
            trainX, trainY = self.create_dataset(train, self.look_back)
            testX, testY = self.create_dataset(test, self.look_back)
            
            # Reshape for LSTM [samples, time steps, features]
            trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1], 1))
            testX = np.reshape(testX, (testX.shape[0], testX.shape[1], 1))
            
            return trainX, trainY, testX, testY, dataset
            
        except Exception as e:
            print(f"❌ Data preparation failed: {e}")
            return None, None, None, None, None
    
    def build_lstm_model(self, input_shape):
        """Build enhanced LSTM model architecture"""
        try:
            if not KERAS_AVAILABLE:
                return None
                
            model = Sequential()
            # Enhanced architecture with 2 LSTM layers for better learning
            model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
            model.add(Dropout(0.2))
            model.add(LSTM(50, return_sequences=False))
            model.add(Dropout(0.2))
            model.add(Dense(25))  # Additional dense layer
            model.add(Dense(1))
            
            model.compile(optimizer='adam', loss='mean_squared_error')
            return model
            
        except Exception as e:
            print(f"❌ Model building failed: {e}")
            return None
    
    def train_lstm_model(self, trainX, trainY, symbol, epochs=100, batch_size=32):
        """Train LSTM model with caching and validation"""
        try:
            if not KERAS_AVAILABLE or trainX is None:
                return None
            
            # Check if we have a cached model that's still fresh (< 24 hours)
            cache_key = f"{symbol}_{trainX.shape[0]}_{trainX.shape[1]}"
            current_time = datetime.now()
            
            if (cache_key in self.model_cache and 
                cache_key in self.model_cache_time and
                (current_time - self.model_cache_time[cache_key]).seconds < 86400):  # 24 hours
                print(f"✅ Using cached model for {symbol}")
                return self.model_cache[cache_key]
                
            # Build model
            model = self.build_lstm_model((trainX.shape[1], 1))
            if model is None:
                return None
            
            # Enhanced training with validation split and early stopping
            from tensorflow.keras.callbacks import EarlyStopping
            early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
            
            # Train model with validation
            history = model.fit(
                trainX, trainY, 
                epochs=epochs, 
                batch_size=batch_size, 
                validation_split=0.2,
                callbacks=[early_stopping],
                verbose=0
            )
            
            # Cache the trained model
            self.model_cache[cache_key] = model
            self.model_cache_time[cache_key] = current_time
            
            print(f"✅ Model trained for {symbol} - Final loss: {history.history['loss'][-1]:.6f}")
            
            return model
            
        except Exception as e:
            print(f"❌ Model training failed: {e}")
            return None
    
    def predict_with_lstm(self, symbol: str, days_ahead: int = 30):
        """Main LSTM prediction function"""
        try:
            # Get historical data
            price_data = self._get_price_data(symbol)
            if price_data is None or len(price_data) < 100:
                return self._fallback_prediction(symbol, days_ahead)
            
            # Prepare data for LSTM
            trainX, trainY, testX, testY, dataset = self.prepare_data(price_data)
            if trainX is None:
                return self._fallback_prediction(symbol, days_ahead)
            
            # Train LSTM model with optimized parameters
            model = self.train_lstm_model(trainX, trainY, symbol, epochs=100, batch_size=32)
            if model is None:
                return self._fallback_prediction(symbol, days_ahead)
            
            # Make predictions
            train_predict = model.predict(trainX, verbose=0)
            test_predict = model.predict(testX, verbose=0)
            
            # Inverse transform predictions
            train_predict = self.scaler.inverse_transform(train_predict)
            test_predict = self.scaler.inverse_transform(test_predict)
            trainY = self.scaler.inverse_transform([trainY])
            testY = self.scaler.inverse_transform([testY])
            
            # Calculate RMSE
            train_score = np.sqrt(mean_squared_error(trainY[0], train_predict[:, 0]))
            test_score = np.sqrt(mean_squared_error(testY[0], test_predict[:, 0]))
            
            # Predict future prices
            future_predictions = self._predict_future_prices(model, dataset, days_ahead)
            
            # Calculate confidence based on model performance
            confidence = self._calculate_lstm_confidence(train_score, test_score, price_data)
            
            current_price = float(price_data.iloc[-1])
            
            # Determine trend based on LSTM predictions
            trend_direction = self._determine_lstm_trend(current_price, future_predictions)
            
            return {
                'symbol': symbol,
                'method': 'LSTM Neural Network',
                'current_price': current_price,
                'predictions': future_predictions,
                'trend': trend_direction,  # Add trend determination
                'model_performance': {
                    'train_rmse': round(train_score, 2),
                    'test_rmse': round(test_score, 2),
                    'confidence': confidence
                },
                'data_points_used': len(price_data),
                'look_back_period': self.look_back,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ LSTM prediction failed: {e}")
            return self._fallback_prediction(symbol, days_ahead)
    
    def _get_price_data(self, symbol: str):
        """Get historical price data with validation"""
        try:
            price_data = None
            
            # Try VNStock first for Vietnamese stocks
            if self.vn_api and self.vn_api.is_vn_stock(symbol):
                from vnstock import Vnstock
                stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
                end_date = datetime.now().strftime('%Y-%m-%d')
                # Get more historical data for better training (3 years)
                start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')
                hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                
                if not hist_data.empty:
                    price_data = hist_data['close']
            
            # Fallback to Yahoo Finance
            if price_data is None:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="3y")  # Get 3 years of data
                
                if not hist.empty:
                    price_data = hist['Close']
            
            # Data validation and cleaning
            if price_data is not None:
                # Remove NaN values
                price_data = price_data.dropna()
                
                # Check for sufficient data points
                if len(price_data) < 200:
                    print(f"⚠️ Insufficient data for {symbol}: {len(price_data)} points")
                    return None
                
                # Check for data quality (no extreme outliers)
                q1 = price_data.quantile(0.25)
                q3 = price_data.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # Remove extreme outliers
                price_data = price_data[(price_data >= lower_bound) & (price_data <= upper_bound)]
                
                print(f"✅ Retrieved {len(price_data)} valid data points for {symbol}")
                return price_data
            
            return None
            
        except Exception as e:
            print(f"⚠️ Failed to get price data for {symbol}: {e}")
            return None
    
    def _predict_future_prices(self, model, dataset, days_ahead):
        """Enhanced future price prediction with rolling window approach"""
        try:
            # Get last sequence for prediction (use look_back period)
            last_sequence = dataset[-self.look_back:].copy()
            predictions = []
            
            # Enhanced prediction with rolling window
            x_future = last_sequence.reshape((1, last_sequence.shape[0], 1))
            
            for _ in range(days_ahead):
                # Predict next value
                pred = model.predict(x_future, verbose=0)
                predictions.append(pred[0, 0])
                
                # Update x_future by removing first value and adding prediction
                x_future = np.append(x_future[:, 1:, :], [[pred[0]]], axis=1)
            
            # Inverse transform predictions
            predictions = np.array(predictions).reshape(-1, 1)
            predictions = self.scaler.inverse_transform(predictions)
            
            # Format predictions by timeframe with confidence intervals
            formatted_predictions = {}
            
            # Short term (1, 3, 7 days) - higher confidence
            formatted_predictions['short_term'] = {
                '1_days': {
                    'price': round(float(predictions[0]), 2), 
                    'days': 1,
                    'confidence_interval': self._calculate_confidence_interval(predictions[0], 0.05)
                },
                '3_days': {
                    'price': round(float(predictions[2]), 2), 
                    'days': 3,
                    'confidence_interval': self._calculate_confidence_interval(predictions[2], 0.08)
                },
                '7_days': {
                    'price': round(float(predictions[6]), 2), 
                    'days': 7,
                    'confidence_interval': self._calculate_confidence_interval(predictions[6], 0.12)
                }
            }
            
            # Medium term (14, 30 days)
            if days_ahead >= 30:
                formatted_predictions['medium_term'] = {
                    '14_days': {
                        'price': round(float(predictions[13]), 2), 
                        'days': 14,
                        'confidence_interval': self._calculate_confidence_interval(predictions[13], 0.18)
                    },
                    '30_days': {
                        'price': round(float(predictions[29]), 2), 
                        'days': 30,
                        'confidence_interval': self._calculate_confidence_interval(predictions[29], 0.25)
                    }
                }
            
            # Long term (60, 90 days) - lower confidence
            if days_ahead >= 90:
                formatted_predictions['long_term'] = {
                    '60_days': {
                        'price': round(float(predictions[59]), 2), 
                        'days': 60,
                        'confidence_interval': self._calculate_confidence_interval(predictions[59], 0.35)
                    },
                    '90_days': {
                        'price': round(float(predictions[89]), 2), 
                        'days': 90,
                        'confidence_interval': self._calculate_confidence_interval(predictions[89], 0.45)
                    }
                }
            
            return formatted_predictions
            
        except Exception as e:
            print(f"❌ Future prediction failed: {e}")
            return {}
    
    def _calculate_lstm_confidence(self, train_rmse, test_rmse, price_data):
        """Calculate confidence based on LSTM model performance"""
        try:
            # Calculate relative errors
            avg_price = float(price_data.mean())
            train_error_pct = (train_rmse / avg_price) * 100
            test_error_pct = (test_rmse / avg_price) * 100
            
            # Base confidence from model accuracy
            base_confidence = max(20, 100 - (test_error_pct * 2))
            
            # Adjust for overfitting (train vs test performance)
            overfitting_penalty = abs(train_error_pct - test_error_pct) * 2
            confidence = max(20, base_confidence - overfitting_penalty)
            
            # Adjust for data quality
            data_quality_bonus = min(20, len(price_data) / 50)  # More data = higher confidence
            confidence += data_quality_bonus
            
            return min(95, round(confidence, 1))
            
        except Exception as e:
            return 50  # Default confidence
    
    def _determine_lstm_trend(self, current_price, predictions):
        """Determine trend direction based on LSTM predictions - CONSISTENT with price_predictor.py"""
        try:
            # Get key prediction points
            short_7d = predictions.get('short_term', {}).get('7_days', {}).get('price', current_price)
            medium_30d = predictions.get('medium_term', {}).get('30_days', {}).get('price', current_price)
            
            # Calculate percentage changes
            change_7d = ((short_7d - current_price) / current_price) * 100
            change_30d = ((medium_30d - current_price) / current_price) * 100
            
            # Use SAME logic as price_predictor.py _analyze_market_trend
            if change_7d > 2 and change_30d > 3:
                return 'bullish'
            elif change_7d < -2 and change_30d < -3:
                return 'bearish'
            elif abs(change_7d) <= 2 and abs(change_30d) <= 3:
                return 'neutral'
            else:
                # Mixed signals - use 30-day as primary
                return 'bullish' if change_30d > 0 else 'bearish'
                
        except Exception as e:
            return 'neutral'
    
    def _calculate_confidence_interval(self, prediction, uncertainty_factor):
        """Calculate confidence interval for predictions"""
        try:
            lower_bound = prediction * (1 - uncertainty_factor)
            upper_bound = prediction * (1 + uncertainty_factor)
            return {
                'lower': round(float(lower_bound), 2),
                'upper': round(float(upper_bound), 2),
                'uncertainty': round(uncertainty_factor * 100, 1)
            }
        except Exception as e:
            return {
                'lower': float(prediction),
                'upper': float(prediction),
                'uncertainty': 0.0
            }
    
    def _fallback_prediction(self, symbol: str, days_ahead: int):
        """Fallback prediction when LSTM fails"""
        try:
            # Get basic price data
            price_data = self._get_price_data(symbol)
            if price_data is None:
                return {'error': f'No data available for {symbol}'}
            
            current_price = float(price_data.iloc[-1])
            
            # Simple trend-based prediction
            recent_prices = price_data.tail(30)
            trend = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
            
            # Generate simple predictions
            predictions = {}
            for timeframe in ['short_term', 'medium_term', 'long_term']:
                predictions[timeframe] = {}
                
                if timeframe == 'short_term':
                    periods = [1, 3, 7]
                elif timeframe == 'medium_term':
                    periods = [14, 30]
                else:
                    periods = [60, 90]
                
                for days in periods:
                    if days <= days_ahead:
                        # Simple linear extrapolation with some randomness
                        predicted_price = current_price * (1 + trend * (days / 30))
                        predictions[timeframe][f'{days}_days'] = {
                            'price': round(predicted_price, 2),
                            'days': days
                        }
            
            # Determine trend for fallback
            trend_direction = self._determine_fallback_trend(current_price, recent_prices)
            
            return {
                'symbol': symbol,
                'method': 'Fallback Linear Trend',
                'current_price': current_price,
                'predictions': predictions,
                'trend': trend_direction,  # Add trend for fallback
                'model_performance': {
                    'confidence': 40,  # Lower confidence for fallback
                    'note': 'LSTM not available, using simple trend analysis'
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {'error': f'Fallback prediction failed: {str(e)}'}
    
    def _determine_fallback_trend(self, current_price, recent_prices):
        """Determine trend for fallback method - CONSISTENT logic"""
        try:
            if len(recent_prices) < 10:
                return 'neutral'
            
            # Calculate trend from recent prices
            start_price = recent_prices.iloc[0]
            end_price = recent_prices.iloc[-1]
            change_pct = ((end_price - start_price) / start_price) * 100
            
            # Use consistent thresholds with LSTM trend logic
            if change_pct > 3:  # Consistent with LSTM 30d > 3%
                return 'bullish'
            elif change_pct < -3:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            return 'neutral'
    
    def predict_with_ai_enhancement(self, symbol: str, days_ahead: int = 30):
        """LSTM prediction with AI enhancement"""
        # Get base LSTM prediction
        lstm_result = self.predict_with_lstm(symbol, days_ahead)
        
        if lstm_result.get('error'):
            return lstm_result
        
        # Add AI enhancement if available
        if self.ai_agent:
            try:
                ai_analysis = self._get_ai_lstm_analysis(symbol, lstm_result)
                lstm_result.update(ai_analysis)
                
                # Let AI override trend if it has strong opinion
                if ai_analysis.get('ai_trend_override'):
                    lstm_result['trend'] = ai_analysis['ai_trend_override']
                    lstm_result['trend_source'] = 'AI Enhanced'
                else:
                    lstm_result['trend_source'] = 'LSTM'
                    
            except Exception as e:
                print(f"⚠️ AI enhancement failed: {e}")
                lstm_result['ai_enhanced'] = False
                lstm_result['ai_error'] = str(e)
        else:
            lstm_result['ai_enhanced'] = False
            lstm_result['ai_error'] = 'AI agent not configured'
            lstm_result['trend_source'] = 'LSTM'
        
        return lstm_result
    
    def _get_ai_lstm_analysis(self, symbol: str, lstm_result: dict):
        """Get AI analysis of LSTM predictions"""
        try:
            current_price = lstm_result['current_price']
            confidence = lstm_result['model_performance']['confidence']
            train_rmse = lstm_result['model_performance']['train_rmse']
            test_rmse = lstm_result['model_performance']['test_rmse']
            
            # Get short and medium term predictions
            short_pred = lstm_result['predictions'].get('short_term', {}).get('7_days', {}).get('price', current_price)
            medium_pred = lstm_result['predictions'].get('medium_term', {}).get('30_days', {}).get('price', current_price)
            
            # Calculate trend changes for AI analysis
            change_7d = ((short_pred - current_price) / current_price * 100)
            change_30d = ((medium_pred - current_price) / current_price * 100)
            current_trend = lstm_result.get('trend', 'neutral')
            
            context = f"""
Phân tích dự đoán LSTM cho {symbol}:

HIỆU SUẤT MÔ HÌNH:
- Confidence: {confidence}%
- Train RMSE: {train_rmse}
- Test RMSE: {test_rmse}
- Xu hướng LSTM: {current_trend.upper()}

DỰ ĐOÁN GIÁ:
- Hiện tại: {current_price:,.0f} VND
- 7 ngày: {short_pred:,.0f} VND ({change_7d:+.1f}%)
- 30 ngày: {medium_pred:,.0f} VND ({change_30d:+.1f}%)

Dựa trên dự đoán LSTM, đánh giá xu hướng và đưa ra khuyến nghị:

TREND_ANALYSIS: [BULLISH/BEARISH/NEUTRAL - có thể khác với LSTM]
CONFIDENCE: [HIGH/MEDIUM/LOW]
ADVICE: [lời khuyên đầu tư cụ thể]
REASONING: [lý do chi tiết]
"""
            
            ai_result = self.ai_agent.generate_with_fallback(context, 'lstm_analysis', max_tokens=400)
            
            if ai_result['success']:
                # Parse AI trend analysis
                ai_trend = self._parse_ai_trend(ai_result['response'])
                
                return {
                    'ai_enhanced': True,
                    'ai_lstm_analysis': ai_result['response'],
                    'ai_model_used': ai_result.get('model_used', 'Gemini'),
                    'ai_confidence_adjustment': self._parse_ai_confidence(ai_result['response']),
                    'ai_trend_override': ai_trend  # AI can override LSTM trend
                }
            else:
                return {
                    'ai_enhanced': False,
                    'ai_error': ai_result.get('error', 'AI analysis failed')
                }
                
        except Exception as e:
            return {
                'ai_enhanced': False,
                'ai_error': str(e)
            }
    
    def _parse_ai_confidence(self, ai_response: str):
        """Parse AI confidence assessment"""
        try:
            if 'HIGH confidence' in ai_response.upper() or 'CONFIDENCE: HIGH' in ai_response.upper():
                return 10  # Boost confidence by 10%
            elif 'LOW confidence' in ai_response.upper() or 'CONFIDENCE: LOW' in ai_response.upper():
                return -15  # Reduce confidence by 15%
            else:
                return 0  # No adjustment
        except:
            return 0
    
    def _parse_ai_trend(self, ai_response: str):
        """Parse AI trend analysis to potentially override LSTM trend"""
        try:
            response_upper = ai_response.upper()
            
            # Look for trend analysis patterns
            if 'TREND_ANALYSIS: BULLISH' in response_upper or 'XU HƯỚNG: TĂNG' in response_upper:
                return 'bullish'
            elif 'TREND_ANALYSIS: BEARISH' in response_upper or 'XU HƯỚNG: GIẢM' in response_upper:
                return 'bearish'
            elif 'TREND_ANALYSIS: NEUTRAL' in response_upper or 'XU HƯỚNG: TRUNG TÍNH' in response_upper:
                return 'neutral'
            
            # Fallback patterns
            if 'BULLISH' in response_upper and 'STRONG' in response_upper:
                return 'bullish'
            elif 'BEARISH' in response_upper and 'STRONG' in response_upper:
                return 'bearish'
            
            # No clear AI trend override
            return None
            
        except Exception as e:
            return None

# Integration function for existing price_predictor.py
def enhance_price_predictor_with_lstm(price_predictor_instance):
    """Enhance existing PricePredictor with LSTM capabilities"""
    
    # Add LSTM predictor as attribute
    price_predictor_instance.lstm_predictor = LSTMPricePredictor(price_predictor_instance.vn_api)
    
    # Add LSTM prediction method
    def predict_with_lstm_enhanced(self, symbol: str, days_ahead: int = 30):
        """Enhanced prediction using both traditional methods and LSTM"""
        try:
            # Get traditional prediction
            traditional_result = self.predict_comprehensive(symbol)
            
            # Get LSTM prediction
            lstm_result = self.lstm_predictor.predict_with_ai_enhancement(symbol, days_ahead)
            
            if lstm_result.get('error'):
                # Return traditional result if LSTM fails
                traditional_result['lstm_status'] = 'Failed - using traditional methods'
                return traditional_result
            
            # Combine results
            combined_result = traditional_result.copy()
            combined_result['lstm_predictions'] = lstm_result['predictions']
            combined_result['lstm_confidence'] = lstm_result['model_performance']['confidence']
            combined_result['lstm_method'] = lstm_result['method']
            combined_result['prediction_methods'] = ['Technical Analysis', 'LSTM Neural Network']
            
            # Use LSTM for main predicted_price if confidence is high (lowered threshold for LSTM priority)
            if lstm_result['model_performance']['confidence'] > 20:
                lstm_30d = lstm_result['predictions'].get('medium_term', {}).get('30_days', {})
                if lstm_30d:
                    combined_result['predicted_price'] = lstm_30d['price']
                    combined_result['primary_method'] = 'LSTM'
                    combined_result['change_percent'] = ((lstm_30d['price'] - traditional_result['current_price']) / traditional_result['current_price']) * 100
            
            return combined_result
            
        except Exception as e:
            # Fallback to traditional method
            traditional_result = self.predict_comprehensive(symbol)
            traditional_result['lstm_error'] = str(e)
            return traditional_result
    
    # Bind method to instance
    import types
    price_predictor_instance.predict_with_lstm_enhanced = types.MethodType(predict_with_lstm_enhanced, price_predictor_instance)
    
    # Set AI agent for LSTM if available
    if hasattr(price_predictor_instance, 'ai_agent') and price_predictor_instance.ai_agent:
        price_predictor_instance.lstm_predictor.set_ai_agent(price_predictor_instance.ai_agent)
    
    return price_predictor_instance