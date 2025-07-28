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
        """Analyze using real data from VN API with enhanced metrics like stock_info.py"""
        try:
            # Get CrewAI data if not provided
            if not real_company_data:
                vn_api = self._get_vn_api()
                self.crewai_collector = getattr(vn_api, 'crewai_collector', None) if vn_api else None
                
                if self.crewai_collector and self.crewai_collector.enabled:
                    try:
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
            
            # Try to get enhanced real data using vnstock directly for better metrics
            enhanced_metrics = self._fetch_real_detailed_investment_metrics(symbol)
            if enhanced_metrics:
                print(f"✅ Using enhanced real metrics for {symbol} from VN API data")
                return self._analyze_with_enhanced_real_data(symbol, enhanced_metrics, real_company_data)
            
            # Fallback to basic analysis with VN API data
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
            
            # Enhanced investment logic with scoring system
            score = 0
            reasons = []
            
            # P/E Analysis
            if pe_ratio > 0:
                if pe_ratio < 12:
                    score += 2
                    reasons.append(f"PE {pe_ratio:.1f} rất thấp")
                elif pe_ratio < 18:
                    score += 1
                    reasons.append(f"PE {pe_ratio:.1f} hợp lý")
                elif pe_ratio > 25:
                    score -= 2
                    reasons.append(f"PE {pe_ratio:.1f} cao")
                else:
                    score -= 1
                    reasons.append(f"PE {pe_ratio:.1f} hơi cao")
            
            # P/B Analysis
            if pb_ratio > 0:
                if pb_ratio < 1.5:
                    score += 1
                    reasons.append(f"PB {pb_ratio:.2f} thấp")
                elif pb_ratio > 3:
                    score -= 1
                    reasons.append(f"PB {pb_ratio:.2f} cao")
            
            # Price Position Analysis
            if price_position < 0.3:
                score += 2
                reasons.append(f"Giá ở {price_position*100:.0f}% range (cơ hội)")
            elif price_position > 0.8:
                score -= 2
                reasons.append(f"Giá ở {price_position*100:.0f}% range (cao)")
            elif price_position < 0.6:
                score += 1
                reasons.append(f"Giá ở {price_position*100:.0f}% range (hợp lý)")
            
            # Final recommendation based on score
            if score >= 3:
                recommendation = "STRONG_BUY"
                target_multiplier = 1.25
            elif score >= 1:
                recommendation = "BUY"
                target_multiplier = 1.15
            elif score <= -3:
                recommendation = "STRONG_SELL"
                target_multiplier = 0.85
            elif score <= -1:
                recommendation = "SELL"
                target_multiplier = 0.9
            else:
                recommendation = "HOLD"
                target_multiplier = 1.05
            
            target_price = current_price * target_multiplier
            reason = "; ".join(reasons) if reasons else "Phân tích tổng hợp"
            
            # Calculate market cap
            market_cap = f"{stock_data.market_cap / 1_000_000_000_000:.1f} nghìn tỷ VND" if stock_data.market_cap > 0 else "N/A"
            
            result = {
                "symbol": symbol,
                "recommendation": recommendation,
                "reason": reason,
                "investment_score": score,
                "current_price": round(current_price, 2),
                "target_price": round(target_price, 2),
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else 0,
                "pb_ratio": round(pb_ratio, 3) if pb_ratio else 0,
                "roe": round(roe, 2) if roe else 0,
                "market_cap": market_cap,
                "dividend_yield": 0,  # Not available in current data
                "year_high": round(year_high, 2),
                "year_low": round(year_low, 2),
                "price_position_pct": round(price_position * 100, 1),
                "market": "Vietnam",
                "data_source": data_source + "_Enhanced" + ("_with_CrewAI" if real_company_data else "")
            }
            
            # Add CrewAI company context if available
            if real_company_data:
                result['sector'] = real_company_data['sector']
                result['exchange'] = real_company_data['exchange']
                result['news_sentiment'] = real_company_data['news_sentiment']
                result['market_sentiment'] = real_company_data['market_sentiment']
                result['company_context'] = f"Sector: {real_company_data['sector']}, News: {real_company_data['news_sentiment']}"
                
                # Enhance recommendation with sentiment
                if real_company_data['news_sentiment'] == 'Positive' and recommendation in ['HOLD', 'BUY']:
                    if recommendation == 'HOLD':
                        result['enhanced_recommendation'] = 'BUY'
                    elif recommendation == 'BUY':
                        result['enhanced_recommendation'] = 'STRONG_BUY'
                    result['sentiment_boost'] = 'Positive news supports stronger buy recommendation'
                elif real_company_data['news_sentiment'] == 'Negative' and recommendation in ['BUY', 'STRONG_BUY']:
                    if recommendation == 'STRONG_BUY':
                        result['enhanced_recommendation'] = 'BUY'
                    elif recommendation == 'BUY':
                        result['enhanced_recommendation'] = 'HOLD'
                    result['sentiment_warning'] = 'Negative news suggests caution'
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing with real data: {e}")
            return self._analyze_with_vnstock_fallback(symbol)
    
    def _analyze_with_vnstock_fallback(self, symbol: str):
        """Fallback to direct VNStock call with enhanced real data handling like stock_info.py"""
        try:
            # Initialize real_company_data
            real_company_data = None
            
            # Step 1: Try to get CrewAI data first (similar to price_predictor and risk_expert)
            vn_api = self._get_vn_api()
            self.crewai_collector = getattr(vn_api, 'crewai_collector', None) if vn_api else None
            
            if self.crewai_collector and self.crewai_collector.enabled:
                try:
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
            
            # Step 2: Get enhanced VNStock data using stock_info.py approach
            real_detailed_metrics = self._fetch_real_detailed_investment_metrics(symbol)
            
            if real_detailed_metrics:
                # Use real detailed metrics for investment analysis
                return self._analyze_with_enhanced_real_data(symbol, real_detailed_metrics, real_company_data)
            else:
                # Fallback to basic VNStock approach
                return self._analyze_with_basic_vnstock(symbol, real_company_data)
                
        except Exception as e:
            print(f"❌ Investment analysis fallback failed: {e}")
            return self._get_mock_investment_analysis(symbol)
    
    def _fetch_real_detailed_investment_metrics(self, symbol: str):
        """Fetch real detailed investment metrics from vnstock with enhanced data collection"""
        try:
            from vnstock import Vnstock
            from datetime import datetime, timedelta
            import logging
            
            # Suppress vnstock logging
            vnstock_logger = logging.getLogger('vnstock')
            vnstock_logger.setLevel(logging.ERROR)
            
            stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
            
            # Get recent price data (1 year for better analysis)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # Try multiple periods if data is not available
            hist_data = None
            for days in [365, 180, 90, 30]:
                try:
                    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                    hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                    if not hist_data.empty:
                        break
                except Exception as e:
                    print(f"⚠️ Failed to get {days} days data for {symbol}: {e}")
                    continue
            
            if hist_data is None or hist_data.empty:
                print(f"⚠️ No historical data available for {symbol}")
                return None
                
            current_price = float(hist_data['close'].iloc[-1])
            high_52w = float(hist_data['high'].max())
            low_52w = float(hist_data['low'].min())
            avg_volume = int(hist_data['volume'].mean())
            current_volume = int(hist_data['volume'].iloc[-1])
            
            # Get comprehensive financial ratios with multiple attempts
            pe_ratio = pb_ratio = eps = dividend = roe = 0
            debt_to_equity = current_ratio = quick_ratio = 0
            
            # Try different periods for financial ratios
            for period in ['quarter', 'year']:
                try:
                    ratios = stock_obj.finance.ratio(period=period, lang='vi', dropna=True)
                    if not ratios.empty:
                        latest_ratio = ratios.iloc[-1]
                        
                        # Get PE ratio
                        pe_ratio = latest_ratio.get('pe', 0) or latest_ratio.get('PE', 0)
                        if pe_ratio == 0:
                            pe_ratio = latest_ratio.get('priceToEarning', 0)
                        
                        # Get PB ratio
                        pb_ratio = latest_ratio.get('pb', 0) or latest_ratio.get('PB', 0)
                        if pb_ratio == 0:
                            pb_ratio = latest_ratio.get('priceToBook', 0)
                        
                        # Get EPS
                        eps = latest_ratio.get('eps', 0) or latest_ratio.get('EPS', 0)
                        if eps == 0:
                            eps = latest_ratio.get('earningPerShare', 0)
                        
                        # Get dividend
                        dividend = latest_ratio.get('dividend_per_share', 0) or latest_ratio.get('dividendPerShare', 0)
                        
                        # Get ROE
                        roe = latest_ratio.get('roe', 0) or latest_ratio.get('ROE', 0) or latest_ratio.get('ro', 0)
                        if roe == 0:
                            roe = latest_ratio.get('returnOnEquity', 0)
                        
                        # Additional financial metrics
                        debt_to_equity = latest_ratio.get('debt_to_equity', 0) or latest_ratio.get('debtToEquity', 0)
                        current_ratio = latest_ratio.get('current_ratio', 0) or latest_ratio.get('currentRatio', 0)
                        quick_ratio = latest_ratio.get('quick_ratio', 0) or latest_ratio.get('quickRatio', 0)
                        
                        # If we got some data, break
                        if pe_ratio > 0 or pb_ratio > 0 or eps > 0:
                            print(f"✅ Got financial ratios from {period} data for {symbol}")
                            break
                            
                except Exception as ratio_error:
                    print(f"⚠️ Could not get {period} financial ratios for {symbol}: {ratio_error}")
                    continue
            
            # Try to get company overview for market cap
            market_cap = 0
            try:
                overview = stock_obj.company.overview()
                if not overview.empty:
                    overview_data = overview.iloc[0]
                    issue_share = overview_data.get('issue_share', 0) or overview_data.get('issueShare', 0)
                    if issue_share and issue_share > 0:
                        market_cap = issue_share * current_price
                    else:
                        # Estimate market cap based on typical Vietnamese stocks
                        market_cap = current_price * 1_000_000_000  # 1B shares estimate
            except Exception as e:
                print(f"⚠️ Could not get company overview for {symbol}: {e}")
                market_cap = current_price * 1_000_000_000  # Estimate
            
            # Calculate dividend yield
            dividend_yield = (dividend / current_price * 100) if dividend > 0 and current_price > 0 else 0
            
            # Calculate price position in 52-week range
            price_position = (current_price - low_52w) / (high_52w - low_52w) if high_52w != low_52w else 0.5
            
            # Validate and clean data
            pe_ratio = float(pe_ratio) if pe_ratio and pe_ratio > 0 and pe_ratio < 1000 else 0
            pb_ratio = float(pb_ratio) if pb_ratio and pb_ratio > 0 and pb_ratio < 100 else 0
            eps = float(eps) if eps and eps > 0 else 0
            roe = float(roe) if roe and roe > -100 and roe < 200 else 0  # ROE should be reasonable
            dividend_yield = float(dividend_yield) if dividend_yield >= 0 and dividend_yield < 50 else 0
            
            print(f"✅ Got REAL detailed investment metrics for {symbol}: PE={pe_ratio:.1f}, PB={pb_ratio:.2f}, ROE={roe:.1f}%")
            
            return {
                'current_price': current_price,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'price_position': price_position,
                'volume': current_volume,
                'avg_volume': avg_volume,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'eps': eps,
                'dividend': dividend,
                'dividend_yield': dividend_yield,
                'roe': roe,
                'debt_to_equity': debt_to_equity,
                'current_ratio': current_ratio,
                'quick_ratio': quick_ratio,
                'data_quality': 'REAL'
            }
            
        except Exception as e:
            print(f"⚠️ Real detailed investment metrics failed for {symbol}: {e}")
            return None
    
    def _analyze_with_enhanced_real_data(self, symbol: str, metrics: dict, real_company_data=None):
        """Analyze using enhanced real data with comprehensive investment logic"""
        try:
            current_price = metrics['current_price']
            pe_ratio = metrics['pe_ratio']
            pb_ratio = metrics['pb_ratio']
            roe = metrics['roe']
            price_position = metrics['price_position']
            dividend_yield = metrics['dividend_yield']
            debt_to_equity = metrics.get('debt_to_equity', 0)
            
            # Enhanced investment logic with multiple factors
            score = 0
            reasons = []
            
            # P/E Analysis
            if pe_ratio > 0:
                if pe_ratio < 12:
                    score += 2
                    reasons.append(f"PE {pe_ratio:.1f} rất thấp")
                elif pe_ratio < 18:
                    score += 1
                    reasons.append(f"PE {pe_ratio:.1f} hợp lý")
                elif pe_ratio > 25:
                    score -= 2
                    reasons.append(f"PE {pe_ratio:.1f} cao")
                else:
                    score -= 1
                    reasons.append(f"PE {pe_ratio:.1f} hơi cao")
            
            # P/B Analysis
            if pb_ratio > 0:
                if pb_ratio < 1.5:
                    score += 1
                    reasons.append(f"PB {pb_ratio:.2f} thấp")
                elif pb_ratio > 3:
                    score -= 1
                    reasons.append(f"PB {pb_ratio:.2f} cao")
            
            # ROE Analysis
            if roe > 0:
                if roe > 20:
                    score += 1
                    reasons.append(f"ROE {roe:.1f}% tốt")
                elif roe < 10:
                    score -= 1
                    reasons.append(f"ROE {roe:.1f}% thấp")
            
            # Price Position Analysis
            if price_position < 0.3:
                score += 2
                reasons.append(f"Giá ở {price_position*100:.0f}% range (cơ hội)")
            elif price_position > 0.8:
                score -= 2
                reasons.append(f"Giá ở {price_position*100:.0f}% range (cao)")
            elif price_position < 0.6:
                score += 1
                reasons.append(f"Giá ở {price_position*100:.0f}% range (hợp lý)")
            
            # Dividend Analysis
            if dividend_yield > 5:
                score += 1
                reasons.append(f"Cổ tức {dividend_yield:.1f}% cao")
            elif dividend_yield > 3:
                reasons.append(f"Cổ tức {dividend_yield:.1f}% ổn")
            
            # Debt Analysis
            if debt_to_equity > 0:
                if debt_to_equity > 2:
                    score -= 1
                    reasons.append(f"Nợ/Vốn {debt_to_equity:.1f} cao")
                elif debt_to_equity < 0.5:
                    score += 1
                    reasons.append(f"Nợ/Vốn {debt_to_equity:.1f} thấp")
            
            # Final recommendation based on score
            if score >= 3:
                recommendation = "STRONG_BUY"
                target_multiplier = 1.25
            elif score >= 1:
                recommendation = "BUY"
                target_multiplier = 1.15
            elif score <= -3:
                recommendation = "STRONG_SELL"
                target_multiplier = 0.85
            elif score <= -1:
                recommendation = "SELL"
                target_multiplier = 0.9
            else:
                recommendation = "HOLD"
                target_multiplier = 1.05
            
            target_price = current_price * target_multiplier
            reason = "; ".join(reasons) if reasons else "Phân tích tổng hợp"
            
            # Format market cap
            market_cap_display = f"{metrics['market_cap'] / 1_000_000_000_000:.1f} nghìn tỷ VND" if metrics['market_cap'] > 0 else "N/A"
            
            result = {
                "symbol": symbol,
                "recommendation": recommendation,
                "reason": reason,
                "investment_score": score,
                "current_price": round(current_price, 2),
                "target_price": round(target_price, 2),
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else 0,
                "pb_ratio": round(pb_ratio, 3) if pb_ratio else 0,
                "roe": round(roe, 2) if roe else 0,
                "market_cap": market_cap_display,
                "dividend_yield": round(dividend_yield, 2),
                "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity else 0,
                "year_high": round(metrics['high_52w'], 2),
                "year_low": round(metrics['low_52w'], 2),
                "price_position_pct": round(price_position * 100, 1),
                "market": "Vietnam",
                "data_source": "VNStock_Enhanced_Real" + ("_with_CrewAI" if real_company_data else ""),
                "data_quality": "REAL"
            }
            
            # Add CrewAI company context if available
            if real_company_data:
                result['sector'] = real_company_data['sector']
                result['exchange'] = real_company_data['exchange']
                result['news_sentiment'] = real_company_data['news_sentiment']
                result['market_sentiment'] = real_company_data['market_sentiment']
                result['company_context'] = f"Sector: {real_company_data['sector']}, News: {real_company_data['news_sentiment']}"
                
                # Enhance recommendation with sentiment
                if real_company_data['news_sentiment'] == 'Positive' and recommendation in ['HOLD', 'BUY']:
                    if recommendation == 'HOLD':
                        result['enhanced_recommendation'] = 'BUY'
                    elif recommendation == 'BUY':
                        result['enhanced_recommendation'] = 'STRONG_BUY'
                    result['sentiment_boost'] = 'Positive news supports stronger buy recommendation'
                elif real_company_data['news_sentiment'] == 'Negative' and recommendation in ['BUY', 'STRONG_BUY']:
                    if recommendation == 'STRONG_BUY':
                        result['enhanced_recommendation'] = 'BUY'
                    elif recommendation == 'BUY':
                        result['enhanced_recommendation'] = 'HOLD'
                    result['sentiment_warning'] = 'Negative news suggests caution'
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing with enhanced real data: {e}")
            return self._analyze_with_basic_vnstock(symbol, real_company_data)
    
    def _analyze_with_basic_vnstock(self, symbol: str, real_company_data=None):
        """Basic VNStock analysis as fallback"""
        try:
            from vnstock import Vnstock
            from datetime import datetime, timedelta
            
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
                "data_source": "VNStock_Basic" + ("_with_CrewAI" if real_company_data else "")
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
            print(f"❌ VNStock basic fallback failed: {vnstock_error}")
            return self._get_mock_investment_analysis(symbol, real_company_data)
    
    def _get_mock_investment_analysis(self, symbol: str, real_company_data=None):
        """Enhanced mock investment analysis with realistic Vietnamese stock data"""
        import random
        
        # Enhanced mock data based on real Vietnamese stock characteristics
        realistic_mock_data = {
            'VCB': {
                'pe': 12.8, 'pb': 2.1, 'roe': 18.5, 'dividend_yield': 2.1,
                'rec': 'BUY', 'price': 85000, 'market_cap': 365.2
            },
            'BID': {
                'pe': 8.9, 'pb': 1.8, 'roe': 16.2, 'dividend_yield': 2.7,
                'rec': 'BUY', 'price': 45000, 'market_cap': 156.8
            },
            'CTG': {
                'pe': 7.2, 'pb': 1.6, 'roe': 14.8, 'dividend_yield': 3.1,
                'rec': 'BUY', 'price': 32000, 'market_cap': 98.5
            },
            'TCB': {
                'pe': 11.5, 'pb': 2.3, 'roe': 19.8, 'dividend_yield': 1.8,
                'rec': 'BUY', 'price': 28000, 'market_cap': 89.2
            },
            'VIC': {
                'pe': 15.2, 'pb': 2.8, 'roe': 12.5, 'dividend_yield': 0.0,
                'rec': 'HOLD', 'price': 42000, 'market_cap': 195.6
            },
            'VHM': {
                'pe': 18.9, 'pb': 2.3, 'roe': 11.8, 'dividend_yield': 0.0,
                'rec': 'HOLD', 'price': 55000, 'market_cap': 168.9
            },
            'HPG': {
                'pe': 9.8, 'pb': 1.4, 'roe': 15.6, 'dividend_yield': 7.1,
                'rec': 'BUY', 'price': 26000, 'market_cap': 89.5
            },
            'MSN': {
                'pe': 14.5, 'pb': 2.1, 'roe': 13.2, 'dividend_yield': 1.5,
                'rec': 'HOLD', 'price': 68000, 'market_cap': 78.9
            },
            'FPT': {
                'pe': 16.8, 'pb': 3.2, 'roe': 18.9, 'dividend_yield': 2.8,
                'rec': 'BUY', 'price': 125000, 'market_cap': 89.2
            },
            'GAS': {
                'pe': 11.2, 'pb': 1.9, 'roe': 16.8, 'dividend_yield': 5.2,
                'rec': 'BUY', 'price': 89000, 'market_cap': 156.8
            }
        }
        
        # Get data for symbol or generate realistic fallback
        if symbol in realistic_mock_data:
            data = realistic_mock_data[symbol]
        else:
            # Generate realistic data for unknown symbols
            data = {
                'pe': random.uniform(8, 25),
                'pb': random.uniform(1.2, 3.5),
                'roe': random.uniform(10, 20),
                'dividend_yield': random.uniform(0, 6),
                'rec': random.choice(['BUY', 'HOLD', 'SELL']),
                'price': random.uniform(15000, 120000),
                'market_cap': random.uniform(20, 300)
            }
        
        current_price = data['price']
        pe_ratio = data['pe']
        pb_ratio = data['pb']
        roe = data['roe']
        dividend_yield = data['dividend_yield']
        market_cap = data['market_cap']
        recommendation = data['rec']
        
        # Calculate realistic year high/low based on Vietnamese market volatility
        year_high = current_price * random.uniform(1.15, 1.45)
        year_low = current_price * random.uniform(0.65, 0.85)
        
        # Calculate target price based on recommendation
        if recommendation == "BUY":
            target_price = current_price * random.uniform(1.15, 1.25)
        elif recommendation == "SELL":
            target_price = current_price * random.uniform(0.85, 0.95)
        else:
            target_price = current_price * random.uniform(1.02, 1.08)
        
        # Generate realistic reason
        reasons = []
        if pe_ratio < 12:
            reasons.append(f"PE {pe_ratio:.1f} thấp")
        elif pe_ratio > 20:
            reasons.append(f"PE {pe_ratio:.1f} cao")
        else:
            reasons.append(f"PE {pe_ratio:.1f} hợp lý")
            
        if pb_ratio < 1.5:
            reasons.append(f"PB {pb_ratio:.2f} thấp")
        elif pb_ratio > 3:
            reasons.append(f"PB {pb_ratio:.2f} cao")
            
        if roe > 15:
            reasons.append(f"ROE {roe:.1f}% tốt")
        elif roe < 10:
            reasons.append(f"ROE {roe:.1f}% thấp")
            
        if dividend_yield > 4:
            reasons.append(f"Cổ tức {dividend_yield:.1f}% cao")
        
        reason = "; ".join(reasons) if reasons else f"Phân tích tổng hợp - PE {pe_ratio:.1f}, PB {pb_ratio:.2f}"
        
        result = {
            "symbol": symbol,
            "recommendation": recommendation,
            "reason": reason,
            "current_price": round(current_price, 2),
            "target_price": round(target_price, 2),
            "pe_ratio": round(pe_ratio, 2),
            "pb_ratio": round(pb_ratio, 3),
            "roe": round(roe, 2),
            "market_cap": f"{market_cap:.1f} nghìn tỷ VND",
            "dividend_yield": round(dividend_yield, 2),
            "year_high": round(year_high, 2),
            "year_low": round(year_low, 2),
            "price_position_pct": round(random.uniform(20, 80), 1),
            "market": "Vietnam",
            "data_source": "Enhanced_Mock_Fallback" + ("_with_CrewAI" if real_company_data else ""),
            "data_quality": "MOCK",
            "warning": "Enhanced mock data based on market patterns - use with caution"
        }
        
        # Add CrewAI company context if available
        if real_company_data:
            result['sector'] = real_company_data['sector']
            result['exchange'] = real_company_data['exchange']
            result['news_sentiment'] = real_company_data['news_sentiment']
            result['market_sentiment'] = real_company_data['market_sentiment']
            result['company_context'] = f"Sector: {real_company_data['sector']}, News: {real_company_data['news_sentiment']}"
        
        print(f"⚠️ Using ENHANCED MOCK investment analysis for {symbol} - Based on market patterns")
        return result
    
    def _analyze_international_stock(self, symbol: str):
        """Analyze international stocks using Yahoo Finance"""
        try:
            # Get real company data from CrewAI first
            real_company_data = None
            if self.crewai_collector and self.crewai_collector.enabled:
                try:
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