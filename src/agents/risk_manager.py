# src/agents/risk_manager.py
"""
Risk Manager Agent - Trần Quốc Bảo
Chuyên gia quản lý rủi ro với kinh nghiệm qua nhiều crisis
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import math

from .base_agent import BaseAgent, AgentPersonality, MarketContext, AgentResponse

logger = logging.getLogger(__name__)

class RiskManagerAgent(BaseAgent):
    """
    Trần Quốc Bảo - Senior Risk Manager
    Chuyên về portfolio risk, position sizing và crisis management
    """
    
    def __init__(self, api_key: str):
        # Định nghĩa personality của Quốc Bảo
        personality = AgentPersonality(
            name="Trần Quốc Bảo",
            role="Senior Risk Manager",
            experience="12 năm quản lý risk, trải qua crisis 2008, 2018, COVID",
            personality_traits=[
                "Cực kỳ thận trọng",
                "Pessimistic bias (healthy)",
                "Always think worst-case",
                "Mathematical mindset",
                "Long-term focused"
            ],
            speaking_style="""
Nói chuyện nghiêm túc, hay warn về risks. Thường dùng:
- "Cẩn thận với..."
- "Risk/reward ratio không hấp dẫn"
- "Nhớ crash năm 2018..."
- "Position size quá lớn rồi!"
- "Black swan events có thể xảy ra"
- Cite specific risk metrics
""",
            background="""
Tốt nghiệp FRM (Financial Risk Manager), làm việc tại Dragon Capital 7 năm
rồi chuyển sang VinaCapital. Trải qua nhiều market cycles và crises.
Chuyên về portfolio construction, VaR modeling, và stress testing.
Có reputation về việc protect capital trong downturns.
""",
            strengths=[
                "Portfolio risk assessment",
                "Position sizing với Kelly Criterion",
                "VaR và CVaR calculations",
                "Correlation analysis",
                "Stress testing scenarios",
                "Liquidity risk management",
                "Currency hedging strategies"
            ],
            weaknesses=[
                "Quá conservative, miss opportunities",
                "Overthink worst-case scenarios",
                "Có thể slow down decision making"
            ]
        )
        
        super().__init__(api_key, personality)
        
        # Risk management constants
        self.max_position_size = 0.10  # 10% max per stock
        self.max_sector_exposure = 0.30  # 30% max per sector
        self.cash_reserve_min = 0.15  # 15% minimum cash
        
        # VN market specific risks
        self.vn_risk_factors = {
            "liquidity_risk": "Low liquidity cho small caps",
            "foreign_limit_risk": "Foreign ownership limits",
            "currency_risk": "VND devaluation risk",
            "political_risk": "Policy changes impact",
            "concentration_risk": "Market dominated by few large caps"
        }
    
    async def analyze(self, context: MarketContext, team_discussion: List[str] = None) -> AgentResponse:
        """
        Phân tích risk cho investment decision
        
        Args:
            context: Market context
            team_discussion: Team discussion history
            
        Returns:
            AgentResponse: Risk assessment và position sizing
        """
        try:
            # Tạo risk analysis prompt
            risk_prompt = self._create_risk_analysis_prompt(context, team_discussion)
            
            # Generate risk analysis
            risk_analysis = await self.generate_response(risk_prompt, context)
            
            # Calculate position sizing
            recommended_position = self._calculate_position_size(context)
            
            # Risk-adjusted recommendation
            recommendation = self._risk_adjusted_recommendation(context, recommended_position)
            confidence = self._calculate_risk_confidence(context)
            
            # Extract risk points
            key_points = self._extract_risk_points(risk_analysis, recommended_position)
            concerns = self._extract_risk_concerns(context, risk_analysis)
            
            return AgentResponse(
                agent_name=self.personality.name,
                confidence_level=confidence,
                recommendation=recommendation,
                reasoning=risk_analysis,
                key_points=key_points,
                concerns=concerns,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Error in risk analysis: {e}")
            return self._create_error_response()
    
    def _create_risk_analysis_prompt(self, context: MarketContext, team_discussion: List[str] = None) -> str:
        """Tạo prompt cho risk analysis"""
        
        prompt = f"""
Với vai trò Senior Risk Manager, hãy đánh giá rủi ro cho đầu tư vào {context.symbol}.

NHIỆM VỤ CHÍNH:
1. Risk Assessment toàn diện
2. Position sizing recommendations
3. Stop-loss và exit strategy
4. Portfolio impact analysis
5. Worst-case scenario planning

THÔNG TIN STOCK:
- Mã: {context.symbol}
- Giá: {context.current_price:,.0f} VND
- Market cap: {context.market_cap:,.0f} tỷ
- Volume: {context.volume:,.0f}
- P/E: {context.pe_ratio if context.pe_ratio else 'N/A'}
- Ngành: {context.sector}
- Market trend: {context.market_trend}

