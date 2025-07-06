# agents/enhanced_news_agent.py
"""
Enhanced News Agent with CrewAI Integration
Kết hợp CrewAI để lấy tin tức thật từ các nguồn Việt Nam
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

try:
    from src.data.crewai_collector import get_crewai_collector
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedNewsAgent:
    """Enhanced news agent with CrewAI real news collection"""
    
    def __init__(self, gemini_api_key: str = None, serper_api_key: str = None):
        self.name = "Enhanced News Agent"
        self.description = "Collects real news using CrewAI + fallback methods"
        
        # Initialize CrewAI collector
        if CREWAI_AVAILABLE and gemini_api_key:
            self.crewai_collector = get_crewai_collector(gemini_api_key, serper_api_key)
            self.enhanced_mode = self.crewai_collector.enabled
        else:
            self.crewai_collector = None
            self.enhanced_mode = False
        
        logger.info(f"Enhanced News Agent initialized - Enhanced mode: {self.enhanced_mode}")
    
    async def get_stock_news(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock news"""
        try:
            if self.enhanced_mode:
                # Use CrewAI for real news
                logger.info(f"🤖 Getting real news for {symbol} via CrewAI")
                crewai_news = await self.crewai_collector.get_stock_news(symbol, limit=5)
                
                # Enhance with additional analysis
                enhanced_news = self._enhance_news_analysis(crewai_news, symbol)
                return enhanced_news
            else:
                # Fallback to enhanced mock news
                logger.info(f"📰 Using enhanced mock news for {symbol}")
                return self._get_enhanced_mock_news(symbol)
                
        except Exception as e:
            logger.error(f"❌ Error in enhanced news collection for {symbol}: {e}")
            return self._get_enhanced_mock_news(symbol)
    
    async def get_market_news(self) -> Dict[str, Any]:
        """Get comprehensive market news"""
        try:
            if self.enhanced_mode:
                # Use CrewAI for real market news
                logger.info("🤖 Getting real market news via CrewAI")
                crewai_market = await self.crewai_collector.get_market_overview_news()
                
                # Enhance with market analysis
                enhanced_market = self._enhance_market_analysis(crewai_market)
                return enhanced_market
            else:
                # Fallback to enhanced mock market news
                logger.info("📰 Using enhanced mock market news")
                return self._get_enhanced_mock_market()
                
        except Exception as e:
            logger.error(f"❌ Error in enhanced market news collection: {e}")
            return self._get_enhanced_mock_market()
    
    def _enhance_news_analysis(self, news_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Enhance CrewAI news with additional analysis"""
        try:
            # Add technical sentiment scoring
            sentiment_score = news_data.get('sentiment_score', 0.5)
            
            # Categorize impact level
            if sentiment_score >= 0.7:
                impact_level = "High Positive"
                recommendation = "Consider buying on positive sentiment"
            elif sentiment_score >= 0.6:
                impact_level = "Moderate Positive"  
                recommendation = "Monitor for entry opportunities"
            elif sentiment_score <= 0.3:
                impact_level = "High Negative"
                recommendation = "Consider risk management"
            elif sentiment_score <= 0.4:
                impact_level = "Moderate Negative"
                recommendation = "Exercise caution"
            else:
                impact_level = "Neutral"
                recommendation = "No significant sentiment impact"
            
            # Enhanced analysis
            enhanced_data = {
                **news_data,
                "analysis": {
                    "impact_level": impact_level,
                    "recommendation": recommendation,
                    "confidence": min(0.9, sentiment_score + 0.2),
                    "key_factors": self._extract_key_factors(news_data.get('headlines', [])),
                    "risk_factors": self._extract_risk_factors(news_data.get('summaries', []))
                },
                "enhanced_by": "CrewAI + Enhanced Analysis",
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing news analysis: {e}")
            return news_data
    
    def _enhance_market_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance CrewAI market news with additional analysis"""
        try:
            # Add market sentiment indicators
            overview = market_data.get('overview', '')
            
            # Simple sentiment analysis on overview text
            positive_words = ['tăng', 'tích cực', 'khả quan', 'tốt', 'mạnh', 'phục hồi']
            negative_words = ['giảm', 'tiêu cực', 'lo ngại', 'xấu', 'yếu', 'suy giảm']
            
            positive_count = sum(1 for word in positive_words if word in overview.lower())
            negative_count = sum(1 for word in negative_words if word in overview.lower())
            
            if positive_count > negative_count:
                market_sentiment = "Bullish"
                sentiment_score = 0.6 + (positive_count - negative_count) * 0.1
            elif negative_count > positive_count:
                market_sentiment = "Bearish"
                sentiment_score = 0.4 - (negative_count - positive_count) * 0.1
            else:
                market_sentiment = "Neutral"
                sentiment_score = 0.5
            
            # Enhanced market data
            enhanced_data = {
                **market_data,
                "market_analysis": {
                    "sentiment": market_sentiment,
                    "sentiment_score": max(0.1, min(0.9, sentiment_score)),
                    "key_themes": self._extract_market_themes(overview),
                    "trading_recommendation": self._get_trading_recommendation(market_sentiment),
                    "risk_level": self._assess_market_risk(market_sentiment, sentiment_score)
                },
                "enhanced_by": "CrewAI + Market Analysis",
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing market analysis: {e}")
            return market_data
    
    def _extract_key_factors(self, headlines: List[str]) -> List[str]:
        """Extract key factors from headlines"""
        key_factors = []
        
        factor_keywords = {
            "Earnings": ["lãi", "lợi nhuận", "doanh thu", "kết quả kinh doanh"],
            "Expansion": ["mở rộng", "đầu tư", "dự án", "phát triển"],
            "Partnership": ["hợp tác", "liên kết", "thỏa thuận", "ký kết"],
            "Regulation": ["chính sách", "quy định", "luật", "nghị định"],
            "Market": ["thị trường", "cạnh tranh", "ngành", "lĩnh vực"]
        }
        
        for headline in headlines:
            headline_lower = headline.lower()
            for factor, keywords in factor_keywords.items():
                if any(keyword in headline_lower for keyword in keywords):
                    if factor not in key_factors:
                        key_factors.append(factor)
        
        return key_factors[:3]  # Top 3 factors
    
    def _extract_risk_factors(self, summaries: List[str]) -> List[str]:
        """Extract risk factors from summaries"""
        risk_factors = []
        
        risk_keywords = {
            "Market Risk": ["cạnh tranh", "thị trường khó khăn", "suy thoái"],
            "Operational Risk": ["sản xuất", "vận hành", "chi phí tăng"],
            "Financial Risk": ["nợ", "thanh khoản", "tài chính"],
            "Regulatory Risk": ["chính sách", "quy định mới", "thuế"],
            "External Risk": ["kinh tế", "chính trị", "dịch bệnh"]
        }
        
        for summary in summaries:
            summary_lower = summary.lower()
            for risk, keywords in risk_keywords.items():
                if any(keyword in summary_lower for keyword in keywords):
                    if risk not in risk_factors:
                        risk_factors.append(risk)
        
        return risk_factors[:3]  # Top 3 risks
    
    def _extract_market_themes(self, overview: str) -> List[str]:
        """Extract key market themes"""
        themes = []
        
        theme_keywords = {
            "Banking Sector": ["ngân hàng", "tín dụng", "lãi suất"],
            "Real Estate": ["bất động sản", "nhà đất", "xây dựng"],
            "Technology": ["công nghệ", "số hóa", "fintech"],
            "Manufacturing": ["sản xuất", "công nghiệp", "xuất khẩu"],
            "Consumer": ["tiêu dùng", "bán lẻ", "thương mại"]
        }
        
        overview_lower = overview.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in overview_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]  # Top 3 themes
    
    def _get_trading_recommendation(self, sentiment: str) -> str:
        """Get trading recommendation based on sentiment"""
        recommendations = {
            "Bullish": "Consider increasing equity exposure, focus on growth stocks",
            "Bearish": "Consider defensive positioning, reduce risk exposure", 
            "Neutral": "Maintain balanced portfolio, wait for clearer signals"
        }
        return recommendations.get(sentiment, "Monitor market developments")
    
    def _assess_market_risk(self, sentiment: str, sentiment_score: float) -> str:
        """Assess overall market risk level"""
        if sentiment == "Bearish" or sentiment_score < 0.3:
            return "High"
        elif sentiment == "Bullish" and sentiment_score > 0.7:
            return "Low"
        else:
            return "Medium"
    
    def _get_enhanced_mock_news(self, symbol: str) -> Dict[str, Any]:
        """Enhanced mock news with better structure"""
        import random
        
        # More realistic mock data
        mock_scenarios = {
            'VCB': {
                'sentiment': 'Positive',
                'headlines': ['VCB báo lãi quý 4 tăng 15% so với cùng kỳ', 'Vietcombank mở rộng mạng lưới chi nhánh'],
                'impact_level': 'Moderate Positive'
            },
            'FPT': {
                'sentiment': 'Positive', 
                'headlines': ['FPT ký hợp đồng AI trị giá 50 triệu USD', 'Doanh thu công nghệ FPT tăng trưởng mạnh'],
                'impact_level': 'High Positive'
            },
            'HPG': {
                'sentiment': 'Neutral',
                'headlines': ['HPG công bố kế hoạch sản xuất 2024', 'Giá thép trong nước ổn định'],
                'impact_level': 'Neutral'
            }
        }
        
        scenario = mock_scenarios.get(symbol, {
            'sentiment': random.choice(['Positive', 'Negative', 'Neutral']),
            'headlines': [f'{symbol} có diễn biến mới trên thị trường'],
            'impact_level': 'Neutral'
        })
        
        return {
            'symbol': symbol,
            'sentiment': scenario['sentiment'],
            'sentiment_score': random.uniform(0.4, 0.8),
            'headlines': scenario['headlines'],
            'summaries': [f"Phân tích chi tiết về {headline}" for headline in scenario['headlines']],
            'news_count': len(scenario['headlines']),
            'analysis': {
                'impact_level': scenario['impact_level'],
                'recommendation': f"Theo dõi diễn biến {symbol}",
                'confidence': 0.6,
                'key_factors': ['Market', 'Earnings'],
                'risk_factors': ['Market Risk']
            },
            'source': 'Enhanced Mock',
            'enhanced_by': 'Enhanced Mock Analysis',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_enhanced_mock_market(self) -> Dict[str, Any]:
        """Enhanced mock market news"""
        return {
            'overview': 'Thị trường chứng khoán Việt Nam giao dịch tích cực với thanh khoản cải thiện. '
                       'VN-Index dao động quanh vùng kháng cự, nhóm ngân hàng dẫn dắt thị trường.',
            'key_points': [
                'VN-Index tăng nhẹ 0.5% trong phiên',
                'Thanh khoản cải thiện đáng kể',
                'Khối ngoại mua ròng 100 tỷ đồng',
                'Nhóm ngân hàng và công nghệ tích cực'
            ],
            'market_analysis': {
                'sentiment': 'Bullish',
                'sentiment_score': 0.65,
                'key_themes': ['Banking Sector', 'Technology'],
                'trading_recommendation': 'Consider increasing equity exposure, focus on growth stocks',
                'risk_level': 'Medium'
            },
            'source': 'Enhanced Mock',
            'enhanced_by': 'Enhanced Mock Market Analysis',
            'timestamp': datetime.now().isoformat()
        }

# Factory function
def create_enhanced_news_agent(gemini_api_key: str = None, serper_api_key: str = None) -> EnhancedNewsAgent:
    """Create enhanced news agent instance"""
    return EnhancedNewsAgent(gemini_api_key, serper_api_key)