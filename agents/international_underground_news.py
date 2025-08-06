import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json
import random
from typing import Dict, List, Optional

class InternationalUndergroundNewsAgent:
    def __init__(self):
        self.name = "International Underground News Agent"
        self.description = "Agent for crawling underground international financial news"
        
        # Reddit sources
        self.reddit_sources = {
            'stocks': 'https://www.reddit.com/r/stocks/',
            'investing': 'https://www.reddit.com/r/investing/',
            'financialindependence': 'https://www.reddit.com/r/financialindependence/',
            'worldnews': 'https://www.reddit.com/r/worldnews/',
            'geopolitics': 'https://www.reddit.com/r/geopolitics/'
        }
        
        # Twitter sources (Note: Twitter API requires authentication, using mock data)
        self.twitter_sources = {
            'unusual_whales': 'https://twitter.com/unusual_whales',
            'zerohedge': 'https://twitter.com/zerohedge',
            'chigrl': 'https://twitter.com/chigrl'
        }
        
        # Web sources for underground financial news
        self.web_sources = {
            'zerohedge': 'https://www.zerohedge.com/',
            'seekingalpha': 'https://seekingalpha.com/',
            'agorafinancial': 'https://agorafinancial.com/',
            'insidermonkey': 'https://www.insidermonkey.com/',
            'wolfstreet': 'https://wolfstreet.com/',
            'oilprice': 'https://oilprice.com/',
            'armstrongeconomics': 'https://www.armstrongeconomics.com/',
            'macrotrends': 'https://www.macrotrends.net/',
            'investing': 'https://www.investing.com/news/',
            'shadowstats': 'https://www.shadowstats.com/'
        }
        
        # Forum sources for underground discussions
        self.forum_sources = {
            '4chan_biz': 'https://boards.4channel.org/biz/',
            'disboard_stock': 'https://disboard.org/search?q=stock',
            'reddit_discussions': 'https://www.reddit.com/r/stocks/comments/'
        }
        
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.ai_agent = None
        
    def set_ai_agent(self, ai_agent):
        """Set AI agent for enhanced analysis"""
        self.ai_agent = ai_agent
    
    async def get_underground_news_by_risk_profile(self, risk_tolerance: int, time_horizon: str, investment_amount: int):
        """Get underground international news based on risk profile"""
        try:
            # Determine news type based on risk tolerance
            if risk_tolerance > 70:  # Mạo hiểm - Show underground + official
                news_type = 'underground_mixed'
                sources_to_crawl = ['reddit', 'twitter', 'official']
            elif risk_tolerance > 30:  # Cân bằng - Official only
                news_type = 'official_only'
                sources_to_crawl = ['official']
            else:  # Thận trọng - Official only
                news_type = 'conservative_official'
                sources_to_crawl = ['official']
            
            all_news = []
            
            # Crawl based on risk profile
            if 'reddit' in sources_to_crawl:
                reddit_news = await self._crawl_reddit_sources()
                all_news.extend(reddit_news)
            
            if 'twitter' in sources_to_crawl:
                twitter_news = await self._crawl_twitter_sources()
                all_news.extend(twitter_news)
            
            if 'official' in sources_to_crawl:
                official_news = await self._get_official_international_news()
                all_news.extend(official_news)
            
            # If no news found, use fallback
            if not all_news:
                all_news = self._get_fallback_international_news(risk_tolerance)
            
            # Sort by relevance and time
            all_news = sorted(all_news, key=lambda x: (
                x.get('priority', 0),
                x.get('timestamp', datetime.now())
            ), reverse=True)
            
            # Limit news based on risk profile
            max_news = 20 if risk_tolerance > 70 else 15 if risk_tolerance > 30 else 10
            all_news = all_news[:max_news]
            
            result = {
                'category': 'International Underground News',
                'news_type': news_type,
                'risk_profile': self._get_risk_profile_name(risk_tolerance),
                'news_count': len(all_news),
                'news': all_news,
                'source': f"Underground International ({len(all_news)} sources)",
                'crawl_summary': self._get_crawl_summary(all_news),
                'recommendation': self._get_news_recommendation(risk_tolerance, time_horizon)
            }
            
            # Add AI enhancement if available
            if self.ai_agent and all_news:
                try:
                    ai_analysis = await self._get_ai_underground_analysis(result)
                    result.update(ai_analysis)
                except Exception as e:
                    result['ai_error'] = str(e)
            
            return result
            
        except Exception as e:
            return {
                'error': f"Underground news crawling failed: {str(e)}",
                'fallback_news': self._get_fallback_international_news(risk_tolerance)
            }
    
    async def _crawl_reddit_sources(self) -> List[Dict]:
        """Crawl Reddit sources for financial discussions"""
        reddit_news = []
        
        for source_name, url in self.reddit_sources.items():
            try:
                # Add .json to get Reddit API format
                json_url = url.rstrip('/') + '.json'
                
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(json_url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            posts = data.get('data', {}).get('children', [])
                            
                            for post in posts[:5]:  # Top 5 posts per subreddit
                                post_data = post.get('data', {})
                                
                                # Filter for financial relevance
                                title = post_data.get('title', '')
                                if self._is_financially_relevant(title):
                                    reddit_news.append({
                                        'title': title,
                                        'summary': post_data.get('selftext', '')[:200] + '...' if post_data.get('selftext') else title,
                                        'source': f"Reddit r/{source_name}",
                                        'type': 'underground',
                                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                        'score': post_data.get('score', 0),
                                        'comments': post_data.get('num_comments', 0),
                                        'timestamp': datetime.fromtimestamp(post_data.get('created_utc', 0)),
                                        'priority': self._calculate_reddit_priority(post_data),
                                        'details': {
                                            'upvotes': post_data.get('ups', 0),
                                            'downvotes': post_data.get('downs', 0),
                                            'engagement': post_data.get('num_comments', 0),
                                            'subreddit': source_name,
                                            'confidence': 'Medium',
                                            'source_reliability': 'Community-driven'
                                        }
                                    })
                        
                        # Add delay to avoid rate limiting
                        await asyncio.sleep(1)
                        
            except Exception as e:
                print(f"❌ Reddit {source_name} crawling failed: {e}")
                # Add simulated Reddit news as fallback
                reddit_news.extend(self._simulate_reddit_news(source_name))
        
        return reddit_news
    
    async def _crawl_twitter_sources(self) -> List[Dict]:
        """Simulate Twitter crawling (Twitter API requires authentication)"""
        twitter_news = []
        
        # Since Twitter API requires authentication, we'll simulate the data
        # In production, you would use Twitter API v2 with proper authentication
        
        for source_name, url in self.twitter_sources.items():
            simulated_tweets = self._simulate_twitter_news(source_name)
            twitter_news.extend(simulated_tweets)
        
        return twitter_news
    
    async def _get_official_international_news(self) -> List[Dict]:
        """Get official international financial news"""
        official_news = []
        
        # Reuters Business
        try:
            reuters_news = await self._crawl_reuters_business()
            official_news.extend(reuters_news)
        except Exception as e:
            print(f"❌ Reuters crawling failed: {e}")
        
        # Bloomberg (simulated due to paywall)
        bloomberg_news = self._simulate_bloomberg_news()
        official_news.extend(bloomberg_news)
        
        return official_news
    
    async def _crawl_reuters_business(self) -> List[Dict]:
        """Crawl Reuters business news"""
        try:
            url = 'https://www.reuters.com/business/'
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        news_items = []
                        articles = soup.find_all(['article', 'div'], class_=re.compile(r'story|article|news'), limit=5)
                        
                        for article in articles:
                            try:
                                title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                                title = title_elem.get_text(strip=True) if title_elem else ''
                                
                                link_elem = article.find('a') or title_elem
                                link = link_elem.get('href', '') if link_elem else ''
                                if link and not link.startswith('http'):
                                    link = 'https://www.reuters.com' + link
                                
                                if title and len(title) > 10:
                                    news_items.append({
                                        'title': title,
                                        'summary': f"Reuters business news: {title[:100]}...",
                                        'source': 'Reuters',
                                        'type': 'official',
                                        'url': link,
                                        'timestamp': datetime.now(),
                                        'priority': 8,
                                        'details': {
                                            'credibility': 'Very High',
                                            'source_type': 'Premium Financial News'
                                        }
                                    })
                            except:
                                continue
                        
                        return news_items
        except:
            pass
        
        return self._simulate_reuters_news()
    
    def _simulate_bloomberg_news(self) -> List[Dict]:
        """Simulate Bloomberg news"""
        return [
            {
                'title': 'Global Markets Rally on Fed Policy Optimism',
                'summary': 'International markets surge as investors anticipate dovish Fed stance in upcoming meeting...',
                'source': 'Bloomberg',
                'type': 'official',
                'url': 'https://bloomberg.com',
                'timestamp': datetime.now(),
                'priority': 9,
                'details': {
                    'credibility': 'Very High',
                    'source_type': 'Premium Financial News'
                }
            }
        ]
    
    def _simulate_reuters_news(self) -> List[Dict]:
        """Simulate Reuters news"""
        return [
            {
                'title': 'Asian Markets Mixed Amid Trade Tensions',
                'summary': 'Asian equity markets show mixed performance as trade tensions continue to impact sentiment...',
                'source': 'Reuters',
                'type': 'official', 
                'url': 'https://reuters.com',
                'timestamp': datetime.now(),
                'priority': 8,
                'details': {
                    'credibility': 'Very High',
                    'source_type': 'International News Agency'
                }
            }
        ]
    
    def _simulate_reddit_news(self, source_name: str) -> List[Dict]:
        """Simulate Reddit news for fallback"""
        reddit_posts = {
            'stocks': [
                {
                    'title': 'DD: Why NVDA is still undervalued despite recent gains',
                    'summary': 'Deep dive analysis on NVIDIA fundamentals and future growth prospects...',
                    'details': {
                        'upvotes': 1250,
                        'engagement': 340,
                        'subreddit': 'stocks',
                        'confidence': 'Medium'
                    }
                }
            ],
            'investing': [
                {
                    'title': 'Market crash incoming? Analysis of current indicators',
                    'summary': 'Comprehensive analysis of market indicators suggesting potential correction...',
                    'details': {
                        'upvotes': 890,
                        'engagement': 220,
                        'subreddit': 'investing',
                        'confidence': 'Low'
                    }
                }
            ]
        }
        
        posts = reddit_posts.get(source_name, [reddit_posts['stocks'][0]])
        
        return [{
            'title': post['title'],
            'summary': post['summary'],
            'source': f"Reddit r/{source_name}",
            'type': 'underground',
            'url': f"https://reddit.com/r/{source_name}",
            'timestamp': datetime.now(),
            'priority': 5,
            'details': post['details']
        } for post in posts]
    
    def _simulate_twitter_news(self, source_name: str) -> List[Dict]:
        """Simulate Twitter news"""
        twitter_posts = {
            'unusual_whales': [
                {
                    'title': 'BREAKING: Unusual options activity detected in tech sector',
                    'summary': 'Large volume of calls spotted in major tech names, suggesting institutional positioning...',
                    'details': {
                        'engagement': '2.5K likes, 450 retweets',
                        'account_followers': '1.2M',
                        'confidence': 'High'
                    }
                }
            ],
            'zerohedge': [
                {
                    'title': 'Central Bank Digital Currencies: The End of Financial Privacy?',
                    'summary': 'Analysis of CBDC implications for global financial system and individual privacy...',
                    'details': {
                        'engagement': '5.2K likes, 1.8K retweets',
                        'account_followers': '1.8M',
                        'confidence': 'Medium'
                    }
                }
            ]
        }
        
        posts = twitter_posts.get(source_name, [twitter_posts['unusual_whales'][0]])
        
        return [{
            'title': post['title'],
            'summary': post['summary'],
            'source': f"Twitter @{source_name}",
            'type': 'underground',
            'url': f"https://twitter.com/{source_name}",
            'timestamp': datetime.now(),
            'priority': 6,
            'details': post['details']
        } for post in posts]
    
    def _is_financially_relevant(self, title: str) -> bool:
        """Check if title is financially relevant"""
        financial_keywords = [
            'stock', 'market', 'trading', 'investment', 'portfolio', 'dividend',
            'earnings', 'fed', 'inflation', 'economy', 'recession', 'bull', 'bear',
            'crypto', 'bitcoin', 'ethereum', 'options', 'futures', 'bond'
        ]
        return any(keyword in title.lower() for keyword in financial_keywords)
    
    def _calculate_reddit_priority(self, post_data: Dict) -> int:
        """Calculate priority score for Reddit posts"""
        score = post_data.get('score', 0)
        comments = post_data.get('num_comments', 0)
        
        if score > 1000 and comments > 100:
            return 9
        elif score > 500 and comments > 50:
            return 7
        elif score > 100 and comments > 20:
            return 5
        else:
            return 3
    
    def _get_risk_profile_name(self, risk_tolerance: int) -> str:
        """Get risk profile name"""
        if risk_tolerance <= 30:
            return "Conservative"
        elif risk_tolerance <= 70:
            return "Moderate"
        else:
            return "Aggressive"
    
    def _get_crawl_summary(self, all_news: List[Dict]) -> Dict:
        """Get crawl summary"""
        sources = {}
        types = {'underground': 0, 'official': 0, 'international': 0}
        
        for news in all_news:
            source = news.get('source', 'Unknown')
            news_type = news.get('type', 'unknown')
            
            sources[source] = sources.get(source, 0) + 1
            if news_type in types:
                types[news_type] += 1
        
        return {
            'total_news': len(all_news),
            'sources_count': len(sources),
            'sources': sources,
            'official_news': types['official'],
            'underground_news': types['underground']
        }
    
    def _get_news_recommendation(self, risk_tolerance: int, time_horizon: str) -> Dict:
        """Get news recommendation based on risk profile"""
        if risk_tolerance <= 30:
            return {
                'advice': 'Tập trung tin tức chính thống từ Reuters, Bloomberg, Financial Times',
                'warning': 'Tránh tin đồn từ mạng xã hội, chỉ theo dõi nguồn uy tín',
                'focus': 'Phân tích vĩ mô, chính sách Fed, báo cáo kinh tế chính thức'
            }
        elif risk_tolerance <= 70:
            return {
                'advice': 'Kết hợp tin chính thống và thông tin cộng đồng có uy tín',
                'warning': 'Xác minh thông tin từ nhiều nguồn trước khi đầu tư',
                'focus': 'Cân bằng tin tức chính thống và sentiment thị trường'
            }
        else:
            return {
                'advice': 'Sử dụng tất cả nguồn tin từ Reddit, Twitter đến tin chính thống',
                'warning': 'Luôn DYOR - thông tin mạng xã hội có thể không chính xác',
                'focus': 'Tin nóng, unusual activity, sentiment analysis, insider info'
            }
    
    async def _get_ai_underground_analysis(self, news_data: Dict) -> Dict:
        """Get AI analysis of underground news"""
        try:
            if not self.ai_agent:
                return {'ai_enhanced': False, 'ai_error': 'No AI agent available'}
            
            # Prepare context for AI analysis
            news_titles = []
            for news_item in news_data.get('news', [])[:8]:
                news_titles.append(f"- {news_item.get('title', '')}")
            
            news_context = "\n".join(news_titles)
            
            context = f"""
Phân tích tin tức tài chính quốc tế từ các nguồn underground và chính thống:

HỒ SƠ RỦI RO: {news_data.get('risk_profile', 'Unknown')}
LOẠI TIN TỨC: {news_data.get('news_type', 'Unknown')}
SỐ LƯỢNG TIN: {news_data.get('news_count', 0)}

TIN TỨC QUỐC TẾ:
{news_context}

Hãy phân tích:
1. Sentiment thị trường toàn cầu (BULLISH/BEARISH/NEUTRAL)
2. Mức độ rủi ro của thông tin (HIGH_RISK/MEDIUM_RISK/LOW_RISK)
3. Tác động đến thị trường Việt Nam
4. Khuyến nghị cho nhà đầu tư

Trả lời ngắn gọn, tập trung vào điểm quan trọng.
"""
            
            ai_result = self.ai_agent.generate_with_fallback(context, 'underground_analysis', max_tokens=500)
            
            if ai_result['success']:
                response = ai_result['response']
                return {
                    'ai_underground_analysis': response,
                    'ai_enhanced': True,
                    'ai_model_used': ai_result['model_used'],
                    'market_sentiment': self._extract_sentiment(response),
                    'risk_assessment': self._extract_risk_assessment(response)
                }
            else:
                return {'ai_enhanced': False, 'ai_error': ai_result.get('error', 'AI analysis failed')}
                
        except Exception as e:
            return {'ai_enhanced': False, 'ai_error': str(e)}
    
    def _extract_sentiment(self, ai_response: str) -> str:
        """Extract market sentiment from AI response"""
        response_lower = ai_response.lower()
        if 'bullish' in response_lower or 'tích cực' in response_lower:
            return 'BULLISH'
        elif 'bearish' in response_lower or 'tiêu cực' in response_lower:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _extract_risk_assessment(self, ai_response: str) -> str:
        """Extract risk assessment from AI response"""
        response_lower = ai_response.lower()
        if 'high_risk' in response_lower or 'rủi ro cao' in response_lower:
            return 'HIGH_RISK'
        elif 'low_risk' in response_lower or 'rủi ro thấp' in response_lower:
            return 'LOW_RISK'
        else:
            return 'MEDIUM_RISK'
    
    def _get_fallback_international_news(self, risk_tolerance: int) -> List[Dict]:
        """Get fallback international news based on risk tolerance"""
        if risk_tolerance > 70:
            # Aggressive: Include underground + official
            return self._simulate_reddit_news('stocks') + self._simulate_twitter_news('unusual_whales') + self._simulate_bloomberg_news()
        elif risk_tolerance > 30:
            # Moderate: Official only
            return self._simulate_bloomberg_news() + self._simulate_reuters_news()
        else:
            # Conservative: Conservative official only
            return self._simulate_reuters_news()
        official_news.extend(bloomberg_news)
        
        # Financial Times (simulated due to paywall)
        ft_news = self._simulate_ft_news()
        official_news.extend(ft_news)
        
        return official_news
    
    async def _crawl_reuters_business(self) -> List[Dict]:
        """Crawl Reuters business news"""
        try:
            url = "https://www.reuters.com/business/"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        news_items = []
                        
                        # Find article elements
                        articles = soup.find_all(['article', 'div'], class_=re.compile(r'(story|article|news)'))
                        
                        for article in articles[:10]:
                            try:
                                # Extract title
                                title_elem = article.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'(headline|title)'))
                                if not title_elem:
                                    title_elem = article.find('a')
                                
                                title = title_elem.get_text(strip=True) if title_elem else None
                                
                                if title and len(title) > 20:
                                    # Extract link
                                    link = title_elem.get('href', '') if title_elem.name == 'a' else ''
                                    if link and not link.startswith('http'):
                                        link = 'https://www.reuters.com' + link
                                    
                                    # Extract summary
                                    summary_elem = article.find(['p', 'div'], class_=re.compile(r'(summary|description)'))
                                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title[:100] + '...'
                                    
                                    news_items.append({
                                        'title': title,
                                        'summary': summary,
                                        'source': 'Reuters Business',
                                        'type': 'official',
                                        'url': link,
                                        'timestamp': datetime.now(),
                                        'priority': 3,  # High priority for Reuters
                                        'details': {
                                            'credibility': 'Very High',
                                            'source_type': 'Major News Agency',
                                            'confidence': 'High'
                                        }
                                    })
                            except Exception:
                                continue
                        
                        return news_items
                        
        except Exception as e:
            print(f"❌ Reuters crawling failed: {e}")
            return []
    
    def _simulate_reddit_news(self, subreddit: str) -> List[Dict]:
        """Simulate Reddit news for fallback"""
        reddit_templates = {
            'stocks': [
                "🚀 TSLA breaking out after earnings beat - technical analysis inside",
                "📊 Market rotation into value stocks - what are your plays?",
                "⚠️ Fed meeting next week - how are you positioning?",
                "💎 Hidden gem found in small cap biotech sector",
                "📈 SPY hitting resistance - time to take profits?"
            ],
            'investing': [
                "🏦 Best dividend stocks for 2024 - comprehensive analysis",
                "📊 Portfolio rebalancing strategy in current market",
                "💰 Dollar cost averaging vs lump sum - which is better?",
                "🌍 International diversification - emerging markets outlook",
                "📈 REITs vs stocks in inflationary environment"
            ],
            'worldnews': [
                "🌍 China's economic data shows mixed signals for global markets",
                "⚡ Energy crisis in Europe affecting commodity prices",
                "🏛️ Central bank policies diverging across major economies",
                "🛢️ OPEC+ production cuts impact on oil markets",
                "💱 Currency wars heating up as dollar strengthens"
            ],
            'geopolitics': [
                "🌏 Trade tensions escalating between major economies",
                "🛡️ Defense spending increases affecting aerospace stocks",
                "🌊 Supply chain disruptions in key shipping routes",
                "⚖️ Regulatory changes in tech sector across regions",
                "🏭 Manufacturing shifts impacting global trade flows"
            ]
        }
        
        templates = reddit_templates.get(subreddit, reddit_templates['stocks'])
        news_items = []
        
        for i, template in enumerate(templates):
            news_items.append({
                'title': template,
                'summary': f"Community discussion about {template.lower()}. Multiple perspectives and analysis from retail investors.",
                'source': f"Reddit r/{subreddit}",
                'type': 'underground',
                'url': f"https://reddit.com/r/{subreddit}/post_{i+1}",
                'score': random.randint(50, 500),
                'comments': random.randint(20, 200),
                'timestamp': datetime.now() - timedelta(hours=random.randint(1, 24)),
                'priority': 2,
                'details': {
                    'upvotes': random.randint(100, 1000),
                    'engagement': random.randint(50, 300),
                    'subreddit': subreddit,
                    'confidence': 'Medium',
                    'source_reliability': 'Community-driven'
                }
            })
        
        return news_items
    
    def _simulate_twitter_news(self, account: str) -> List[Dict]:
        """Simulate Twitter news for different accounts"""
        twitter_templates = {
            'unusual_whales': [
                "🐋 Massive options flow detected in $SPY - someone knows something",
                "📊 Dark pool activity spiking in tech names",
                "⚡ Unusual volume in $NVDA ahead of earnings",
                "🎯 Smart money moving into defensive sectors",
                "📈 Institutional buying pressure in small caps"
            ],
            'zerohedge': [
                "🚨 BREAKING: Central bank intervention rumors circulating",
                "⚠️ Credit markets showing stress signals",
                "💥 Derivative markets flashing warning signs",
                "🔥 Liquidity crisis brewing in bond markets",
                "⚡ Systemic risk indicators reaching critical levels"
            ],
            'chigrl': [
                "📊 Technical analysis: Major support level being tested",
                "🎯 Key resistance levels to watch this week",
                "📈 Momentum indicators showing divergence",
                "⚡ Breakout patterns forming in sector rotation",
                "🔍 Volume analysis revealing institutional activity"
            ]
        }
        
        templates = twitter_templates.get(account, twitter_templates['unusual_whales'])
        news_items = []
        
        for i, template in enumerate(templates):
            news_items.append({
                'title': template,
                'summary': f"Market insight from @{account}: {template}",
                'source': f"Twitter @{account}",
                'type': 'underground',
                'url': f"https://twitter.com/{account}/status/{random.randint(1000000000000000000, 9999999999999999999)}",
                'retweets': random.randint(10, 500),
                'likes': random.randint(50, 2000),
                'timestamp': datetime.now() - timedelta(minutes=random.randint(30, 1440)),
                'priority': 2,
                'details': {
                    'engagement': random.randint(100, 1000),
                    'account_followers': '100K+' if account == 'unusual_whales' else '500K+' if account == 'zerohedge' else '50K+',
                    'confidence': 'High' if account == 'zerohedge' else 'Medium',
                    'source_reliability': 'Specialized Financial Account'
                }
            })
        
        return news_items
    
    def _simulate_bloomberg_news(self) -> List[Dict]:
        """Simulate Bloomberg news"""
        bloomberg_templates = [
            "📊 Global markets face headwinds as central banks diverge",
            "💰 Corporate earnings season reveals mixed signals",
            "🏦 Banking sector stress tests show resilience",
            "🌍 Emerging markets capital flows turning positive",
            "⚡ Energy transition investments reach record highs"
        ]
        
        news_items = []
        for i, template in enumerate(bloomberg_templates):
            news_items.append({
                'title': template,
                'summary': f"Bloomberg analysis: {template}. Detailed market implications and expert commentary.",
                'source': 'Bloomberg',
                'type': 'official',
                'url': f"https://bloomberg.com/news/article_{i+1}",
                'timestamp': datetime.now() - timedelta(hours=random.randint(1, 12)),
                'priority': 3,
                'details': {
                    'credibility': 'Very High',
                    'source_type': 'Premium Financial News',
                    'confidence': 'Very High'
                }
            })
        
        return news_items
    
    def _simulate_ft_news(self) -> List[Dict]:
        """Simulate Financial Times news"""
        ft_templates = [
            "🏛️ Central bank policy divergence creates market volatility",
            "📈 Private equity deals surge despite economic uncertainty",
            "🌍 Geopolitical tensions impact global supply chains",
            "💱 Currency markets react to inflation data releases",
            "🏭 Manufacturing PMI data shows economic resilience"
        ]
        
        news_items = []
        for i, template in enumerate(ft_templates):
            news_items.append({
                'title': template,
                'summary': f"Financial Times report: {template}. In-depth analysis of market implications.",
                'source': 'Financial Times',
                'type': 'official',
                'url': f"https://ft.com/content/article_{i+1}",
                'timestamp': datetime.now() - timedelta(hours=random.randint(2, 18)),
                'priority': 3,
                'details': {
                    'credibility': 'Very High',
                    'source_type': 'Premium Financial News',
                    'confidence': 'Very High'
                }
            })
        
        return news_items
    
    def _is_financially_relevant(self, title: str) -> bool:
        """Check if title is financially relevant"""
        financial_keywords = [
            'stock', 'market', 'trading', 'investment', 'portfolio', 'dividend',
            'earnings', 'fed', 'inflation', 'economy', 'recession', 'bull', 'bear',
            'crypto', 'bitcoin', 'options', 'futures', 'bond', 'yield', 'rate',
            'gdp', 'unemployment', 'retail', 'consumer', 'spending', 'debt'
        ]
        
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in financial_keywords)
    
    def _calculate_reddit_priority(self, post_data: Dict) -> int:
        """Calculate priority score for Reddit posts"""
        score = post_data.get('score', 0)
        comments = post_data.get('num_comments', 0)
        
        # Higher score and comments = higher priority
        if score > 1000 or comments > 100:
            return 3
        elif score > 100 or comments > 20:
            return 2
        else:
            return 1
    
    def _get_risk_profile_name(self, risk_tolerance: int) -> str:
        """Get risk profile name"""
        if risk_tolerance <= 30:
            return "Thận trọng"
        elif risk_tolerance <= 70:
            return "Cân bằng"
        else:
            return "Mạo hiểm"
    
    def _get_crawl_summary(self, all_news: List[Dict]) -> Dict:
        """Get summary of crawled news"""
        sources = {}
        types = {'official': 0, 'underground': 0}
        
        for news in all_news:
            source = news.get('source', 'Unknown')
            news_type = news.get('type', 'official')
            
            sources[source] = sources.get(source, 0) + 1
            types[news_type] = types.get(news_type, 0) + 1
        
        return {
            'total_news': len(all_news),
            'sources_count': len(sources),
            'sources': sources,
            'official_news': types['official'],
            'underground_news': types['underground']
        }
    
    def _get_news_recommendation(self, risk_tolerance: int, time_horizon: str) -> Dict:
        """Get personalized news reading recommendations"""
        if risk_tolerance > 70:
            return {
                'advice': 'Bạn có thể đọc cả tin chính thống và tin ngầm để có cái nhìn toàn diện về thị trường.',
                'warning': 'Luôn xác minh thông tin từ nhiều nguồn trước khi đưa ra quyết định đầu tư.',
                'focus': 'Tập trung vào tin tức có độ tin cậy cao và phân tích kỹ thuật chuyên sâu.'
            }
        elif risk_tolerance > 30:
            return {
                'advice': 'Nên tập trung vào tin tức chính thống từ các nguồn uy tín.',
                'warning': 'Tránh các tin đồn thất thiệt và thông tin chưa được xác minh.',
                'focus': 'Chú ý đến phân tích cơ bản và xu hướng dài hạn của thị trường.'
            }
        else:
            return {
                'advice': 'Chỉ nên đọc tin tức chính thống từ các tổ chức tài chính uy tín.',
                'warning': 'Tránh hoàn toàn các tin tức ngầm và thông tin không được xác minh.',
                'focus': 'Tập trung vào phân tích dài hạn và các chỉ số kinh tế vĩ mô.'
            }
    
    def _get_fallback_international_news(self, risk_tolerance: int) -> List[Dict]:
        """Get fallback news when crawling fails"""
        if risk_tolerance > 70:
            # Mix of official and underground
            return (self._simulate_bloomberg_news()[:3] + 
                   self._simulate_reddit_news('stocks')[:2] + 
                   self._simulate_twitter_news('zerohedge')[:2])
        else:
            # Official only
            return (self._simulate_bloomberg_news()[:3] + 
                   self._simulate_ft_news()[:2])
    
    async def _get_ai_underground_analysis(self, news_data: Dict) -> Dict:
        """Get AI analysis of underground news"""
        try:
            news_titles = []
            underground_count = 0
            official_count = 0
            
            for news in news_data.get('news', []):
                news_titles.append(f"- {news.get('title', '')}")
                if news.get('type') == 'underground':
                    underground_count += 1
                else:
                    official_count += 1
            
            context = f"""
Phân tích tin tức tài chính quốc tế ngầm và chính thống:

THÔNG TIN TỔNG QUAN:
- Hồ sơ rủi ro: {news_data.get('risk_profile', 'N/A')}
- Loại tin tức: {news_data.get('news_type', 'N/A')}
- Tổng số tin: {news_data.get('news_count', 0)}
- Tin chính thống: {official_count}
- Tin ngầm: {underground_count}

TIN TỨC QUỐC TẾ:
{chr(10).join(news_titles[:10])}

Hãy phân tích:
1. Xu hướng thị trường tài chính toàn cầu từ các nguồn tin
2. Độ tin cậy của thông tin ngầm vs chính thống
3. Tác động tiềm tàng đến thị trường Việt Nam
4. Cảnh báo rủi ro từ thông tin chưa được xác minh
5. Khuyến nghị cho nhà đầu tư theo hồ sơ rủi ro

Trả lời ngắn gọn, tập trung vào những điểm quan trọng nhất.
"""
            
            ai_result = self.ai_agent.generate_with_fallback(context, 'underground_analysis', max_tokens=800)
            
            if ai_result['success']:
                return {
                    'ai_underground_analysis': ai_result['response'],
                    'ai_model_used': ai_result['model_used'],
                    'ai_enhanced': True,
                    'market_sentiment': self._extract_market_sentiment(ai_result['response']),
                    'risk_assessment': self._extract_risk_assessment(ai_result['response'])
                }
            else:
                return {'ai_enhanced': False, 'ai_error': ai_result.get('error', 'AI not available')}
                
        except Exception as e:
            return {'ai_enhanced': False, 'ai_error': str(e)}
    
    def _extract_market_sentiment(self, ai_response: str) -> str:
        """Extract market sentiment from AI response"""
        try:
            ai_lower = ai_response.lower()
            
            positive_indicators = ['tích cực', 'positive', 'tăng', 'bull', 'optimistic']
            negative_indicators = ['tiêu cực', 'negative', 'giảm', 'bear', 'pessimistic']
            
            positive_count = sum(1 for indicator in positive_indicators if indicator in ai_lower)
            negative_count = sum(1 for indicator in negative_indicators if indicator in ai_lower)
            
            if positive_count > negative_count:
                return 'BULLISH'
            elif negative_count > positive_count:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception:
            return 'NEUTRAL'
    
    def _extract_risk_assessment(self, ai_response: str) -> str:
        """Extract risk assessment from AI response"""
        try:
            ai_lower = ai_response.lower()
            
            if any(phrase in ai_lower for phrase in ['rủi ro cao', 'high risk', 'nguy hiểm']):
                return 'HIGH_RISK'
            elif any(phrase in ai_lower for phrase in ['rủi ro thấp', 'low risk', 'an toàn']):
                return 'LOW_RISK'
            else:
                return 'MODERATE_RISK'
                
        except Exception:
            return 'MODERATE_RISK'