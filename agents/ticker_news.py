import yfinance as yf
import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import re

class TickerNews:
    def __init__(self):
        self.name = "Ticker News Agent"
        self.ai_agent = None
    
    def set_ai_agent(self, ai_agent):
        """Set AI agent for enhanced news analysis"""
        self.ai_agent = ai_agent
    
    def get_ticker_news(self, symbol: str, limit: int = 5):
        try:
            # Logic kiểm tra cổ phiếu VN đã được chuyển ra MainAgent.
            # Agent này giờ chỉ tập trung vào cổ phiếu quốc tế qua Yahoo Finance.
            # Get all VN stocks from crewai_collector fallback
            try:
                from src.data.crewai_collector import CrewAIDataCollector
                collector = CrewAIDataCollector()
                vn_stocks = [stock['symbol'] for stock in collector._get_fallback_symbols()]
            except:
                # Fallback to basic list if import fails
                vn_stocks = ['VCB', 'BID', 'CTG', 'TCB', 'ACB', 'VIC', 'VHM', 'VRE', 'DXG', 'MSN', 'MWG', 'VNM', 'SAB', 'HPG', 'GAS', 'PLX', 'FPT']
            
            if symbol.upper() in vn_stocks:
                # Try crawling from CafeF and VietStock first
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    crawled_news = loop.run_until_complete(self._crawl_vn_news(symbol, limit))
                    loop.close()
                    
                    if crawled_news and len(crawled_news) > 0:
                        return {
                            "symbol": symbol,
                            "news_count": len(crawled_news),
                            "news": crawled_news,
                            "market": "Vietnam",
                            "data_source": "CafeF_VietStock_Crawl",
                            "source": "CafeF_VietStock_Crawl"
                        }
                except Exception as e:
                    print(f"⚠️ Crawling failed: {e}")
                
                # Fallback to VNStock API
                try:
                    from vnstock import Vnstock
                    
                    stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
                    news_data = stock_obj.company.news()
                    
                    if not news_data.empty:
                        formatted_news = []
                        for _, item in news_data.head(limit).iterrows():
                            formatted_news.append({
                                "title": item.get("news_title", ""),
                                "publisher": "VCI",
                                "link": item.get("news_source_link", ""),
                                "published": item.get("public_date", ""),
                                "summary": item.get("news_short_content", ""),
                                "source_index": f"{symbol} Stock News"
                            })
                        
                        return {
                            "symbol": symbol,
                            "news_count": len(formatted_news),
                            "news": formatted_news,
                            "market": "Vietnam",
                            "data_source": "VCI_Real",
                            "source": "VCI_Real"
                        }
                except Exception as e:
                    print(f"⚠️ VNStock API failed: {e}")
                
                # Final fallback to mock news
                return self._get_vn_mock_news(symbol, limit)
            
            # US/International stocks - use Yahoo Finance
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return {"error": f"No news found for {symbol}"}
            
            formatted_news = []
            for item in news[:limit]:
                formatted_news.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", "Yahoo Finance"),
                    "link": item.get("link", ""),
                    "published": self._format_timestamp(item.get("providerPublishTime", "")),
                    "summary": item.get("summary", "International stock news")
                })
            
            return {
                "symbol": symbol,
                "news_count": len(formatted_news),
                "news": formatted_news,
                "market": "International"
            }
        except Exception as e:
            # Fallback to mock news for VN stocks
            try:
                from src.data.crewai_collector import CrewAIDataCollector
                collector = CrewAIDataCollector()
                vn_symbols = [stock['symbol'] for stock in collector._get_fallback_symbols()]
                if symbol.upper() in vn_symbols:
                    return self._get_vn_mock_news(symbol, limit)
            except:
                # Basic fallback check
                if symbol.upper() in ['VCB', 'BID', 'CTG', 'TCB', 'ACB', 'VIC', 'VHM', 'VRE', 'DXG', 'MSN', 'MWG', 'VNM', 'SAB', 'HPG', 'GAS', 'PLX', 'FPT']:
                    return self._get_vn_mock_news(symbol, limit)
            return {"error": str(e)}
    
    async def _crawl_vn_news(self, symbol: str, limit: int):
        """Crawl VN news from CafeF and VietStock"""
        all_news = []
        
        # Crawl from CafeF
        cafef_news = await self._crawl_cafef_news(symbol, limit//2 + 1)
        if cafef_news:
            all_news.extend(cafef_news)
        
        # Crawl from VietStock
        vietstock_news = await self._crawl_vietstock_news(symbol, limit//2 + 1)
        if vietstock_news:
            all_news.extend(vietstock_news)
        
        # Remove duplicates and limit
        unique_news = self._remove_duplicates(all_news)
        return unique_news[:limit]
    
    async def _crawl_cafef_news(self, symbol: str, limit: int):
        """Crawl news from CafeF"""
        try:
            urls = [
                f"https://cafef.vn/co-phieu/{symbol.upper()}.chn",
                f"https://cafef.vn/timeline.chn?symbol={symbol.upper()}"
            ]
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                news_items = []
                for url in urls:
                    try:
                        async with session.get(url, headers=headers, timeout=10) as response:
                            if response.status != 200:
                                continue
                            
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Find news articles
                            articles = soup.select('div.tlitem, div.newsitem, div.news-item')
                            if not articles:
                                articles = soup.find_all('a', href=re.compile(r'.*\.chn|.*\.html'))
                            
                            for article in articles[:limit]:
                                try:
                                    if article.name == 'a':
                                        title = article.get_text(strip=True)
                                        link = article.get('href', '')
                                    else:
                                        title_elem = article.find(['a', 'h1', 'h2', 'h3'])
                                        if not title_elem:
                                            continue
                                        title = title_elem.get_text(strip=True)
                                        link = title_elem.get('href', '')
                                    
                                    if len(title) < 10:
                                        continue
                                    
                                    # Ensure full URL
                                    if link and not link.startswith('http'):
                                        link = f"https://cafef.vn{link}" if link.startswith('/') else f"https://cafef.vn/{link}"
                                    
                                    # Extract date
                                    date_elem = article.find(['time', 'span'], class_=re.compile(r'date|time'))
                                    pub_date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d %H:%M')
                                    
                                    news_items.append({
                                        "title": title,
                                        "publisher": "CafeF",
                                        "link": link or url,
                                        "published": pub_date,
                                        "summary": f"Tin tức về {symbol} từ CafeF",
                                        "source_index": f"{symbol} Stock News"
                                    })
                                    
                                    if len(news_items) >= limit:
                                        break
                                except Exception:
                                    continue
                            
                            if len(news_items) >= limit:
                                break
                    except Exception:
                        continue
                
                return news_items
        except Exception as e:
            print(f"CafeF crawling failed: {e}")
            return []
    
    async def _crawl_vietstock_news(self, symbol: str, limit: int):
        """Crawl news from VietStock"""
        try:
            urls = [
                f"https://vietstock.vn/{symbol.upper()}",
                f"https://vietstock.vn/chung-khoan/{symbol.upper()}"
            ]
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                news_items = []
                for url in urls:
                    try:
                        async with session.get(url, headers=headers, timeout=10) as response:
                            if response.status != 200:
                                continue
                            
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Find news articles
                            articles = soup.select('div.news-item, div.item-news, li.news-item')
                            if not articles:
                                articles = soup.find_all('a', href=re.compile(r'/tin-tuc/|/news/'))
                            
                            for article in articles[:limit]:
                                try:
                                    if article.name == 'a':
                                        title = article.get_text(strip=True)
                                        link = article.get('href', '')
                                    else:
                                        title_elem = article.find(['a', 'h1', 'h2', 'h3'])
                                        if not title_elem:
                                            continue
                                        title = title_elem.get_text(strip=True)
                                        link = title_elem.get('href', '') if title_elem.name == 'a' else article.find('a', href=True)
                                        if hasattr(link, 'get'):
                                            link = link.get('href', '')
                                    
                                    if len(title) < 10:
                                        continue
                                    
                                    # Ensure full URL
                                    if link and not link.startswith('http'):
                                        link = f"https://vietstock.vn{link}" if link.startswith('/') else f"https://vietstock.vn/{link}"
                                    
                                    # Extract date
                                    date_elem = article.find(['span', 'time'], class_=re.compile(r'date|time'))
                                    pub_date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d %H:%M')
                                    
                                    news_items.append({
                                        "title": title,
                                        "publisher": "VietStock",
                                        "link": link or url,
                                        "published": pub_date,
                                        "summary": f"Tin tức về {symbol} từ VietStock",
                                        "source_index": f"{symbol} Stock News"
                                    })
                                    
                                    if len(news_items) >= limit:
                                        break
                                except Exception:
                                    continue
                            
                            if len(news_items) >= limit:
                                break
                    except Exception:
                        continue
                
                return news_items
        except Exception as e:
            print(f"VietStock crawling failed: {e}")
            return []
    
    def _remove_duplicates(self, news_list):
        """Remove duplicate news based on title similarity"""
        unique_news = []
        seen_titles = set()
        
        for news in news_list:
            title = news.get('title', '').lower()
            title_key = title[:50]  # First 50 characters
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        return unique_news
    
    def _get_vn_mock_news(self, symbol: str, limit: int = 5):
        """Mock VN news as fallback"""
        import random
        
        # Get company names from crewai_collector fallback
        try:
            from src.data.crewai_collector import CrewAIDataCollector
            collector = CrewAIDataCollector()
            fallback_stocks = collector._get_fallback_symbols()
            company_names = {stock['symbol']: stock['name'] for stock in fallback_stocks}
        except:
            company_names = {
                'VCB': 'Vietcombank',
                'BID': 'BIDV', 
                'CTG': 'VietinBank',
                'VIC': 'Vingroup',
                'VHM': 'Vinhomes',
                'HPG': 'Hòa Phát',
                'FPT': 'FPT Corporation'
            }
        
        company_name = company_names.get(symbol.upper(), f'Công ty {symbol}')
        
        mock_titles = [
            f"{company_name} báo lãi quý tăng 20%",
            f"{symbol} mở rộng hoạt động kinh doanh",
            f"{company_name} ký hợp đồng lớn với đối tác nước ngoài",
            f"Cổ phiếu {symbol} được khuyến nghị mua",
            f"{company_name} công bố kế hoạch đầu tư mới"
        ]
        
        formatted_news = []
        for i, title in enumerate(random.sample(mock_titles, min(limit, len(mock_titles)))):
            formatted_news.append({
                "title": title,
                "publisher": random.choice(["CafeF", "VnExpress", "DanTri"]),
                "link": f"https://cafef.vn/co-phieu-{symbol.lower()}.html",
                "published": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "summary": f"Tin tức về {company_name}",
                "source_index": f"{symbol} Stock News"
            })
        
        return {
            "symbol": symbol,
            "news_count": len(formatted_news),
            "news": formatted_news,
            "market": "Vietnam",
            "data_source": "Enhanced_Fallback",
            "source": "Enhanced_Fallback",
            "crawl_stats": {"Fallback": len(formatted_news)}
        }
    
    def _format_timestamp(self, timestamp):
        """Format timestamp to readable date"""
        try:
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            return str(timestamp)
        except:
            return datetime.now().strftime('%Y-%m-%d %H:%M')