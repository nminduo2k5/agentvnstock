import yfinance as yf
import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class InvestmentExpert:
    def __init__(self, vn_api=None):
        self.name = "Investment Expert Agent"
        # Use provided VN API or lazy initialization
        self._vn_api = vn_api
    
    def _get_vn_api(self):
        """Get VN API instance (provided or lazy initialization)"""
        if self._vn_api is None:
            try:
                from src.data.vn_stock_api import VNStockAPI
                self._vn_api = VNStockAPI()
                print("⚠️ InvestmentExpert: Using fallback VN API initialization")
            except Exception as e:
                print(f"⚠️ Failed to initialize VN API: {e}")
                self._vn_api = None
        return self._vn_api
    
    def analyze_stock(self, symbol: str):
        try:
            # Get VN API instance
            vn_api = self._get_vn_api()
            
            # Check if VN stock using real API
            if vn_api and vn_api.is_vn_stock(symbol):
                # Handle async properly
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If already in async context, use sync fallback
                        print(f"⚠️ Using VNStock fallback for {symbol} due to async context")
                        return self._analyze_with_vnstock_fallback(symbol)
                    else:
                        return asyncio.run(self._analyze_vn_stock_with_real_data(symbol, vn_api))
                except RuntimeError:
                    # Fallback if async issues
                    print(f"⚠️ Using VNStock fallback for {symbol} due to async conflict")
                    return self._analyze_with_vnstock_fallback(symbol)
            else:
                # International stocks
                return self._analyze_international_stock(symbol)
                
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_vn_stock_with_real_data(self, symbol: str, vn_api):
        """Analyze VN stock using VN Stock API → CrewAI Collector → Real Data flow"""
        try:
            # Step 1: Try to get real data from VN Stock API
            stock_data = await vn_api.get_stock_data(symbol, force_refresh=False)
            price_history = await vn_api.get_price_history(symbol, days=365)
            
            if stock_data and price_history and len(price_history) > 0:
                # Use real data from VN API
                return self._analyze_with_real_data(symbol, stock_data, price_history, "VN_API_Real")
            
            # Step 2: Fallback to VNStock direct call
            print(f"⚠️ VN API data not available for {symbol}, trying VNStock fallback...")
            return self._analyze_with_vnstock_fallback(symbol)
            
        except Exception as e:
            print(f"❌ Real data analysis failed for {symbol}: {e}")
            return self._analyze_with_vnstock_fallback(symbol)
    
    def _analyze_with_real_data(self, symbol: str, stock_data, price_history, data_source: str):
        """Analyze using real data from VN API"""
        try:
            # Extract current price and price range
            current_price = stock_data.price
            
            # Calculate year high/low from price history
            prices = [float(p['close']) for p in price_history if p.get('close')]
            if not prices:
                return {"error": f"No price data available for {symbol}"}
            
            year_high = max(prices)
            year_low = min(prices)
            price_position = (current_price - year_low) / (year_high - year_low) if year_high != year_low else 0.5
            
            # Use financial ratios from stock_data
            pe_ratio = stock_data.pe_ratio or 0
            pb_ratio = stock_data.pb_ratio or 0
            
            # Estimate ROE (simplified)
            roe = 15.0 if pe_ratio > 0 and pb_ratio > 0 else 0
            
            # Investment logic based on real data
            if pe_ratio > 0 and pb_ratio > 0:
                if pe_ratio < 15 and pb_ratio < 2 and price_position < 0.7:
                    recommendation = "BUY"
                    reason = f"PE {pe_ratio:.1f} thấp, PB {pb_ratio:.2f} hợp lý, giá ở {price_position*100:.0f}% range"
                elif pe_ratio > 25 or pb_ratio > 3 or price_position > 0.8:
                    recommendation = "SELL"
                    reason = f"PE {pe_ratio:.1f} cao hoặc giá ở {price_position*100:.0f}% range"
                else:
                    recommendation = "HOLD"
                    reason = f"PE {pe_ratio:.1f}, PB {pb_ratio:.2f} ở mức hợp lý"
            else:
                # Price-based analysis
                if price_position > 0.7:
                    recommendation = "HOLD"
                    reason = f"Giá ở {price_position*100:.0f}% của range năm"
                elif price_position < 0.4:
                    recommendation = "BUY"
                    reason = f"Giá ở {price_position*100:.0f}% của range năm, cơ hội tốt"
                else:
                    recommendation = "HOLD"
                    reason = f"Giá ở {price_position*100:.0f}% của range năm"
            
            # Calculate market cap
            market_cap = f"{stock_data.market_cap / 1_000_000_000_000:.1f} nghìn tỷ VND" if stock_data.market_cap > 0 else "N/A"
            
            return {
                "symbol": symbol,
                "recommendation": recommendation,
                "reason": reason,
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else 0,
                "pb_ratio": round(pb_ratio, 3) if pb_ratio else 0,
                "roe": round(roe, 2) if roe else 0,
                "market_cap": market_cap,
                "dividend_yield": 0,  # Not available in current data
                "current_price": round(current_price, 2),
                "year_high": round(year_high, 2),
                "year_low": round(year_low, 2),
                "market": "Vietnam",
                "data_source": data_source
            }
            
        except Exception as e:
            print(f"❌ Error analyzing with real data: {e}")
            return self._analyze_with_vnstock_fallback(symbol)
    
    def _analyze_with_vnstock_fallback(self, symbol: str):
        """Fallback to direct VNStock call"""
        try:
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
                "data_source": "VNStock_Fallback"
            }
            
        except Exception as e:
            return {"error": f"VNStock fallback failed: {str(e)}"}
    
    def _analyze_international_stock(self, symbol: str):
        """Analyze international stocks using Yahoo Finance"""
        try:
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
                "market": "International",
                "data_source": "Yahoo_Finance"
            }
        except Exception as e:
            return {"error": str(e)}