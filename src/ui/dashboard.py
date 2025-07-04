# src/ui/dashboard.py
"""
Main Streamlit Dashboard for AI Trading Team Vietnam
6 AI Agents + Gemini Chatbot Integration
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import project modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI
from src.ui.components import (
    render_agent_card, render_stock_overview_card, 
    render_recommendation_summary, render_stock_chart,
    render_loading_animation, render_error_message
)
from src.ui.styles import load_custom_css

class AITradingDashboard:
    """Main dashboard for AI Trading Team Vietnam"""
    
    def __init__(self):
        self.vn_api = VNStockAPI()
        self.main_agent = MainAgent(self.vn_api)
        
        # Initialize session state
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def setup_page(self):
        """Setup page configuration"""
        st.set_page_config(
            page_title="🇻🇳 AI Trading Team Vietnam",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        load_custom_css()
    
    def render_header(self):
        """Render main header"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        ">
            <h1 style="margin: 0; font-size: 2.5rem;">🇻🇳 AI Trading Team Vietnam</h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                Hệ thống phân tích đầu tư chứng khoán với 6 AI Agents chuyên nghiệp + Gemini Chatbot
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self) -> Optional[Dict[str, Any]]:
        """Render sidebar with 6 AI agents status and controls"""
        with st.sidebar:
            st.header("⚙️ Cài đặt")
            
            # 6 AI Agents Status
            st.subheader("🤖 6 AI Agents")
            agents_info = [
                {"name": "📈 PricePredictor", "desc": "Dự đoán giá", "status": "🟢"},
                {"name": "📰 TickerNews", "desc": "Tin tức cổ phiếu", "status": "🟢"},
                {"name": "🌍 MarketNews", "desc": "Tin tức thị trường", "status": "🟢"},
                {"name": "💼 InvestmentExpert", "desc": "Phân tích đầu tư", "status": "🟢"},
                {"name": "⚠️ RiskExpert", "desc": "Quản lý rủi ro", "status": "🟢"},
                {"name": "🧠 GeminiAgent", "desc": "AI Chatbot", "status": "🟢"}
            ]
            
            for agent in agents_info:
                st.write(f"{agent['status']} **{agent['name']}**: {agent['desc']}")
            
            st.divider()
            
            # Stock selection
            st.subheader("📊 Chọn cổ phiếu")
            symbols = self.vn_api.get_available_symbols()
            symbol_options = [f"{s['symbol']} - {s['name']}" for s in symbols]
            selected_symbol = st.selectbox("Mã cổ phiếu:", symbol_options)
            symbol = selected_symbol.split(" - ")[0] if selected_symbol else "VCB"
            
            # Investment amount
            investment_amount = st.number_input(
                "Số tiền đầu tư (VND):",
                min_value=1_000_000,
                max_value=1_000_000_000,
                value=100_000_000,
                step=10_000_000,
                format="%d"
            )
            
            return {
                'symbol': symbol,
                'investment_amount': investment_amount
            }
    
    def render_stock_analysis_tab(self, symbol: str, investment_amount: float):
        """Render stock analysis tab"""
        st.header(f"📈 Phân tích toàn diện {symbol}")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🚀 Phân tích toàn diện", type="primary"):
                self.run_comprehensive_analysis(symbol, investment_amount)
        
        with col2:
            st.subheader("🎯 Quick Actions")
            if st.button("📈 Dự đoán giá"):
                self.run_price_prediction(symbol)
            
            if st.button("⚠️ Đánh giá rủi ro"):
                self.run_risk_assessment(symbol)
    
    def run_comprehensive_analysis(self, symbol: str, investment_amount: float):
        """Run comprehensive analysis with all 6 agents"""
        with st.spinner("6 AI Agents đang phân tích..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.main_agent.analyze_stock(symbol))
                
                # Display VN Stock Data
                if result.get('vn_stock_data'):
                    stock_data = result['vn_stock_data']
                    render_stock_overview_card(stock_data)
                    
                    # Display metrics
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.metric("Giá hiện tại", f"{stock_data.price:,.0f} VND", 
                                f"{stock_data.change_percent:+.2f}%")
                    with col_b:
                        st.metric("Khối lượng", f"{stock_data.volume:,}")
                    with col_c:
                        st.metric("Vốn hóa", f"{stock_data.market_cap:,.1f}B VND")
                    with col_d:
                        st.metric("P/E Ratio", f"{stock_data.pe_ratio}")
                
                # Display agent results
                self.display_agent_results(result)
                
                # Store in history
                st.session_state.analysis_history.append({
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'result': result
                })
                
            except Exception as e:
                render_error_message(f"Lỗi phân tích: {str(e)}", 
                                   "Vui lòng thử lại sau vài phút")
    
    def display_agent_results(self, result: Dict[str, Any]):
        """Display results from all agents"""
        
        # Price Prediction
        if result.get('price_prediction'):
            st.subheader("🔮 Dự đoán giá (PricePredictor Agent)")
            pred = result['price_prediction']
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Xu hướng:** {pred.get('trend', 'N/A')}")
                st.write(f"**Giá dự đoán:** {pred.get('predicted_price', 'N/A')}")
            with col_b:
                st.write(f"**Độ tin cậy:** {pred.get('confidence', 'N/A')}")
                st.write(f"**Thời gian:** {pred.get('timeframe', 'N/A')}")
        
        # Risk Assessment
        if result.get('risk_assessment'):
            st.subheader("⚠️ Đánh giá rủi ro (RiskExpert Agent)")
            risk = result['risk_assessment']
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                risk_color = "🔴" if risk.get('risk_level') == 'HIGH' else "🟡" if risk.get('risk_level') == 'MEDIUM' else "🟢"
                st.write(f"**Mức rủi ro:** {risk_color} {risk.get('risk_level', 'N/A')}")
            with col_b:
                st.write(f"**Độ biến động:** {risk.get('volatility', 'N/A')}%")
            with col_c:
                st.write(f"**Beta:** {risk.get('beta', 'N/A')}")
        
        # Investment Analysis
        if result.get('investment_analysis'):
            st.subheader("💼 Phân tích đầu tư (InvestmentExpert Agent)")
            inv = result['investment_analysis']
            rec_color = "🟢" if inv.get('recommendation') == 'BUY' else "🔴" if inv.get('recommendation') == 'SELL' else "🟡"
            st.write(f"**Khuyến nghị:** {rec_color} {inv.get('recommendation', 'N/A')}")
            st.write(f"**Lý do:** {inv.get('reason', 'N/A')}")
    
    def run_price_prediction(self, symbol: str):
        """Run price prediction only"""
        with st.spinner("PricePredictor đang làm việc..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                pred = loop.run_until_complete(
                    asyncio.to_thread(self.main_agent.price_predictor.predict_price, symbol)
                )
                st.json(pred)
            except Exception as e:
                st.error(f"Lỗi dự đoán giá: {str(e)}")
    
    def run_risk_assessment(self, symbol: str):
        """Run risk assessment only"""
        with st.spinner("RiskExpert đang phân tích..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                risk = loop.run_until_complete(
                    asyncio.to_thread(self.main_agent.risk_expert.assess_risk, symbol)
                )
                st.json(risk)
            except Exception as e:
                st.error(f"Lỗi đánh giá rủi ro: {str(e)}")
    
    def render_chatbot_tab(self, symbol: str):
        """Render AI Chatbot tab with Gemini"""
        st.header("💬 AI Chatbot với Gemini")
        st.markdown("**Hỏi đáp tự nhiên với chuyên gia AI về đầu tư chứng khoán**")
        
        # Chat interface
        user_question = st.text_input(
            "💭 Hỏi chuyên gia AI:", 
            placeholder="VD: Phân tích VCB có nên mua không? Dự đoán giá HPG tuần tới?",
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            ask_button = st.button("🚀 Gửi câu hỏi", type="primary")
        
        if ask_button and user_question:
            with st.spinner("🧠 Gemini AI đang suy nghĩ..."):
                try:
                    # Run async function properly in Streamlit
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        self.main_agent.process_query(user_question, symbol)
                    )
                    
                    if response.get('expert_advice'):
                        st.subheader("🎓 Lời khuyên từ chuyên gia AI")
                        st.markdown(response['expert_advice'])
                    
                    if response.get('recommendations'):
                        st.subheader("💡 Khuyến nghị cụ thể")
                        for i, rec in enumerate(response['recommendations'], 1):
                            st.write(f"{i}. {rec}")
                    
                    # Show supporting data if available
                    if response.get('data'):
                        with st.expander("📊 Dữ liệu hỗ trợ phân tích"):
                            st.json(response['data'])
                    
                    # Store in chat history
                    st.session_state.chat_history.append({
                        'timestamp': datetime.now(),
                        'question': user_question,
                        'response': response
                    })
                    
                except Exception as e:
                    render_error_message(f"Lỗi chatbot: {str(e)}", 
                                       "Vui lòng thử lại với câu hỏi khác")
        
        # Sample questions
        st.subheader("💡 Câu hỏi mẫu")
        sample_questions = [
            "Phân tích VCB có nên mua không?",
            "Dự đoán giá HPG tuần tới?",
            "So sánh rủi ro giữa VIC và VHM?",
            "Thị trường VN hôm nay như thế nào?",
            "Nên đầu tư ngân hàng hay bất động sản?"
        ]
        
        for i, question in enumerate(sample_questions):
            if st.button(f"❓ {question}", key=f"sample_{i}"):
                st.session_state.chat_input = question
                st.rerun()
    
    def render_market_tab(self):
        """Render market overview tab"""
        st.header("📈 Tổng quan thị trường Việt Nam")
        
        if st.button("🔄 Cập nhật thị trường", type="primary"):
            with st.spinner("Đang lấy dữ liệu real-time..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    market_data = loop.run_until_complete(self.vn_api.get_market_overview())
                    
                    if market_data.get('vn_index'):
                        st.subheader("📊 VN-Index")
                        vn_index = market_data['vn_index']
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("VN-Index", f"{vn_index['value']:,.2f}", 
                                    f"{vn_index['change_percent']:+.2f}%")
                        with col2:
                            st.metric("Thay đổi", f"{vn_index['change']:+,.2f}")
                        with col3:
                            st.metric("Khối lượng", f"{vn_index.get('volume', 0):,}")
                    
                    # Top movers
                    if market_data.get('top_gainers'):
                        st.subheader("🚀 Top tăng mạnh")
                        for stock in market_data['top_gainers'][:5]:
                            st.write(f"• **{stock['symbol']}**: +{stock['change_percent']:.2f}%")
                    
                    if market_data.get('top_losers'):
                        st.subheader("📉 Top giảm mạnh")
                        for stock in market_data['top_losers'][:5]:
                            st.write(f"• **{stock['symbol']}**: {stock['change_percent']:.2f}%")
                            
                except Exception as e:
                    render_error_message(f"Lỗi tải thị trường: {str(e)}")
        
        # Available VN stocks
        self.render_available_stocks()
    
    def render_available_stocks(self):
        """Render available stocks by sector"""
        st.subheader("📋 Danh sách cổ phiếu hỗ trợ")
        symbols = self.vn_api.get_available_symbols()
        
        # Group by sector
        sectors = {}
        for stock in symbols:
            sector = stock['sector']
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(stock)
        
        for sector, stocks in sectors.items():
            with st.expander(f"🏢 {sector} ({len(stocks)} mã)"):
                cols = st.columns(3)
                for i, stock in enumerate(stocks):
                    with cols[i % 3]:
                        st.write(f"**{stock['symbol']}** - {stock['name']}")
    
    def render_footer(self):
        """Render footer"""
        st.markdown("---")
        st.markdown("**🇻🇳 AI Trading Team Vietnam** - Powered by vnstock, Google Gemini & 6 AI Agents")
        st.markdown("*Real-time data từ thị trường chứng khoán Việt Nam*")
    
    def run(self):
        """Main run method"""
        self.setup_page()
        self.render_header()
        
        # Sidebar
        config = self.render_sidebar()
        if not config:
            st.stop()
        
        # Main content tabs
        tab1, tab2, tab3 = st.tabs([
            "📊 Phân tích cổ phiếu", 
            "💬 AI Chatbot", 
            "📈 Thị trường VN"
        ])
        
        with tab1:
            self.render_stock_analysis_tab(config['symbol'], config['investment_amount'])
        
        with tab2:
            self.render_chatbot_tab(config['symbol'])
        
        with tab3:
            self.render_market_tab()
        
        self.render_footer()

def main():
    """Main function"""
    dashboard = AITradingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()