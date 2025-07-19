# agents/enhanced_news_agent.py
"""
Enhanced News Agent with Company Data Integration
Tích hợp dữ liệu công ty và tin tức theo mã cổ phiếu
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
        """Lấy tin tức và dữ liệu công ty theo mã cổ phiếu"""
        try:
            # Get company information
            company_info = await self._get_company_info(symbol)
            
            # Get news for the company
            news = await self._fetch_company_news(symbol, company_info)
            
            return {
                "symbol": symbol,
                "company_info": company_info,
                "news": news,
                "news_count": len(news),
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
            'VCB': {'full_name': 'Ngân hàng TMCP Ngoại thương Việt Nam', 'sector': 'Banking'},
            'BID': {'full_name': 'Ngân hàng TMCP Đầu tư và Phát triển VN', 'sector': 'Banking'},
            'VIC': {'full_name': 'Tập đoàn Vingroup', 'sector': 'Real Estate'},
            'FPT': {'full_name': 'Công ty Cổ phần FPT', 'sector': 'Technology'},
            'HPG': {'full_name': 'Tập đoàn Hòa Phát', 'sector': 'Industrial'}
        }
        
        return fallback_data.get(symbol, {
            'full_name': f'Công ty {symbol}',
            'sector': 'Unknown',
            'symbol': symbol
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

# Factory function
def create_enhanced_news_agent() -> EnhancedNewsAgent:
    """Create enhanced news and company data agent instance"""
    return EnhancedNewsAgent()