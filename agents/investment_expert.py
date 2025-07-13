import yfinance as yf

class InvestmentExpert:
    def __init__(self):
        self.name = "Investment Expert Agent"
    
    def analyze_stock(self, symbol: str):
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
                
                # Lấy chỉ số tài chính
                try:
                    ratios = stock_obj.finance.ratio(period='quarter', lang='vi', dropna=True)
                    if not ratios.empty:
                        latest_ratio = ratios.iloc[-1]
                        pe_ratio = latest_ratio.get('pe', 0)
                        pb_ratio = latest_ratio.get('pb', 0)
                        roe = latest_ratio.get('roe', 0)
                    else:
                        pe_ratio = pb_ratio = roe = 0
                except:
                    pe_ratio = pb_ratio = roe = 0
                
                dividend_yield = 0  # Not available
                
                # Phân tích giá
                current_price = float(hist_data['close'].iloc[-1])
                year_high = float(hist_data['high'].max())
                year_low = float(hist_data['low'].min())
                
                price_position = (current_price - year_low) / (year_high - year_low)
                
                # Logic khuyến nghị dựa trên PE, PB, ROE và vị trí giá
                if pe_ratio > 0 and pb_ratio > 0 and roe > 0:
                    if pe_ratio < 15 and pb_ratio < 2 and roe > 15 and price_position < 0.7:
                        recommendation = "BUY"
                        reason = "PE thấp, PB hợp lý, ROE cao, giá chưa cao"
                    elif pe_ratio > 25 or pb_ratio > 3 or price_position > 0.8:
                        recommendation = "SELL"
                        reason = "Định giá cao hoặc giá gần đỉnh"
                    else:
                        recommendation = "HOLD"
                        reason = "Định giá hợp lý, quan sát thêm"
                else:
                    # Fallback to price position analysis
                    if price_position > 0.7:
                        recommendation = "HOLD"
                        reason = "Cổ phiếu ở vùng giá cao"
                    elif price_position < 0.4:
                        recommendation = "BUY"
                        reason = "Cổ phiếu ở vùng giá thấp, cơ hội mua vào"
                    else:
                        recommendation = "HOLD"
                        reason = "Cổ phiếu ở vùng giá trung bình"
                
                # Tính market cap
                try:
                    overview = stock_obj.company.overview()
                    if not overview.empty:
                        overview_data = overview.iloc[0]
                        issue_share = overview_data.get('issue_share', 0)
                        if issue_share and issue_share > 0:
                            market_cap = f"{round(issue_share * current_price / 1_000_000_000_000, 1)} nghìn tỷ VND"
                        else:
                            market_cap = "N/A"
                    else:
                        market_cap = "N/A"
                except:
                    market_cap = "N/A"
                
                return {
                    "symbol": symbol,
                    "recommendation": recommendation,
                    "reason": reason,
                    "pe_ratio": round(pe_ratio, 2) if pe_ratio else 0,
                    "pb_ratio": round(pb_ratio, 3) if pb_ratio else 0,
                    "roe": round(roe, 2) if roe else 0,
                    "market_cap": market_cap,
                    "dividend_yield": round(dividend_yield, 2) if dividend_yield else 0,
                    "current_price": round(current_price, 2),
                    "year_high": round(year_high, 2),
                    "year_low": round(year_low, 2),
                    "market": "Vietnam",
                    "data_source": "VCI_Real"
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