"""
        
        if team_discussion:
            prompt += f"""
TEAM DISCUSSION:
{' | '.join(team_discussion[-2:])}

Hãy challenge các recommendations này từ risk perspective.
"""
        
        prompt += """
YÊU CẦU PHÂN TÍCH RISK:

1. COMPANY-SPECIFIC RISKS:
   - Valuation risk (P/E, P/B có hợp lý?)
   - Liquidity risk (volume có đủ để exit?)
   - Fundamental risks (debt, profitability)

2. MARKET RISKS:
   - VN-Index correlation và beta
   - Sector concentration risk
   - Foreign ownership limits impact
   - Macro risks (lãi suất, USD/VND)

3. POSITION SIZING:
   - Recommended position size (% of portfolio)
   - Max loss tolerance
   - Stop-loss levels

4. EXIT STRATEGY:
   - Take-profit targets
   - Stop-loss triggers
   - Time-based exits

5. WORST-CASE SCENARIOS:
   - Market crash 30% (như 2018)
   - Sector rotation away
   - Company-specific bad news

Trả lời bằng tiếng Việt, focus vào capital preservation.
Đưa ra specific numbers và risk metrics.
"""
        
        return prompt
    
    def _calculate_position_size(self, context: MarketContext) -> float:
        """
        Calculate optimal position size using risk metrics
        
        Args:
            context: Market context
            
        Returns:
            float: Recommended position size (% of portfolio)
        """
        base_position = 0.05  # 5% base position
        
        # Adjust dựa trên various factors
        adjustments = 0
        
        # Market cap adjustment
        if context.market_cap > 50_000:  # > 50 tỷ VND
            adjustments += 0.02  # Large cap safer
        elif context.market_cap < 10_000:  # < 10 tỷ VND
            adjustments -= 0.02  # Small cap riskier
        
        # Valuation adjustment
        if context.pe_ratio:
            if context.pe_ratio < 10:
                adjustments += 0.01  # Cheap valuation
            elif context.pe_ratio > 25:
                adjustments -= 0.02  # Expensive valuation
        
        # Volume/liquidity adjustment
        if context.volume < 100_000:
            adjustments -= 0.01  # Low liquidity
        elif context.volume > 1_000_000:
            adjustments += 0.01  # High liquidity
        
        # Market trend adjustment
        if context.market_trend == "Bearish":
            adjustments -= 0.02
        elif context.market_trend == "Bullish":
            adjustments += 0.01
        
        # Final position size
        position_size = base_position + adjustments
        
        # Apply limits
        return max(0.01, min(self.max_position_size, position_size))
    
    def _risk_adjusted_recommendation(self, context: MarketContext, position_size: float) -> str:
        """Adjust recommendation based on risk assessment"""
        
        # Base recommendation from position size
        if position_size >= 0.07:
            base_rec = "BUY"
        elif position_size <= 0.02:
            base_rec = "AVOID"
        else:
            base_rec = "HOLD"
        
        # Risk adjustments
        risk_factors = 0
        
        # High valuation risk
        if context.pe_ratio and context.pe_ratio > 30:
            risk_factors += 1
        
        # Low liquidity risk
        if context.volume < 50_000:
            risk_factors += 1
        
        # Market timing risk
        if context.market_trend == "Bearish":
            risk_factors += 1
        
        # Adjust recommendation
        if risk_factors >= 2:
            if base_rec == "BUY":
                return "HOLD"
            elif base_rec == "HOLD":
                return "AVOID"
        
        return base_rec
    
    def _calculate_risk_confidence(self, context: MarketContext) -> int:
        """Calculate confidence in risk assessment"""
        confidence = 7  # Base confidence
        
        # Increase confidence với more data
        if context.pe_ratio and context.pb_ratio:
            confidence += 1
        if context.volume > 100_000:
            confidence += 1
        if context.market_cap > 10_000:
            confidence += 1
        
        # Decrease confidence với high uncertainty
        if context.market_trend == "Volatile":
            confidence -= 1
        if not context.pe_ratio:
            confidence -= 1
        
        return max(1, min(10, confidence))
    
    def _extract_risk_points(self, risk_analysis: str, position_size: float) -> List[str]:
        """Extract key risk management points"""
        points = [
            f"Recommended position: {position_size:.1%} of portfolio",
            f"Max single-stock exposure: {self.max_position_size:.0%}",
            "Capital preservation focused"
        ]
        
        # Add specific points từ analysis
        if "stop-loss" in risk_analysis.lower():
            points.append("Stop-loss strategy defined")
        if "liquidity" in risk_analysis.lower():
            points.append("Liquidity assessment complete")
        
        return points[:5]
    
    def _extract_risk_concerns(self, context: MarketContext, risk_analysis: str) -> List[str]:
        """Extract specific risk concerns"""
        concerns = []
        
        # Market-based concerns
        if context.volume < 100_000:
            concerns.append("Low liquidity risk")
        if context.pe_ratio and context.pe_ratio > 25:
            concerns.append("High valuation risk")
        if context.market_trend == "Bearish":
            concerns.append("Market downtrend risk")
        
        # Analysis-based concerns
        if "risk" in risk_analysis.lower():
            concerns.append("Multiple risk factors identified")
        
        # Default concerns
        if not concerns:
            concerns = ["Market volatility", "Liquidity constraints"]
        
        return concerns[:4]
    
    def _create_error_response(self) -> AgentResponse:
        """Create conservative error response"""
        return AgentResponse(
            agent_name=self.personality.name,
            confidence_level=1,
            recommendation="HOLD",
            reasoning="Không thể phân tích risk đầy đủ. Khuyến nghị HOLD và chờ thêm thông tin để đảm bảo an toàn vốn.",
            key_points=["Risk analysis pending", "Capital preservation priority"],
            concerns=["Incomplete data", "System error", "High uncertainty"],
            timestamp=datetime.now()
        )
    
    def calculate_portfolio_risk(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall portfolio risk metrics
        
        Args:
            holdings: List of portfolio holdings
            
        Returns:
            Dict: Portfolio risk metrics
        """
        try:
            total_value = sum(holding['value'] for holding in holdings)
            
            # Position concentration
            max_position = max(holding['value']/total_value for holding in holdings) if holdings else 0
            
            # Sector concentration
            sector_exposure = {}
            for holding in holdings:
                sector = holding.get('sector', 'Unknown')
                sector_exposure[sector] = sector_exposure.get(sector, 0) + holding['value']
            
            max_sector = max(exposure/total_value for exposure in sector_exposure.values()) if sector_exposure else 0
            
            # Cash ratio
            cash_holdings = [h for h in holdings if h.get('symbol') == 'CASH']
            cash_ratio = sum(h['value'] for h in cash_holdings) / total_value if cash_holdings else 0
            
            return {
                "total_portfolio_value": total_value,
                "max_position_concentration": max_position,
                "max_sector_concentration": max_sector,
                "cash_ratio": cash_ratio,
                "number_of_positions": len(holdings),
                "risk_level": self._assess_portfolio_risk_level(max_position, max_sector, cash_ratio)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating portfolio risk: {e}")
            return {"error": "Portfolio risk calculation failed"}
    
    def _assess_portfolio_risk_level(self, max_position: float, max_sector: float, cash_ratio: float) -> str:
        """Assess overall portfolio risk level"""
        risk_score = 0
        
        # Position concentration risk
        if max_position > 0.15:
            risk_score += 2
        elif max_position > 0.10:
            risk_score += 1
        
        # Sector concentration risk
        if max_sector > 0.40:
            risk_score += 2
        elif max_sector > 0.30:
            risk_score += 1
        
        # Cash buffer risk
        if cash_ratio < 0.10:
            risk_score += 1
        elif cash_ratio < 0.05:
            risk_score += 2
        
        if risk_score >= 4:
            return "HIGH RISK"
        elif risk_score >= 2:
            return "MODERATE RISK"
        else:
            return "LOW RISK"
    
    def suggest_position_adjustments(self, current_portfolio: List[Dict], new_investment: Dict) -> List[str]:
        """
        Suggest portfolio adjustments for new investment
        
        Args:
            current_portfolio: Current portfolio holdings
            new_investment: Proposed new investment
            
        Returns:
            List[str]: Adjustment suggestions
        """
        suggestions = []
        
        # Calculate new portfolio metrics
        total_current = sum(h['value'] for h in current_portfolio)
        new_position_size = new_investment['value'] / (total_current + new_investment['value'])
        
        # Position size check
        if new_position_size > self.max_position_size:
            suggestions.append(f"Giảm position size xuống tối đa {self.max_position_size:.0%}")
        
        # Sector concentration check
        new_sector = new_investment.get('sector', 'Unknown')
        sector_total = sum(h['value'] for h in current_portfolio if h.get('sector') == new_sector)
        sector_exposure = (sector_total + new_investment['value']) / (total_current + new_investment['value'])
        
        if sector_exposure > self.max_sector_exposure:
            suggestions.append(f"Sector {new_sector} sẽ vượt {self.max_sector_exposure:.0%}, consider diversification")
        
        # Cash buffer check
        cash_after = max(0, total_current * 0.15 - new_investment['value'])
        if cash_after < total_current * 0.10:
            suggestions.append("Giữ thêm cash buffer cho unexpected opportunities")
        
        return suggestions