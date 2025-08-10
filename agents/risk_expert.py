import yfinance as yf
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class RiskExpert:
    def __init__(self, vn_api=None):
        self.name = "Risk Expert Agent"
        # Use provided VN API or lazy initialization
        self._vn_api = vn_api
        self.ai_agent = None  # Will be set by main_agent
        self.crewai_collector = None  # Will be set from vn_api
    
    def set_ai_agent(self, ai_agent):
        """Set AI agent for enhanced risk analysis"""
        self.ai_agent = ai_agent
    
    def _get_vn_api(self):
        """Get VN API instance (provided or lazy initialization)"""
        if self._vn_api is None:
            try:
                from src.data.vn_stock_api import VNStockAPI
                self._vn_api = VNStockAPI()
                print("⚠️ RiskExpert: Using fallback VN API initialization")
            except Exception as e:
                print(f"⚠️ Failed to initialize VN API: {e}")
                self._vn_api = None
        return self._vn_api
    

    
    def _adjust_risk_for_profile(self, base_risk: dict, risk_tolerance: int, time_horizon: str, investment_amount: int):
        """Adjust risk assessment based on investment profile"""
        adjusted = base_risk.copy()
        
        # Adjust risk level based on user's risk tolerance
        base_risk_level = base_risk.get('risk_level', 'MEDIUM')
        
        if risk_tolerance <= 30:  # Conservative
            # Conservative investors should see higher risk warnings
            if base_risk_level == 'MEDIUM':
                adjusted['risk_level'] = 'HIGH'
                adjusted['profile_adjustment'] = 'Risk increased for conservative profile'
            elif base_risk_level == 'LOW':
                adjusted['risk_level'] = 'MEDIUM'
                adjusted['profile_adjustment'] = 'Risk adjusted for conservative profile'
        elif risk_tolerance >= 70:  # Aggressive
            # Aggressive investors can handle more risk
            if base_risk_level == 'HIGH':
                adjusted['risk_level'] = 'MEDIUM'
                adjusted['profile_adjustment'] = 'Risk reduced for aggressive profile'
            elif base_risk_level == 'MEDIUM':
                adjusted['risk_level'] = 'LOW'
                adjusted['profile_adjustment'] = 'Risk reduced for aggressive profile'
        
        # Adjust position sizing recommendations
        max_position = self._calculate_max_position(risk_tolerance, investment_amount)
        stop_loss_pct = self._calculate_stop_loss(risk_tolerance, time_horizon)
        
        adjusted['position_recommendations'] = {
            'max_position_pct': max_position * 100,
            'max_investment_amount': investment_amount * max_position,
            'stop_loss_pct': stop_loss_pct,
            'time_horizon_days': self._get_time_horizon_days(time_horizon)
        }
        
        return adjusted
    
    def _get_risk_profile_name(self, risk_tolerance: int) -> str:
        """Get risk profile name from tolerance level"""
        if risk_tolerance <= 30:
            return "Thận trọng"
        elif risk_tolerance <= 70:
            return "Cân bằng"
        else:
            return "Mạo hiểm"
    
    def _calculate_max_position(self, risk_tolerance: int, investment_amount: int) -> float:
        """Calculate maximum position size based on risk tolerance"""
        if risk_tolerance <= 30:
            return 0.05  # 5% max
        elif risk_tolerance <= 70:
            return 0.10  # 10% max
        else:
            return 0.20  # 20% max
    
    def _calculate_stop_loss(self, risk_tolerance: int, time_horizon: str) -> float:
        """Calculate stop loss percentage"""
        base_stop_loss = 10  # Base 10%
        
        # Adjust for risk tolerance
        if risk_tolerance <= 30:
            base_stop_loss = 5  # Conservative: 5%
        elif risk_tolerance >= 70:
            base_stop_loss = 15  # Aggressive: 15%
        
        # Adjust for time horizon
        if "Ngắn hạn" in time_horizon:
            base_stop_loss *= 0.8  # Tighter stop loss for short term
        elif "Dài hạn" in time_horizon:
            base_stop_loss *= 1.5  # Wider stop loss for long term
        
        return base_stop_loss
    
    def _get_time_horizon_days(self, time_horizon: str) -> int:
        """Convert time horizon to days"""
        if "Ngắn hạn" in time_horizon:
            return 90
        elif "Dài hạn" in time_horizon:
            return 365
        else:
            return 180
    
    def assess_risk(self, symbol: str, risk_tolerance: int = 50, time_horizon: str = "Trung hạn", investment_amount: int = 100000000):
        try:
            print(f"🔍 Starting risk assessment for {symbol} with profile: {risk_tolerance}% risk, {time_horizon}, {investment_amount:,} VND...")
            
            # Store current parameters for AI analysis
            self._current_risk_tolerance = risk_tolerance
            self._current_time_horizon = time_horizon
            self._current_investment_amount = investment_amount
            
            # Get VN API instance
            vn_api = self._get_vn_api()
            
            # Get CrewAI collector for real data
            self.crewai_collector = getattr(vn_api, 'crewai_collector', None) if vn_api else None
            
            # Get real market data from CrewAI first
            real_market_data = None
            if self.crewai_collector and self.crewai_collector.enabled:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Get market overview and stock news for risk context
                    market_news = loop.run_until_complete(self.crewai_collector.get_market_overview_news())
                    stock_news = loop.run_until_complete(self.crewai_collector.get_stock_news(symbol, limit=3))
                    
                    loop.close()
                    
                    real_market_data = {
                        'market_news': market_news,
                        'stock_news': stock_news,
                        'market_sentiment': market_news.get('sentiment', 'Neutral'),
                        'stock_sentiment': stock_news.get('sentiment', 'Neutral')
                    }
                    print(f"✅ Got real market data for {symbol} risk analysis from CrewAI")
                    
                except Exception as e:
                    print(f"⚠️ CrewAI market data failed for {symbol}: {e}")
            
            # Get base risk analysis first
            base_risk_analysis = None
            
            # Check if VN stock using real API
            if vn_api and vn_api.is_vn_stock(symbol):
                # Try real VN data first
                try:
                    from vnstock import Vnstock
                    from datetime import datetime, timedelta
                    
                    stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
                    
                    # Lấy dữ liệu lịch sử 1 năm
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                    
                    hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                    
                    if not hist_data.empty and len(hist_data) > 30:
                        # Tính toán volatility
                        returns = hist_data['close'].pct_change().dropna()
                        
                        if len(returns) > 10:
                            volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility %
                            
                            # Tính max drawdown
                            cumulative = (1 + returns).cumprod()
                            running_max = cumulative.expanding().max()
                            drawdown = (cumulative - running_max) / running_max
                            max_drawdown = drawdown.min() * 100
                            
                            # Đánh giá rủi ro
                            if volatility > 40:
                                risk_level = "HIGH"
                            elif volatility > 25:
                                risk_level = "MEDIUM"
                            else:
                                risk_level = "LOW"
                            
                            # Beta vs VN-Index (simplified)
                            beta = 1.0
                            try:
                                vnindex_obj = Vnstock().stock(symbol='VNINDEX', source='VCI')
                                vnindex_data = vnindex_obj.quote.history(start=start_date, end=end_date, interval='1D')
                                if not vnindex_data.empty:
                                    vnindex_returns = vnindex_data['close'].pct_change().dropna()
                                    
                                    # Align dates
                                    common_dates = returns.index.intersection(vnindex_returns.index)
                                    if len(common_dates) > 50:
                                        stock_aligned = returns.loc[common_dates]
                                        vnindex_aligned = vnindex_returns.loc[common_dates]
                                        if np.var(vnindex_aligned) > 0:
                                            beta = np.cov(stock_aligned, vnindex_aligned)[0, 1] / np.var(vnindex_aligned)
                            except Exception as beta_error:
                                print(f"⚠️ Beta calculation failed: {beta_error}")
                                beta = 1.0
                            
                            # Calculate additional risk metrics
                            var_95 = abs(np.percentile(returns, 5) * 100)
                            excess_returns = returns - 0.03/252
                            sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252) if excess_returns.std() > 0 else 0
                            correlation_market = min(0.9, beta * 0.8)
                            
                            base_risk_analysis = {
                                "symbol": symbol,
                                "risk_level": risk_level,
                                "volatility": round(volatility, 2),
                                "max_drawdown": round(max_drawdown, 2),
                                "beta": round(beta, 3),
                                "risk_score": round(min(10, max(1, volatility / 5)), 0),
                                "var_95": round(var_95, 2),
                                "sharpe_ratio": round(sharpe_ratio, 3),
                                "correlation_market": round(correlation_market, 3),
                                "market": "Vietnam",
                                "benchmark": "VN-Index",
                                "data_source": "VCI_Real" + ("_with_CrewAI" if real_market_data else "")
                            }
                            
                            # Add CrewAI market context if available
                            if real_market_data:
                                base_risk_analysis['market_sentiment'] = real_market_data['market_sentiment']
                                base_risk_analysis['stock_sentiment'] = real_market_data['stock_sentiment']
                                base_risk_analysis['market_context'] = f"Market: {real_market_data['market_sentiment']}, Stock: {real_market_data['stock_sentiment']}"
                                
                                # Adjust risk level based on sentiment
                                if real_market_data['market_sentiment'] == 'Negative' or real_market_data['stock_sentiment'] == 'Negative':
                                    if risk_level == 'LOW':
                                        base_risk_analysis['risk_level'] = 'MEDIUM'
                                        base_risk_analysis['sentiment_adjustment'] = 'Risk increased due to negative sentiment'
                                    elif risk_level == 'MEDIUM':
                                        base_risk_analysis['risk_level'] = 'HIGH'
                                        base_risk_analysis['sentiment_adjustment'] = 'Risk increased due to negative sentiment'
                            
                            # Enhance with AI analysis if available
                            if self.ai_agent:
                                try:
                                    ai_enhancement = self._get_ai_risk_analysis(symbol, base_risk_analysis)
                                    base_risk_analysis.update(ai_enhancement)
                                except Exception as e:
                                    print(f"⚠️ AI risk analysis failed: {e}")
                                    base_risk_analysis['ai_enhanced'] = False
                                    base_risk_analysis['ai_error'] = str(e)
                            
                            return base_risk_analysis
                            
                except Exception as vnstock_error:
                    print(f"⚠️ VNStock risk analysis failed for {symbol}: {vnstock_error}")
                
                # Enhanced fallback for VN stocks
                base_risk_analysis = self._get_vn_fallback_risk(symbol)
            
            else:
                # US/International stocks with enhanced error handling
                if not self._is_valid_symbol(symbol):
                    return {"error": f"Invalid symbol: {symbol}"}
                    
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1y")
                    
                    if hist.empty or len(hist) < 30:
                        base_risk_analysis = self._get_international_fallback_risk(symbol)
                    else:
                        # Calculate volatility
                        returns = hist['Close'].pct_change().dropna()
                        
                        if len(returns) < 10:
                            base_risk_analysis = self._get_international_fallback_risk(symbol)
                        else:
                            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                            
                            # Calculate max drawdown
                            cumulative = (1 + returns).cumprod()
                            running_max = cumulative.expanding().max()
                            drawdown = (cumulative - running_max) / running_max
                            max_drawdown = drawdown.min()
                            
                            # Risk assessment
                            if volatility > 0.4:
                                risk_level = "HIGH"
                            elif volatility > 0.2:
                                risk_level = "MEDIUM"
                            else:
                                risk_level = "LOW"
                            
                            # Beta calculation (vs S&P 500) with error handling
                            beta = 1.0
                            try:
                                spy = yf.Ticker("SPY")
                                spy_hist = spy.history(period="1y")
                                
                                if not spy_hist.empty:
                                    spy_returns = spy_hist['Close'].pct_change().dropna()
                                    
                                    # Align dates
                                    common_dates = returns.index.intersection(spy_returns.index)
                                    if len(common_dates) > 50:
                                        stock_aligned = returns.loc[common_dates]
                                        spy_aligned = spy_returns.loc[common_dates]
                                        if np.var(spy_aligned) > 0:
                                            beta = np.cov(stock_aligned, spy_aligned)[0, 1] / np.var(spy_aligned)
                            except Exception as beta_error:
                                print(f"⚠️ Beta calculation failed for {symbol}: {beta_error}")
                                beta = 1.0
                            
                            # Calculate additional risk metrics
                            var_95 = abs(np.percentile(returns, 5) * 100)
                            excess_returns = returns - 0.03/252
                            sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252) if excess_returns.std() > 0 else 0
                            correlation_market = min(0.9, beta * 0.8)
                            
                            base_risk_analysis = {
                                "symbol": symbol,
                                "risk_level": risk_level,
                                "volatility": round(volatility * 100, 2),
                                "max_drawdown": round(max_drawdown * 100, 2),
                                "beta": round(beta, 3),
                                "risk_score": round(min(10, max(1, volatility * 100 / 5)), 0),
                                "var_95": round(var_95, 2),
                                "sharpe_ratio": round(sharpe_ratio, 3),
                                "correlation_market": round(correlation_market, 3),
                                "market": "International",
                                "benchmark": "S&P 500",
                                "data_source": "Yahoo_Finance" + ("_with_CrewAI" if real_market_data else "")
                            }
                            
                            # Add CrewAI context for international stocks too
                            if real_market_data:
                                base_risk_analysis['market_context'] = f"Global sentiment: {real_market_data['market_sentiment']}"
                            
                except Exception as yf_error:
                    print(f"⚠️ Yahoo Finance failed for {symbol}: {yf_error}")
                    base_risk_analysis = self._get_international_fallback_risk(symbol)
                    
        except Exception as e:
            print(f"❌ Critical error in risk assessment for {symbol}: {e}")
            base_risk_analysis = self._get_fallback_risk(symbol)
        
        # Add investment profile to base analysis before AI enhancement
        if base_risk_analysis and "error" not in base_risk_analysis:
            # Add investment profile context
            base_risk_analysis['investment_profile'] = {
                'risk_tolerance': risk_tolerance,
                'time_horizon': time_horizon,
                'investment_amount': investment_amount,
                'risk_profile': self._get_risk_profile_name(risk_tolerance)
            }
            
            # Adjust risk assessment based on investment profile
            base_risk_analysis = self._adjust_risk_for_profile(base_risk_analysis, risk_tolerance, time_horizon, investment_amount)
        
        # Enhance with AI analysis if available
        if base_risk_analysis and "error" not in base_risk_analysis and self.ai_agent:
            try:
                ai_enhancement = self._get_ai_risk_analysis(symbol, base_risk_analysis)
                base_risk_analysis.update(ai_enhancement)
            except Exception as e:
                print(f"⚠️ AI risk analysis failed: {e}")
                base_risk_analysis['ai_enhanced'] = False
                base_risk_analysis['ai_error'] = str(e)
        
        return base_risk_analysis
    
    def _get_vn_fallback_risk(self, symbol: str):
        """Enhanced fallback risk assessment for VN stocks"""
        import random
        
        # Realistic risk profiles for major VN stocks
        vn_risk_profiles = {
            'VCB': {'volatility': 18.5, 'risk_level': 'LOW', 'beta': 0.85, 'max_drawdown': -12.3},
            'BID': {'volatility': 22.1, 'risk_level': 'LOW', 'beta': 0.92, 'max_drawdown': -15.7},
            'CTG': {'volatility': 24.8, 'risk_level': 'MEDIUM', 'beta': 1.05, 'max_drawdown': -18.2},
            'VIC': {'volatility': 35.2, 'risk_level': 'HIGH', 'beta': 1.35, 'max_drawdown': -28.5},
            'VHM': {'volatility': 32.8, 'risk_level': 'HIGH', 'beta': 1.28, 'max_drawdown': -25.9},
            'HPG': {'volatility': 28.7, 'risk_level': 'MEDIUM', 'beta': 1.15, 'max_drawdown': -22.1},
            'FPT': {'volatility': 26.3, 'risk_level': 'MEDIUM', 'beta': 1.08, 'max_drawdown': -19.4}
        }
        
        profile = vn_risk_profiles.get(symbol, {
            'volatility': 25.0, 'risk_level': 'MEDIUM', 'beta': 1.0, 'max_drawdown': -20.0
        })
        
        # Add some randomness to make it more realistic
        volatility = profile['volatility'] + random.uniform(-2, 2)
        beta = profile['beta'] + random.uniform(-0.1, 0.1)
        max_drawdown = profile['max_drawdown'] + random.uniform(-3, 3)
        
        print(f"⚠️ Using ENHANCED FALLBACK risk assessment for {symbol} - May not be current!")
        
        # Calculate fallback additional metrics
        var_95 = abs(max_drawdown * 0.6)
        sharpe_ratio = max(0.1, 2.0 - (volatility / 20))
        correlation_market = min(0.9, beta * 0.8)
        
        return {
            "symbol": symbol,
            "risk_level": profile['risk_level'],
            "volatility": round(volatility, 2),
            "max_drawdown": round(max_drawdown, 2),
            "beta": round(beta, 3),
            "risk_score": round(min(10, max(1, volatility / 5)), 0),
            "var_95": round(var_95, 2),
            "sharpe_ratio": round(sharpe_ratio, 3),
            "correlation_market": round(correlation_market, 3),
            "market": "Vietnam",
            "benchmark": "VN-Index",
            "data_source": "Enhanced_Fallback",
            "warning": "Fallback data - not suitable for real trading decisions"
        }
    
    def _get_international_fallback_risk(self, symbol: str):
        """Fallback risk assessment for international stocks"""
        import random
        
        # Estimate risk based on symbol characteristics
        if len(symbol) <= 4 and symbol.isalpha():
            # Likely large cap
            volatility = random.uniform(15, 25)
            risk_level = "LOW" if volatility < 20 else "MEDIUM"
        else:
            # Likely small cap or ETF
            volatility = random.uniform(20, 35)
            risk_level = "MEDIUM" if volatility < 30 else "HIGH"
        
        beta = random.uniform(0.7, 1.3)
        max_drawdown = -(volatility * random.uniform(0.8, 1.2))
        
        print(f"⚠️ Using FALLBACK risk assessment for {symbol} - Not reliable!")
        
        # Calculate fallback additional metrics
        var_95 = abs(max_drawdown * 0.6)
        sharpe_ratio = max(0.1, 2.0 - (volatility / 20))
        correlation_market = min(0.9, beta * 0.8)
        
        return {
            "symbol": symbol,
            "risk_level": risk_level,
            "volatility": round(volatility, 2),
            "max_drawdown": round(max_drawdown, 2),
            "beta": round(beta, 3),
            "risk_score": round(min(10, max(1, volatility / 5)), 0),
            "var_95": round(var_95, 2),
            "sharpe_ratio": round(sharpe_ratio, 3),
            "correlation_market": round(correlation_market, 3),
            "market": "International",
            "benchmark": "S&P 500",
            "data_source": "Fallback",
            "warning": "Fallback data - not suitable for real trading decisions"
        }
    
    def _get_fallback_risk(self, symbol: str):
        """General fallback risk assessment"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.data.vn_stock_api import VNStockAPI
        
        vn_api = VNStockAPI()
        
        if vn_api.is_vn_stock(symbol):
            return self._get_vn_fallback_risk(symbol)
        else:
            return self._get_international_fallback_risk(symbol)
    
    def _is_valid_symbol(self, symbol: str) -> bool:
        """Kiểm tra symbol hợp lệ"""
        if not symbol or len(symbol) < 1:
            return False
        
        # Loại bỏ các mã biết là không hợp lệ
        invalid_symbols = ['X20', 'X21', 'X22', 'X23', 'X24', 'X25', 'TEST', 'DEMO']
        if symbol.upper() in invalid_symbols:
            return False
        
        return True
    
    def _get_ai_risk_analysis(self, symbol: str, base_analysis: dict):
        """Get AI-enhanced risk analysis with DIVERSE advice based on profile"""
        try:
            # Get investment profile data from the assess_risk call parameters
            risk_tolerance = getattr(self, '_current_risk_tolerance', 50)
            time_horizon = getattr(self, '_current_time_horizon', 'Trung hạn')
            investment_amount = getattr(self, '_current_investment_amount', 100000000)
            
            # Calculate risk profile name
            if risk_tolerance <= 30:
                risk_profile = "Thận trọng"
            elif risk_tolerance <= 70:
                risk_profile = "Cân bằng"
            else:
                risk_profile = "Mạo hiểm"
            
            # Calculate position sizing based on actual parameters
            max_position = self._calculate_max_position(risk_tolerance, investment_amount)
            stop_loss_pct = self._calculate_stop_loss(risk_tolerance, time_horizon)
            max_investment = investment_amount * max_position
            
            # Create DIVERSE context based on profile combination
            context = self._create_diverse_risk_context(symbol, base_analysis, risk_tolerance, time_horizon, investment_amount, risk_profile, max_position, stop_loss_pct, max_investment)
            
            # Get AI analysis
            ai_result = self.ai_agent.generate_with_fallback(context, 'risk_assessment', max_tokens=400)
            
            if ai_result['success']:
                # Parse AI response for advice and reasoning
                ai_advice, ai_reasoning = self._parse_ai_advice(ai_result['response'])
                
                # If AI doesn't provide diverse enough response, create fallback
                if not ai_advice or len(ai_advice) < 50:
                    ai_advice, ai_reasoning = self._create_diverse_fallback_advice(symbol, base_analysis, risk_tolerance, time_horizon, investment_amount, max_position, stop_loss_pct)
                
                # Parse AI response for actual adjustments
                ai_adjustments = self._parse_ai_risk_adjustments(ai_result['response'])
                
                # Apply AI adjustments to base analysis
                adjusted_analysis = self._apply_ai_risk_adjustments(base_analysis, ai_adjustments)
                
                return {
                    'ai_risk_analysis': ai_result['response'],
                    'ai_model_used': ai_result['model_used'],
                    'ai_enhanced': True,
                    'ai_advice': ai_advice,
                    'ai_reasoning': ai_reasoning,
                    'ai_adjustments': ai_adjustments,
                    'enhanced_risk_level': ai_adjustments.get('risk_level', base_analysis.get('risk_level', 'MEDIUM')),
                    'ai_volatility': adjusted_analysis.get('ai_volatility', base_analysis.get('volatility')),
                    'ai_var_95': adjusted_analysis.get('ai_var_95', base_analysis.get('var_95')),
                    'ai_sharpe_ratio': ai_adjustments.get('sharpe_ratio', base_analysis.get('sharpe_ratio')),
                    'ai_risk_score': ai_adjustments.get('risk_score', base_analysis.get('risk_score')),
                    'position_size_recommendation': ai_adjustments.get('position_size', 10),
                    'stop_loss_recommendation': ai_adjustments.get('stop_loss', 10)
                }
            else:
                # Create diverse fallback advice
                ai_advice, ai_reasoning = self._create_diverse_fallback_advice(symbol, base_analysis, risk_tolerance, time_horizon, investment_amount, max_position, stop_loss_pct)
                return {
                    'ai_enhanced': False, 
                    'ai_error': ai_result.get('error', 'AI not available'),
                    'ai_advice': ai_advice,
                    'ai_reasoning': ai_reasoning
                }
                
        except Exception as e:
            # Create diverse fallback advice even on error
            ai_advice, ai_reasoning = self._create_diverse_fallback_advice(symbol, base_analysis, getattr(self, '_current_risk_tolerance', 50), getattr(self, '_current_time_horizon', 'Trung hạn'), getattr(self, '_current_investment_amount', 100000000), 0.1, 10)
            return {
                'ai_enhanced': False, 
                'ai_error': str(e),
                'ai_advice': ai_advice,
                'ai_reasoning': ai_reasoning
            }
    
    def _parse_ai_risk_adjustments(self, ai_response: str):
        """Parse AI response for risk adjustments"""
        import re
        adjustments = {
            'risk_level': 'MEDIUM',
            'volatility_adj': 0,
            'var_adj': 0,
            'sharpe_ratio': 1.0,
            'risk_score': 5,
            'position_size': 10,
            'stop_loss': 10,
            'reason': ai_response
        }
        
        try:
            # Extract AI risk level
            risk_match = re.search(r'AI_RISK_LEVEL:\s*(LOW|MEDIUM|HIGH|VERY_HIGH)', ai_response, re.IGNORECASE)
            if risk_match:
                adjustments['risk_level'] = risk_match.group(1).upper()
            
            # Extract volatility adjustment
            vol_match = re.search(r'VOLATILITY_ADJUSTMENT:\s*([+-]?\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if vol_match:
                adjustments['volatility_adj'] = float(vol_match.group(1))
            
            # Extract VaR adjustment
            var_match = re.search(r'VAR_ADJUSTMENT:\s*([+-]?\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if var_match:
                adjustments['var_adj'] = float(var_match.group(1))
            
            # Extract Sharpe ratio
            sharpe_match = re.search(r'SHARPE_RATIO:\s*(\d+(?:\.\d+)?)', ai_response, re.IGNORECASE)
            if sharpe_match:
                adjustments['sharpe_ratio'] = float(sharpe_match.group(1))
            
            # Extract risk score
            score_match = re.search(r'RISK_SCORE:\s*(\d+)', ai_response, re.IGNORECASE)
            if score_match:
                adjustments['risk_score'] = int(score_match.group(1))
            
            # Extract position size
            pos_match = re.search(r'POSITION_SIZE:\s*(\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if pos_match:
                adjustments['position_size'] = float(pos_match.group(1))
            
            # Extract stop loss
            stop_match = re.search(r'STOP_LOSS:\s*(\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if stop_match:
                adjustments['stop_loss'] = float(stop_match.group(1))
                
        except Exception as e:
            print(f"⚠️ AI risk adjustment parsing failed: {e}")
            
        return adjustments
    
    def _create_diverse_risk_context(self, symbol, base_analysis, risk_tolerance, time_horizon, investment_amount, risk_profile, max_position, stop_loss_pct, max_investment):
        """Create diverse context based on specific profile combination"""
        volatility = base_analysis.get('volatility', 25)
        risk_level = base_analysis.get('risk_level', 'MEDIUM')
        
        # Create different contexts based on profile combinations
        if risk_tolerance <= 30:  # Conservative
            if "Ngắn hạn" in time_horizon:
                focus = "bảo toàn vốn và thanh khoản cao"
                strategy = "ưu tiên blue-chip, tránh biến động mạnh"
            elif "Dài hạn" in time_horizon:
                focus = "tăng trưởng ổn định với cổ tức"
                strategy = "đầu tư vào cổ phiếu có cổ tức cao, tăng trưởng bền vững"
            else:
                focus = "cân bằng giữa an toàn và tăng trưởng nhẹ"
                strategy = "phân bổ 70% blue-chip, 30% cổ phiếu tăng trưởng ổn định"
        elif risk_tolerance >= 70:  # Aggressive
            if "Ngắn hạn" in time_horizon:
                focus = "tối đa hóa lợi nhuận trong thời gian ngắn"
                strategy = "có thể chấp nhận biến động cao để đạt mục tiêu nhanh"
            elif "Dài hạn" in time_horizon:
                focus = "tăng trưởng mạnh với khả năng chịu rủi ro cao"
                strategy = "tập trung vào cổ phiếu tăng trưởng, công nghệ, mid-cap"
            else:
                focus = "cân bằng giữa tăng trưởng và rủi ro có kiểm soát"
                strategy = "60% growth stocks, 40% established companies"
        else:  # Balanced
            if "Ngắn hạn" in time_horizon:
                focus = "tăng trưởng vừa phải với rủi ro kiểm soát"
                strategy = "đa dạng hóa giữa các nhóm cổ phiếu"
            elif "Dài hạn" in time_horizon:
                focus = "tăng trưởng dài hạn với rủi ro cân bằng"
                strategy = "kết hợp cổ phiếu tăng trưởng và cổ tức"
            else:
                focus = "cân bằng tối ưu giữa rủi ro và lợi nhuận"
                strategy = "phân bổ đều giữa các loại tài sản"
        
        return f"""
