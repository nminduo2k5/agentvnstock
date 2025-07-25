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
                            
                            return {
                                "symbol": symbol,
                                "risk_level": risk_level,
                                "volatility": round(volatility, 2),
                                "max_drawdown": round(max_drawdown, 2),
                                "beta": round(beta, 2),
                                "risk_score": round(volatility / 10, 2),
                                "market": "Vietnam",
                                "benchmark": "VN-Index",
                                "data_source": "VCI_Real"
                            }
                            
                except Exception as vnstock_error:
                    print(f"⚠️ VNStock risk analysis failed for {symbol}: {vnstock_error}")
                
                # Enhanced fallback for VN stocks
                return self._get_vn_fallback_risk(symbol)
            
            # US/International stocks with enhanced error handling
            if not self._is_valid_symbol(symbol):
                return {"error": f"Invalid symbol: {symbol}"}
                
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                
                if hist.empty or len(hist) < 30:
                    return self._get_international_fallback_risk(symbol)
                
                # Calculate volatility
                returns = hist['Close'].pct_change().dropna()
                
                if len(returns) < 10:
                    return self._get_international_fallback_risk(symbol)
                    
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
                
                return {
                    "symbol": symbol,
                    "risk_level": risk_level,
                    "volatility": round(volatility * 100, 2),
                    "max_drawdown": round(max_drawdown * 100, 2),
                    "beta": round(beta, 2),
                    "risk_score": round(volatility * 10, 2),
                    "market": "International",
                    "benchmark": "S&P 500",
                    "data_source": "Yahoo_Finance"
                }
                
            except Exception as yf_error:
                print(f"⚠️ Yahoo Finance failed for {symbol}: {yf_error}")
                return self._get_international_fallback_risk(symbol)
        except Exception as e:
            print(f"❌ Critical error in risk assessment for {symbol}: {e}")
            return self._get_fallback_risk(symbol)
    
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
        
        return {
            "symbol": symbol,
            "risk_level": profile['risk_level'],
            "volatility": round(volatility, 2),
            "max_drawdown": round(max_drawdown, 2),
            "beta": round(beta, 3),
            "risk_score": round(volatility / 10, 2),
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
        
        return {
            "symbol": symbol,
            "risk_level": risk_level,
            "volatility": round(volatility, 2),
            "max_drawdown": round(max_drawdown, 2),
            "beta": round(beta, 3),
            "risk_score": round(volatility / 10, 2),
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