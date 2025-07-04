import yfinance as yf

class InvestmentExpert:
    def __init__(self):
        self.name = "Investment Expert Agent"
    
    def analyze_stock(self, symbol: str):
        try:
            # Check if VN stock
            vn_stocks = ['VCB', 'BID', 'CTG', 'TCB', 'ACB', 'VIC', 'VHM', 'VRE', 'DXG', 'MSN', 'MWG', 'VNM', 'SAB', 'HPG', 'GAS', 'PLX', 'FPT']
            
            if symbol.upper() in vn_stocks:
                # Mock analysis for VN stocks
                import random
                
                base_prices = {
                    'VCB': 85000, 'BID': 45000, 'CTG': 35000, 'TCB': 55000,
                    'VIC': 90000, 'VHM': 75000, 'MSN': 120000, 'MWG': 80000,
                    'HPG': 25000, 'FPT': 95000, 'VNM': 85000, 'GAS': 95000
                }
                
                current_price = base_prices.get(symbol.upper(), 50000)
                year_high = current_price * random.uniform(1.1, 1.4)
                year_low = current_price * random.uniform(0.7, 0.9)
                
                price_position = (current_price - year_low) / (year_high - year_low)
                
                if price_position > 0.7:
                    recommendation = "HOLD"
                    reason = "Cổ phiếu ở vùng giá cao"
                elif price_position < 0.4:
                    recommendation = "BUY"
                    reason = "Cổ phiếu ở vùng giá thấp, cơ hội mua vào"
                else:
                    recommendation = "HOLD"
                    reason = "Cổ phiếu ở vùng giá trung bình"
                
                return {
                    "symbol": symbol,
                    "recommendation": recommendation,
                    "reason": reason,
                    "pe_ratio": round(random.uniform(8, 25), 1),
                    "market_cap": f"{random.randint(50, 500)} nghìn tỷ VND",
                    "dividend_yield": round(random.uniform(2, 8), 1),
                    "current_price": current_price,
                    "year_high": round(year_high, -2),
                    "year_low": round(year_low, -2),
                    "market": "Vietnam"
                }
            
            # US/International stocks
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {"error": f"No data found for {symbol}"}
            
            # Basic financial metrics
            pe_ratio = info.get("trailingPE", 0)
            market_cap = info.get("marketCap", 0)
            dividend_yield = info.get("dividendYield", 0)
            
            # Price analysis
            current_price = hist['Close'].iloc[-1]
            year_high = hist['High'].max()
            year_low = hist['Low'].min()
            
            # Simple recommendation logic
            price_position = (current_price - year_low) / (year_high - year_low)
            
            if price_position > 0.8:
                recommendation = "SELL"
                reason = "Stock near yearly high"
            elif price_position < 0.3:
                recommendation = "BUY"
                reason = "Stock near yearly low"
            else:
                recommendation = "HOLD"
                reason = "Stock in middle range"
            
            return {
                "symbol": symbol,
                "recommendation": recommendation,
                "reason": reason,
                "pe_ratio": pe_ratio,
                "market_cap": market_cap,
                "dividend_yield": dividend_yield * 100 if dividend_yield else 0,
                "current_price": round(current_price, 2),
                "year_high": round(year_high, 2),
                "year_low": round(year_low, 2),
                "market": "International"
            }
        except Exception as e:
            return {"error": str(e)}