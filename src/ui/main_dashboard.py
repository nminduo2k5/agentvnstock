# src/ui/main_dashboard.py
"""
Main Streamlit Dashboard cho AI Trading Team Vietnam
UI chính của application
"""

import streamlit as st
import asyncio
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any

# Import project modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import AgentManager, create_market_context
from agents.market_analyst import MarketAnalystAgent
from agents.risk_manager import RiskManagerAgent  
from agents.portfolio_manager import PortfolioManagerAgent
from data.vn_stock_api import VNStockAPI, get_multiple_stocks
from ui.components import render_agent_card, render_stock_chart, render_performance_metrics
from ui.styles import load_custom_css
from utils.config import load_config
from utils.helpers import format_vnd, calculate_risk_metrics

# Page config
st.set_page_config(
    page_title="🇻🇳 AI Trading Team Vietnam",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = []
if 'agent_manager' not in st.session_state:
    st.session_state.agent_manager = None

class TradingDashboard:
    """Main dashboard class"""
    
    def __init__(self):
        self.config = load_config()
        self.stock_api = VNStockAPI()
        
    def render_header(self):
        """Render header section"""
        st.markdown("""
        <div class="header-container">
            <h1>🇻🇳 AI Trading Team Vietnam</h1>
            <p>Hệ thống phân tích đầu tư chứng khoán Việt Nam với 3 AI Agents chuyên nghiệp</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Market overview ticker
        self.render_market_ticker()
    
    def render_market_ticker(self):
        """Render market overview ticker"""
        try:
            # Get market data
            market_data = asyncio.run(self.stock_api.get_market_overview())
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                vn_index = market_data.get('vn_index', {})
                delta = vn_index.get('change', 0)
                st.metric(
                    "VN-Index",
                    f"{vn_index.get('value', 1200):.2f}",
                    delta=f"{delta:+.2f} ({vn_index.get('change_percent', 0):+.2f}%)"
                )
            
            with col2:
                foreign_flows = market_data.get('foreign_flows', {})
                net_flow = foreign_flows.get('net_value', 0)
                st.metric(
                    "Foreign Net",
                    format_vnd(abs(net_flow)),
                    delta="Buy" if net_flow > 0 else "Sell",
                    delta_color="normal"
                )
            
            with col3:
                sentiment = market_data.get('market_sentiment', 'Neutral')
                sentiment_color = {
                    'Bullish': '🟢',
                    'Bearish': '🔴', 
                    'Neutral': '🟡'
                }.get(sentiment, '🟡')
                st.metric("Market Sentiment", f"{sentiment_color} {sentiment}")
            
            with col4:
                top_gainers = market_data.get('top_gainers', [])
                if top_gainers:
                    best_performer = top_gainers[0]
                    st.metric(
                        "Top Gainer",
                        best_performer['symbol'],
                        delta=f"+{best_performer['change_percent']:.1f}%"
                    )
            
            with col5:
                st.metric(
                    "Active Users",
                    "1,247",
                    delta="+15.2%"
                )
                
        except Exception as e:
            st.error(f"❌ Lỗi tải market data: {e}")
    
    def render_sidebar(self):
        """Render sidebar with controls"""
        with st.sidebar:
            st.header("⚙️ Cấu hình")
            
            # API Key input
            api_key = st.text_input(
                "Google GenAI API Key",
                type="password",
                help="Nhập API key từ Google AI Studio"
            )
            
            if not api_key:
                st.warning("⚠️ Vui lòng nhập API key để sử dụng!")
                st.info("💡 Lấy API key miễn phí tại: https://makersuite.google.com/app/apikey")
                return None
            
            st.success("✅ API key đã được thiết lập")
            
            # Stock selection
            st.subheader("📊 Chọn cổ phiếu")
            
            available_stocks = self.stock_api.get_available_symbols()
            stock_options = {f"{stock['symbol']} - {stock['name']}": stock['symbol'] 
                           for stock in available_stocks}
            
            selected_stock_display = st.selectbox(
                "Mã cổ phiếu:",
                options=list(stock_options.keys()),
                index=0
            )
            selected_stock = stock_options[selected_stock_display]
            
            # Investment amount
            investment_amount = st.number_input(
                "Số tiền đầu tư (VND):",
                min_value=1_000_000,
                max_value=1_000_000_000,
                value=100_000_000,
                step=10_000_000,
                format="%d"
            )
            
            # Risk tolerance
            risk_tolerance = st.select_slider(
                "Mức độ rủi ro:",
                options=['Conservative', 'Moderate', 'Aggressive'],
                value='Moderate'
            )
            
            # Time horizon
            time_horizon = st.selectbox(
                "Thời gian đầu tư:",
                ['Ngắn hạn (1-3 tháng)', 'Trung hạn (3-12 tháng)', 'Dài hạn (>1 năm)']
            )
            
            st.markdown("---")
            
            # Team info
            st.subheader("👥 Đội ngũ AI")
            
            st.markdown("""
            **🔍 Nguyễn Minh Anh**  
            *Senior Market Analyst*  
            CFA, 8 năm kinh nghiệm VPS & SSI
            
            **⚠️ Trần Quốc Bảo**  
            *Senior Risk Manager*  
            12 năm quản lý risk, FRM certified
            
            **💼 Lê Thị Mai**  
            *Portfolio Manager*  
            10 năm fund management, top performer
            """)
            
            return {
                'api_key': api_key,
                'selected_stock': selected_stock,
                'investment_amount': investment_amount,
                'risk_tolerance': risk_tolerance,
                'time_horizon': time_horizon
            }
    
    def render_stock_analysis_section(self, stock_symbol: str):
        """Render stock analysis section"""
        st.subheader(f"📈 Phân tích {stock_symbol}")
        
        try:
            # Get stock data
            stock_data = asyncio.run(self.stock_api.get_stock_data(stock_symbol))
            
            if not stock_data:
                st.error(f"❌ Không thể tải dữ liệu cho {stock_symbol}")
                return None
            
            # Display current stock info
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Giá hiện tại",
                    f"{stock_data.price:,.0f} VND",
                    delta=f"{stock_data.change:+,.0f} VND ({stock_data.change_percent:+.2f}%)"
                )
            
            with col2:
                st.metric("Volume", f"{stock_data.volume:,}")
            
            with col3:
                st.metric("P/E Ratio", f"{stock_data.pe_ratio:.1f}" if stock_data.pe_ratio else "N/A")
            
            with col4:
                st.metric("Market Cap", format_vnd(stock_data.market_cap * 1_000_000_000))
            
            # Stock chart
            self.render_stock_chart(stock_symbol)
            
            return stock_data
            
        except Exception as e:
            st.error(f"❌ Lỗi phân tích {stock_symbol}: {e}")
            return None
    
    def render_stock_chart(self, stock_symbol: str):
        """Render stock price chart"""
        try:
            # Get historical data
            historical_data = asyncio.run(self.stock_api.get_historical_data(stock_symbol, days=30))
            
            if not historical_data:
                st.warning("⚠️ Không có dữ liệu lịch sử")
                return
            
            # Create DataFrame
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Create candlestick chart
            fig = go.Figure()
            
            # Price line
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='lines',
                name='Price',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # Volume bars
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['volume'],
                name='Volume',
                yaxis='y2',
                opacity=0.3,
                marker_color='gray'
            ))
            
            # Layout
            fig.update_layout(
                title=f"Biểu đồ giá {stock_symbol} - 30 ngày gần nhất",
                xaxis_title="Thời gian",
                yaxis_title="Giá (VND)",
                yaxis2=dict(
                    title="Volume",
                    overlaying='y',
                    side='right'
                ),
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Lỗi tạo biểu đồ: {e}")
    
    def render_ai_analysis_section(self, config: Dict[str, Any], stock_data):
        """Render AI team analysis section"""
        st.subheader("🤖 Phân tích từ AI Team")
        
        # Start analysis button
        if st.button("🚀 Bắt đầu phân tích", type="primary", use_container_width=True):
            return self.run_ai_analysis(config, stock_data)
        
        return None
    
    def run_ai_analysis(self, config: Dict[str, Any], stock_data):
        """Run AI team analysis"""
        try:
            # Initialize agent manager
            if not st.session_state.agent_manager:
                st.session_state.agent_manager = AgentManager()
                
                # Create agents
                analyst = MarketAnalystAgent(config['api_key'])
                risk_manager = RiskManagerAgent(config['api_key'])
                portfolio_manager = PortfolioManagerAgent(config['api_key'])
                
                # Add to manager
                st.session_state.agent_manager.add_agent('analyst', analyst)
                st.session_state.agent_manager.add_agent('risk_manager', risk_manager)
                st.session_state.agent_manager.add_agent('portfolio_manager', portfolio_manager)
            
            # Create market context
            context = create_market_context(
                symbol=config['selected_stock'],
                current_price=stock_data.price,
                market_cap=stock_data.market_cap,
                volume=stock_data.volume,
                pe_ratio=stock_data.pe_ratio,
                pb_ratio=stock_data.pb_ratio,
                sector=stock_data.sector,
                market_trend='Bullish'  # Simplified
            )
            
            # Progress indicators
            progress_placeholder = st.empty()
            conversation_placeholder = st.empty()
            
            with progress_placeholder.container():
                st.info("🔄 AI Team đang phân tích...")
                progress_bar = st.progress(0)
            
            # Run analysis
            responses = []
            
            # Step 1: Market Analyst
            progress_bar.progress(25)
            st.info("🔍 Minh Anh đang phân tích technical...")
            analyst_response = asyncio.run(
                st.session_state.agent_manager.get_agent('analyst').analyze(context)
            )
            responses.append(analyst_response)
            
            # Step 2: Risk Manager
            progress_bar.progress(50)
            st.info("⚠️ Quốc Bảo đang đánh giá rủi ro...")
            risk_response = asyncio.run(
                st.session_state.agent_manager.get_agent('risk_manager').analyze(
                    context, [analyst_response.reasoning]
                )
            )
            responses.append(risk_response)
            
            # Step 3: Portfolio Manager
            progress_bar.progress(75)
            st.info("💼 Thị Mai đang đưa ra quyết định...")
            pm_response = asyncio.run(
                st.session_state.agent_manager.get_agent('portfolio_manager').analyze(
                    context, [analyst_response.reasoning, risk_response.reasoning]
                )
            )
            responses.append(pm_response)
            
            progress_bar.progress(100)
            progress_placeholder.empty()
            
            # Display results
            self.display_analysis_results(responses, conversation_placeholder)
            
            # Store in session state
            st.session_state.conversation_history.append({
                'timestamp': datetime.now(),
                'stock': config['selected_stock'],
                'responses': responses
            })
            
            return responses
            
        except Exception as e:
            st.error(f"❌ Lỗi trong quá trình phân tích: {e}")
            return None
    
    def display_analysis_results(self, responses: List, placeholder):
        """Display analysis results from AI team"""
        with placeholder.container():
            st.subheader("💬 Cuộc thảo luận của AI Team")
            
            for i, response in enumerate(responses):
                # Determine agent color and icon
                if "Analyst" in response.agent_name:
                    color = "#e3f2fd"
                    icon = "🔍"
                elif "Risk" in response.agent_name:
                    color = "#fff3e0"
                    icon = "⚠️"
                else:
                    color = "#f3e5f5"
                    icon = "💼"
                
                # Render agent response
                st.markdown(f"""
                <div style="background-color: {color}; padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #2196f3;">
                    <h4>{icon} {response.agent_name}</h4>
                    <p><strong>Recommendation:</strong> <span style="color: {'green' if response.recommendation == 'BUY' else 'red' if response.recommendation == 'SELL' else 'orange'}; font-weight: bold;">{response.recommendation}</span></p>
                    <p><strong>Confidence:</strong> {response.confidence_level}/10</p>
                    <p><strong>Analysis:</strong></p>
                    <p>{response.reasoning}</p>
                    <details>
                        <summary>Chi tiết</summary>
                        <p><strong>Key Points:</strong> {', '.join(response.key_points)}</p>
                        <p><strong>Concerns:</strong> {', '.join(response.concerns)}</p>
                    </details>
                </div>
                """, unsafe_allow_html=True)
            
            # Final recommendation summary
            self.render_final_recommendation(responses)
    
    def render_final_recommendation(self, responses: List):
        """Render final investment recommendation"""
        st.subheader("📋 Tổng kết & Khuyến nghị")
        
        # Calculate consensus
        recommendations = [r.recommendation for r in responses]
        avg_confidence = sum(r.confidence_level for r in responses) / len(responses)
        
        # Determine final recommendation
        buy_count = recommendations.count('BUY')
        sell_count = recommendations.count('SELL')
        hold_count = recommendations.count('HOLD')
        
        if buy_count > sell_count and buy_count > hold_count:
            final_rec = "BUY"
            rec_color = "green"
        elif sell_count > buy_count and sell_count > hold_count:
            final_rec = "SELL"
            rec_color = "red"
        else:
            final_rec = "HOLD"
            rec_color = "orange"
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Quyết định cuối cùng",
                final_rec,
                delta=f"Consensus: {max(buy_count, sell_count, hold_count)}/3 agents"
            )
        
        with col2:
            st.metric(
                "Độ tin cậy trung bình",
                f"{avg_confidence:.1f}/10"
            )
        
        with col3:
            consensus_level = "Cao" if max(buy_count, sell_count, hold_count) == 3 else "Trung bình"
            st.metric("Mức độ đồng thuận", consensus_level)
        
        # Action plan
        if final_rec == "BUY":
            st.success(f"""
            ✅ **KHUYẾN NGHỊ MUA**
            
            **Hành động tiếp theo:**
            - Thực hiện lệnh mua với position size được khuyến nghị
            - Đặt stop-loss theo hướng dẫn của Risk Manager
            - Theo dõi các mức support/resistance
            - Review lại sau 2 tuần
            """)
        elif final_rec == "SELL":
            st.error(f"""
            🚫 **KHUYẾN NGHỊ BÁN/TRÁNH**
            
            **Hành động tiếp theo:**
            - Tránh đầu tư vào thời điểm này
            - Chờ điều kiện thị trường tốt hơn
            - Theo dõi các catalyst tích cực
            - Xem xét lại sau 1 tháng
            """)
        else:
            st.warning(f"""
            ⏸️ **KHUYẾN NGHỊ HOLD/QUAN SÁT**
            
            **Hành động tiếp theo:**
            - Tiếp tục theo dõi
            - Chờ tín hiệu rõ ràng hơn
            - Không thay đổi position hiện tại
            - Review lại trong 2 tuần
            """)
    
    def render_portfolio_section(self):
        """Render portfolio management section"""
        st.subheader("💼 Quản lý Portfolio")
        
        # Portfolio overview
        if st.session_state.portfolio_data:
            self.display_portfolio_overview()
        else:
            st.info("👥 Chưa có dữ liệu portfolio. Thực hiện phân tích đầu tiên để bắt đầu!")
        
        # Portfolio simulation
        self.render_portfolio_simulator()
    
    def display_portfolio_overview(self):
        """Display current portfolio"""
        st.write("Portfolio overview sẽ được implement...")
    
    def render_portfolio_simulator(self):
        """Render portfolio simulator"""
        with st.expander("🎮 Portfolio Simulator"):
            st.write("Tính năng mô phỏng portfolio đang được phát triển...")
            
            # Mock portfolio data
            mock_portfolio = {
                'VCB': 30,
                'VIC': 25, 
                'FPT': 20,
                'HPG': 15,
                'Cash': 10
            }
            
            # Pie chart
            fig = px.pie(
                values=list(mock_portfolio.values()),
                names=list(mock_portfolio.keys()),
                title="Phân bổ Portfolio mẫu"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_history_section(self):
        """Render analysis history"""
        st.subheader("📚 Lịch sử phân tích")
        
        if not st.session_state.conversation_history:
            st.info("🕒 Chưa có lịch sử phân tích. Thực hiện phân tích đầu tiên!")
            return
        
        # Display history
        for i, analysis in enumerate(reversed(st.session_state.conversation_history[-5:])):
            with st.expander(f"📊 {analysis['stock']} - {analysis['timestamp'].strftime('%d/%m/%Y %H:%M')}"):
                for response in analysis['responses']:
                    st.write(f"**{response.agent_name}:** {response.recommendation} (Confidence: {response.confidence_level}/10)")
                
                if st.button(f"Export Analysis {i+1}", key=f"export_{i}"):
                    export_data = {
                        'stock': analysis['stock'],
                        'timestamp': analysis['timestamp'].isoformat(),
                        'analysis': [
                            {
                                'agent': r.agent_name,
                                'recommendation': r.recommendation,
                                'confidence': r.confidence_level,
                                'reasoning': r.reasoning
                            }
                            for r in analysis['responses']
                        ]
                    }
                    
                    st.download_button(
                        "📥 Download JSON",
                        data=json.dumps(export_data, indent=2, ensure_ascii=False),
                        file_name=f"analysis_{analysis['stock']}_{analysis['timestamp'].strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key=f"download_{i}"
                    )

def main():
    """Main function"""
    dashboard = TradingDashboard()
    
    # Render header
    dashboard.render_header()
    
    # Render sidebar and get config
    config = dashboard.render_sidebar()
    
    if not config:
        st.stop()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Phân tích Stock", "💼 Portfolio", "📚 Lịch sử", "ℹ️ Hướng dẫn"])
    
    with tab1:
        # Stock analysis
        stock_data = dashboard.render_stock_analysis_section(config['selected_stock'])
        
        if stock_data:
            # AI analysis
            analysis_results = dashboard.render_ai_analysis_section(config, stock_data)
    
    with tab2:
        dashboard.render_portfolio_section()
    
    with tab3:
        dashboard.render_history_section()
    
    with tab4:
        st.subheader("📖 Hướng dẫn sử dụng")
        st.markdown("""
        ### 🚀 Cách sử dụng AI Trading Team Vietnam
        
        1. **Setup API Key**: Nhập Google GenAI API key ở sidebar
        2. **Chọn cổ phiếu**: Chọn mã cổ phiếu muốn phân tích
        3. **Cấu hình**: Thiết lập số tiền và mức độ rủi ro
        4. **Phân tích**: Bấm "Bắt đầu phân tích" để AI team thảo luận
        5. **Quyết định**: Xem recommendation và action plan
        
        ### 👥 Đội ngũ AI Experts
        
        **🔍 Nguyễn Minh Anh - Market Analyst**
        - Chuyên gia phân tích kỹ thuật và cơ bản
        - 8 năm kinh nghiệm tại VPS và SSI
        - Tập trung vào technical indicators, patterns, volume analysis
        
        **⚠️ Trần Quốc Bảo - Risk Manager** 
        - Chuyên gia quản lý rủi ro và capital preservation
        - 12 năm kinh nghiệm, trải qua nhiều crisis
        - Tính toán position sizing, stop-loss, risk metrics
        
        **💼 Lê Thị Mai - Portfolio Manager**
        - Giám đốc đầu tư với track record top 10%
        - 10 năm quản lý fund 500 tỷ VND
        - Đưa ra quyết định cuối cùng và strategy coordination
        
        ### 🎯 Features chính
        
        - **Real-time Analysis**: Phân tích real-time với AI
        - **Multi-perspective**: 3 góc nhìn chuyên nghiệp khác nhau
        - **Vietnamese Market Focus**: Tối ưu cho thị trường VN
        - **Risk Management**: Tích hợp risk assessment
        - **Portfolio Tracking**: Theo dõi performance
        - **Export Results**: Lưu analysis dưới dạng JSON
        
        ### 📊 Supported Stocks
        
        Hệ thống hỗ trợ các bluechips chính:
        - **Banking**: VCB, BID, CTG, TCB, ACB
        - **Real Estate**: VIC, VHM, VRE, DXG  
        - **Consumer**: MSN, MWG, VNM, SAB
        - **Industrial**: HPG, GAS, PLX
        - **Technology**: FPT
        
        ### ⚠️ Disclaimer
        
        - Đây là công cụ hỗ trợ quyết định, không phải lời khuyên đầu tư
        - Luôn thực hiện due diligence riêng
        - Đầu tư có rủi ro, có thể mất vốn
        - Chỉ đầu tư số tiền có thể chấp nhận mất
        """)

if __name__ == "__main__":
    main()