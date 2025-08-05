import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import asyncio
from agents.international_underground_news import InternationalUndergroundNewsAgent

class InternationalMarketNews:
    def __init__(self):
        self.name = "International Market News Agent"
        self.description = "Agent for international market news"
        self.source = "CafeF.vn"
        self.cafef_url = "https://cafef.vn/tai-chinh-quoc-te.chn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.ai_agent = None  # Will be set by main_agent
        self.underground_agent = InternationalUndergroundNewsAgent()
    
    def set_ai_agent(self, ai_agent):
        """Set AI agent for enhanced international news analysis"""
        self.ai_agent = ai_agent
        # Also set AI agent for underground news agent
        self.underground_agent.set_ai_agent(ai_agent)
    
    def get_international_news(self):
        """Lấy tin tức thị trường quốc tế với AI analysis"""
        try:
            # Get base international news first
            base_news = None
            
            # Try CafeF first
            cafef_news = self._crawl_cafef_news()
            if cafef_news:
                base_news = {
                    "category": "International Market",
                    "news_count": len(cafef_news),
                    "news": cafef_news,
                    "source": "CafeF.vn"
                }
            else:
                # Fallback to mock international news
                base_news = self._get_international_mock_news()
            
            # Enhance with AI analysis if available
            if base_news and self.ai_agent:
                try:
                    ai_enhancement = self._get_ai_international_analysis(base_news)
                    base_news.update(ai_enhancement)
                except Exception as e:
                    print(f"⚠️ AI international analysis failed: {e}")
                    base_news['ai_enhanced'] = False
                    base_news['ai_error'] = str(e)
            
            return base_news

        except Exception as e:
            print(f"❌ Error crawling CafeF: {e}")
            return self._get_international_mock_news()
    
    def get_market_news(self, category="general", risk_tolerance=50, time_horizon="Trung hạn", investment_amount=10000000, **kwargs):
        """Get international market news based on risk profile"""
        return self._get_market_news_impl(category, risk_tolerance, time_horizon, investment_amount)
    
    def _get_market_news_impl(self, category: str = "general", risk_tolerance: int = 50, time_horizon: str = "Trung hạn", investment_amount: int = 10000000):
        """Get international market news based on risk profile"""
        try:
            # Get underground news based on risk profile first
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                underground_news = loop.run_until_complete(
                    self.underground_agent.get_underground_news_by_risk_profile(
                        risk_tolerance, time_horizon, investment_amount
                    )
                )
                loop.close()
                
                if not underground_news.get('error'):
                    base_news = {
                        "category": "International Market",
                        "news_count": underground_news['news_count'],
                        "news": underground_news['news'],
                        "source": underground_news['source'],
                        "risk_profile": underground_news['risk_profile'],
                        "news_type": underground_news['news_type'],
                        "recommendation": underground_news.get('recommendation'),
                        "crawl_summary": underground_news.get('crawl_summary')
                    }
                    
                    # Add AI analysis if available
                    if underground_news.get('ai_underground_analysis'):
                        base_news['ai_underground_analysis'] = underground_news['ai_underground_analysis']
                        base_news['ai_enhanced'] = True
                        base_news['market_sentiment'] = underground_news.get('market_sentiment')
                        base_news['risk_assessment'] = underground_news.get('risk_assessment')
                    
                    return base_news
                else:
                    raise Exception("Underground news failed")
                    
            except Exception as e:
                print(f"⚠️ Underground news failed: {e}")
                # Fallback to traditional CafeF news
                cafef_news = self._crawl_cafef_news()
                if cafef_news:
                    base_news = {
                        "category": "International Market",
                        "news_count": len(cafef_news),
                        "news": cafef_news,
                        "source": "📰 CafeF.vn (Tin chính thống)",
                        "risk_profile": "Default",
                        "news_type": "official"
                    }
                    
                    # Enhance with AI analysis if available
                    if self.ai_agent:
                        try:
                            ai_enhancement = self._get_ai_international_analysis(base_news)
                            base_news.update(ai_enhancement)
                        except Exception as ai_e:
                            print(f"⚠️ AI analysis failed: {ai_e}")
                    
                    return base_news
                else:
                    return self._get_international_mock_news()

        except Exception as e:
            print(f"❌ Error in international market news: {e}")
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
            "source": "Mock International News"
        }
    
    def _get_ai_international_analysis(self, base_news: dict):
        """Get AI-enhanced international market analysis"""
        try:
            # Prepare international news context for AI analysis
            news_titles = []
            for news_item in base_news.get('news', []):
                news_titles.append(f"- {news_item.get('title', '')}")
            
            news_context = "\n".join(news_titles[:8])  # Limit to top 8 news
            
            context = f"""
Phân tích thị trường tài chính quốc tế dựa trên tin tức mới nhất:

THÔNG TIN THỊ TRƯỜNG QUỐC TẾ:
- Danh mục: {base_news.get('category', 'N/A')}
- Số lượng tin: {base_news.get('news_count', 0)}
- Nguồn: {base_news.get('source', 'N/A')}

TIN TỨC QUỐC TẾ:
{news_context}

Hãy đưa ra phân tích chuyên sâu về:
1. Xu hướng thị trường tài chính toàn cầu
2. Tác động đến thị trường chứng khoán Việt Nam
3. Các yếu tố địa chính trị và kinh tế quan trọng
4. Dự báo cho các thị trường chính (Mỹ, châu Âu, châu Á)
5. Khuyến nghị đầu tư trong bối cảnh quốc tế

Trả lời ngắn gọn, tập trung vào những điểm quan trọng nhất.
"""
            
            # Get AI analysis
            ai_result = self.ai_agent.generate_with_fallback(context, 'international_analysis', max_tokens=600)
            
            if ai_result['success']:
                return {
                    'ai_international_analysis': ai_result['response'],
                    'ai_model_used': ai_result['model_used'],
                    'ai_enhanced': True,
                    'global_sentiment': self._extract_global_sentiment(ai_result['response']),
                    'vn_impact': self._extract_vn_impact(ai_result['response'])
                }
            else:
                return {'ai_enhanced': False, 'ai_error': ai_result.get('error', 'AI not available')}
                
        except Exception as e:
            return {'ai_enhanced': False, 'ai_error': str(e)}
    
    def _extract_global_sentiment(self, ai_response: str):
        """Extract global market sentiment from AI response"""
        try:
            ai_lower = ai_response.lower()
            
            # Global sentiment indicators
            positive_indicators = ['tích cực', 'positive', 'tăng trưởng', 'phục hồi', 'ổn định']
            negative_indicators = ['tiêu cực', 'negative', 'suy thoái', 'lo ngại', 'bất ổn']
            
            positive_count = sum(1 for indicator in positive_indicators if indicator in ai_lower)
            negative_count = sum(1 for indicator in negative_indicators if indicator in ai_lower)
            
            if positive_count > negative_count:
                return 'POSITIVE'
            elif negative_count > positive_count:
                return 'NEGATIVE'
            else:
                return 'NEUTRAL'
                
        except Exception:
            return 'NEUTRAL'
    
    def _extract_vn_impact(self, ai_response: str):
        """Extract impact on Vietnam market from AI response"""
        try:
            ai_lower = ai_response.lower()
            
            if any(phrase in ai_lower for phrase in ['tác động tích cực', 'positive impact', 'có lợi']):
                return 'POSITIVE_IMPACT'
            elif any(phrase in ai_lower for phrase in ['tác động tiêu cực', 'negative impact', 'bất lợi']):
                return 'NEGATIVE_IMPACT'
            elif any(phrase in ai_lower for phrase in ['ít tác động', 'limited impact', 'không đáng kể']):
                return 'LIMITED_IMPACT'
            else:
                return 'MODERATE_IMPACT'
                
        except Exception:
            return 'MODERATE_IMPACT'