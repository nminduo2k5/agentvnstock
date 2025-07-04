# src/agents/base_agent.py
"""
Base Agent Class cho AI Trading Team Vietnam
Định nghĩa interface chung cho tất cả agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentPersonality:
    """Định nghĩa tính cách của agent"""
    name: str
    role: str
    experience: str
    personality_traits: List[str]
    speaking_style: str
    background: str
    strengths: List[str]
    weaknesses: List[str]

@dataclass
class MarketContext:
    """Context thị trường hiện tại"""
    symbol: str
    current_price: float
    market_cap: float
    volume: float
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    sector: str
    market_trend: str
    news_sentiment: str

@dataclass
class AgentResponse:
    """Response từ agent"""
    agent_name: str
    confidence_level: int  # 1-10
    recommendation: str    # "BUY", "SELL", "HOLD"
    reasoning: str
    key_points: List[str]
    concerns: List[str]
    timestamp: datetime

class BaseAgent(ABC):
    """
    Base class cho tất cả trading agents
    Cung cấp common functionality và interface
    """
    
    def __init__(self, api_key: str, personality: AgentPersonality):
        """
        Khởi tạo base agent
        
        Args:
            api_key: Google GenAI API key
            personality: Agent personality configuration
        """
        self.api_key = api_key
        self.personality = personality
        self.model = None
        self.conversation_history = []
        self.initialize_model()
        
    def initialize_model(self):
        """Khởi tạo Google GenAI model với model names mới"""
        try:
            genai.configure(api_key=self.api_key)
            
            # Try different model names (Google đã update)
            model_names = [
                'gemini-1.5-flash',     # Model mới nhất
                'gemini-1.5-pro',       # Pro version
                'gemini-1.0-pro',       # Fallback
                'models/gemini-1.5-flash',  # With prefix
                'models/gemini-1.0-pro'     # With prefix fallback
            ]
            
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    # Test the model with a simple request
                    test_response = self.model.generate_content("Hello")
                    logger.info(f"✅ {self.personality.name} using model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Model {model_name} not available: {e}")
                    continue
            else:
                # If no model works, raise error
                raise Exception("No available Gemini models found")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize model for {self.personality.name}: {e}")
            # Set to None so we can handle gracefully
            self.model = None
    
    def get_system_prompt(self) -> str:
        """
        Tạo system prompt based on agent personality
        
        Returns:
            str: System prompt cho agent
        """
        return f"""
Bạn là {self.personality.name}, {self.personality.role} với {self.personality.experience} kinh nghiệm.

BACKGROUND:
{self.personality.background}

TÍNH CÁCH:
{', '.join(self.personality.personality_traits)}

ĐIỂM MẠNH:
{', '.join(self.personality.strengths)}

ĐIỂM YẾU CẦN LƯU Ý:
{', '.join(self.personality.weaknesses)}

CÁCH NÓI CHUYỆN:
{self.personality.speaking_style}

NHIỆM VỤ:
- Phân tích thông tin thị trường chứng khoán Việt Nam
- Đưa ra góc nhìn chuyên môn từ perspective của {self.personality.role}
- Tương tác tự nhiên với team members khác
- Luôn explain reasoning đằng sau recommendations
- Sử dụng terminology và số liệu Việt Nam (VND, VN-Index, HOSE, HNX)

QUY TẮC:
1. Trả lời bằng tiếng Việt tự nhiên
2. Thể hiện personality và expertise rõ ràng
3. Cite specific data points khi có thể
4. Acknowledge uncertainty khi không chắc chắn
5. Tương tác respectful với team members khác
"""

    async def generate_response(self, prompt: str, context: MarketContext = None) -> str:
        """
        Generate response từ AI model với error handling
        
        Args:
            prompt: Input prompt
            context: Market context nếu có
            
        Returns:
            str: AI response
        """
        # Check if model is available
        if self.model is None:
            logger.warning(f"⚠️ No model available for {self.personality.name}, using fallback response")
            return self._generate_fallback_response(prompt, context)
        
        try:
            # Combine system prompt với user prompt
            full_prompt = self.get_system_prompt()
            
            if context:
                full_prompt += f"""