Bạn là chuyên gia quản lý rủi ro cho nhà đầu tư {risk_profile}. Phân tích rủi ro {symbol}:

HỒ SƠ ĐẦU TƯ CỤ THỂ:
- Mức độ rủi ro: {risk_tolerance}% ({risk_profile})
- Thời gian: {time_horizon} - {focus}
- Vốn đầu tư: {investment_amount:,} VND
- Chiến lược: {strategy}

DỮ LIỆU RỦI RO {symbol}:
- Risk Level: {risk_level}, Volatility: {volatility:.1f}%
- Max Drawdown: {base_analysis.get('max_drawdown', -15):.1f}%
- Beta: {base_analysis.get('beta', 1.0):.3f}

KHUYẾN NGHỊ TÍNH TOÁN:
- Tỷ trọng tối đa: {max_position*100:.0f}% = {max_investment:,.0f} VND
- Stop-loss: {stop_loss_pct:.0f}%

Yêu cầu phân tích CỤ THỂ cho hồ sơ {risk_profile} + {time_horizon}:

ADVICE: [khuyến nghị cụ thể cho {risk_profile} với {time_horizon}]
REASONING: [giải thích tại sao phù hợp với {risk_tolerance}% risk + {investment_amount:,} VND]
"""
    
    def _create_diverse_fallback_advice(self, symbol, base_analysis, risk_tolerance, time_horizon, investment_amount, max_position, stop_loss_pct):
        """Create diverse fallback advice based on profile"""
        risk_level = base_analysis.get('risk_level', 'MEDIUM')
        volatility = base_analysis.get('volatility', 25)
        
        # Create profile-specific advice
        if risk_tolerance <= 30:  # Conservative
            if "Ngắn hạn" in time_horizon:
                advice = f"Với hồ sơ thận trọng + ngắn hạn: Chỉ đầu tư {max_position*100:.0f}% ({investment_amount * max_position:,.0f} VND) vào {symbol}. Ưu tiên bảo toàn vốn, stop-loss chặt {stop_loss_pct:.0f}%."
                reasoning = f"Volatility {volatility:.1f}% của {symbol} cần quản lý cẩn thận cho nhà đầu tư thận trọng. Thời gian ngắn không cho phép phục hồi từ tổn thất lớn."
            elif "Dài hạn" in time_horizon:
                advice = f"Hồ sơ thận trọng + dài hạn: {symbol} phù hợp với {max_position*100:.0f}% danh mục ({investment_amount * max_position:,.0f} VND). Tập trung vào cổ tức và tăng trưởng ổn định."
                reasoning = f"Thời gian dài hạn giúp làm mịn volatility {volatility:.1f}%. Risk level {risk_level} chấp nhận được với chiến lược buy-and-hold."
            else:
                advice = f"Hồ sơ thận trọng + trung hạn: Đầu tư thận trọng {max_position*100:.0f}% vào {symbol} ({investment_amount * max_position:,.0f} VND). Theo dõi sát, sẵn sàng cắt lỗ {stop_loss_pct:.0f}%."
                reasoning = f"Cân bằng giữa thời gian và rủi ro. Volatility {volatility:.1f}% cần monitoring thường xuyên với hồ sơ thận trọng."
        
        elif risk_tolerance >= 70:  # Aggressive
            if "Ngắn hạn" in time_horizon:
                advice = f"Hồ sơ mạo hiểm + ngắn hạn: Có thể đầu tư tối đa {max_position*100:.0f}% vào {symbol} ({investment_amount * max_position:,.0f} VND). Chấp nhận volatility cao để tối đa hóa lợi nhuận."
                reasoning = f"Với risk tolerance {risk_tolerance}%, volatility {volatility:.1f}% của {symbol} là cơ hội. Stop-loss rộng {stop_loss_pct:.0f}% cho phép cổ phiếu dao động."
            elif "Dài hạn" in time_horizon:
                advice = f"Hồ sơ mạo hiểm + dài hạn: {symbol} là lựa chọn tốt với {max_position*100:.0f}% danh mục ({investment_amount * max_position:,.0f} VND). Tập trung vào tiềm năng tăng trưởng dài hạn."
                reasoning = f"Kết hợp risk tolerance {risk_tolerance}% và thời gian dài hạn tạo lợi thế. Volatility {volatility:.1f}% sẽ được làm mịn theo thời gian."
            else:
                advice = f"Hồ sơ mạo hiểm + trung hạn: Đầu tư tích cực {max_position*100:.0f}% vào {symbol} ({investment_amount * max_position:,.0f} VND). Cân bằng giữa tăng trưởng và kiểm soát rủi ro."
                reasoning = f"Risk tolerance {risk_tolerance}% cho phép chấp nhận volatility {volatility:.1f}%. Thời gian trung hạn đủ để tận dụng chu kỳ thị trường."
        
        else:  # Balanced
            if "Ngắn hạn" in time_horizon:
                advice = f"Hồ sơ cân bằng + ngắn hạn: Đầu tư vừa phải {max_position*100:.0f}% vào {symbol} ({investment_amount * max_position:,.0f} VND). Cân bằng giữa cơ hội và rủi ro."
                reasoning = f"Risk tolerance {risk_tolerance}% phù hợp với volatility {volatility:.1f}%. Thời gian ngắn cần cân bằng tốt giữa lợi nhuận và an toàn."
            elif "Dài hạn" in time_horizon:
                advice = f"Hồ sơ cân bằng + dài hạn: {symbol} phù hợp với {max_position*100:.0f}% danh mục ({investment_amount * max_position:,.0f} VND). Tối ưu hóa risk-adjusted return."
                reasoning = f"Kết hợp tốt giữa risk tolerance {risk_tolerance}% và thời gian dài hạn. Volatility {volatility:.1f}% có thể quản lý được với chiến lược dài hạn."
            else:
                advice = f"Hồ sơ cân bằng + trung hạn: Đầu tư cân bằng {max_position*100:.0f}% vào {symbol} ({investment_amount * max_position:,.0f} VND). Đa dạng hóa để tối ưu rủi ro."
                reasoning = f"Risk tolerance {risk_tolerance}% và thời gian trung hạn tạo sự cân bằng tối ưu. Volatility {volatility:.1f}% nằm trong ngưỡng chấp nhận được."
        
        return advice, reasoning
    
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
                else:
                    advice = ai_response[:200] + "..." if len(ai_response) > 200 else ai_response
                    
        except Exception as e:
            print(f"⚠️ Risk advice parsing failed: {e}")
            advice = "Cần quản lý rủi ro thận trọng"
            reasoning = "Dựa trên phân tích các chỉ số rủi ro hiện tại"
            
        return advice, reasoning
    
    def _apply_ai_risk_adjustments(self, base_analysis: dict, ai_adjustments: dict):
        """Apply AI adjustments to base risk analysis"""
        try:
            adjusted_analysis = base_analysis.copy()
            
            # Adjust volatility
            base_volatility = base_analysis.get('volatility', 25)
            volatility_adj = ai_adjustments.get('volatility_adj', 0)
            ai_volatility = base_volatility * (1 + volatility_adj / 100)
            # Ensure reasonable bounds (5% - 100%)
            ai_volatility = max(5, min(100, ai_volatility))
            adjusted_analysis['ai_volatility'] = round(ai_volatility, 2)
            
            # Adjust VaR
            base_var = base_analysis.get('var_95', 8)
            var_adj = ai_adjustments.get('var_adj', 0)
            ai_var = base_var * (1 + var_adj / 100)
            # Ensure reasonable bounds (1% - 50%)
            ai_var = max(1, min(50, ai_var))
            adjusted_analysis['ai_var_95'] = round(ai_var, 2)
            
            return adjusted_analysis
            
        except Exception as e:
            print(f"⚠️ AI risk adjustment application failed: {e}")
            return base_analysis
    
    def _extract_ai_risk_level(self, ai_response: str, base_risk_level: str):
        """Extract enhanced risk level from AI response"""
        try:
            ai_lower = ai_response.lower()
            
            # Look for risk level indicators in AI response
            if any(phrase in ai_lower for phrase in ['rủi ro rất cao', 'very high risk', 'extremely risky']):
                return 'VERY_HIGH'
            elif any(phrase in ai_lower for phrase in ['rủi ro cao', 'high risk', 'risky']):
                return 'HIGH'
            elif any(phrase in ai_lower for phrase in ['rủi ro trung bình', 'medium risk', 'moderate']):
                return 'MEDIUM'
            elif any(phrase in ai_lower for phrase in ['rủi ro thấp', 'low risk', 'safe']):
                return 'LOW'
            elif any(phrase in ai_lower for phrase in ['rủi ro rất thấp', 'very low risk', 'very safe']):
                return 'VERY_LOW'
            else:
                # Return base risk level if no clear signal
                return base_risk_level
                
        except Exception:
            return base_risk_level