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
    
    def assess_risk(self, symbol: str):
        try:
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
        """Get AI-enhanced risk analysis with REAL adjustments"""
        try:
            # Prepare context for AI analysis with advice request
            context = f"""
Bạn là chuyên gia quản lý rủi ro. Hãy phân tích rủi ro cổ phiếu {symbol}:

DỮ LIỆU RỦI RO:
- Mức rủi ro: {base_analysis.get('risk_level', 'MEDIUM')}
- Volatility: {base_analysis.get('volatility', 25)}%
- Max Drawdown: {base_analysis.get('max_drawdown', -15)}%
- Beta: {base_analysis.get('beta', 1.0)}
- VaR 95%: {base_analysis.get('var_95', 8)}%
- Risk Score: {base_analysis.get('risk_score', 5)}/10

YÊU CẦU:
1. Đưa ra lời khuyên quản lý rủi ro cụ thể
2. Giải thích cách kiểm soát rủi ro
3. Khuyến nghị về tỷ trọng đầu tư và stop-loss

Trả lời ngắn gọn, thực tế cho nhà đầu tư Việt Nam.

ADVICE: [lời khuyên quản lý rủi ro]
REASONING: [lý do và cách thực hiện]
"""
            
            # Get AI analysis
            ai_result = self.ai_agent.generate_with_fallback(context, 'risk_assessment', max_tokens=400)
            
            if ai_result['success']:
                # Parse AI response for advice and reasoning
                ai_advice, ai_reasoning = self._parse_ai_advice(ai_result['response'])
                
                # Parse AI response for actual adjustments (fallback to existing method)
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
                return {'ai_enhanced': False, 'ai_error': ai_result.get('error', 'AI not available')}
                
        except Exception as e:
            return {'ai_enhanced': False, 'ai_error': str(e)}
    
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