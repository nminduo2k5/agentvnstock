import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

class MarketNews:
    def __init__(self):
        self.name = "Market News Agent"
        self.cafef_url = "https://cafef.vn/thi-truong-chung-khoan.chn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_market_news(self, category: str = "general"):
        try:
            # Try CafeF first
            cafef_news = self._crawl_cafef_news()
            if cafef_news:
                return {
                    "category": "Vietnam Market",
                    "news_count": len(cafef_news),
                    "news": cafef_news,
                    "source": "CafeF.vn"
                }
            else:
                # Fallback to mock VN news
                return self._get_vn_mock_news()
                
        except Exception as e:
            print(f"❌ Error crawling CafeF: {e}")
            return self._get_vn_mock_news()
    
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
                            "source_index": "VN Market"
                        })
                        
                except Exception as article_error:
                    continue
            
            print(f"✅ Crawled {len(news_items)} news from CafeF")
            return news_items
            
        except Exception as e:
            print(f"❌ CafeF crawling failed: {e}")
            return None
    
    def _get_vn_mock_news(self):
        """Fallback VN market news"""
        import random
        
        mock_news = [
            "VN-Index tăng điểm trong phiên giao dịch sáng nay",
            "Khối ngoại mua ròng 200 tỷ đồng trên HOSE",
            "Nhóm cổ phiếu ngân hàng dẫn dắt thị trường",
            "Thanh khoản thị trường cải thiện đáng kể",
            "Cổ phiếu bất động sản có dấu hiệu phục hồi",
            "Thị trường phái sinh giao dịch tích cực",
            "HNX-Index tăng nhẹ theo đà chung",
            "Nhóm cổ phiếu công nghệ thu hút dòng tiền",
            "Chỉ số VN30 vượt qua vùng kháng cự quan trọng",
            "Thị trường chứng khoán Việt Nam ổn định"
        ]
        
        news_items = []
        for i, title in enumerate(mock_news):
            news_items.append({
                "title": title,
                "link": f"https://cafef.vn/mock-news-{i+1}",
                "published": datetime.now().strftime('%d/%m/%Y %H:%M'),
                "summary": f"Phân tích chi tiết về {title.lower()}",
                "publisher": "CafeF Mock",
                "source_index": "VN Market"
            })
        
        return {
            "category": "Vietnam Market",
            "news_count": len(news_items),
            "news": news_items,
            "source": "Mock VN News"
        }