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
        self.ai_agent = None  # Will be set by main_agent
        self.crewai_collector = None  # Will be set from vn_api
    
    def set_ai_agent(self, ai_agent):
        """Set AI agent for enhanced investment analysis"""
        self.ai_agent = ai_agent
    
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
            
            # Get CrewAI collector for real data
            self.crewai_collector = getattr(vn_api, 'crewai_collector', None) if vn_api else None
            
            # Get real company and financial data from CrewAI
            real_company_data = None
            if self.crewai_collector and self.crewai_collector.enabled:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Get company info and news for investment context
                    symbols = loop.run_until_complete(self.crewai_collector.get_available_symbols())
                    company_info = next((s for s in symbols if s['symbol'] == symbol), {})
                    
                    stock_news = loop.run_until_complete(self.crewai_collector.get_stock_news(symbol, limit=5))
                    market_news = loop.run_until_complete(self.crewai_collector.get_market_overview_news())
                    
                    loop.close()
                    
                    real_company_data = {
                        'company_info': company_info,
                        'stock_news': stock_news,
                        'market_news': market_news,
                        'sector': company_info.get('sector', 'Unknown'),
                        'exchange': company_info.get('exchange', 'HOSE'),
                        'news_sentiment': stock_news.get('sentiment', 'Neutral'),
                        'market_sentiment': market_news.get('sentiment', 'Neutral')
                    }
                    print(f"✅ Got real company data for {symbol} investment analysis from CrewAI")
                    
                except Exception as e:
                    print(f"⚠️ CrewAI company data failed for {symbol}: {e}")
            
            # Get base analysis first
            base_analysis = None
            
            # Check if VN stock using real API
            if vn_api and vn_api.is_vn_stock(symbol):
                # Handle async properly
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If already in async context, use sync fallback
                        print(f"⚠️ Using VNStock fallback for {symbol} due to async context")
                        base_analysis = self._analyze_with_vnstock_fallback(symbol)
                    else:
                        base_analysis = asyncio.run(self._analyze_vn_stock_with_real_data(symbol, vn_api))
                except RuntimeError:
                    # Fallback if async issues
                    print(f"⚠️ Using VNStock fallback for {symbol} due to async conflict")
                    base_analysis = self._analyze_with_vnstock_fallback(symbol)
            else:
                # International stocks
                base_analysis = self._analyze_international_stock(symbol)
            
            # Enhance with AI analysis if available
            if base_analysis and "error" not in base_analysis and self.ai_agent:
                try:
                    ai_enhancement = self._get_ai_investment_analysis(symbol, base_analysis)
                    base_analysis.update(ai_enhancement)
                except Exception as e:
                    print(f"⚠️ AI investment analysis failed: {e}")
                    base_analysis['ai_enhanced'] = False
                    base_analysis['ai_error'] = str(e)
            
            return base_analysis
                
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_vn_stock_with_real_data(self, symbol: str, vn_api):
        """Analyze VN stock using VN Stock API → CrewAI Collector → Real Data flow"""
        try:
            # Get real company data from CrewAI first
            real_company_data = None
            if self.crewai_collector and self.crewai_collector.enabled:
                try:
                    # Get company info and news for investment context
                    symbols = await self.crewai_collector.get_available_symbols()
                    company_info = next((s for s in symbols if s['symbol'] == symbol), {})
                    
                    stock_news = await self.crewai_collector.get_stock_news(symbol, limit=5)
                    market_news = await self.crewai_collector.get_market_overview_news()
                    
                    real_company_data = {
                        'company_info': company_info,
                        'stock_news': stock_news,
                        'market_news': market_news,
                        'sector': company_info.get('sector', 'Unknown'),
                        'exchange': company_info.get('exchange', 'HOSE'),
                        'news_sentiment': stock_news.get('sentiment', 'Neutral'),
                        'market_sentiment': market_news.get('sentiment', 'Neutral')
                    }
                    print(f"✅ Got real company data for {symbol} investment analysis from CrewAI")
                except Exception as e:
                    print(f"⚠️ CrewAI company data failed for {symbol}: {e}")
            
            # Step 1: Try to get real data from VN Stock API
            stock_data = await vn_api.get_stock_data(symbol, force_refresh=False)
            price_history = await vn_api.get_price_history(symbol, days=365)
            
            if stock_data and price_history and len(price_history) > 0:
                # Use real data from VN API
                return self._analyze_with_real_data(symbol, stock_data, price_history, "VN_API_Real", real_company_data)
            
            # Step 2: Fallback to VNStock direct call
            print(f"⚠️ VN API data not available for {symbol}, trying VNStock fallback...")
            return self._analyze_with_vnstock_fallback(symbol)
            
        except Exception as e:
            print(f"❌ Real data analysis failed for {symbol}: {e}")
            return self._analyze_with_vnstock_fallback(symbol)
    
    def _analyze_with_real_data(self, symbol: str, stock_data, price_history, data_source: str, real_company_data=None):
        """Analyze using real data from VN API"""
        try:
            # Get CrewAI data if not provided
            if not real_company_data:
                vn_api = self._get_vn_api()
                self.crewai_collector = getattr(vn_api, 'crewai_collector', None) if vn_api else None
                
                if self.crewai_collector and self.crewai_collector.enabled:
                    try:
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Get company info and news for investment context
                        symbols = loop.run_until_complete(self.crewai_collector.get_available_symbols())
                        company_info = next((s for s in symbols if s['symbol'] == symbol), {})
                        
                        stock_news = loop.run_until_complete(self.crewai_collector.get_stock_news(symbol, limit=5))
                        market_news = loop.run_until_complete(self.crewai_collector.get_market_overview_news())
                        
                        loop.close()
                        
                        real_company_data = {
                            'company_info': company_info,
                            'stock_news': stock_news,
                            'market_news': market_news,
                            'sector': company_info.get('sector', 'Unknown'),
                            'exchange': company_info.get('exchange', 'HOSE'),
                            'news_sentiment': stock_news.get('sentiment', 'Neutral'),
                            'market_sentiment': market_news.get('sentiment', 'Neutral')
                        }
                        print(f"✅ Got real company data for {symbol} in _analyze_with_real_data")
                    except Exception as e:
                        print(f"⚠️ Could not get CrewAI data: {e}")
                        real_company_data = None
            
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
            
            # Calculate target price based on recommendation
            if recommendation == "BUY":
                target_price = current_price * 1.2
            elif recommendation == "SELL":
                target_price = current_price * 0.9
            else:
                target_price = current_price * 1.05
            
            result = {
                "symbol": symbol,
                "recommendation": recommendation,
                "reason": reason,
                "current_price": round(current_price, 2),
                "target_price": round(target_price, 2),
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else 0,
                "pb_ratio": round(pb_ratio, 3) if pb_ratio else 0,
                "roe": round(roe, 2) if roe else 0,
                "market_cap": market_cap,
                "dividend_yield": 0,  # Not available in current data
                "year_high": round(year_high, 2),
                "year_low": round(year_low, 2),
                "market": "Vietnam",
                "data_source": data_source + ("_with_CrewAI" if real_company_data else "")
            }
            
            # Add CrewAI company context if available
            if real_company_data:
                result['sector'] = real_company_data['sector']
                result['exchange'] = real_company_data['exchange']
                result['news_sentiment'] = real_company_data['news_sentiment']
                result['market_sentiment'] = real_company_data['market_sentiment']
                result['company_context'] = f"Sector: {real_company_data['sector']}, News: {real_company_data['news_sentiment']}"
                
                # Enhance recommendation with sentiment
                if real_company_data['news_sentiment'] == 'Positive' and recommendation == 'HOLD':
                    result['enhanced_recommendation'] = 'BUY'
                    result['sentiment_boost'] = 'Positive news supports buy recommendation'
                elif real_company_data['news_sentiment'] == 'Negative' and recommendation == 'BUY':
                    result['enhanced_recommendation'] = 'HOLD'
                    result['sentiment_warning'] = 'Negative news suggests caution'
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing with real data: {e}")
            return self._analyze_with_vnstock_fallback(symbol)
    
    def _analyze_with_vnstock_fallback(self, symbol: str):
        """Fallback to direct VNStock call with improved real data handling"""
        try:
            # Initialize real_company_data
            real_company_data = None
            
            # Step 1: Try to get CrewAI data first (similar to price_predictor and risk_expert)
            vn_api = self._get_vn_api()
            self.crewai_collector = getattr(vn_api, 'crewai_collector', None) if vn_api else None
            
            if self.crewai_collector and self.crewai_collector.enabled:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Get company info and news for investment context
                    symbols = loop.run_until_complete(self.crewai_collector.get_available_symbols())
                    company_info = next((s for s in symbols if s['symbol'] == symbol), {})
                    
                    stock_news = loop.run_until_complete(self.crewai_collector.get_stock_news(symbol, limit=5))
                    market_news = loop.run_until_complete(self.crewai_collector.get_market_overview_news())
                    
                    loop.close()
                    
                    real_company_data = {
                        'company_info': company_info,
                        'stock_news': stock_news,
                        'market_news': market_news,
                        'sector': company_info.get('sector', 'Unknown'),
                        'exchange': company_info.get('exchange', 'HOSE'),
                        'news_sentiment': stock_news.get('sentiment', 'Neutral'),
                        'market_sentiment': market_news.get('sentiment', 'Neutral')
                    }
                    print(f"✅ Got real company data for {symbol} in fallback method")
                except Exception as e:
                    print(f"⚠️ Could not get CrewAI data in fallback: {e}")
            
            # Step 2: Get VNStock data directly
            from vnstock import Vnstock
            from datetime import datetime, timedelta
            
            try:
                stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
                
                # Get 1-year historical data
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                
                hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                
                if hist_data.empty:
                    return {"error": f"No data found for {symbol}"}
                
                # Get financial ratios
                try:
                    ratios = stock_obj.finance.ratio(period='quarter', lang='vi', dropna=True)
                    if not ratios.empty:
                        latest_ratio = ratios.iloc[-1]
                        pe_ratio = latest_ratio.get('pe', 0)
                        pb_ratio = latest_ratio.get('pb', 0)
                        roe = latest_ratio.get('roe', 0) or latest_ratio.get('ro', 0)
                    else:
                        pe_ratio = pb_ratio = roe = 0
                except Exception as ratio_error:
                    print(f"⚠️ Could not get financial ratios: {ratio_error}")
                    pe_ratio = pb_ratio = roe = 0
                
                # Get current price
                current_price = float(hist_data['close'].iloc[-1])
                
                # Calculate year high/low
                year_high = float(hist_data['high'].max())
                year_low = float(hist_data['low'].min())
                price_position = (current_price - year_low) / (year_high - year_low) if year_high != year_low else 0.5
                
                # Investment logic
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
                
                # Calculate target price
                if recommendation == "BUY":
                    target_price = current_price * 1.2
                elif recommendation == "SELL":
                    target_price = current_price * 0.9
                else:
                    target_price = current_price * 1.05
                
                result = {
                    "symbol": symbol,
                    "recommendation": recommendation,
                    "reason": reason,
                    "current_price": round(current_price, 2),
                    "target_price": round(target_price, 2),
                    "pe_ratio": round(pe_ratio, 2) if pe_ratio else 0,
                    "pb_ratio": round(pb_ratio, 3) if pb_ratio else 0,
                    "roe": round(roe, 2) if roe else 0,
                    "market_cap": "N/A",
                    "dividend_yield": 0,
                    "year_high": round(year_high, 2),
                    "year_low": round(year_low, 2),
                    "market": "Vietnam",
                    "data_source": "VNStock_Fallback" + ("_with_CrewAI" if real_company_data else "")
                }
                
                # Add CrewAI company context if available
                if real_company_data:
                    result['sector'] = real_company_data['sector']
                    result['exchange'] = real_company_data['exchange']
                    result['news_sentiment'] = real_company_data['news_sentiment']
                    result['market_sentiment'] = real_company_data['market_sentiment']
                    result['company_context'] = f"Sector: {real_company_data['sector']}, News: {real_company_data['news_sentiment']}"
                    
                    # Enhance recommendation with sentiment
                    if real_company_data['news_sentiment'] == 'Positive' and recommendation == 'HOLD':
                        result['enhanced_recommendation'] = 'BUY'
                        result['sentiment_boost'] = 'Positive news supports buy recommendation'
                    elif real_company_data['news_sentiment'] == 'Negative' and recommendation == 'BUY':
                        result['enhanced_recommendation'] = 'HOLD'
                        result['sentiment_warning'] = 'Negative news suggests caution'
                
                return result
                
            except Exception as vnstock_error:
                print(f"❌ VNStock fallback failed: {vnstock_error}")
                return self._get_mock_investment_analysis(symbol, real_company_data)
                
        except Exception as e:
            print(f"❌ Investment analysis fallback failed: {e}")
            return self._get_mock_investment_analysis(symbol)
    
    def _get_mock_investment_analysis(self, symbol: str, real_company_data=None):
        """Mock investment analysis as final fallback"""
        import random
        
        # Mock data based on symbol
        mock_data = {
            'VCB': {'pe': 12.5, 'pb': 1.8, 'rec': 'BUY', 'price': 85000},
            'BID': {'pe': 14.2, 'pb': 1.9, 'rec': 'BUY', 'price': 45000},
            'CTG': {'pe': 16.8, 'pb': 2.1, 'rec': 'HOLD', 'price': 32000},
            'VIC': {'pe': 22.5, 'pb': 2.8, 'rec': 'HOLD', 'price': 42000},
            'VHM': {'pe': 18.9, 'pb': 2.3, 'rec': 'HOLD', 'price': 55000}
        }
        
        data = mock_data.get(symbol, {
            'pe': random.uniform(10, 25),
            'pb': random.uniform(1.5, 3.0),
            'rec': random.choice(['BUY', 'HOLD', 'SELL']),
            'price': random.uniform(20000, 80000)
        })
        
        current_price = data['price']
        pe_ratio = data['pe']
        pb_ratio = data['pb']
        recommendation = data['rec']
        
        # Calculate target price
        if recommendation == "BUY":
            target_price = current_price * 1.2
        elif recommendation == "SELL":
            target_price = current_price * 0.9
        else:
            target_price = current_price * 1.05
        
        result = {
            "symbol": symbol,
            "recommendation": recommendation,
            "reason": f"Mock analysis - PE {pe_ratio:.1f}, PB {pb_ratio:.2f}",
            "current_price": round(current_price, 2),
            "target_price": round(target_price, 2),
            "pe_ratio": round(pe_ratio, 2),
            "pb_ratio": round(pb_ratio, 3),
            "roe": 15.0,
            "market_cap": "N/A",
            "dividend_yield": 0,
            "year_high": round(current_price * 1.3, 2),
            "year_low": round(current_price * 0.7, 2),
            "market": "Vietnam",
            "data_source": "Mock_Fallback" + ("_with_CrewAI" if real_company_data else ""),
            "warning": "Mock data - not suitable for real trading decisions"
        }
        
        # Add CrewAI company context if available
        if real_company_data:
            result['sector'] = real_company_data['sector']
            result['exchange'] = real_company_data['exchange']
            result['news_sentiment'] = real_company_data['news_sentiment']
            result['market_sentiment'] = real_company_data['market_sentiment']
            result['company_context'] = f"Sector: {real_company_data['sector']}, News: {real_company_data['news_sentiment']}"
        
        print(f"⚠️ Using MOCK investment analysis for {symbol} - Not reliable!")
        return result
    
    def _analyze_international_stock(self, symbol: str):
        """Analyze international stocks using Yahoo Finance"""
        try:
            # Get real company data from CrewAI first
            real_company_data = None
            if self.crewai_collector and self.crewai_collector.enabled:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Get market news for international context
                    market_news = loop.run_until_complete(self.crewai_collector.get_market_overview_news())
                    
                    loop.close()
                    
                    real_company_data = {
                        'market_news': market_news,
                        'market_sentiment': market_news.get('sentiment', 'Neutral')
                    }
                    print(f"✅ Got real market data for {symbol} international analysis")
                except Exception as e:
                    print(f"⚠️ CrewAI market data failed for {symbol}: {e}")
            
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
            
            # Calculate target price and additional metrics
            if recommendation == "BUY":
                target_price = current_price * 1.15
            elif recommendation == "SELL":
                target_price = current_price * 0.85
            else:
                target_price = current_price * 1.0
            
            # Get additional info if available
            pb_ratio = info.get("priceToBook", 1.5)
            roe = info.get("returnOnEquity", 0.15) * 100 if info.get("returnOnEquity") else 15.0
            
            result = {
                "symbol": symbol,
                "recommendation": recommendation,
                "reason": reason,
                "current_price": round(current_price, 2),
                "target_price": round(target_price, 2),
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else 0,
                "pb_ratio": round(pb_ratio, 2) if pb_ratio else 0,
                "roe": round(roe, 2),
                "market_cap": f"{market_cap/1e9:.1f}B USD" if market_cap else "N/A",
                "dividend_yield": round(dividend_yield * 100, 2) if dividend_yield else 0,
                "year_high": round(year_high, 2),
                "year_low": round(year_low, 2),
                "market": "International",
                "data_source": "Yahoo_Finance" + ("_with_CrewAI" if real_company_data else "")
            }
            
            # Add CrewAI context for international stocks
            if real_company_data:
                result['market_sentiment'] = real_company_data['market_sentiment']
                result['global_context'] = f"Global market sentiment: {real_company_data['market_sentiment']}"
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def _get_ai_investment_analysis(self, symbol: str, base_analysis: dict):
        """Get AI-enhanced investment analysis with REAL adjustments"""
        try:
            # Prepare context for AI analysis
            context = f"""
Phân tích đầu tư chuyên sâu cho cổ phiếu {symbol}:

DỮ LIỆU TÀI CHÍNH:
- Khuyến nghị hiện tại: {base_analysis.get('recommendation', 'N/A')}
- Lý do: {base_analysis.get('reason', 'N/A')}
- P/E: {base_analysis.get('pe_ratio', 'N/A')}
- P/B: {base_analysis.get('pb_ratio', 'N/A')}
- ROE: {base_analysis.get('roe', 'N/A')}%
- Vốn hóa: {base_analysis.get('market_cap', 'N/A')}
- Cổ tức: {base_analysis.get('dividend_yield', 'N/A')}%
- Giá hiện tại: {base_analysis.get('current_price', 'N/A')}
- Giá mục tiêu hiện tại: {base_analysis.get('target_price', 'N/A')}
- Cao nhất 1 năm: {base_analysis.get('year_high', 'N/A')}
- Thấp nhất 1 năm: {base_analysis.get('year_low', 'N/A')}

Hãy đưa ra:
1. Khuyến nghị AI (BUY/SELL/HOLD/STRONG_BUY/STRONG_SELL)
2. Điều chỉnh giá mục tiêu (% thay đổi so với hiện tại)
3. Điều chỉnh định giá P/E hợp lý
4. Điều chỉnh định giá P/B hợp lý
5. Mức độ tin cậy (0-100%)
6. Lý do chi tiết

Trả lời theo format:
AI_RECOMMENDATION: [BUY/SELL/HOLD/STRONG_BUY/STRONG_SELL]
TARGET_PRICE_ADJUSTMENT: [+/-]X%
FAIR_PE: Y
FAIR_PB: Z
CONFIDENCE: W%
REASON: [lý do chi tiết]
"""
            
            # Get AI analysis
            ai_result = self.ai_agent.generate_with_fallback(context, 'investment_analysis', max_tokens=700)
            
            if ai_result['success']:
                # Parse AI response for actual adjustments
                ai_adjustments = self._parse_ai_investment_adjustments(ai_result['response'])
                
                # Apply AI adjustments to base analysis
                adjusted_analysis = self._apply_ai_investment_adjustments(base_analysis, ai_adjustments)
                
                return {
                    'ai_investment_analysis': ai_result['response'],
                    'ai_model_used': ai_result['model_used'],
                    'ai_enhanced': True,
                    'ai_adjustments': ai_adjustments,
                    'enhanced_recommendation': ai_adjustments.get('recommendation', base_analysis.get('recommendation', 'HOLD')),
                    'ai_target_price': adjusted_analysis.get('ai_target_price', base_analysis.get('target_price')),
                    'ai_fair_pe': ai_adjustments.get('fair_pe', base_analysis.get('pe_ratio', 15)),
                    'ai_fair_pb': ai_adjustments.get('fair_pb', base_analysis.get('pb_ratio', 1.5)),
                    'ai_confidence': ai_adjustments.get('confidence', 70)
                }
            else:
                return {'ai_enhanced': False, 'ai_error': ai_result.get('error', 'AI not available')}
                
        except Exception as e:
            return {'ai_enhanced': False, 'ai_error': str(e)}
    
    def _parse_ai_investment_adjustments(self, ai_response: str):
        """Parse AI response for investment adjustments"""
        import re
        adjustments = {
            'recommendation': 'HOLD',
            'target_price_adj': 0,
            'fair_pe': 15,
            'fair_pb': 1.5,
            'confidence': 70,
            'reason': ai_response
        }
        
        try:
            # Extract AI recommendation
            rec_match = re.search(r'AI_RECOMMENDATION:\s*(BUY|SELL|HOLD|STRONG_BUY|STRONG_SELL)', ai_response, re.IGNORECASE)
            if rec_match:
                adjustments['recommendation'] = rec_match.group(1).upper()
            
            # Extract target price adjustment
            target_match = re.search(r'TARGET_PRICE_ADJUSTMENT:\s*([+-]?\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if target_match:
                adjustments['target_price_adj'] = float(target_match.group(1))
            
            # Extract fair PE
            pe_match = re.search(r'FAIR_PE:\s*(\d+(?:\.\d+)?)', ai_response, re.IGNORECASE)
            if pe_match:
                adjustments['fair_pe'] = float(pe_match.group(1))
            
            # Extract fair PB
            pb_match = re.search(r'FAIR_PB:\s*(\d+(?:\.\d+)?)', ai_response, re.IGNORECASE)
            if pb_match:
                adjustments['fair_pb'] = float(pb_match.group(1))
            
            # Extract confidence
            conf_match = re.search(r'CONFIDENCE:\s*(\d+(?:\.\d+)?)%', ai_response, re.IGNORECASE)
            if conf_match:
                adjustments['confidence'] = float(conf_match.group(1))
                
        except Exception as e:
            print(f"⚠️ AI investment adjustment parsing failed: {e}")
            
        return adjustments
    
    def _apply_ai_investment_adjustments(self, base_analysis: dict, ai_adjustments: dict):
        """Apply AI adjustments to base investment analysis"""
        try:
            adjusted_analysis = base_analysis.copy()
            
            # Adjust target price
            current_price = base_analysis.get('current_price', 50000)
            target_price_adj = ai_adjustments.get('target_price_adj', 0)
            base_target = base_analysis.get('target_price', current_price)
            
            ai_target_price = base_target * (1 + target_price_adj / 100)
            # Ensure reasonable bounds (max 50% change)
            max_change = 0.5
            min_target = current_price * (1 - max_change)
            max_target = current_price * (1 + max_change)
            ai_target_price = max(min_target, min(max_target, ai_target_price))
            
            adjusted_analysis['ai_target_price'] = round(ai_target_price, 2)
            adjusted_analysis['ai_upside_potential'] = round(((ai_target_price - current_price) / current_price) * 100, 1)
            
            return adjusted_analysis
            
        except Exception as e:
            print(f"⚠️ AI investment adjustment application failed: {e}")
            return base_analysis