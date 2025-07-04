# src/agents/market_analyst.py
"""
Market Analyst Agent - Nguyễn Minh Anh
Chuyên gia phân tích kỹ thuật và cơ bản cho thị trường chứng khoán Việt Nam
"""

from datetime import datetime
from typing import List, Dict, Any
import logging

from .base_agent import BaseAgent, AgentPersonality, MarketContext, AgentResponse

logger = logging.getLogger(__name__)

class MarketAnalystAgent(BaseAgent):
    """
    Nguyễn Minh Anh - Senior Market Analyst
    Chuyên về technical analysis và market sentiment
    """
    
    def __init__(self, api_key: str):
        # Định nghĩa personality của Minh Anh
        personality = AgentPersonality(
            name="Nguyễn Minh Anh",
            role="Senior Market Analyst",
            experience="8 năm kinh nghiệm tại VPS Securities và SSI",
            personality_traits=[
                "Tỉ mỉ với data",
                "Thích phân tích charts",
                "Hay quote Warren Buffett",
                "Technical-focused",
                "Objective và data-driven"
            ],
            speaking_style="""
Nói chuyện chuyên nghiệp nhưng friendly. Hay sử dụng:
- "Theo technical analysis thì..."
- "Data cho thấy..."
- "Chart pattern suggest..."
- "Warren Buffett từng nói..."
- Cite specific numbers và indicators
""",
            background="""
Tốt nghiệp CFA Institute, làm việc 5 năm tại VPS rồi chuyển sang SSI. 
Chuyên phân tích bluechips Việt Nam và tracking foreign flows.
Có track record tốt trong việc predict market corrections và rallies.
Strong background về technical analysis và quantitative methods.
""",
            strengths=[
                "Technical analysis với RSI, MACD, Bollinger Bands",
                "Pattern recognition (cup & handle, triangles, etc)",
                "Volume analysis và money flow",
                "Foreign investor behavior tracking",
                "Sector rotation analysis",
                "VN-Index momentum prediction"
            ],
            weaknesses=[
                "Đôi khi quá focus vào short-term patterns",
                "Có thể miss big picture macro trends",
                "Over-analyze khi market flat"
            ]
        )
        
        super().__init__(api_key, personality)
        
        # Specific knowledge cho market analyst
        self.technical_indicators = [
            "RSI", "MACD", "Bollinger Bands", "Moving Averages",
            "Stochastic", "Williams %R", "Volume Profile"
        ]
        
        self.vn_market_knowledge = {
            "trading_hours": "9:00-15:00",
            "major_indices": ["VN-Index", "HNX-Index", "VN30"],
            "bluechips": ["VCB", "VIC", "VHM", "MSN", "MWG", "FPT", "HPG"],
            "sectors": ["Banking", "Real Estate", "Consumer", "Industrial", "Tech"],
            "foreign_limits": "49% for most stocks, 30% for banks"
        }
    
    async def analyze(self, context: MarketContext, team_discussion: List[str] = None) -> AgentResponse:
        """
        Phân tích technical và fundamental cho stock
        
        Args:
            context: Market context với stock data
            team_discussion: Previous team discussion
            
        Returns:
            AgentResponse: Technical analysis và recommendation
        """
        try:
            # Tạo analysis prompt
            analysis_prompt = self._create_analysis_prompt(context, team_discussion)
            
            # Generate analysis từ AI
            analysis_text = await self.generate_response(analysis_prompt, context)
            
            # Parse recommendation từ analysis
            recommendation = self._extract_recommendation(analysis_text)
            confidence = self._calculate_confidence(context, analysis_text)
            
            # Extract key points và concerns
            key_points = self._extract_key_points(analysis_text)
            concerns = self._extract_concerns(analysis_text)
            
            return AgentResponse(
                agent_name=self.personality.name,
                confidence_level=confidence,
                recommendation=recommendation,
                reasoning=analysis_text,
                key_points=key_points,
                concerns=concerns,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Error in market analysis: {e}")
            return self._create_error_response()
    
    def _create_analysis_prompt(self, context: MarketContext, team_discussion: List[str] = None) -> str:
        """Tạo prompt cho technical analysis"""
        
        prompt = f"""
Hãy phân tích cổ phiếu {context.symbol} với vai trò Senior Market Analyst.

NHIỆM VỤ CHÍNH:
1. Technical Analysis với indicators phổ biến
2. Đánh giá momentum và trend direction
3. Volume analysis và liquidity assessment
4. So sánh với VN-Index và sector performance
5. Foreign investor behavior nếu có data

THÔNG TIN HIỆN TẠI:
- Giá: {context.current_price:,.0f} VND
- Volume: {context.volume:,.0f}
- P/E: {context.pe_ratio if context.pe_ratio else 'N/A'}
- P/B: {context.pb_ratio if context.pb_ratio else 'N/A'}
- Ngành: {context.sector}

"""
        
        if team_discussion:
            prompt += f"""
THẢO LUẬN TEAM TRƯỚC ĐÓ:
{' | '.join(team_discussion[-3:])}  # Chỉ lấy 3 comments gần nhất

Hãy respond dựa trên discussion context này.
"""
        
        prompt += """
YÊU CẦU PHÂN TÍCH:

1. TECHNICAL SETUP:
   - Chart pattern hiện tại (nếu có)
   - Key support/resistance levels
   - RSI và momentum indicators
   - Volume trend và accumulation/distribution

2. MARKET POSITION:
   - So sánh performance vs VN-Index
   - Sector strength/weakness
   - Relative performance vs peers

3. RECOMMENDATION:
   - BUY/SELL/HOLD với confidence level
   - Entry/exit points cụ thể
   - Time horizon (short-term/medium-term)

4. RISK FACTORS:
   - Key risks cần watch out
   - What could invalidate thesis

Trả lời bằng tiếng Việt, professional nhưng accessible. 
Cite specific levels và indicators khi possible.
"""
        
        return prompt
    
    def _extract_recommendation(self, analysis_text: str) -> str:
        """Extract recommendation từ analysis text"""
        text_upper = analysis_text.upper()
        
        if any(word in text_upper for word in ["MUA", "BUY", "TÍCH CỰC", "KHUYẾN MẠI"]):
            return "BUY"
        elif any(word in text_upper for word in ["BÁN", "SELL", "THOÁT", "GIẢM"]):
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_confidence(self, context: MarketContext, analysis_text: str) -> int:
        """Calculate confidence level 1-10 based on analysis"""
        confidence = 5  # Base confidence
        
        # Tăng confidence nếu có strong signals
        if context.pe_ratio and context.pe_ratio < 15:
            confidence += 1
        if context.volume > 1000000:  # High volume
            confidence += 1
        if "breakthrough" in analysis_text.lower() or "breakout" in analysis_text.lower():
            confidence += 1
        if "strong support" in analysis_text.lower():
            confidence += 1
            
        # Giảm confidence nếu có risk factors
        if "uncertain" in analysis_text.lower() or "không chắc" in analysis_text.lower():
            confidence -= 1
        if context.market_trend == "Bearish":
            confidence -= 1
        if context.news_sentiment == "Negative":
            confidence -= 1
            
        return max(1, min(10, confidence))
    
    def _extract_key_points(self, analysis_text: str) -> List[str]:
        """Extract key investment points"""
        # Simple extraction - trong production sẽ dùng NLP
        key_phrases = [
            "technical breakout", "strong support", "high volume",
            "oversold condition", "bullish pattern", "resistance level",
            "vượt kháng cự", "hỗ trợ mạnh", "tăng đột biến volume"
        ]
        
        points = []
        for phrase in key_phrases:
            if phrase.lower() in analysis_text.lower():
                points.append(phrase.title())
        
        # Fallback nếu không tìm thấy
        if not points:
            points = ["Technical analysis complete", "Market position assessed"]
            
        return points[:5]  # Max 5 points
    
    def _extract_concerns(self, analysis_text: str) -> List[str]:
        """Extract risk concerns"""
        risk_phrases = [
            "risk", "uncertain", "volatile", "resistance",
            "rủi ro", "không chắc chắn", "biến động", "kháng cự"
        ]
        
        concerns = []
        for phrase in risk_phrases:
            if phrase.lower() in analysis_text.lower():
                concerns.append(f"Monitor {phrase}")
        
        # Default concerns
        if not concerns:
            concerns = ["Market volatility", "Technical levels"]
            
        return concerns[:3]  # Max 3 concerns
    
    def _create_error_response(self) -> AgentResponse:
        """Create error response when analysis fails"""
        return AgentResponse(
            agent_name=self.personality.name,
            confidence_level=1,
            recommendation="HOLD",
            reasoning="Xin lỗi, tôi đang gặp vấn đề kỹ thuật trong việc phân tích. Khuyến nghị HOLD cho đến khi có thêm thông tin.",
            key_points=["Technical analysis pending"],
            concerns=["System error", "Incomplete data"],
            timestamp=datetime.now()
        )
    
    async def analyze_market_sentiment(self, market_data: Dict[str, Any]) -> str:
        """
        Phân tích sentiment tổng quan thị trường
        
        Args:
            market_data: VN-Index, volume, foreign flows data
            
        Returns:
            str: Market sentiment analysis
        """
        prompt = f"""
Với vai trò Market Analyst, hãy phân tích sentiment thị trường Việt Nam hiện tại:

VN-INDEX DATA:
- Điểm số hiện tại: {market_data.get('vn_index', 'N/A')}
- Volume giao dịch: {market_data.get('total_volume', 'N/A')}
- Foreign flows: {market_data.get('foreign_flows', 'N/A')}
- Top gainers/losers: {market_data.get('top_movers', 'N/A')}

Đưa ra market sentiment: Bullish/Bearish/Neutral với reasoning.
"""
        
        try:
            sentiment_analysis = await self.generate_response(prompt)
            return sentiment_analysis
        except Exception as e:
            logger.error(f"❌ Error in sentiment analysis: {e}")
            return "Market sentiment analysis temporarily unavailable."

    def get_technical_levels(self, symbol: str, price_data: List[float]) -> Dict[str, float]:
        """
        Tính toán technical levels cho stock
        
        Args:
            symbol: Stock symbol
            price_data: List of recent prices
            
        Returns:
            Dict: Support/resistance levels
        """
        if not price_data or len(price_data) < 20:
            return {"support": 0, "resistance": 0, "sma_20": 0}
        
        try:
            current_price = price_data[-1]
            sma_20 = sum(price_data[-20:]) / 20
            
            # Simple support/resistance calculation
            recent_high = max(price_data[-10:])
            recent_low = min(price_data[-10:])
            
            return {
                "support": recent_low,
                "resistance": recent_high,
                "sma_20": sma_20,
                "current": current_price
            }
        except Exception as e:
            logger.error(f"❌ Error calculating technical levels: {e}")
            return {"support": 0, "resistance": 0, "sma_20": 0}