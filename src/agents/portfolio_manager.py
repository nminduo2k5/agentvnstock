# src/agents/portfolio_manager.py
"""
Portfolio Manager Agent - Lê Thị Mai
Giám đốc đầu tư với khả năng synthesis và decision making
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from .base_agent import BaseAgent, AgentPersonality, MarketContext, AgentResponse

logger = logging.getLogger(__name__)

class PortfolioManagerAgent(BaseAgent):
    """
    Lê Thị Mai - Senior Portfolio Manager
    Chuyên về strategic decisions, team coordination và final calls
    """
    
    def __init__(self, api_key: str):
        # Định nghĩa personality của Thị Mai
        personality = AgentPersonality(
            name="Lê Thị Mai",
            role="Senior Portfolio Manager",
            experience="10 năm quản lý fund, track record top 10% trong ngành",
            personality_traits=[
                "Decisive leader",
                "Strategic thinker",
                "Team coordinator",
                "Balanced risk-taker",
                "Long-term vision"
            ],
            speaking_style="""
Nói chuyện confident và decisive. Thường dùng:
- "Quyết định cuối cùng là..."
- "Từ macro perspective..."
- "Balance giữa risk và opportunity"
- "Team insight rất valuable"
- "Timing là quan trọng"
- Quote từ successful investors
""",
            background="""
MBA từ INSEAD, bắt đầu career tại Deutsche Bank rồi về Việt Nam.
Quản lý fund 500 tỷ VND tại VinaCapital với performance top quartile.
Strong network trong investment community và hiểu deep macro Việt Nam.
Có khả năng synthesize different viewpoints và make final decisions.
""",
            strengths=[
                "Strategic asset allocation",
                "Team coordination và synthesis",
                "Macro economic analysis",
                "Timing market entries/exits",
                "Stakeholder communication",
                "Performance attribution",
                "Crisis management"
            ],
            weaknesses=[
                "Đôi khi overthink decisions",
                "Có thể slow khi quá nhiều conflicting views",
                "Pressure từ performance expectations"
            ]
        )
        
        super().__init__(api_key, personality)
        
        # Portfolio management parameters
        self.target_sectors = {
            "Banking": 0.25,
            "Real Estate": 0.20,
            "Consumer": 0.15,
            "Industrial": 0.15,
            "Technology": 0.10,
            "Utilities": 0.05,
            "Cash": 0.10
        }
        
        self.performance_targets = {
            "annual_return": 0.15,  # 15% target return
            "max_drawdown": 0.20,   # 20% max drawdown
            "sharpe_ratio": 1.0,    # Target Sharpe > 1.0
            "win_rate": 0.60        # 60% winning trades
        }
    
    async def analyze(self, context: MarketContext, team_discussion: List[str] = None) -> AgentResponse:
        """
        Make final investment decision sau khi nghe team input
        
        Args:
            context: Market context
            team_discussion: Input từ analyst và risk manager
            
        Returns:
            AgentResponse: Final decision và strategy
        """
        try:
            # Tạo synthesis prompt
            decision_prompt = self._create_decision_prompt(context, team_discussion)
            
            # Generate final decision
            decision_analysis = await self.generate_response(decision_prompt, context)
            
            # Make final recommendation
            final_recommendation = self._synthesize_team_input(team_discussion, context)
            confidence = self._calculate_decision_confidence(context, team_discussion)
            
            # Strategic points và actions
            key_points = self._extract_strategic_points(decision_analysis, team_discussion)
            action_items = self._create_action_items(final_recommendation, context)
            
            return AgentResponse(
                agent_name=self.personality.name,
                confidence_level=confidence,
                recommendation=final_recommendation,
                reasoning=decision_analysis,
                key_points=key_points,
                concerns=action_items,  # Using concerns field for action items
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Error in portfolio decision: {e}")
            return self._create_error_response()
    
    def _create_decision_prompt(self, context: MarketContext, team_discussion: List[str] = None) -> str:
        """Tạo prompt cho final decision making"""
        
        prompt = f"""
Với vai trò Senior Portfolio Manager, hãy đưa ra quyết định cuối cùng cho investment vào {context.symbol}.

NHIỆM VỤ:
1. Synthesize input từ Market Analyst và Risk Manager
2. Đưa ra final investment decision
3. Define execution strategy và timeline
4. Set performance expectations và monitoring plan

STOCK CONTEXT:
- Mã: {context.symbol}
- Giá: {context.current_price:,.0f} VND
- Market cap: {context.market_cap:,.0f} tỷ
- Ngành: {context.sector}
- Market environment: {context.market_trend}

