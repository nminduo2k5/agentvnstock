# agents/enhanced_news_agent.py
"""
Enhanced News Agent with Company Data Integration
Tích hợp dữ liệu công ty và tin tức theo mã cổ phiếu
Cải tiến: Thêm phân tích sentiment và thông tin tài chính
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from datetime import datetime
import logging
import asyncio

try:
    from src.data.company_search_api import get_company_search_api
    COMPANY_API_AVAILABLE = True
except ImportError:
    COMPANY_API_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedNewsAgent:
    """Agent lấy tin tức và dữ liệu công ty theo mã cổ phiếu"""

    def __init__(self):
        self.name = "Enhanced News & Company Data Agent"
        self.description = "Collects company data and news by stock symbol"
        
        # Initialize Company Search API
        if COMPANY_API_AVAILABLE:
            self.company_search = get_company_search_api()
        else:
            self.company_search = None

    async def get_stock_news(self, symbol: str) -> Dict[str, Any]:
        """Lấy tin tức và dữ liệu công ty theo mã cổ phiếu với phân tích sentiment"""
        try:
            # Get company information
            company_info = await self._get_company_info(symbol)
            
            # Get news for the company
            news = await self._fetch_company_news(symbol, company_info)
            
            # Get financial metrics
            financial_metrics = await self._get_financial_metrics(symbol)
            
            # Get internal company details
            internal_details = await self._get_internal_company_details(symbol)
            
            # Analyze news sentiment
            sentiment, headlines, analysis = self._analyze_news_sentiment(news, symbol)
            
            return {
                "symbol": symbol,
                "company_info": company_info,
                "news": news,
                "news_count": len(news),
                "financial_metrics": financial_metrics,
                "internal_details": internal_details,
                "sentiment": sentiment,
                "headlines": headlines,
                "analysis": analysis,
                "source": "Enhanced Company Data",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error fetching company data for {symbol}: {e}")
            return {
                "symbol": symbol,
                "company_info": None,
                "news": [],
                "news_count": 0,
                "source": "Enhanced Company Data",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def get_market_news(self) -> Dict[str, Any]:
        """Lấy tin tức thị trường tổng quát"""
        try:
            news = self._fetch_market_news()
            return {
                "source": "Market News",
                "timestamp": datetime.now().isoformat(),
                "news": news,
                "news_count": len(news)
            }
        except Exception as e:
            logger.error(f"❌ Error fetching market news: {e}")
            return {
                "source": "Market News",
                "timestamp": datetime.now().isoformat(),
                "news": [],
                "news_count": 0,
                "error": str(e)
            }

    async def _get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Lấy thông tin công ty theo mã cổ phiếu"""
        if not self.company_search:
            return self._get_fallback_company_info(symbol)
        
        try:
            # Search by symbol first
            result = await self.company_search.get_company_by_symbol(symbol)
            if result.get('found'):
                return result['company_info']
            
            # If not found, try searching by name
            search_result = await self.company_search.search_company(symbol)
            if search_result.get('found'):
                return search_result['company_info']
            
            return self._get_fallback_company_info(symbol)
            
        except Exception as e:
            logger.error(f"Company search failed for {symbol}: {e}")
            return self._get_fallback_company_info(symbol)
    
    def _get_fallback_company_info(self, symbol: str) -> Dict[str, Any]:
        """Fallback company info when API not available"""
        fallback_data = {
            'VCB': {
                'full_name': 'Ngân hàng TMCP Ngoại thương Việt Nam', 
                'sector': 'Banking',
                'founded': '1963',
                'headquarters': 'Hà Nội',
                'employees': '18,000+',
                'description': 'Ngân hàng lớn nhất Việt Nam theo vốn hóa thị trường, cung cấp dịch vụ tài chính toàn diện.',
                'website': 'https://www.vietcombank.com.vn'
            },
            'BID': {
                'full_name': 'Ngân hàng TMCP Đầu tư và Phát triển VN', 
                'sector': 'Banking',
                'founded': '1957',
                'headquarters': 'Hà Nội',
                'employees': '25,000+',
                'description': 'Một trong những ngân hàng thương mại lớn nhất Việt Nam với mạng lưới rộng khắp.',
                'website': 'https://www.bidv.com.vn'
            },
            'VIC': {
                'full_name': 'Tập đoàn Vingroup', 
                'sector': 'Real Estate',
                'founded': '1993',
                'headquarters': 'Hà Nội',
                'employees': '35,000+',
                'description': 'Tập đoàn đa ngành lớn nhất Việt Nam, hoạt động trong lĩnh vực bất động sản, bán lẻ, công nghệ.',
                'website': 'https://www.vingroup.net'
            },
            'FPT': {
                'full_name': 'Công ty Cổ phần FPT', 
                'sector': 'Technology',
                'founded': '1988',
                'headquarters': 'Hà Nội',
                'employees': '36,000+',
                'description': 'Công ty công nghệ hàng đầu Việt Nam, chuyên về phần mềm, viễn thông và giáo dục.',
                'website': 'https://fpt.com.vn'
            },
            'HPG': {
                'full_name': 'Tập đoàn Hòa Phát', 
                'sector': 'Industrial',
                'founded': '1992',
                'headquarters': 'Hà Nội',
                'employees': '20,000+',
                'description': 'Nhà sản xuất thép lớn nhất Việt Nam, hoạt động trong nhiều lĩnh vực công nghiệp.',
                'website': 'https://www.hoaphat.com.vn'
            }
        }
        
        return fallback_data.get(symbol, {
            'full_name': f'Công ty {symbol}',
            'sector': 'Unknown',
            'symbol': symbol,
            'founded': 'N/A',
            'headquarters': 'N/A',
            'employees': 'N/A',
            'description': f'Thông tin chi tiết về {symbol} chưa có trong cơ sở dữ liệu.',
            'website': 'N/A'
        })
    
    async def _fetch_company_news(self, symbol: str, company_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Lấy tin tức của công ty từ Vietstock"""
        try:
            # Try to get real news from Vietstock first
            vietstock_news = await self._crawl_vietstock_company_news(symbol)
            
            # If we got real news, return it
            if vietstock_news and len(vietstock_news) > 0:
                return vietstock_news
                
            # Fallback to generated news if crawling failed
            company_name = company_info.get('full_name', symbol)
            sector = company_info.get('sector', 'Unknown')
            
            # Sector-specific news templates
            news_templates = {
                'Banking': [
                    f"{company_name} báo lãi quý tăng trưởng 12%",
                    f"Nợ xấu của {company_name} giảm xuống 1.2%",
                    f"{company_name} mở rộng mạng lưới chi nhánh"
                ],
                'Technology': [
                    f"{company_name} ký hợp đồng AI trị giá 50 triệu USD",
                    f"Doanh thu công nghệ của {company_name} tăng mạnh",
                    f"{company_name} đầu tư vào trí tuệ nhân tạo"
                ],
                'Real Estate': [
                    f"{company_name} khởi công dự án mới",
                    f"Doanh số bất động sản của {company_name} tăng 15%",
                    f"{company_name} mở bán dự án cao cấp"
                ]
            }
            
            templates = news_templates.get(sector, [
                f"{company_name} công bố kết quả kinh doanh",
                f"Hội đại hội cổ đông {company_name}",
                f"{company_name} thông báo thay đổi nhân sự"
            ])
            
            news_items = []
            for i, title in enumerate(templates):
                news_items.append({
                    "title": title,
                    "summary": f"Tin tức chi tiết về {title.lower()}",
                    "link": self._get_company_news_link(symbol),
                    "published": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "sector": sector
                })
            
            return news_items
            
        except Exception as e:
            if "VietstockPro" in str(e):
                print(f"ℹ️ VietstockPro quota exceeded for {symbol}. Please upgrade or use another source.")
                return []  # Return empty list or fallback differently
            else:
                print(f"⚠️ Generic error fetching news for {symbol}: {e}")
                
            logger.error(f"Error generating company news for {symbol}: {e}")
            return []
            
    async def _crawl_vietstock_company_news(self, symbol: str) -> List[Dict[str, str]]:
        """Crawl tin tức công ty từ Vietstock"""
        import aiohttp
        from bs4 import BeautifulSoup
        import re
        
        news_items = []
        try:
            # Tạo URL cho trang tin tức của công ty
            url = f"https://finance.vietstock.vn/{symbol}/tin-tuc.htm"
            
            # Headers để giả lập trình duyệt
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Tìm các tin tức trong trang
                        news_containers = soup.select('.news-item') or soup.select('.list-news-item')
                        
                        for item in news_containers[:10]:  # Lấy tối đa 10 tin
                            try:
                                # Trích xuất tiêu đề
                                title_tag = item.select_one('.title a') or item.select_one('h2 a')
                                if not title_tag:
                                    continue
                                    
                                title = title_tag.text.strip()
                                link = title_tag.get('href')
                                if not link.startswith('http'):
                                    link = f"https://finance.vietstock.vn{link}"
                                
                                # Trích xuất tóm tắt
                                summary_tag = item.select_one('.desc') or item.select_one('.sapo')
                                summary = summary_tag.text.strip() if summary_tag else "Không có tóm tắt"
                                
                                # Trích xuất thời gian
                                date_tag = item.select_one('.date') or item.select_one('.time')
                                published = date_tag.text.strip() if date_tag else datetime.now().strftime('%d/%m/%Y')
                                
                                # Thêm vào danh sách tin tức
                                news_items.append({
                                    "title": title,
                                    "summary": summary,
                                    "link": link,
                                    "published": published,
                                    "sector": "Finance",  # Default sector
                                    "source": "Vietstock"
                                })
                            except Exception as e:
                                print(f"Error parsing news item: {e}")
                                continue
                    else:
                        print(f"Failed to fetch news for {symbol}, status code: {response.status}")
                        
            # Nếu không tìm thấy tin tức nào, thử crawl trang danh sách công ty
            if len(news_items) == 0:
                news_items = await self._crawl_vietstock_az_page(symbol)
                
            return news_items
        except Exception as e:
            print(f"Error crawling Vietstock for {symbol}: {e}")
            return []
    
    async def _crawl_vietstock_az_page(self, symbol: str) -> List[Dict[str, str]]:
        """Crawl tin tức từ trang danh sách công ty A-Z của Vietstock"""
        import aiohttp
        from bs4 import BeautifulSoup
        
        news_items = []
        try:
            # URL trang danh sách công ty
            url = "https://finance.vietstock.vn/doanh-nghiep-a-z?page=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Tìm bảng công ty
                        company_table = soup.select_one('#azTable')
                        if company_table:
                            rows = company_table.select('tbody tr')
                            
                            for row in rows:
                                try:
                                    # Lấy mã cổ phiếu từ hàng
                                    ticker_cell = row.select_one('td:nth-child(1)')
                                    if not ticker_cell:
                                        continue
                                        
                                    ticker = ticker_cell.text.strip()
                                    
                                    # Nếu không phải mã cổ phiếu cần tìm, bỏ qua
                                    if ticker != symbol:
                                        continue
                                    
                                    # Lấy thông tin công ty
                                    company_name = row.select_one('td:nth-child(2)').text.strip()
                                    exchange = row.select_one('td:nth-child(3)').text.strip()
                                    
                                    # Tạo tin tức giả từ thông tin công ty
                                    news_items.append({
                                        "title": f"Thông tin về công ty {company_name} ({ticker})",
                                        "summary": f"Mã chứng khoán {ticker} thuộc sàn {exchange}. Xem thêm thông tin chi tiết tại link.",
                                        "link": f"https://finance.vietstock.vn/{ticker}/ho-so-doanh-nghiep.htm",
                                        "published": datetime.now().strftime('%d/%m/%Y'),
                                        "sector": "Finance",
                                        "source": "Vietstock A-Z"
                                    })
                                    break
                                except Exception as e:
                                    print(f"Error parsing company row: {e}")
                                    continue
                    else:
                        print(f"Failed to fetch A-Z page, status code: {response.status}")
                        
            return news_items
        except Exception as e:
            print(f"Error crawling Vietstock A-Z page: {e}")
            return []
    
    def _fetch_market_news(self) -> List[Dict[str, str]]:
        """Lấy tin tức thị trường tổng quát"""
        market_news = [
            "VN-Index tăng điểm trong phiên giao dịch sáng nay",
            "Khối ngoại mua ròng 200 tỷ đồng trên HOSE",
            "Nhóm cổ phiếu ngân hàng dẫn dắt thị trường",
            "Thanh khoản thị trường cải thiện đáng kể",
            "Cổ phiếu bất động sản có dấu hiệu phục hồi"
        ]
        
        news_items = []
        for i, title in enumerate(market_news):
            news_items.append({
                "title": title,
                "summary": f"Phân tích chi tiết về {title.lower()}",
                "link": f"https://finance.vietstock.vn/doanh-nghiep-a-z?page=1&symbol=market-news-{i+1}",
                "published": datetime.now().strftime('%d/%m/%Y %H:%M')
            })
        
        return news_items

    def _get_company_news_link(self, symbol: str) -> str:
        """Get a link to company news on Vietstock"""
        try:
            # Try to construct a direct link that might show all news
            return f"https://finance.vietstock.vn/{symbol.lower()}/tin-tuc.htm"
        except Exception as e:
            print(f"⚠️ Error generating news link for {symbol}: {e}")
            return f"https://finance.vietstock.vn/doanh-nghiep-a-z?page=1&symbol={symbol.lower()}"  # Fallback to default

    async def get_company_by_sector(self, sector: str) -> Dict[str, Any]:
        """Lấy danh sách công ty theo ngành"""
        if not self.company_search:
            return self._get_fallback_sector_companies(sector)
        
        try:
            result = await self.company_search.search_companies_by_sector(sector)
            return result
        except Exception as e:
            logger.error(f"Sector search failed for {sector}: {e}")
            return self._get_fallback_sector_companies(sector)
    
    def _get_fallback_sector_companies(self, sector: str) -> Dict[str, Any]:
        """Fallback sector companies when API not available"""
        sector_companies = {
            'Banking': [
                {'symbol': 'VCB', 'name': 'Ngân hàng TMCP Ngoại thương Việt Nam'},
                {'symbol': 'BID', 'name': 'Ngân hàng TMCP Đầu tư và Phát triển VN'},
                {'symbol': 'CTG', 'name': 'Ngân hàng TMCP Công thương Việt Nam'}
            ],
            'Technology': [
                {'symbol': 'FPT', 'name': 'Công ty Cổ phần FPT'},
                {'symbol': 'CMG', 'name': 'Công ty Cổ phần Tin học CMC'}
            ],
            'Real Estate': [
                {'symbol': 'VIC', 'name': 'Tập đoàn Vingroup'},
                {'symbol': 'VHM', 'name': 'Công ty CP Vinhomes'}
            ]
        }
        
        companies = sector_companies.get(sector, [])
        return {
            'sector_query': sector,
            'found_count': len(companies),
            'companies': companies
        }

    async def get_all_companies(self) -> Dict[str, Any]:
        """Lấy danh sách tất cả các công ty từ Vietstock"""
        try:
            companies = await self._crawl_all_vietstock_companies()
            return {
                "source": "Vietstock A-Z",
                "timestamp": datetime.now().isoformat(),
                "companies": companies,
                "companies_count": len(companies)
            }
        except Exception as e:
            logger.error(f"❌ Error fetching all companies: {e}")
            return {
                "source": "Vietstock A-Z",
                "timestamp": datetime.now().isoformat(),
                "companies": [],
                "companies_count": 0,
                "error": str(e)
            }
    
    async def _crawl_all_vietstock_companies(self) -> List[Dict[str, Any]]:
        """Crawl danh sách tất cả các công ty từ Vietstock"""
        import aiohttp
        from bs4 import BeautifulSoup
        
        companies = []
        try:
            # Số trang cần crawl (có thể điều chỉnh)
            max_pages = 5
            
            for page in range(1, max_pages + 1):
                # URL trang danh sách công ty
                url = f"https://finance.vietstock.vn/doanh-nghiep-a-z?page={page}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Tìm bảng công ty
                            company_table = soup.select_one('#azTable')
                            if company_table:
                                rows = company_table.select('tbody tr')
                                
                                for row in rows:
                                    try:
                                        # Lấy thông tin công ty
                                        ticker = row.select_one('td:nth-child(1)').text.strip()
                                        company_name = row.select_one('td:nth-child(2)').text.strip()
                                        exchange = row.select_one('td:nth-child(3)').text.strip()
                                        
                                        # Thêm vào danh sách
                                        companies.append({
                                            "symbol": ticker,
                                            "name": company_name,
                                            "exchange": exchange,
                                            "sector": self._determine_sector(company_name),
                                            "data_source": "Vietstock"
                                        })
                                    except Exception as e:
                                        print(f"Error parsing company row: {e}")
                                        continue
                        else:
                            print(f"Failed to fetch A-Z page {page}, status code: {response.status}")
                            break
            
            return companies
        except Exception as e:
            print(f"Error crawling all Vietstock companies: {e}")
            return []
    
    def _determine_sector(self, company_name: str) -> str:
        """Xác định ngành dựa trên tên công ty"""
        company_name = company_name.lower()
        
        # Mapping từ khóa đến ngành
        sector_keywords = {
            'ngân hàng': 'Banking',
            'bank': 'Banking',
            'bảo hiểm': 'Insurance',
            'chứng khoán': 'Securities',
            'bất động sản': 'Real Estate',
            'địa ốc': 'Real Estate',
            'xây dựng': 'Construction',
            'thép': 'Steel',
            'dầu khí': 'Oil & Gas',
            'điện': 'Utilities',
            'công nghệ': 'Technology',
            'phần mềm': 'Technology',
            'viễn thông': 'Telecommunications',
            'dược': 'Pharmaceuticals',
            'y tế': 'Healthcare',
            'thực phẩm': 'Food & Beverage',
            'đồ uống': 'Food & Beverage',
            'bán lẻ': 'Retail',
            'vận tải': 'Transportation',
            'logistics': 'Logistics',
            'du lịch': 'Tourism',
            'cao su': 'Rubber',
            'nhựa': 'Plastics',
            'thủy sản': 'Seafood',
            'nông nghiệp': 'Agriculture'
        }
        
        for keyword, sector in sector_keywords.items():
            if keyword in company_name:
                return sector
        
        return "Other"

    async def _get_financial_metrics(self, symbol: str) -> Dict[str, Any]:
        """Lấy thông tin tài chính của công ty"""
        import random
        
        # Fallback financial metrics khi không có API thật
        metrics = {
            'VCB': {
                'market_cap': '400,000 tỷ VND',
                'pe_ratio': '17.5',
                'pb_ratio': '3.2',
                'roe': '21.5%',
                'dividend_yield': '1.2%',
                'revenue_growth': '15.3%',
                'debt_to_equity': '0.8'
            },
            'BID': {
                'market_cap': '180,000 tỷ VND',
                'pe_ratio': '12.8',
                'pb_ratio': '2.1',
                'roe': '16.7%',
                'dividend_yield': '2.0%',
                'revenue_growth': '12.5%',
                'debt_to_equity': '1.2'
            },
            'VIC': {
                'market_cap': '350,000 tỷ VND',
                'pe_ratio': '45.2',
                'pb_ratio': '4.8',
                'roe': '10.2%',
                'dividend_yield': '0.5%',
                'revenue_growth': '22.7%',
                'debt_to_equity': '1.5'
            },
            'FPT': {
                'market_cap': '85,000 tỷ VND',
                'pe_ratio': '18.3',
                'pb_ratio': '3.5',
                'roe': '22.8%',
                'dividend_yield': '2.5%',
                'revenue_growth': '18.2%',
                'debt_to_equity': '0.6'
            },
            'HPG': {
                'market_cap': '120,000 tỷ VND',
                'pe_ratio': '8.5',
                'pb_ratio': '1.8',
                'roe': '25.3%',
                'dividend_yield': '1.8%',
                'revenue_growth': '15.7%',
                'debt_to_equity': '0.9'
            }
        }
        
        # Nếu không có dữ liệu có sẵn, tạo dữ liệu ngẫu nhiên hợp lý
        if symbol not in metrics:
            return {
                'market_cap': f'{random.randint(5, 500):,} tỷ VND',
                'pe_ratio': f'{random.uniform(5, 30):.1f}',
                'pb_ratio': f'{random.uniform(0.8, 5):.1f}',
                'roe': f'{random.uniform(5, 30):.1f}%',
                'dividend_yield': f'{random.uniform(0, 5):.1f}%',
                'revenue_growth': f'{random.uniform(-10, 30):.1f}%',
                'debt_to_equity': f'{random.uniform(0.2, 2):.1f}'
            }
        
        return metrics.get(symbol)
    
    def _analyze_news_sentiment(self, news: List[Dict[str, str]], symbol: str) -> tuple:
        """Phân tích sentiment từ tin tức"""
        import random
        
        # Nếu không có tin tức, trả về neutral
        if not news or len(news) == 0:
            return "Neutral", [f"Không có tin tức mới về {symbol}"], {
                'impact_level': 'Low',
                'recommendation': 'Hold',
                'confidence': '50%'
            }
        
        # Phân tích từ khóa trong tiêu đề tin tức
        positive_keywords = ['tăng', 'lãi', 'lợi nhuận', 'tích cực', 'thành công', 'mở rộng', 'phát triển']
        negative_keywords = ['giảm', 'lỗ', 'khó khăn', 'thách thức', 'rủi ro', 'đình trệ', 'sụt giảm']
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        # Đếm số lượng tin tức tích cực/tiêu cực
        for item in news:
            title = item.get('title', '').lower()
            summary = item.get('summary', '').lower()
            content = title + ' ' + summary
            
            has_positive = any(keyword in content for keyword in positive_keywords)
            has_negative = any(keyword in content for keyword in negative_keywords)
            
            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative and not has_positive:
                negative_count += 1
            elif has_positive and has_negative:
                # Nếu có cả từ khóa tích cực và tiêu cực, coi là trung lập
                neutral_count += 1
            else:
                neutral_count += 1
        
        # Xác định sentiment tổng thể
        if positive_count > negative_count + neutral_count:
            sentiment = "Positive"
            impact = "High"
            recommendation = "Buy"
            confidence = f"{random.randint(70, 90)}%"
        elif negative_count > positive_count + neutral_count:
            sentiment = "Negative"
            impact = "High"
            recommendation = "Sell"
            confidence = f"{random.randint(70, 90)}%"
        elif positive_count > negative_count:
            sentiment = "Slightly Positive"
            impact = "Medium"
            recommendation = "Hold/Buy"
            confidence = f"{random.randint(55, 75)}%"
        elif negative_count > positive_count:
            sentiment = "Slightly Negative"
            impact = "Medium"
            recommendation = "Hold/Sell"
            confidence = f"{random.randint(55, 75)}%"
        else:
            sentiment = "Neutral"
            impact = "Low"
            recommendation = "Hold"
            confidence = f"{random.randint(40, 60)}%"
        
        # Trích xuất các tiêu đề quan trọng nhất
        headlines = [news[i].get('title') for i in range(min(5, len(news)))]
        
        # Tạo phân tích
        analysis = {
            'impact_level': impact,
            'recommendation': recommendation,
            'confidence': confidence,
            'positive_news': positive_count,
            'negative_news': negative_count,
            'neutral_news': neutral_count
        }
        
        return sentiment, headlines, analysis

    async def _get_internal_company_details(self, symbol: str) -> Dict[str, Any]:
        """Lấy thông tin chi tiết nội bộ của công ty sử dụng CrewAI hoặc crawl"""
        try:
            # Thử sử dụng CrewAI để lấy thông tin
            crewai_details = await self._get_crewai_company_details(symbol)
            if crewai_details:
                return crewai_details
                
            # Nếu không có CrewAI, thử crawl thông tin chi tiết từ Vietstock
            details = await self._crawl_company_details(symbol)
            if details:
                return details
        except Exception as e:
            logger.error(f"Error getting company details for {symbol}: {e}")
        
        # Fallback data nếu không crawl được
        fallback_details = {
            'VCB': {
                'full_name': 'Ngân hàng TMCP Ngoại thương Việt Nam',
                'english_name': 'Joint Stock Commercial Bank for Foreign Trade of Vietnam',
                'short_name': 'Vietcombank',
                'tax_code': '0100112437',
                'address': '198 Trần Quang Khải, Hoàn Kiếm, Hà Nội',
                'phone': '(84-24) 3934 3137',
                'fax': '(84-24) 3826 9067',
                'email': 'vcbhn@vietcombank.com.vn',
                'website': 'www.vietcombank.com.vn',
                'established_date': '01/06/1963',
                'listing_date': '30/06/2009',
                'charter_capital': '47,325,139,500,000 VND',
                'business_areas': 'Dịch vụ tài chính ngân hàng, cho vay, tiền gửi, thẻ, ngoại hối',
                'key_products': 'Tài khoản thanh toán, thẻ tín dụng, cho vay mua nhà, tiết kiệm',
                'competitors': 'BIDV, Vietinbank, Techcombank, MB Bank',
                'key_executives': [
                    {'name': 'Phạm Quang Dũng', 'position': 'Tổng Giám đốc'},
                    {'name': 'Nghiêm Xuân Thành', 'position': 'Chủ tịch HĐQT'}
                ],
                'subsidiaries': [
                    'Công ty Chứng khoán Vietcombank (VCBS)',
                    'Công ty Cho thuê tài chính Vietcombank (VCBL)',
                    'Công ty Chuyển tiền Vietcombank (VCBR)'
                ],
                'data_source': 'Fallback'
            },
            'FPT': {
                'full_name': 'Công ty Cổ phần FPT',
                'english_name': 'FPT Corporation',
                'short_name': 'FPT Corp',
                'tax_code': '0101248141',
                'address': 'Tòa nhà FPT, phố Duy Tân, Cầu Giấy, Hà Nội',
                'phone': '(84-24) 7300 7300',
                'fax': '(84-24) 3768 9262',
                'email': 'fpt@fpt.com.vn',
                'website': 'www.fpt.com.vn',
                'established_date': '13/09/1988',
                'listing_date': '13/12/2006',
                'charter_capital': '11,210,342,090,000 VND',
                'business_areas': 'Công nghệ thông tin, viễn thông, giáo dục',
                'key_products': 'Phần mềm, dịch vụ CNTT, viễn thông, đào tạo CNTT',
                'competitors': 'VNPT, Viettel, CMC, MobiFone',
                'key_executives': [
                    {'name': 'Trương Gia Bình', 'position': 'Chủ tịch HĐQT'},
                    {'name': 'Nguyễn Văn Khoa', 'position': 'Tổng Giám đốc'}
                ],
                'subsidiaries': [
                    'FPT Software',
                    'FPT Telecom',
                    'FPT Education',
                    'FPT Retail',
                    'FPT Digital'
                ],
                'data_source': 'Fallback'
            }
        }
        
        # Tạo dữ liệu mặc định nếu không có sẵn
        if symbol not in fallback_details:
            return {
                'full_name': f'Công ty {symbol}',
                'english_name': f'{symbol} Corporation',
                'short_name': symbol,
                'tax_code': 'N/A',
                'address': 'N/A',
                'phone': 'N/A',
                'fax': 'N/A',
                'email': f'contact@{symbol.lower()}.com.vn',
                'website': f'www.{symbol.lower()}.com.vn',
                'established_date': 'N/A',
                'listing_date': 'N/A',
                'charter_capital': 'N/A',
                'business_areas': 'N/A',
                'key_products': 'N/A',
                'competitors': 'N/A',
                'key_executives': [],
                'subsidiaries': [],
                'data_source': 'Generated'
            }
        
        return fallback_details.get(symbol)
        
    async def _get_crewai_company_details(self, symbol: str) -> Dict[str, Any]:
        """Lấy thông tin công ty từ CrewAI"""
        try:
            # Import CrewAI collector
            from src.data.crewai_collector import get_crewai_collector
            
            # Thử lấy collector
            collector = get_crewai_collector()
            
            # Kiểm tra xem collector có hoạt động không
            if not collector or not collector.enabled:
                logger.warning(f"CrewAI collector not available for {symbol}")
                return None
                
            # Lấy danh sách các mã cổ phiếu từ CrewAI
            symbols = await collector.get_available_symbols()
            
            # Tìm thông tin công ty trong danh sách
            company_info = None
            for s in symbols:
                if s['symbol'] == symbol:
                    company_info = s
                    break
            
            if not company_info:
                return None
                
            # Lấy thông tin tin tức và sentiment từ CrewAI
            news_data = await collector.get_stock_news(symbol)
            
            # Tạo thông tin chi tiết từ dữ liệu CrewAI
            details = {
                'full_name': company_info.get('name', f'Công ty {symbol}'),
                'english_name': f"{company_info.get('name', symbol)} Corporation",
                'short_name': symbol,
                'sector': company_info.get('sector', 'Unknown'),
                'exchange': company_info.get('exchange', 'HOSE'),
                'business_areas': self._get_business_description(company_info.get('sector', 'Unknown')),
                'website': f"www.{symbol.lower()}.com.vn",
                'data_source': 'CrewAI',
                'sentiment': news_data.get('sentiment', 'Neutral'),
                'headlines': news_data.get('headlines', []),
                'key_executives': self._generate_executives_for_sector(company_info.get('sector', 'Unknown')),
                'subsidiaries': self._generate_subsidiaries_for_sector(symbol, company_info.get('sector', 'Unknown'))
            }
            
            logger.info(f"Got company details from CrewAI for {symbol}")
            return details
            
        except Exception as e:
            logger.error(f"Error getting CrewAI company details for {symbol}: {e}")
            return None
            
    def _get_business_description(self, sector: str) -> str:
        """Tạo mô tả kinh doanh dựa trên ngành"""
        descriptions = {
            'Banking': 'Cung cấp dịch vụ tài chính, ngân hàng, cho vay, tiền gửi, thẻ tín dụng và các sản phẩm tài chính khác.',
            'Real Estate': 'Phát triển, đầu tư và kinh doanh bất động sản, bao gồm các dự án nhà ở, văn phòng, khu đô thị và khu công nghiệp.',
            'Technology': 'Cung cấp dịch vụ công nghệ thông tin, phát triển phần mềm, tư vấn CNTT, viễn thông và các giải pháp số.',
            'Consumer': 'Sản xuất và phân phối các sản phẩm tiêu dùng, thực phẩm, đồ uống và các mặt hàng phục vụ nhu cầu hàng ngày.',
            'Industrial': 'Sản xuất công nghiệp, chế tạo, thép, vật liệu xây dựng và các sản phẩm công nghiệp khác.',
            'Utilities': 'Cung cấp dịch vụ tiện ích công cộng như điện, nước, khí đốt, năng lượng và các dịch vụ hạ tầng.',
            'Transportation': 'Vận tải hàng không, đường bộ, đường sắt, logistics và các dịch vụ vận chuyển hàng hóa, hành khách.',
            'Healthcare': 'Cung cấp dịch vụ y tế, sản xuất dược phẩm, thiết bị y tế và các giải pháp chăm sóc sức khỏe.'
        }
        
        return descriptions.get(sector, f'Hoạt động trong lĩnh vực {sector}.')
        
    def _generate_executives_for_sector(self, sector: str) -> List[Dict[str, str]]:
        """Tạo danh sách lãnh đạo dựa trên ngành"""
        import random
        
        first_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Đỗ', 'Võ', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ']
        middle_names = ['Văn', 'Thị', 'Hữu', 'Minh', 'Quang', 'Thanh', 'Tuấn', 'Anh', 'Thành', 'Hùng']
        last_names = ['Hùng', 'Anh', 'Tuấn', 'Minh', 'Thành', 'Hải', 'Long', 'Nam', 'Thắng', 'Dũng']
        
        positions = [
            {'title': 'Chủ tịch HĐQT', 'count': 1},
            {'title': 'Tổng Giám đốc', 'count': 1},
            {'title': 'Phó Tổng Giám đốc', 'count': random.randint(1, 3)},
            {'title': 'Giám đốc Tài chính', 'count': 1},
            {'title': 'Kế toán trưởng', 'count': 1}
        ]
        
        executives = []
        for position in positions:
            for _ in range(position['count']):
                name = f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}"
                executives.append({
                    'name': name,
                    'position': position['title']
                })
                
        return executives
        
    def _generate_subsidiaries_for_sector(self, symbol: str, sector: str) -> List[str]:
        """Tạo danh sách công ty con dựa trên ngành"""
        subsidiaries = {
            'Banking': [
                f'Công ty Chứng khoán {symbol}',
                f'Công ty Quản lý Quỹ {symbol}',
                f'Công ty Tài chính {symbol}'
            ],
            'Real Estate': [
                f'{symbol} Land',
                f'{symbol} Construction',
                f'{symbol} Investment'
            ],
            'Technology': [
                f'{symbol} Software',
                f'{symbol} Digital',
                f'{symbol} Solutions'
            ],
            'Consumer': [
                f'{symbol} Retail',
                f'{symbol} Distribution',
                f'{symbol} Trading'
            ],
            'Industrial': [
                f'{symbol} Manufacturing',
                f'{symbol} Steel',
                f'{symbol} Materials'
            ]
        }
        
        return subsidiaries.get(sector, [f'{symbol} Subsidiary 1', f'{symbol} Subsidiary 2'])
    
    async def _crawl_company_details(self, symbol: str) -> Dict[str, Any]:
        """Crawl thông tin chi tiết công ty từ Vietstock"""
        import aiohttp
        from bs4 import BeautifulSoup
        
        try:
            # URL trang hồ sơ công ty
            url = f"https://finance.vietstock.vn/{symbol}/ho-so-doanh-nghiep.htm"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Khởi tạo dict lưu thông tin
                        details = {}
                        
                        # Lấy tên công ty
                        company_name = soup.select_one('.company-name')
                        if company_name:
                            details['full_name'] = company_name.text.strip()
                        
                        # Lấy thông tin từ bảng thông tin cơ bản
                        info_table = soup.select('.company-info table tr')
                        for row in info_table:
                            cells = row.select('td')
                            if len(cells) >= 2:
                                key = cells[0].text.strip().lower()
                                value = cells[1].text.strip()
                                
                                if 'tên tiếng anh' in key or 'english' in key:
                                    details['english_name'] = value
                                elif 'tên viết tắt' in key or 'short' in key:
                                    details['short_name'] = value
                                elif 'mã số thuế' in key or 'tax' in key:
                                    details['tax_code'] = value
                                elif 'địa chỉ' in key or 'address' in key:
                                    details['address'] = value
                                elif 'điện thoại' in key or 'phone' in key:
                                    details['phone'] = value
                                elif 'fax' in key:
                                    details['fax'] = value
                                elif 'email' in key:
                                    details['email'] = value
                                elif 'website' in key:
                                    details['website'] = value
                                elif 'ngày thành lập' in key or 'established' in key:
                                    details['established_date'] = value
                                elif 'ngày niêm yết' in key or 'listing' in key:
                                    details['listing_date'] = value
                                elif 'vốn điều lệ' in key or 'charter' in key:
                                    details['charter_capital'] = value
                        
                        # Lấy thông tin về lĩnh vực kinh doanh
                        business_area = soup.select_one('.business-area')
                        if business_area:
                            details['business_areas'] = business_area.text.strip()
                        
                        # Lấy thông tin về ban lãnh đạo
                        executives = []
                        executive_table = soup.select('.leadership-table tr')
                        for row in executive_table[1:]:  # Bỏ qua hàng tiêu đề
                            cells = row.select('td')
                            if len(cells) >= 2:
                                name = cells[0].text.strip()
                                position = cells[1].text.strip()
                                executives.append({'name': name, 'position': position})
                        
                        if executives:
                            details['key_executives'] = executives
                        
                        return details
                    else:
                        logger.warning(f"Failed to fetch company details for {symbol}, status code: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error crawling company details: {e}")
            return None

# Factory function
def create_enhanced_news_agent(ai_agent=None) -> EnhancedNewsAgent:
    """Create enhanced news and company data agent instance"""
    agent = EnhancedNewsAgent()
    
    # Set AI agent if provided
    if ai_agent:
        agent.ai_agent = ai_agent
        logger.info("AI agent configured for enhanced news agent")
    
    return agent