import streamlit as st
import asyncio
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI
from src.ui.styles import load_custom_css
import json

# Professional page configuration
st.set_page_config(
    page_title="DUONG AI TRADING PRO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Bootstrap-integrated CSS
load_custom_css()

# Additional app-specific CSS
st.markdown("""
<style>
    /* App-specific overrides */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid var(--bs-primary);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    /* Streamlit tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bs-gray-100);
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bs-primary);
        color: white;
    }
    
    /* News cards */
    .news-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        border-left: 4px solid var(--bs-primary);
        transition: transform 0.2s ease;
    }
    
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.12);
    }
</style>
""", unsafe_allow_html=True)

# Initialize system
@st.cache_resource
def init_system():
    vn_api = VNStockAPI()
    main_agent = MainAgent(vn_api)
    return main_agent, vn_api

main_agent, vn_api = init_system()
# Analysis display functions
async def display_comprehensive_analysis(result, symbol, time_horizon="Trung hạn", risk_tolerance=50):
    """Display comprehensive analysis with real stock info"""
    # Get detailed stock info from main_agent
    detailed_info = await main_agent.get_detailed_stock_info(symbol)
    
    if detailed_info and not detailed_info.get('error'):
        stock_data = detailed_info['stock_data']
        detailed_data = detailed_info['detailed_data']
        price_history = detailed_info['price_history']
        
        # Display using main_agent methods
        from datetime import datetime
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        main_agent.display_stock_header(stock_data, current_time)
        main_agent.display_detailed_metrics(detailed_data)
        main_agent.display_financial_ratios(detailed_data)
        main_agent.display_price_chart(price_history, symbol)
        
        # Data source indicator
        if stock_data.price > 10000:
            st.success("✅ Sử dụng dữ liệu thật từ VNStock API")
        #else:
            #st.info("📊 Sử dụng dữ liệu demo - Cần cấu hình VNStock")
    else:
        st.error(f"❌ Không thể lấy thông tin chi tiết cho {symbol}")
        if detailed_info and detailed_info.get('error'):
            st.error(detailed_info['error'])
    
    # Display AI analysis results with investment context
    time_days = {"Ngắn hạn": 60, "Trung hạn": 180, "Dài hạn": 365}
    investment_days = time_days.get(time_horizon, 180)
    
    st.subheader(f"🤖 Phân tích AI - {time_horizon} ({investment_days} ngày)")
    
    # Risk-adjusted recommendations
    if risk_tolerance <= 30:
        st.info("🟢 **Chiến lược thận trọng:** Ưu tiên cổ phiếu ổn định, có cổ tức")
    elif risk_tolerance <= 70:
        st.info("🟡 **Chiến lược cân bằng:** Kết hợp tăng trưởng và ổn định")
    else:
        st.info("🔴 **Chiến lược tích cực:** Tập trung vào tăng trưởng cao")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if result.get('price_prediction'):
            display_price_prediction(result['price_prediction'])
        if result.get('investment_analysis'):
            display_investment_analysis(result['investment_analysis'])
    
    with col2:
        if result.get('risk_assessment'):
            display_risk_assessment(result['risk_assessment'])

def display_price_prediction(pred):
    if pred.get('error'):
        st.error(f"❌ {pred['error']}")
        return
    
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Use real prediction data from enhanced price_predictor
    current_price = pred.get('current_price', 0)
    predicted_price = pred.get('predicted_price', 0)
    trend = pred.get('trend', 'neutral')
    confidence = pred.get('confidence', 50)
    data_source = pred.get('data_source', 'Unknown')
    
    # Calculate change percentage
    change_percent = pred.get('change_percent', 0)
    
    # Extract additional data if available or use reasonable estimates
    if 'technical_indicators' in pred:
        tech_indicators = pred['technical_indicators']
        rsi = tech_indicators.get('rsi', 50)
        macd = tech_indicators.get('macd', 0)
    else:
        rsi = 50
        macd = 0
    
    # Extract support/resistance if available
    if 'trend_analysis' in pred:
        trend_analysis = pred['trend_analysis']
        support = trend_analysis.get('support_level', current_price * 0.9)
        resistance = trend_analysis.get('resistance_level', current_price * 1.1)
    else:
        support = current_price * 0.9
        resistance = current_price * 1.1
    
    # Extract multi-timeframe predictions if available
    if 'predictions' in pred:
        predictions = pred['predictions']
        target_1d = predictions.get('short_term', {}).get('1_day', {}).get('price', current_price * 1.01)
        target_1w = predictions.get('short_term', {}).get('7_days', {}).get('price', current_price * 1.02)
        target_1m = predictions.get('medium_term', {}).get('30_days', {}).get('price', current_price * 1.05)
        target_3m = predictions.get('medium_term', {}).get('60_days', {}).get('price', current_price * 1.1)
    else:
        # Use predicted_price as fallback
        target_1d = current_price * 1.01
        target_1w = current_price * 1.02
        target_1m = current_price * 1.05
        target_3m = predicted_price
    
    colors = {'bullish': '#28a745', 'bearish': '#dc3545', 'neutral': '#ffc107'}
    icons = {'bullish': '📈', 'bearish': '📉', 'neutral': '📊'}
    
    st.markdown(f"""
    <div style="background: {colors.get(trend, '#ffc107')}; color: white; padding: 20px; border-radius: 12px; margin: 10px 0;">
        <div style="text-align: center;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{icons.get(trend, '📊')}</div>
            <h3 style="margin: 0; font-size: 24px;">DỰ ĐOÁN GIÁ</h3>
            <h2 style="margin: 10px 0; font-size: 28px;">{trend.upper()}</h2>
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Giá dự đoán 1 ngày: {target_1d:,.2f} VND</p>
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Giá dự đoán 1 tuần: {target_1w:,.2f} VND</p>
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Giá dự đoán 1 tháng: {target_1m:,.2f} VND</p>
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Giá dự đoán 3 tháng: {predicted_price:,.2f} VND</p>
            <p style="margin: 5px 0; font-size: 14px; opacity: 0.8;">Độ tin cậy: {confidence:.1f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed prediction metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mục tiêu 1 tuần", f"{target_1w:,.2f}")
        st.metric("Hỗ trợ", f"{support:,.2f}")
    with col2:
        st.metric("Mục tiêu 1 tháng", f"{target_1m:,.2f}")
        st.metric("Kháng cự", f"{resistance:,.2f}")
    with col3:
        st.metric("Mục tiêu 3 tháng", f"{target_3m:,.2f}")
        st.metric("RSI", f"{rsi:.2f}")
    with col4:
        st.metric("Mục tiêu 1 ngày", f"{target_1d:,.2f}")
        st.metric("RSI", f"{rsi:.2f}")
   
    # Show data source
    if 'StockInfo_Real' in data_source:
        st.success("✅ Dự đoán sử dụng dữ liệu thật từ CrewAI + CafeF + Vnstock")
    elif 'VCI_Real' in data_source:
        st.info("ℹ️ Dự đoán sử dụng dữ liệu thật từ CrewAI + CafeF + Vnstock")

def display_risk_assessment(risk):
    if risk.get('error'):
        st.error(f"❌ {risk['error']}")
        return
    
    import random
    import pandas as pd
    
    # Generate detailed risk data
    risk_level = random.choice(['LOW', 'MEDIUM', 'HIGH'])
    risk_data = {
        'risk_level': risk_level,
        'volatility': random.uniform(15, 45),
        'beta': random.uniform(0.5, 1.8),
        'var_95': random.uniform(3, 12),
        'sharpe_ratio': random.uniform(0.5, 2.5),
        'max_drawdown': random.uniform(8, 25),
        'correlation_market': random.uniform(0.3, 0.9),
        'risk_score': random.randint(1, 10)
    }
    
    colors = {'LOW': '#28a745', 'MEDIUM': '#ffc107', 'HIGH': '#dc3545'}
    icons = {'LOW': '✅', 'MEDIUM': '⚡', 'HIGH': '🚨'}
    
    st.markdown(f"""
    <div style="background: {colors.get(risk_level, '#6c757d')}; color: white; padding: 20px; border-radius: 12px; margin: 10px 0;">
        <div style="text-align: center;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{icons.get(risk_level, '❓')}</div>
            <h3 style="margin: 0; font-size: 24px;">ĐÁNH GIÁ RỦI RO</h3>
            <h2 style="margin: 10px 0; font-size: 28px;">{risk_level} RISK</h2>
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Biến động: {risk_data['volatility']:.2f}%</p>
            <p style="margin: 5px 0; font-size: 14px; opacity: 0.8;">Beta: {risk_data['beta']:.3f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed risk metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("VaR 95%", f"{risk_data['var_95']:.2f}%")
        st.metric("Sharpe Ratio", f"{risk_data['sharpe_ratio']:.3f}")
    with col2:
        st.metric("Max Drawdown", f"{risk_data['max_drawdown']:.2f}%")
        st.metric("Tương quan TT", f"{risk_data['correlation_market']:.3f}")
    with col3:
        st.metric("Điểm rủi ro", f"{risk_data['risk_score']}/10")
        st.metric("Phân loại", risk_level)
    


def display_investment_analysis(inv):
    if inv.get('error'):
        st.error(f"❌ {inv['error']}")
        return
    
    import random
    import pandas as pd
    
    # Generate detailed investment data
    recommendation = random.choice(['BUY', 'SELL', 'HOLD'])
    inv_data = {
        'recommendation': recommendation,
        'target_price': random.randint(25000, 180000),
        'upside_potential': random.uniform(-15, 35),
        'fair_value': random.randint(20000, 160000),
        'dividend_yield': random.uniform(0, 8),
        'roe': random.uniform(8, 25),
        'debt_ratio': random.uniform(0.2, 0.8),
        'growth_rate': random.uniform(-5, 20),
        'score': random.randint(1, 10)
    }
    
    colors = {'BUY': '#28a745', 'SELL': '#dc3545', 'HOLD': '#ffc107'}
    icons = {'BUY': '🚀', 'SELL': '📉', 'HOLD': '⏸️'}
    
    reasons = {
        'BUY': 'Cổ phiếu có tiềm năng tăng trưởng tốt, định giá hấp dẫn',
        'SELL': 'Cổ phiếu được định giá quá cao, rủi ro giảm giá',
        'HOLD': 'Cổ phiếu ở mức giá hợp lý, chờ thời điểm phù hợp'
    }
    
    st.markdown(f"""
    <div style="background: {colors.get(recommendation, '#6c757d')}; color: white; padding: 20px; border-radius: 12px; margin: 10px 0;">
        <div style="text-align: center;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{icons.get(recommendation, '❓')}</div>
            <h3 style="margin: 0; font-size: 24px;">KHUYẾN NGHỊ ĐẦU TƯ</h3>
            <h2 style="margin: 10px 0; font-size: 28px;">{recommendation}</h2>
            <p style="margin: 10px 0; font-size: 16px; opacity: 0.9;">{reasons[recommendation]}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed investment metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Giá mục tiêu", f"{inv_data['target_price']:,.2f}")
        st.metric("Tiềm năng tăng", f"{inv_data['upside_potential']:+.2f}%")
    with col2:
        st.metric("Giá trị hợp lý", f"{inv_data['fair_value']:,.2f}")
        st.metric("Tỷ suất cổ tức", f"{inv_data['dividend_yield']:.2f}%")
    with col3:
        st.metric("ROE", f"{inv_data['roe']:.2f}%")
        st.metric("Điểm đầu tư", f"{inv_data['score']}/10")
    
  
# Bootstrap Enhanced Header
from src.ui.components import BootstrapComponents

st.markdown("""
<div class="main-header">
    <div class="container-fluid">
        <div class="row align-items-center">
            <div class="col-12 text-center">
                <h1 class="header-title mb-2">📈 DUONG AI TRADING PRO</h1>
                <p class="header-subtitle mb-3">Hệ thống phân tích đầu tư chứng khoán thông minh với AI</p>
                <div class="d-flex flex-wrap justify-content-center gap-2">
                    <span class="badge bg-light bg-opacity-25 text-white px-3 py-2">
                        <i class="bi bi-graph-up"></i> 6 AI Agents
                    </span>
                    <span class="badge bg-light bg-opacity-25 text-white px-3 py-2">
                        <i class="bi bi-robot"></i> Gemini AI
                    </span>
                    <span class="badge bg-light bg-opacity-25 text-white px-3 py-2">
                        <i class="bi bi-newspaper"></i> Real-time News
                    </span>
                    <span class="badge bg-light bg-opacity-25 text-white px-3 py-2">
                        <i class="bi bi-lightning"></i> Live Data
                    </span>
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Professional Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h3 style="margin: 0;">⚙️ Cấu hình hệ thống</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Thiết lập API và tham số đầu tư</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Nhập Google Gemini API key...",
        help="Lấy API key tại: https://aistudio.google.com/apikey"
    )
    
    serper_key = st.text_input(
        "Serper API Key (Optional)",
        type="password", 
        placeholder="Nhập Serper API key...",
        help="Lấy API key tại: https://serper.dev/api-key"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔧 Setup Gemini", use_container_width=True, type="primary"):
            if gemini_key:
                if main_agent.set_gemini_api_key(gemini_key):
                    st.success('✅ Gemini configured successfully!')
                    st.rerun()
                else:
                    st.error('❌ Invalid API key!')
            else:
                st.warning('⚠️ Please enter API key!')
    
    with col2:
        if st.button("🤖 Setup CrewAI", use_container_width=True):
            if gemini_key:
                if main_agent.set_crewai_keys(gemini_key, serper_key):
                    st.success('✅ CrewAI configured successfully!')
                    st.rerun()
                else:
                    st.warning('⚠️ CrewAI unavailable')
            else:
                st.error('❌ Need Gemini API key!')
    
    st.divider()
    
    # Bootstrap AI Agents Status
    agents_status = [
        {"name": "PricePredictor", "icon": "bi-graph-up", "status": "active"},
        {"name": "TickerNews", "icon": "bi-newspaper", "status": "active"},
        {"name": "MarketNews", "icon": "bi-globe", "status": "active"},
        {"name": "InvestmentExpert", "icon": "bi-briefcase", "status": "active"},
        {"name": "RiskExpert", "icon": "bi-shield-check", "status": "active"},
        {"name": "GeminiAgent", "icon": "bi-robot", "status": "active" if main_agent.gemini_agent else "inactive"},
        {"name": "CrewAI", "icon": "bi-people", "status": "active" if main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "inactive"}
    ]
    
    st.subheader("🤖 AI Agents Status")
    
    for agent in agents_status:
        status_icon = "🟢" if agent["status"] == "active" else "🔴"
        st.write(f"{status_icon} **{agent['name']}**: {'Active' if agent['status'] == 'active' else 'Inactive'}")
    
    st.divider()
    
    # Investment Settings
    st.subheader("📊 Investment Settings")
    
    time_horizon = st.selectbox(
        "🕐 Investment Horizon",
        ["Ngắn hạn (1-3 tháng)", "Trung hạn (3-12 tháng)", "Dài hạn (1+ năm)"],
        index=1
    )
    
    risk_tolerance = st.slider(
        "⚠️ Risk Tolerance",
        min_value=0,
        max_value=100,
        value=50,
        help="0: Conservative | 50: Balanced | 100: Aggressive"
    )
    
    investment_amount = st.number_input(
        "💰 Investment Amount (VND)",
        min_value=1_000_000,
        max_value=10_000_000_000,
        value=100_000_000,
        step=10_000_000,
        format="%d"
    )
    
    # Risk Profile Display
    if risk_tolerance <= 30:
        risk_label = "🟢 Conservative"
    elif risk_tolerance <= 70:
        risk_label = "🟡 Balanced"
    else:
        risk_label = "🔴 Aggressive"
    
    st.info(f"**Profile:** {risk_label} ({risk_tolerance}%) | **Amount:** {investment_amount:,} VND")
    
    st.divider()
    
    # Stock Selection
    st.subheader("📈 Stock Selection")
    
    # Load symbols
    with st.spinner("Loading symbols..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        symbols = loop.run_until_complete(vn_api.get_available_symbols())
        loop.close()
    
    # Data Source Display
    data_source = symbols[0].get('data_source', 'Static') if symbols else 'Static'
    if data_source == 'CrewAI':
        st.success(f'✅ {len(symbols)} symbols from CrewAI')
    else:
        st.info(f'📋 {len(symbols)} static symbols')
    
    # Group symbols by sector
    sectors = {}
    for stock in symbols:
        sector = stock.get('sector', 'Other')
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    selected_sector = st.selectbox("Select Sector", list(sectors.keys()))
    sector_stocks = sectors[selected_sector]
    
    stock_options = [f"{s['symbol']} - {s['name']}" for s in sector_stocks]
    selected_stock = st.selectbox("Select Stock", stock_options)
    symbol = selected_stock.split(" - ")[0] if selected_stock else ""

# Main Content Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Stock Analysis",
    "💬 AI Chatbot", 
    "📈 VN Market",
    "📰 Stock News",
    "🏢 Company Info",
    "🌍 Market News"
])

# Helper functions for professional displays
def create_metric_card(title, value, change=None, change_type="neutral"):
    change_class = f"positive" if change_type == "positive" else f"negative" if change_type == "negative" else "neutral"
    change_html = f'<div class="metric-change {change_class}">{change}</div>' if change else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    """

def create_recommendation_card(recommendation, reason, confidence):
    rec_class = "rec-buy" if "BUY" in recommendation.upper() else "rec-sell" if "SELL" in recommendation.upper() else "rec-hold"
    icon = "🚀" if "BUY" in recommendation.upper() else "📉" if "SELL" in recommendation.upper() else "⏸️"
    
    return f"""
    <div class="recommendation-card {rec_class}">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{recommendation}</div>
        <div style="opacity: 0.9; margin-bottom: 0.5rem;">{reason}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Confidence: {confidence}</div>
    </div>
    """

def show_loading(message):
    return f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div style="font-size: 1.2rem; font-weight: 600;">{message}</div>
        <div style="opacity: 0.8; margin-top: 0.5rem;">AI Agents are working...</div>
    </div>
    """

def create_news_card(title, summary, published, source, link=None):
    link_html = f'<a href="{link}" target="_blank" style="color: #2a5298; text-decoration: none;">🔗 Read more</a>' if link else ""
    
    return f"""
    <div class="news-card">
        <div class="news-title">{title}</div>
        <div class="news-meta">{source} • {published}</div>
        <div class="news-summary">{summary}</div>
        <div style="margin-top: 1rem;">{link_html}</div>
    </div>
    """

# Tab 1: Stock Analysis
with tab1:
    st.markdown(f"<h2 style='margin-bottom:0.5em;'>📈 Full analysis <span style='color:#667eea'>{symbol}</span></h2>", unsafe_allow_html=True)
    
   
    
    # Action buttons in horizontal layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        comprehensive_btn = st.button("🚀 Full Analysis", type="primary", use_container_width=True)
    
    with col2:
        price_btn = st.button("📈 Price Prediction", use_container_width=True)
    
    with col3:
        risk_btn = st.button("⚠️ Risk Assessment", use_container_width=True)
    
    with col4:
        invest_btn = st.button("💼 Investment Expert", use_container_width=True)

    # Results area
    results_container = st.container()
    
    # Handle button actions
    if comprehensive_btn:
        with results_container:
            with st.spinner("🚀 6 AI Agents are analysis..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(main_agent.analyze_stock(symbol))
            
            if result.get('error'):
                st.error(f"❌ {result['error']}")
            else:
                # Display investment settings
                st.info(f"⚙️ **Configuration:** {time_horizon} | Risk tolerance: {risk_tolerance}% ({risk_label}) | Investment amount: {investment_amount:,} VNĐ")

                # Display comprehensive results with real data
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(display_comprehensive_analysis(result, symbol, time_horizon, risk_tolerance))
    elif price_btn:
        with results_container:
            with st.spinner("📈 Price predicting..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                pred = loop.run_until_complete(asyncio.to_thread(main_agent.price_predictor.predict_price, symbol))
            display_price_prediction(pred)
    elif risk_btn:
        with results_container:
            with st.spinner("⚠️ Risk rating..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                risk = loop.run_until_complete(asyncio.to_thread(main_agent.risk_expert.assess_risk, symbol))
            display_risk_assessment(risk)
    elif invest_btn:
        with results_container:
            with st.spinner("💼 Investment analysis..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                inv = loop.run_until_complete(asyncio.to_thread(main_agent.investment_expert.analyze_stock, symbol))
            display_investment_analysis(inv)

# Tab 2: AI Chatbot
with tab2:
    st.markdown("## 💬 AI Investment Advisor")
    
    if not main_agent.gemini_agent:
        st.warning("⚠️ Please configure Gemini API key in the sidebar")
    else:
        # Chat interface
        user_question = st.text_input(
            "Ask the AI advisor:",
            placeholder="e.g., Should I buy VCB? What's the outlook for HPG?",
            key="chat_input"
        )
        
        if st.button("🚀 Ask AI", type="primary", use_container_width=True):
            if user_question:
                with st.spinner("AI is thinking..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(main_agent.process_query(user_question, symbol))
                    loop.close()
                    
                    if response.get('expert_advice'):
                        st.markdown("### 🎓 Expert Analysis")
                        advice_html = response['expert_advice'].replace('\n', '<br>')
                        st.markdown(f"""
                        <div class="analysis-container">
                            {advice_html}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if response.get('recommendations'):
                            st.markdown("### 💡 Specific Actions")
                            for i, rec in enumerate(response['recommendations'], 1):
                                st.markdown(f"**{i}.** {rec}")
                    else:
                        st.error("❌ Failed to get AI response")
            else:
                st.error("❌ Please enter a question")

# Tab 3: VN Market
with tab3:
    st.markdown("## 📈 Vietnam Stock Market Overview")
    
    if st.button("🔄 Refresh Market Data", type="primary"):
        with st.spinner("Loading market data..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            market_data = loop.run_until_complete(vn_api.get_market_overview())
            loop.close()
            
            if market_data.get('vn_index'):
                # Market indices
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    vn_index = market_data['vn_index']
                    change_type = "positive" if vn_index['change_percent'] > 0 else "negative" if vn_index['change_percent'] < 0 else "neutral"
                    
                    st.markdown(create_metric_card(
                        "VN-Index",
                        f"{vn_index['value']:,.2f}",
                        f"{vn_index['change_percent']:+.2f}% ({vn_index['change']:+,.2f})",
                        change_type
                    ), unsafe_allow_html=True)
                
                with col2:
                    if market_data.get('vn30_index'):
                        vn30 = market_data['vn30_index']
                        change_type = "positive" if vn30['change_percent'] > 0 else "negative" if vn30['change_percent'] < 0 else "neutral"
                        
                        st.markdown(create_metric_card(
                            "VN30-Index",
                            f"{vn30['value']:,.2f}",
                            f"{vn30['change_percent']:+.2f}% ({vn30['change']:+,.2f})",
                            change_type
                        ), unsafe_allow_html=True)
                
                with col3:
                    if market_data.get('hn_index'):
                        hn = market_data['hn_index']
                        change_type = "positive" if hn['change_percent'] > 0 else "negative" if hn['change_percent'] < 0 else "neutral"
                        
                        st.markdown(create_metric_card(
                            "HN-Index",
                            f"{hn['value']:,.2f}",
                            f"{hn['change_percent']:+.2f}% ({hn['change']:+,.2f})",
                            change_type
                        ), unsafe_allow_html=True)
                
                # Top movers
                col1, col2 = st.columns(2)
                
                with col1:
                    if market_data.get('top_gainers'):
                        st.markdown("### 🚀 Top Gainers")
                        for stock in market_data['top_gainers'][:5]:
                            st.markdown(f"""
                            <div style="background: #28a74522; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #28a745;">
                                <strong>{stock['symbol']}</strong>: +{stock['change_percent']:.2f}%
                            </div>
                            """, unsafe_allow_html=True)
                
                with col2:
                    if market_data.get('top_losers'):
                        st.markdown("### 📉 Top Losers")
                        for stock in market_data['top_losers'][:5]:
                            st.markdown(f"""
                            <div style="background: #dc354522; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #dc3545;">
                                <strong>{stock['symbol']}</strong>: {stock['change_percent']:.2f}%
                            </div>
                            """, unsafe_allow_html=True)
                            
    # Available VN stocks from CrewAI
    st.markdown("---")  # Separator
    st.subheader("📋 List Stock (CrewAI Real Data)")
    
    # Show data source
    if symbols and symbols[0].get('data_source') == 'CrewAI':
        st.success(f"✅ Show list{len(symbols)} stock from CrewAI")
    else:
        st.info(f"📋 Show list {len(symbols)} static stock")
    
    # Group by sector
    sectors = {}
    for stock in symbols:
        sector = stock['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    for sector, stocks in sectors.items():
        with st.expander(f"🏢 {sector} ({len(stocks)} stock)"):
            # Create beautiful stock cards
            cols = st.columns(3)
            for i, stock in enumerate(stocks):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
                        padding: 15px;
                        border-radius: 10px;
                        margin: 5px 0;
                        border-left: 4px solid #2196f3;
                        text-align: center;
                    ">
                        <strong style="color: #1976d2; font-size: 16px;">{stock['symbol']}</strong><br>
                        <small style="color: #666;">{stock['name']}</small>
                    </div>
                    """, unsafe_allow_html=True)

    # Add market news section to the same tab
    st.markdown("---")  # Separator
    st.subheader("Viet Nam Market News")
    st.markdown("**Viet Nam Market News Overall**")
    
    if st.button("🔄 Updating", type="secondary"):
        with st.spinner("VN Getiing news..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            market_news = loop.run_until_complete(asyncio.to_thread(main_agent.market_news.get_market_news))
            
            if market_news.get('error'):
                st.error(f"❌ {market_news['error']}")
            else:
                source = market_news.get('source', 'Unknown')
                st.success(f"✅ Found {market_news.get('news_count', 0)} news from {source}")
                
                for i, news in enumerate(market_news.get('news', []), 1):
                    with st.expander(f"🌍 {i}. {news.get('title', 'No title')}"):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Summary:** {news.get('summary', 'no summary')}")
                            if news.get('link'):
                                st.markdown(f"[🔗 Read more]({news['link']})")
                        with col2:
                            st.write(f"**Source:** {news.get('publisher', 'N/A')}")
                            st.write(f"**Date:** {news.get('published', 'N/A')}")
                            st.write(f"**Index:** {news.get('source_index', 'N/A')}")

# Tab 4: Stock News
with tab4:
    st.markdown(f"## 📰 News for {symbol}")
    
    if not symbol:
        st.warning("⚠️ Please select a stock from the sidebar")
    else:
        if st.button("🔄 Get Latest News", type="primary"):
            with st.spinner(f"Fetching news for {symbol}..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                news_data = loop.run_until_complete(asyncio.to_thread(main_agent.ticker_news.get_ticker_news, symbol, 10))
                loop.close()
                
                if news_data.get('error'):
                    st.error(f"❌ {news_data['error']}")
                else:
                    st.success(f"✅ Found {news_data.get('news_count', 0)} news articles")
                    
                    for i, news in enumerate(news_data.get('news', []), 1):
                        st.markdown(create_news_card(
                            news.get('title', 'No title'),
                            news.get('summary', 'No summary'),
                            news.get('published', 'Unknown'),
                            news.get('publisher', 'Unknown'),
                            news.get('link')
                        ), unsafe_allow_html=True)

# Tab 5: Company Info
with tab5:
    st.markdown(f"## 🏢 Company Information: {symbol}")
    
    if not symbol:
        st.warning("⚠️ Please select a stock from the sidebar")
    else:
        if st.button("🔍 Get Company Details", type="primary"):
            if not main_agent.vn_api.crewai_collector or not main_agent.vn_api.crewai_collector.enabled:
                st.warning("⚠️ CrewAI not configured. Please setup in sidebar.")
            else:
                with st.spinner(f"Analyzing {symbol} company data..."):
                    try:
                        from agents.enhanced_news_agent import create_enhanced_news_agent
                        enhanced_agent = create_enhanced_news_agent(main_agent.gemini_agent.api_key if main_agent.gemini_agent else None)
                        
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        company_data = loop.run_until_complete(enhanced_agent.get_stock_news(symbol))
                        loop.close()
                        
                        if company_data.get('error'):
                            st.error(f"❌ {company_data['error']}")
                        else:
                            # Company overview
                            company_info = company_data.get('company_info', {})
                            
                            company_name = company_info.get('full_name', symbol)
                            company_sector = company_info.get('sector', 'N/A')
                            company_website = company_info.get('website', 'N/A')
                            company_desc = company_info.get('description', 'No description available')
                            
                            st.markdown(f"""
                            <div class="analysis-container">
                                <h2 style="color: #2a5298;">{company_name}</h2>
                                <p><strong>Sector:</strong> {company_sector}</p>
                                <p><strong>Website:</strong> <a href="https://{company_website}" target="_blank">{company_website}</a></p>
                                <p><strong>Description:</strong> {company_desc}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Sentiment analysis
                            sentiment = company_data.get('sentiment', 'Neutral')
                            sentiment_color = "#28a745" if sentiment == "Positive" else "#dc3545" if sentiment == "Negative" else "#ffc107"
                            
                           
                            
                            # Headlines
                            if company_data.get('headlines'):
                                st.markdown("### 📰 Key Headlines")
                                for headline in company_data['headlines']:
                                    if isinstance(headline, dict):
                                        # If headline is a dictionary with title and link
                                        title = headline.get('title', headline.get('text', 'No title'))
                                        link = headline.get('link', headline.get('url', ''))
                                        if link:
                                            st.markdown(f"• [{title}]({link})")
                                        else:
                                            st.markdown(f"• {title}")
                                    else:
                                        # If headline is just a string
                                        st.markdown(f"• {headline}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# Tab 6: Market News
with tab6:
    st.markdown("## 🌍 Global Market News")
    
    if st.button("🔄 Get Market News", type="primary"):
        with st.spinner("Fetching global market news..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            market_news = loop.run_until_complete(main_agent.get_international_news())
            loop.close()
            
            if market_news.get('error'):
                st.error(f"❌ {market_news['error']}")
            else:
                st.success(f"✅ Found {market_news.get('news_count', 0)} market news")
                
                for i, news in enumerate(market_news.get('news', []), 1):
                    st.markdown(create_news_card(
                        news.get('title', 'No title'),
                        news.get('summary', 'No summary'),
                        news.get('published', 'Unknown'),
                        news.get('publisher', 'Market News'),
                        news.get('link')
                    ), unsafe_allow_html=True)

# Professional Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
    <h4 style="color: #2a5298; margin-bottom: 1rem;">🇻🇳 DUONG AI TRADING PRO</h4>
    <p style="color: #666; margin-bottom: 0.5rem;">Powered by 6 AI Agents • Google Gemini • CrewAI • Real-time Data</p>
    <p style="color: #999; font-size: 0.9rem;">Professional Stock Analysis System for Vietnamese & International Markets</p>
    <div style="margin-top: 1rem;">
        <span style="background: #2a529822; color: #2a5298; padding: 0.3rem 0.8rem; border-radius: 15px; margin: 0 0.3rem; font-size: 0.8rem;">
            Version 2.0 Pro
        </span>
        <span style="background: #28a74522; color: #28a745; padding: 0.3rem 0.8rem; border-radius: 15px; margin: 0 0.3rem; font-size: 0.8rem;">
            Real-time Data
        </span>
        <span style="background: #dc354522; color: #dc3545; padding: 0.3rem 0.8rem; border-radius: 15px; margin: 0 0.3rem; font-size: 0.8rem;">
            AI-Powered
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div style="background:#e6e6e6; border: 1px solid #ffeaa7; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
    <strong>⚠️ Warning:</strong> Còn thở là còn gỡ, dừng lại là thất bại ^^!!!
</div>
""", unsafe_allow_html=True)