THÔNG TIN THỊ TRƯỜNG HIỆN TẠI:
- Mã cổ phiếu: {context.symbol}
- Giá hiện tại: {context.current_price:,.0f} VND
- Market cap: {context.market_cap:,.0f} tỷ VND
- Volume: {context.volume:,.0f}
- P/E: {context.pe_ratio if context.pe_ratio else 'N/A'}
- P/B: {context.pb_ratio if context.pb_ratio else 'N/A'}
- Ngành: {context.sector}
- Xu hướng thị trường: {context.market_trend}
- Sentiment tin tức: {context.news_sentiment}
"""

            full_prompt += f"\n\nYÊU CẦU HIỆN TẠI:\n{prompt}"
            
            # Generate response với retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await asyncio.to_thread(
                        self.model.generate_content, full_prompt
                    )
                    
                    if response and response.text:
                        # Log conversation
                        self.conversation_history.append({
                            "timestamp": datetime.now(),
                            "prompt": prompt,
                            "response": response.text,
                            "context": context
                        })
                        
                        return response.text
                    else:
                        logger.warning(f"⚠️ Empty response from model, attempt {attempt + 1}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Model error attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(1)  # Wait before retry
            
            # If we get here, all retries failed
            return self._generate_fallback_response(prompt, context)
            
        except Exception as e:
            logger.error(f"❌ Error generating response for {self.personality.name}: {e}")
            return self._generate_fallback_response(prompt, context)
    
    def _generate_fallback_response(self, prompt: str, context: MarketContext = None) -> str:
        """Generate fallback response when AI model fails"""
        
        if "Market Analyst" in self.personality.role:
            return f"""
            Phân tích kỹ thuật cho {context.symbol if context else 'cổ phiếu này'}:
            
            Dựa trên thông tin hiện tại, tôi thấy:
            - Giá đang ở mức {context.current_price:,.0f} VND nếu có context else 'reasonable'
            - Volume giao dịch {'tốt' if context and context.volume > 100000 else 'cần theo dõi'}
            - P/E ratio {context.pe_ratio if context and context.pe_ratio else 'cần đánh giá thêm'}
            
            Khuyến nghị: Cần phân tích kỹ hơn với dữ liệu đầy đủ.
            
            *Lưu ý: Đây là phân tích cơ bản do hệ thống AI tạm thời không khả dụng.*
            """
        
        elif "Risk Manager" in self.personality.role:
            return f"""
            Đánh giá rủi ro cho {context.symbol if context else 'investment này'}:
            
            Từ góc độ quản lý rủi ro:
            - Position size đề xuất: Không quá 5% portfolio
            - Stop-loss: Set ở 5-7% dưới giá mua
            - Thời gian review: 2 tuần
            
            Lưu ý rủi ro:
            - Biến động thị trường chung
            - Rủi ro thanh khoản
            - Tác động từ yếu tố vĩ mô
            
            Khuyến nghị: Thận trọng và diversify.
            
            *Lưu ý: Phân tích chi tiết cần AI system hoàn chỉnh.*
            """
        
        else:  # Portfolio Manager
            return f"""
            Quyết định đầu tư cho {context.symbol if context else 'cổ phiếu này'}:
            
            Sau khi tổng hợp ý kiến team:
            - Cổ phiếu có tiềm năng trong dài hạn
            - Cần entry point hợp lý
            - Risk/reward ratio cần cân nhắc
            
            Quyết định: HOLD - chờ thêm signal
            
            Action plan:
            1. Monitor price action
            2. Watch volume patterns  
            3. Review in 1 week
            
            *Lưu ý: Quyết định cuối cùng cần analysis đầy đủ từ AI team.*
            """
    
    @abstractmethod
    async def analyze(self, context: MarketContext, team_discussion: List[str] = None) -> AgentResponse:
        """
        Abstract method cho analysis logic của từng agent
        Mỗi agent sẽ implement riêng
        
        Args:
            context: Market context
            team_discussion: Cuộc thảo luận trước đó của team
            
        Returns:
            AgentResponse: Phân tích và recommendation
        """
        pass
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Lấy summary của conversation history
        
        Returns:
            Dict: Summary data
        """
        return {
            "agent_name": self.personality.name,
            "role": self.personality.role,
            "total_interactions": len(self.conversation_history),
            "last_interaction": self.conversation_history[-1]["timestamp"] if self.conversation_history else None,
            "recent_topics": [conv["prompt"][:50] + "..." for conv in self.conversation_history[-3:]]
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info(f"🔄 Conversation history reset for {self.personality.name}")

class AgentManager:
    """
    Manager class để coordinate giữa các agents
    """
    
    def __init__(self):
        self.agents = {}
        self.team_discussion = []
        
    def add_agent(self, agent_id: str, agent: BaseAgent):
        """Thêm agent vào team"""
        self.agents[agent_id] = agent
        logger.info(f"➕ Added {agent.personality.name} to team")
    
    def get_agent(self, agent_id: str) -> BaseAgent:
        """Lấy agent by ID"""
        return self.agents.get(agent_id)
    
    def get_team_summary(self) -> Dict[str, Any]:
        """Lấy summary của cả team"""
        return {
            "team_size": len(self.agents),
            "agents": [agent.get_conversation_summary() for agent in self.agents.values()],
            "discussion_rounds": len(self.team_discussion)
        }
    
    async def facilitate_discussion(self, context: MarketContext, rounds: int = 3) -> List[AgentResponse]:
        """
        Facilitate discussion giữa các agents
        
        Args:
            context: Market context
            rounds: Số rounds thảo luận
            
        Returns:
            List[AgentResponse]: Responses từ tất cả agents
        """
        all_responses = []
        
        for round_num in range(rounds):
            round_responses = []
            
            # Mỗi agent phân tích với context của discussion trước đó
            for agent_id, agent in self.agents.items():
                try:
                    response = await agent.analyze(context, self.team_discussion)
                    round_responses.append(response)
                    
                    # Add to team discussion
                    self.team_discussion.append(f"{response.agent_name}: {response.reasoning}")
                    
                except Exception as e:
                    logger.error(f"❌ Error in {agent.personality.name} analysis: {e}")
            
            all_responses.extend(round_responses)
            
            # Short delay between rounds
            await asyncio.sleep(1)
        
        return all_responses
    
    def reset_discussion(self):
        """Reset team discussion"""
        self.team_discussion = []
        for agent in self.agents.values():
            agent.reset_conversation()
        logger.info("🔄 Team discussion reset")

# Utility functions
def create_market_context(symbol: str, **kwargs) -> MarketContext:
    """
    Helper function để tạo MarketContext
    
    Args:
        symbol: Stock symbol
        **kwargs: Additional market data
        
    Returns:
        MarketContext: Market context object
    """
    return MarketContext(
        symbol=symbol,
        current_price=kwargs.get('current_price', 0.0),
        market_cap=kwargs.get('market_cap', 0.0),
        volume=kwargs.get('volume', 0.0),
        pe_ratio=kwargs.get('pe_ratio'),
        pb_ratio=kwargs.get('pb_ratio'),
        sector=kwargs.get('sector', 'Unknown'),
        market_trend=kwargs.get('market_trend', 'Neutral'),
        news_sentiment=kwargs.get('news_sentiment', 'Neutral')
    )

def format_vnd(amount: float) -> str:
    """
    Format number thành VND currency
    
    Args:
        amount: Số tiền
        
    Returns:
        str: Formatted string
    """
    if amount >= 1_000_000_000:
        return f"{amount/1_000_000_000:.1f} tỷ VND"
    elif amount >= 1_000_000:
        return f"{amount/1_000_000:.1f} triệu VND"
    elif amount >= 1_000:
        return f"{amount/1_000:.1f} nghìn VND"
    else:
        return f"{amount:.0f} VND"