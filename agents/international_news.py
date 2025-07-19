import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

class InternationalMarketNews:
    def __init__(self):
        self.name = "International Market News Agent"
        self.description = "Agent for international market news"
        self.source = "CafeF.vn"
        self.cafef_url = "https://cafef.vn/tai-chinh-quoc-te.chn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_international_news(self):
        """Lấy tin tức thị trường quốc tế"""
        try:
            # Try CafeF first
            cafef_news = self._crawl_cafef_news()
            if cafef_news:
                return {
                    "category": "International Market",
                    "news_count": len(cafef_news),
                    "news": cafef_news,
                    "source": "CafeF.vn"
                }
            else:
                # Fallback to mock international news
                return self._get_international_mock_news()

        except Exception as e:
            print(f"❌ Error crawling CafeF: {e}")
            return self._get_international_mock_news()
    
    def get_market_news(self, category: str = "general"):
        try:
            # Try CafeF first
            cafef_news = self._crawl_cafef_news()
            if cafef_news:
                return {
                    "category": "International Market",
                    "news_count": len(cafef_news),
                    "news": cafef_news,
                    "source": "CafeF.vn"
                }
            else:
                # Fallback to mock international news
                return self._get_international_mock_news()

        except Exception as e:
            print(f"❌ Error crawling CafeF: {e}")
            return self._get_international_mock_news()

    def _crawl_cafef_news(self):
        try:
            response = requests.get(self.cafef_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Find news articles - multiple selectors
            selectors = [
                '.tlitem',
                '.item-news',
                '.news-item',
                '.article-item',
                'article',
                '.box-category-item'
            ]
            
            articles = []
            for selector in selectors:
                found = soup.select(selector)
                if found:
                    articles = found
                    break
            
            # If no specific selectors work, try finding by common patterns
            if not articles:
                articles = soup.find_all(['div', 'article'], class_=re.compile(r'(news|item|article|post)'))
            
            for article in articles[:20]:  # Limit to 20 articles
                try:
                    # Extract title
                    title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=re.compile(r'(title|headline)'))
                    if not title_elem:
                        title_elem = article.find('a')
                    
                    title = title_elem.get_text(strip=True) if title_elem else "Không có tiêu đề"
                    
                    # Extract link
                    link_elem = title_elem if title_elem and title_elem.name == 'a' else article.find('a')
                    link = link_elem.get('href', '') if link_elem else ''
                    if link and not link.startswith('http'):
                        link = 'https://cafef.vn' + link
                    
                    # Extract time
                    time_elem = article.find(['time', 'span'], class_=re.compile(r'(time|date)'))
                    if not time_elem:
                        time_elem = article.find(text=re.compile(r'\d{1,2}[/\-]\d{1,2}'))
                    
                    published = time_elem.get_text(strip=True) if hasattr(time_elem, 'get_text') else str(time_elem) if time_elem else datetime.now().strftime('%d/%m/%Y')
                    
                    # Extract summary
                    summary_elem = article.find(['p', 'div'], class_=re.compile(r'(summary|desc|content)'))
                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title[:100] + "..."
                    
                    if title and len(title) > 10:  # Valid title
                        news_items.append({
                            "title": title,
                            "link": link,
                            "published": published,
                            "summary": summary,
                            "publisher": "CafeF",
                            "source_index": "International Market"
                        })
                        
                except Exception as article_error:
                    continue
            
            print(f"✅ Crawled {len(news_items)} news from CafeF")
            return news_items
            
        except Exception as e:
            print(f"❌ CafeF crawling failed: {e}")
            return None

    def _get_international_mock_news(self):
        """Fallback International market news"""
        import random
        
        mock_news = [
            "Thị trường chứng khoán quốc tế hôm nay có những biến động mạnh",
            "Chỉ số Dow Jones tăng điểm sau khi công bố báo cáo kinh tế tích cực",
            "Chứng khoán châu Á đồng loạt giảm điểm do lo ngại về lạm phát",
            "Giá dầu thô tiếp tục tăng cao, đạt mức kỷ lục mới",
            "Cổ phiếu công nghệ Mỹ phục hồi sau đợt bán tháo mạnh",
            "Ngân hàng Trung ương châu Âu giữ nguyên lãi suất trong cuộc họp hôm nay",
            "Thị trường chứng khoán Nhật Bản ghi nhận mức tăng trưởng ấn tượng",
            "Các nhà đầu tư lo ngại về căng thẳng địa chính trị tại Trung Đông",
            "Chứng khoán châu Âu giảm điểm do lo ngại về tăng trưởng kinh tế",
            "Cổ phiếu Tesla tiếp tục tăng mạnh sau khi công bố kết quả kinh doanh tốt"  
        ]
        
        news_items = []
        for i, title in enumerate(mock_news):
            news_items.append({
                "title": title,
                "link": f"https://cafef.vn/mock-news-{i+1}",
                "published": datetime.now().strftime('%d/%m/%Y %H:%M'),
                "summary": f"Phân tích chi tiết về {title.lower()}",
                "publisher": "CafeF Mock",
                "source_index": "International Market"
            })
        
        return {
            "category": "International Market",
            "news_count": len(news_items),
            "news": news_items,
            "source": "Mock VN News"
        }