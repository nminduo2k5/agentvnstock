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
                # Mock risk assessment for VN stocks
                import random
                
                # VN market typically has higher volatility
                volatility = random.uniform(25, 45)  # 25-45% annual volatility
                max_drawdown = random.uniform(-25, -10)  # -25% to -10%
                
                if volatility > 35:
                    risk_level = "HIGH"
                elif volatility > 25:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"
                
                # Beta vs VN-Index (mock)
                beta = random.uniform(0.7, 1.3)
                
                return {
                    "symbol": symbol,
                    "risk_level": risk_level,
                    "volatility": round(volatility, 2),
                    "max_drawdown": round(max_drawdown, 2),
                    "beta": round(beta, 2),
                    "risk_score": round(volatility / 10, 1),
                    "market": "Vietnam",
                    "benchmark": "VN-Index"
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