"""
        
        if team_discussion:
            prompt += f"""
TEAM INPUT ANALYSIS:
{chr(10).join(team_discussion)}

Hãy evaluate từng viewpoint và explain final decision reasoning.
"""
        
        prompt += """
YÊU CẦU DECISION FRAMEWORK:

1. TEAM INPUT SYNTHESIS:
   - Analyst insights về technical/fundamental
   - Risk Manager concerns về position sizing
   - Areas of agreement vs disagreement
   - Weight của từng perspective

2. MACRO CONTEXT:
   - VN market cycle hiện tại
   - Sector rotation trends
   - Foreign investment flows
   - Interest rate environment

3. PORTFOLIO FIT:
   - Sector allocation impact
   - Risk budget utilization
   - Correlation với existing holdings
   - Strategic vs tactical allocation

4. EXECUTION PLAN:
   - Entry strategy (immediate vs DCA)
   - Position sizing final decision
   - Timeline và milestones
   - Exit criteria

5. MONITORING FRAMEWORK:
   - Key metrics to track
   - Review frequency
   - Performance attribution
   - Risk monitoring alerts

Trả lời bằng tiếng Việt như một PM experienced.
Be decisive nhưng explain reasoning clearly.
"""
        
        return prompt
    
    def _synthesize_team_input(self, team_discussion: List[str], context: MarketContext) -> str:
        """Synthesize team input thành final recommendation"""
        
        if not team_discussion:
            return "HOLD"  # Conservative default
        
        # Analyze team sentiment
        buy_signals = 0
        sell_signals = 0
        hold_signals = 0
        
        for discussion in team_discussion:
            discussion_lower = discussion.lower()
            if any(word in discussion_lower for word in ["mua", "buy", "tích cực", "khuyến mại"]):
                buy_signals += 1
            elif any(word in discussion_lower for word in ["bán", "sell", "thoát", "avoid"]):
                sell_signals += 1
            else:
                hold_signals += 1
        
        # Weight decisions (Risk Manager có higher weight cho safety)
        if "risk manager" in ' '.join(team_discussion).lower() and sell_signals > 0:
            return "HOLD"  # Conservative khi risk manager concern
        
        # Final synthesis
        if buy_signals > sell_signals and buy_signals > 0:
            return "BUY"
        elif sell_signals > buy_signals:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_decision_confidence(self, context: MarketContext, team_discussion: List[str]) -> int:
        """Calculate confidence trong final decision"""
        
        confidence = 6  # Base PM confidence
        
        # Team consensus bonus
        if team_discussion:
            recommendations = []
            for disc in team_discussion:
                if "buy" in disc.lower() or "mua" in disc.lower():
                    recommendations.append("buy")
                elif "sell" in disc.lower() or "bán" in disc.lower():
                    recommendations.append("sell")
                else:
                    recommendations.append("hold")
            
            # Consensus boost
            if len(set(recommendations)) == 1:  # Full consensus
                confidence += 2
            elif len(set(recommendations)) == 2:  # Partial consensus
                confidence += 1
        
        # Market clarity bonus
        if context.market_trend in ["Bullish", "Bearish"]:  # Clear trend
            confidence += 1
        
        # Data quality bonus
        if context.pe_ratio and context.pb_ratio:
            confidence += 1
        
        return max(1, min(10, confidence))
    
    def _extract_strategic_points(self, decision_analysis: str, team_discussion: List[str]) -> List[str]:
        """Extract strategic decision points"""
        
        points = [
            "Team input fully evaluated",
            "Portfolio strategy alignment checked",
            "Risk-reward optimized"
        ]
        
        # Add specific points từ analysis
        if "macro" in decision_analysis.lower():
            points.append("Macro environment considered")
        if "timing" in decision_analysis.lower():
            points.append("Market timing assessed")
        if team_discussion and len(team_discussion) >= 2:
            points.append("Multiple perspectives synthesized")
        
        return points[:5]
    
    def _create_action_items(self, recommendation: str, context: MarketContext) -> List[str]:
        """Create concrete action items based on decision"""
        
        actions = []
        
        if recommendation == "BUY":
            actions.extend([
                "Execute buy order với recommended sizing",
                "Set stop-loss levels",
                "Monitor volume và price action",
                "Schedule 2-week review"
            ])
        elif recommendation == "SELL":
            actions.extend([
                "Plan exit strategy",
                "Consider tax implications",
                "Reallocate proceeds",
                "Document lessons learned"
            ])
        else:  # HOLD
            actions.extend([
                "Continue monitoring",
                "Wait for better entry point",
                "Review in 1 month",
                "Track key catalysts"
            ])
        
        return actions[:4]
    
    def _create_error_response(self) -> AgentResponse:
        """Create error response with conservative stance"""
        return AgentResponse(
            agent_name=self.personality.name,
            confidence_level=3,
            recommendation="HOLD",
            reasoning="Không thể synthesize đầy đủ thông tin từ team. Quyết định tạm thời HOLD cho đến khi có analysis hoàn chỉnh.",
            key_points=["Decision pending", "Awaiting complete analysis"],
            concerns=["Review team inputs", "Gather more data", "Reassess in 24h"],
            timestamp=datetime.now()
        )
    
    async def portfolio_rebalancing_analysis(self, current_holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Phân tích và đề xuất rebalancing portfolio
        
        Args:
            current_holdings: Danh sách holdings hiện tại
            
        Returns:
            Dict: Rebalancing recommendations
        """
        try:
            # Calculate current allocations
            total_value = sum(holding['value'] for holding in current_holdings)
            current_allocations = {}
            
            for holding in current_holdings:
                sector = holding.get('sector', 'Other')
                current_allocations[sector] = current_allocations.get(sector, 0) + holding['value']
            
            # Convert to percentages
            for sector in current_allocations:
                current_allocations[sector] = current_allocations[sector] / total_value
            
            # Compare với target allocations
            rebalancing_needs = {}
            for sector, target in self.target_sectors.items():
                current = current_allocations.get(sector, 0)
                deviation = current - target
                if abs(deviation) > 0.05:  # 5% threshold
                    rebalancing_needs[sector] = {
                        'current': current,
                        'target': target,
                        'deviation': deviation,
                        'action': 'REDUCE' if deviation > 0 else 'INCREASE'
                    }
            
            # Generate rebalancing prompt
            rebalance_prompt = f"""
Với vai trò Portfolio Manager, hãy phân tích portfolio rebalancing needs:

CURRENT ALLOCATION:
{chr(10).join([f"- {sector}: {alloc:.1%}" for sector, alloc in current_allocations.items()])}

TARGET ALLOCATION:
{chr(10).join([f"- {sector}: {target:.1%}" for sector, target in self.target_sectors.items()])}

REBALANCING NEEDS:
{chr(10).join([f"- {sector}: {data['action']} (current {data['current']:.1%} vs target {data['target']:.1%})" 
               for sector, data in rebalancing_needs.items()])}

Đưa ra strategic rebalancing plan với priority và timeline.
"""
            
            rebalancing_analysis = await self.generate_response(rebalance_prompt)
            
            return {
                'current_allocations': current_allocations,
                'target_allocations': self.target_sectors,
                'rebalancing_needs': rebalancing_needs,
                'analysis': rebalancing_analysis,
                'total_portfolio_value': total_value
            }
            
        except Exception as e:
            logger.error(f"❌ Error in rebalancing analysis: {e}")
            return {'error': 'Rebalancing analysis failed'}
    
    def calculate_portfolio_performance(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate portfolio performance metrics
        
        Args:
            historical_data: Historical portfolio values và benchmarks
            
        Returns:
            Dict: Performance metrics
        """
        try:
            if len(historical_data) < 2:
                return {'error': 'Insufficient data for performance calculation'}
            
            # Calculate returns
            portfolio_values = [data['portfolio_value'] for data in historical_data]
            returns = [(portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1] 
                      for i in range(1, len(portfolio_values))]
            
            # Basic metrics
            total_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]
            avg_return = sum(returns) / len(returns) if returns else 0
            volatility = self._calculate_volatility(returns)
            sharpe_ratio = avg_return / volatility if volatility > 0 else 0
            max_drawdown = self._calculate_max_drawdown(portfolio_values)
            
            return {
                'total_return': total_return,
                'annualized_return': avg_return * 252,  # Assuming daily data
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': len([r for r in returns if r > 0]) / len(returns) if returns else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating performance: {e}")
            return {'error': 'Performance calculation failed'}
    
    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate volatility of returns"""
        if len(returns) < 2:
            return 0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        return variance ** 0.5
    
    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(values) < 2:
            return 0
        
        peak = values[0]
        max_dd = 0
        
        for value in values[1:]:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    async def market_outlook_analysis(self, market_data: Dict[str, Any]) -> str:
        """
        Phân tích market outlook từ PM perspective
        
        Args:
            market_data: Current market conditions
            
        Returns:
            str: Market outlook analysis
        """
        outlook_prompt = f"""
Với vai trò Senior Portfolio Manager, hãy đưa ra market outlook cho thị trường Việt Nam:

MARKET DATA:
- VN-Index: {market_data.get('vn_index', 'N/A')}
- P/E market: {market_data.get('market_pe', 'N/A')}
- Foreign flows: {market_data.get('foreign_flows', 'N/A')}
- Interest rates: {market_data.get('interest_rates', 'N/A')}
- GDP growth: {market_data.get('gdp_growth', 'N/A')}
- Inflation: {market_data.get('inflation', 'N/A')}

SECTOR PERFORMANCE:
{chr(10).join([f"- {sector}: {perf}" for sector, perf in market_data.get('sector_performance', {}).items()])}

Đưa ra:
1. Market outlook 3-6 months
2. Sector allocation strategies
3. Key risks và opportunities
4. Portfolio positioning recommendations

Perspective từ fund manager với fiduciary responsibility.
"""
        
        try:
            outlook = await self.generate_response(outlook_prompt)
            return outlook
        except Exception as e:
            logger.error(f"❌ Error in market outlook: {e}")
            return "Market outlook analysis temporarily unavailable."
    
    def generate_investment_committee_report(self, team_analysis: List[AgentResponse], context: MarketContext) -> Dict[str, Any]:
        """
        Generate comprehensive investment committee report
        
        Args:
            team_analysis: Analysis từ tất cả agents
            context: Market context
            
        Returns:
            Dict: Investment committee report
        """
        try:
            # Synthesize team recommendations
            recommendations = [analysis.recommendation for analysis in team_analysis]
            avg_confidence = sum(analysis.confidence_level for analysis in team_analysis) / len(team_analysis)
            
            # Consensus analysis
            consensus_level = "HIGH" if len(set(recommendations)) == 1 else "MODERATE" if len(set(recommendations)) == 2 else "LOW"
            
            # Key insights from each agent
            analyst_insights = next((a.key_points for a in team_analysis if "Analyst" in a.agent_name), [])
            risk_concerns = next((a.concerns for a in team_analysis if "Risk" in a.agent_name), [])
            pm_strategy = next((a.key_points for a in team_analysis if "Portfolio" in a.agent_name), [])
            
            return {
                'executive_summary': {
                    'stock_symbol': context.symbol,
                    'final_recommendation': self._get_consensus_recommendation(recommendations),
                    'confidence_level': avg_confidence,
                    'consensus_level': consensus_level
                },
                'team_analysis': {
                    'market_analyst_insights': analyst_insights,
                    'risk_manager_concerns': risk_concerns,
                    'portfolio_strategy': pm_strategy
                },
                'detailed_reasoning': [
                    {
                        'agent': analysis.agent_name,
                        'recommendation': analysis.recommendation,
                        'confidence': analysis.confidence_level,
                        'reasoning': analysis.reasoning[:500] + "..." if len(analysis.reasoning) > 500 else analysis.reasoning
                    }
                    for analysis in team_analysis
                ],
                'next_steps': self._generate_next_steps(recommendations, context),
                'report_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating IC report: {e}")
            return {'error': 'Investment committee report generation failed'}
    
    def _get_consensus_recommendation(self, recommendations: List[str]) -> str:
        """Get consensus recommendation từ team"""
        # Count votes
        buy_votes = recommendations.count("BUY")
        sell_votes = recommendations.count("SELL")
        hold_votes = recommendations.count("HOLD")
        
        if buy_votes > sell_votes and buy_votes > hold_votes:
            return "BUY"
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            return "SELL"
        else:
            return "HOLD"
    
    def _generate_next_steps(self, recommendations: List[str], context: MarketContext) -> List[str]:
        """Generate next steps based on team recommendations"""
        consensus_rec = self._get_consensus_recommendation(recommendations)
        
        if consensus_rec == "BUY":
            return [
                f"Initiate position in {context.symbol}",
                "Execute with recommended position sizing",
                "Set monitoring alerts for key levels",
                "Schedule 2-week performance review"
            ]
        elif consensus_rec == "SELL":
            return [
                f"Exit position in {context.symbol}",
                "Document trade rationale",
                "Reallocate capital to better opportunities",
                "Post-trade analysis in 1 month"
            ]
        else:
            return [
                f"Continue monitoring {context.symbol}",
                "Wait for clearer technical/fundamental signals",
                "Re-evaluate with fresh data in 2 weeks",
                "Maintain current allocation"
            ]