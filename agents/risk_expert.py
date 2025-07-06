import yfinance as yf
import numpy as np

class RiskExpert:
    def __init__(self):
        self.name = "Risk Expert Agent"
    
    def assess_risk(self, symbol: str):
        try:
            # Check if VN stock
            vn_stocks = ['VCB', 'BID', 'CTG', 'TCB', 'ACB', 'VIC', 'VHM', 'VRE', 'DXG', 'MSN', 'MWG', 'VNM', 'SAB', 'HPG', 'GAS', 'PLX', 'FPT']
            
            if symbol.upper() in vn_stocks:
                from vnstock import Vnstock
                from datetime import datetime, timedelta
                
                stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
                
                # Lấy dữ liệu lịch sử 1 năm
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                
                hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                
                if hist_data.empty:
                    return {"error": f"No data found for {symbol}"}
                
                # Tính toán volatility
                returns = hist_data['close'].pct_change().dropna()
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
                try:
                    vnindex_obj = Vnstock().stock(symbol='VNINDEX', source='VCI')
                    vnindex_data = vnindex_obj.quote.history(start=start_date, end=end_date, interval='1D')
                    vnindex_returns = vnindex_data['close'].pct_change().dropna()
                    
                    # Align dates
                    common_dates = returns.index.intersection(vnindex_returns.index)
                    if len(common_dates) > 50:
                        stock_aligned = returns.loc[common_dates]
                        vnindex_aligned = vnindex_returns.loc[common_dates]
                        beta = np.cov(stock_aligned, vnindex_aligned)[0, 1] / np.var(vnindex_aligned)
                    else:
                        beta = 1.0
                except:
                    beta = 1.0
                
                return {
                    "symbol": symbol,
                    "risk_level": risk_level,
                    "volatility": round(volatility, 2),
                    "max_drawdown": round(max_drawdown, 2),
                    "beta": round(beta, 2),
                    "risk_score": round(volatility / 10, 1),
                    "market": "Vietnam",
                    "benchmark": "VN-Index",
                    "data_source": "VCI_Real"
                }
            
            # US/International stocks
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {"error": f"No data found for {symbol}"}
            
            # Calculate volatility
            returns = hist['Close'].pct_change().dropna()
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
            
            # Beta calculation (vs S&P 500)
            try:
                spy = yf.Ticker("SPY")
                spy_hist = spy.history(period="1y")
                spy_returns = spy_hist['Close'].pct_change().dropna()
                
                # Align dates
                common_dates = returns.index.intersection(spy_returns.index)
                if len(common_dates) > 50:
                    stock_aligned = returns.loc[common_dates]
                    spy_aligned = spy_returns.loc[common_dates]
                    beta = np.cov(stock_aligned, spy_aligned)[0, 1] / np.var(spy_aligned)
                else:
                    beta = 1.0
            except:
                beta = 1.0
            
            return {
                "symbol": symbol,
                "risk_level": risk_level,
                "volatility": round(volatility * 100, 2),
                "max_drawdown": round(max_drawdown * 100, 2),
                "beta": round(beta, 2),
                "risk_score": round(volatility * 10, 1),
                "market": "International",
                "benchmark": "S&P 500"
            }
        except Exception as e:
            return {"error": str(e)}