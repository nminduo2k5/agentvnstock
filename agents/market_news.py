import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import asyncio
from agents.risk_based_news import RiskBasedNewsAgent

class MarketNews:
    def __init__(self):
        self.name = "Market News Agent"
        self.cafef_url = "https://cafef.vn/thi-truong-chung-khoan.chn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.ai_agent = None  # Will be set by main_agent
        self.risk_news_agent = RiskBasedNewsAgent()
    
    def set_ai_agent(self, ai_agent):
        """Set AI agent for enhanced market news analysis"""
        self.ai_agent = ai_agent
    
    def get_market_news(self, category: str = "general", risk_tolerance: int = 50, time_horizon: str = "Trung hạn", investment_amount: int = 10000000):
        try:
            # Get risk-based news first
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                risk_news = loop.run_until_complete(
                    self.risk_news_agent.get_news_by_risk_profile(risk_tolerance, time_horizon, investment_amount)
                )
                loop.close()
                
                if not risk_news.get('error'):
                    base_news = {
                        "category": "Vietnam Market",
                        "news_count": risk_news['total_news'],
                        "news": risk_news['news_data'],
                        "source": risk_news['source_info'],
                        "risk_profile": risk_news['risk_profile'],
                        "news_type": risk_news['news_type'],
                        "recommendation": risk_news['recommendation']
                    }
                else:
                    raise Exception("Risk news failed")
            except:
                # Fallback to traditional news
                cafef_news = self._crawl_cafef_news()
                if cafef_news:
                    base_news = {
                        "category": "Vietnam Market",
                        "news_count": len(cafef_news),
                        "news": cafef_news,
                        "source": "📰 CafeF.vn (Tin chính thống)",
                        "risk_profile": "Default",
                        "news_type": "official"
                    }
                else:
                    base_news = self._get_vn_mock_news()
            
            # Enhance with AI analysis if available
            if base_news and self.ai_agent:
                try:
                    ai_enhancement = self._get_ai_market_analysis(base_news, category)
                    base_news.update(ai_enhancement)
                except Exception as e:
                    print(f"⚠️ AI market analysis failed: {e}")
                    base_news['ai_enhanced'] = False
                    base_news['ai_error'] = str(e)
            
            return base_news
                
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
            "source": "📰 Mock VN News (Fallback)",
            "risk_profile": "Default",
            "news_type": "official"
        }
    
    def _get_ai_market_analysis(self, base_news: dict, category: str):
        """Get AI-enhanced market analysis"""
        try:
            # Prepare market news context for AI analysis
            news_titles = []
            for news_item in base_news.get('news', []):
                news_titles.append(f"- {news_item.get('title', '')}")
            
            news_context = "\n".join(news_titles[:8])  # Limit to top 8 news
            
            context = f"""
Phân tích thị trường chứng khoán Việt Nam dựa trên tin tức mới nhất:

THÔNG TIN THỊ TRƯỜNG:
- Danh mục: {base_news.get('category', 'N/A')}
- Số lượng tin: {base_news.get('news_count', 0)}
- Nguồn: {base_news.get('source', 'N/A')}

TIN TỨC THỊ TRƯỜNG:
{news_context}

Hãy đưa ra phân tích chuyên sâu về:
1. Xu hướng tổng thể của thị trường (tăng/giảm/sideway)
2. Các yếu tố chính tác động đến thị trường
3. Nhóm ngành nổi bật (tích cực/tiêu cực)
4. Dự báo ngắn hạn cho thị trường
5. Khuyến nghị chiến lược đầu tư

Trả lời ngắn gọn, tập trung vào những điểm quan trọng nhất.
"""
            
            # Get AI analysis
            ai_result = self.ai_agent.generate_with_fallback(context, 'market_analysis', max_tokens=600)
            
            if ai_result['success']:
                return {
                    'ai_market_analysis': ai_result['response'],
                    'ai_model_used': ai_result['model_used'],
                    'ai_enhanced': True,
                    'market_sentiment': self._extract_market_sentiment(ai_result['response']),
                    'market_trend': self._extract_market_trend(ai_result['response'])
                }
            else:
                return {'ai_enhanced': False, 'ai_error': ai_result.get('error', 'AI not available')}
                
        except Exception as e:
            return {'ai_enhanced': False, 'ai_error': str(e)}
    
    def _extract_market_sentiment(self, ai_response: str):
        """Extract market sentiment from AI response"""
        try:
            ai_lower = ai_response.lower()
            
            # Market sentiment indicators
            bullish_indicators = ['tăng', 'tích cực', 'bullish', 'khả quan', 'mạnh', 'tốt']
            bearish_indicators = ['giảm', 'tiêu cực', 'bearish', 'yếu', 'lo ngại', 'rủi ro']
            
            bullish_count = sum(1 for indicator in bullish_indicators if indicator in ai_lower)
            bearish_count = sum(1 for indicator in bearish_indicators if indicator in ai_lower)
            
            if bullish_count > bearish_count:
                return 'BULLISH'
            elif bearish_count > bullish_count:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception:
            return 'NEUTRAL'
    
    def _extract_market_trend(self, ai_response: str):
        """Extract market trend from AI response"""
        try:
            ai_lower = ai_response.lower()
            
            if any(phrase in ai_lower for phrase in ['xu hướng tăng', 'uptrend', 'tăng trưởng']):
                return 'UPTREND'
            elif any(phrase in ai_lower for phrase in ['xu hướng giảm', 'downtrend', 'suy giảm']):
                return 'DOWNTREND'
            elif any(phrase in ai_lower for phrase in ['sideway', 'đi ngang', 'consolidation']):
                return 'SIDEWAYS'
            else:
                return 'MIXED'
                
        except Exception:
            return 'MIXED'