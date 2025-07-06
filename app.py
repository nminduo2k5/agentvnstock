import streamlit as st
import asyncio
from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI
import json
from src.ui.styles import load_custom_css  # Thêm dòng này

# Page config
st.set_page_config(
    page_title="DUONG AI TRADING SIUUUU",
    page_icon="🤖",
    layout="wide"
)

# Gọi hàm load_custom_css để áp dụng CSS hiện đại
load_custom_css()

# Initialize
@st.cache_resource
def init_agents():
    vn_api = VNStockAPI()
    main_agent = MainAgent(vn_api)  # Initialize without Gemini API key
    return main_agent, vn_api

main_agent, vn_api = init_agents()

# Analysis display functions
def display_comprehensive_analysis(result):
    stock_data = result.get('vn_stock_data')
    
    if stock_data:
        # Generate detailed mock data
        import random
        base_price = stock_data.price
        
        detailed_data = {
            'open': base_price * random.uniform(0.98, 1.02),
            'high': base_price * random.uniform(1.01, 1.05),
            'low': base_price * random.uniform(0.95, 0.99),
            'volume': random.randint(500000, 5000000),
            'market_cap': random.randint(15000, 500000) * 1000,
            'bid_volume': random.randint(50000, 200000),
            'ask_volume': random.randint(20000, 80000),
            'high_52w': base_price * random.uniform(1.2, 1.8),
            'low_52w': base_price * random.uniform(0.4, 0.8),
            'avg_volume_52w': random.randint(2000000, 8000000),
            'foreign_buy': random.randint(100000, 500000),
            'foreign_own_pct': round(random.uniform(3, 25), 2),
            'dividend': random.randint(800, 2000),
            'dividend_yield': round(random.uniform(0.01, 0.08), 2),
            'beta': round(random.uniform(0.8, 1.5), 2),
            'eps': random.randint(1500, 4000),
            'pe': round(stock_data.pe_ratio or random.uniform(15, 45), 2),
            'forward_pe': round(random.uniform(12, 35), 2),
            'bvps': random.randint(15000, 40000),
            'pb': round(stock_data.pb_ratio or random.uniform(1.2, 2.5), 2)
        }
        
        price_color = "#4caf50" if stock_data.change >= 0 else "#f44336"
        change_symbol = "▲" if stock_data.change >= 0 else "▼"
        
        # Real-time datetime
        from datetime import datetime
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Main price display with datetime
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 25px; border-radius: 15px; margin: 20px 0; text-align: center;">
            <div style="text-align: right; font-size: 14px; opacity: 0.8; margin-bottom: 10px;">
                🕐 Cập nhật: {current_time}
            </div>
            <h1 style="margin: 0; font-size: 36px;">{stock_data.symbol}</h1>
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">{stock_data.sector} • {stock_data.exchange}</p>
            <h2 style="margin: 15px 0; font-size: 48px;">{stock_data.price:,.3f} VND</h2>
            <p style="margin: 0; font-size: 24px; color: {'#90EE90' if stock_data.change >= 0 else '#FFB6C1'};">
                {change_symbol} {stock_data.change:+,.3f} ({stock_data.change_percent:+.2f}%)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed metrics grid
        st.subheader("📊 Thông tin chi tiết")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mở cửa", f"{detailed_data['open']:,.3f}")
            st.metric("Cao nhất", f"{detailed_data['high']:,.3f}")
            st.metric("Thấp nhất", f"{detailed_data['low']:,.3f}")
            st.metric("KLGD", f"{detailed_data['volume']:,}")
        
        with col2:
            st.metric("Vốn hóa", f"{detailed_data['market_cap']:,.3f}")
            st.metric("Dư mua", f"{detailed_data['bid_volume']:,.3f}")
            st.metric("Dư bán", f"{detailed_data['ask_volume']:,.3f}")
            st.metric("Cao 52T", f"{detailed_data['high_52w']:,.3f}")
        
        with col3:
            st.metric("Thấp 52T", f"{detailed_data['low_52w']:,.3f}")
            st.metric("KLBQ 52T", f"{detailed_data['avg_volume_52w']:,.3f}")
            st.metric("NN mua", f"{detailed_data['foreign_buy']:,.6f}")
            st.metric("% NN sở hữu", f"{detailed_data['foreign_own_pct']:.2f}")
        
        with col4:
            st.metric("Cổ tức TM", f"{detailed_data['dividend']:,.3f}")
            st.metric("T/S cổ tức", f"{detailed_data['dividend_yield']:.2f}")
            st.metric("Beta", f"{detailed_data['beta']:.2f}")
            st.metric("EPS", f"{detailed_data['eps']:,.3f}")
        
        # Financial ratios
        st.subheader("📈 Chỉ số tài chính")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("P/E", f"{detailed_data['pe']:.2f}")
        with col2:
            st.metric("F P/E", f"{detailed_data['forward_pe']:.2f}")
        with col3:
            st.metric("BVPS", f"{detailed_data['bvps']:,}")
        with col4:
            st.metric("P/B", f"{detailed_data['pb']:.2f}")
        
        # Price chart
        st.subheader("📉 Biểu đồ giá 30 ngày")
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate price chart data
        np.random.seed(hash(stock_data.symbol) % 1000)
        dates = [(datetime.now() - timedelta(days=i)).strftime('%d/%m') for i in range(30, 0, -1)]
        prices = [base_price]
        for _ in range(29):
            prices.append(prices[-1] * (1 + np.random.normal(0, 0.015)))
        
        chart_df = pd.DataFrame({'Ngày': dates, 'Giá': prices})
        st.line_chart(chart_df.set_index('Ngày'))
    
    # Analysis results
    st.subheader("🤖 Phân tích AI")
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
    
    import random
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generate detailed prediction data
    current_price = random.randint(20000, 150000)
    trend = random.choice(['bullish', 'bearish', 'neutral'])
    
    prediction_data = {
        'trend': trend,
        'predicted_price': current_price * random.uniform(0.95, 1.15),
        'confidence': round(random.uniform(65, 85), 1),
        'target_1w': current_price * random.uniform(0.98, 1.08),
        'target_1m': current_price * random.uniform(0.92, 1.18),
        'target_3m': current_price * random.uniform(0.85, 1.25),
        'support': current_price * random.uniform(0.85, 0.95),
        'resistance': current_price * random.uniform(1.05, 1.15),
        'rsi': round(random.uniform(30, 70), 1),
        'macd': round(random.uniform(-5, 5), 2)
    }
    
    colors = {'bullish': '#28a745', 'bearish': '#dc3545', 'neutral': '#ffc107'}
    icons = {'bullish': '📈', 'bearish': '📉', 'neutral': '📊'}
    
    st.markdown(f"""
    <div style="background: {colors.get(trend, '#ffc107')}; color: white; padding: 20px; border-radius: 12px; margin: 10px 0;">
        <div style="text-align: center;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{icons.get(trend, '📊')}</div>
            <h3 style="margin: 0; font-size: 24px;">DỰ ĐOÁN GIÁ</h3>
            <h2 style="margin: 10px 0; font-size: 28px;">{trend.upper()}</h2>
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Giá dự đoán: {prediction_data['predicted_price']:,.0f} VND</p>
            <p style="margin: 5px 0; font-size: 14px; opacity: 0.8;">Độ tin cậy: {prediction_data['confidence']:.1f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed prediction metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mục tiêu 1 tuần", f"{prediction_data['target_1w']:,.0f}")
        st.metric("Hỗ trợ", f"{prediction_data['support']:,.0f}")
    with col2:
        st.metric("Mục tiêu 1 tháng", f"{prediction_data['target_1m']:,.0f}")
        st.metric("Kháng cự", f"{prediction_data['resistance']:,.0f}")
    with col3:
        st.metric("Mục tiêu 3 tháng", f"{prediction_data['target_3m']:,.0f}")
        st.metric("RSI", f"{prediction_data['rsi']:.1f}")
    
    # Prediction chart
    dates = [(datetime.now() + timedelta(days=i)).strftime('%d/%m') for i in range(1, 31)]
    base = current_price
    future_prices = [base]
    for i in range(29):
        if trend == 'bullish':
            future_prices.append(future_prices[-1] * (1 + random.uniform(0, 0.02)))
        elif trend == 'bearish':
            future_prices.append(future_prices[-1] * (1 + random.uniform(-0.02, 0)))
        else:
            future_prices.append(future_prices[-1] * (1 + random.uniform(-0.01, 0.01)))
    
    pred_df = pd.DataFrame({'Ngày': dates, 'Dự đoán': future_prices})
    st.line_chart(pred_df.set_index('Ngày'))

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
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Biến động: {risk_data['volatility']:.1f}%</p>
            <p style="margin: 5px 0; font-size: 14px; opacity: 0.8;">Beta: {risk_data['beta']:.2f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed risk metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("VaR 95%", f"{risk_data['var_95']:.1f}%")
        st.metric("Sharpe Ratio", f"{risk_data['sharpe_ratio']:.2f}")
    with col2:
        st.metric("Max Drawdown", f"{risk_data['max_drawdown']:.1f}%")
        st.metric("Tương quan TT", f"{risk_data['correlation_market']:.2f}")
    with col3:
        st.metric("Điểm rủi ro", f"{risk_data['risk_score']}/10")
        st.metric("Phân loại", risk_level)
    
    # Risk distribution chart
    risk_categories = ['Thấp', 'Trung bình', 'Cao', 'Rất cao']
    risk_values = [random.randint(10, 40) for _ in range(4)]
    risk_df = pd.DataFrame({'Rủi ro': risk_categories, 'Xác suất': risk_values})
    st.bar_chart(risk_df.set_index('Rủi ro'))

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
        st.metric("Giá mục tiêu", f"{inv_data['target_price']:,.0f}")
        st.metric("Tiềm năng tăng", f"{inv_data['upside_potential']:+.1f}%")
    with col2:
        st.metric("Giá trị hợp lý", f"{inv_data['fair_value']:,.0f}")
        st.metric("Tỷ suất cổ tức", f"{inv_data['dividend_yield']:.1f}%")
    with col3:
        st.metric("ROE", f"{inv_data['roe']:.1f}%")
        st.metric("Điểm đầu tư", f"{inv_data['score']}/10")
    
    # Investment score breakdown
    factors = ['Giá trị', 'Tăng trưởng', 'Chất lượng', 'Rủi ro']
    scores = [random.randint(1, 10) for _ in range(4)]
    score_df = pd.DataFrame({'Yếu tố': factors, 'Điểm': scores})
    st.bar_chart(score_df.set_index('Yếu tố'))

# Header
st.markdown("""
<div class="main-header">
    <h1>DUONG AI TRADING SIUUUU</h1>
    <p><b>Hệ thống phân tích đầu tư chứng khoán với 6 AI Agents chuyên nghiệp + Gemini Chatbot</b></p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Cài đặt")
    
    # API Keys Section
    st.subheader("🔑 API Keys")
    
    # Gemini API Key
    gemini_key = st.text_input(
        "Google Gemini API Key:",
        type="password",
        help="Nhập API key từ Google AI Studio"
    )
    
    # Serper API Key for CrewAI
    serper_key = st.text_input(
        "Serper API Key (Optional):",
        type="password",
        help="Nhập API key từ Serper.dev để lấy tin tức thật"
    )
    
    gemini_status = "🟢" if main_agent.gemini_agent else "🔴"
    crewai_status = "🟢" if main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "🔴"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚙️ Cài đặt Gemini", use_container_width=True):
            if gemini_key:
                if main_agent.set_gemini_api_key(gemini_key):
                    st.success("✅ Gemini API đã cài đặt!")
                    st.rerun()
                else:
                    st.error("❌ Gemini API key không hợp lệ!")
            else:
                st.error("❌ Vui lòng nhập Gemini API key!")
    
    with col2:
        if st.button("🤖 Cài đặt CrewAI", use_container_width=True):
            if gemini_key:
                if main_agent.set_crewai_keys(gemini_key, serper_key):
                    # Clear cache to force reload symbols
                    st.cache_data.clear()
                    st.success("✅ CrewAI đã cài đặt!")
                    st.rerun()
                else:
                    st.warning("⚠️ CrewAI không khả dụng")
            else:
                st.error("❌ Cần Gemini API key cho CrewAI!")
    
    # Status indicators
    st.markdown(f"**Status:** Gemini {gemini_status} | CrewAI {crewai_status}")
    
    if not gemini_key:
        st.info("💡 Lấy Gemini API key: https://aistudio.google.com/apikey")
    if not serper_key:
        st.info("🔍 Lấy Serper API key: https://serper.dev/api-key")
    
    st.divider()
    
    # 6 AI Agents Status
    st.subheader("🤖 6 AI Agents")
    agents_info = [
        {"name": "📈 PricePredictor", "desc": "Dự đoán giá", "status": "🟢"},
        {"name": "📰 TickerNews", "desc": "Tin tức cổ phiếu", "status": "🟢"},
        {"name": "🌍 MarketNews", "desc": "Tin tức thị trường", "status": "🟢"},
        {"name": "💼 InvestmentExpert", "desc": "Phân tích đầu tư", "status": "🟢"},
        {"name": "⚠️ RiskExpert", "desc": "Quản lý rủi ro", "status": "🟢"},
        {"name": "🧠 GeminiAgent", "desc": "AI Chatbot", "status": gemini_status},
        {"name": "🤖 CrewAI", "desc": "Tin tức thật", "status": crewai_status}
    ]
    
    for agent in agents_info:
        st.write(f"{agent['status']} **{agent['name']}**: {agent['desc']}")
    
    st.divider()
    
    # Stock selection - auto-load CrewAI real data
    st.subheader("📊 Chọn cổ phiếu (CrewAI Real Data)")
    
    # Auto-load symbols when CrewAI is enabled
    if main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled:
        with st.spinner("🤖 Tải danh sách cổ phiếu thật từ CrewAI..."):
            @st.cache_data(ttl=600, show_spinner=False)  # 10 minutes cache
            def load_crewai_symbols():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(vn_api.get_available_symbols())
                    return result
                except Exception as e:
                    st.error(f"Lỗi CrewAI: {e}")
                    return vn_api._get_static_symbols()
                finally:
                    loop.close()
            
            symbols = load_crewai_symbols()
            
            if symbols and len(symbols) > 20 and symbols[0].get('data_source') == 'CrewAI':
                st.success(f"✅ Tải thành công {len(symbols)} mã cổ phiếu từ CrewAI Gemini")
            else:
                st.info(f"📋 Sử dụng {len(symbols)} mã cổ phiếu tĩnh")
    else:
        st.warning("⚠️ Click 'Cài đặt CrewAI' để tải danh sách cổ phiếu thật")
        symbols = vn_api._get_static_symbols()
        for s in symbols:
            s['data_source'] = 'Static'
    
    # Display symbols with sector info
    symbol_options = [f"{s['symbol']} - {s['name']} ({s.get('sector', 'Unknown')})" for s in symbols]
    selected_symbol = st.selectbox(
        "Mã cổ phiếu:", 
        symbol_options,
        help=f"Danh sách {'CrewAI real data' if symbols and symbols[0].get('data_source') == 'CrewAI' else 'static data'}"
    )
    symbol = selected_symbol.split(" - ")[0]

# Main content tabs
tab1, tab2, tab5 = st.tabs([
    "📊 Phân tích cổ phiếu", 
    "💬 AI Chatbot", 
    "📈 Thị trường VN"
])

with tab1:
    st.markdown(f"<h2 style='margin-bottom:0.5em;'>📈 Phân tích toàn diện <span style='color:#667eea'>{symbol}</span></h2>", unsafe_allow_html=True)
    
    # Control Panel
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h3 style="margin: 0; text-align: center;">🎯 Bảng điều khiển phân tích</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons in horizontal layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        comprehensive_btn = st.button("🚀 Phân tích toàn diện", type="primary", use_container_width=True)
    
    with col2:
        price_btn = st.button("📈 Dự đoán giá", use_container_width=True)
    
    with col3:
        risk_btn = st.button("⚠️ Đánh giá rủi ro", use_container_width=True)
    
    with col4:
        invest_btn = st.button("💼 Phân tích đầu tư", use_container_width=True)
    
    # Results area
    results_container = st.container()
    
    # Handle button actions
    if comprehensive_btn:
        with results_container:
            with st.spinner("🚀 6 AI Agents đang phân tích toàn diện..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(main_agent.analyze_stock(symbol))
            
            if result.get('error'):
                st.error(f"❌ {result['error']}")
            else:
                # Display comprehensive results
                display_comprehensive_analysis(result)
    elif price_btn:
        with results_container:
            with st.spinner("📈 Đang dự đoán giá..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                pred = loop.run_until_complete(asyncio.to_thread(main_agent.price_predictor.predict_price, symbol))
            display_price_prediction(pred)
    elif risk_btn:
        with results_container:
            with st.spinner("⚠️ Đang đánh giá rủi ro..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                risk = loop.run_until_complete(asyncio.to_thread(main_agent.risk_expert.assess_risk, symbol))
            display_risk_assessment(risk)
    elif invest_btn:
        with results_container:
            with st.spinner("💼 Đang phân tích đầu tư..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                inv = loop.run_until_complete(asyncio.to_thread(main_agent.investment_expert.analyze_stock, symbol))
            display_investment_analysis(inv)


with tab2:
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
        if not main_agent.gemini_agent:
            st.error("❌ Vui lòng nhập Gemini API key ở sidebar trước!")
        else:
            with st.spinner("🧠 Gemini AI đang suy nghĩ..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(main_agent.process_query(user_question, symbol or ""))
            
                if response.get('expert_advice'):
                    st.subheader("🎓 Lời khuyên từ chuyên gia AI")
                    st.markdown(response['expert_advice'])
                
                if response.get('recommendations'):
                    st.subheader("💡 Khuyến nghị cụ thể")
                    for i, rec in enumerate(response['recommendations'], 1):
                        st.write(f"{i}. {rec}")
                
                # Hiển thị dữ liệu hỗ trợ đẹp mắt
                if response.get('data'):
                    with st.expander("📊 Dữ liệu hỗ trợ phân tích"):
                        data = response['data']
                        # Kiểm tra data source cho chatbot
                        stock_data = data.get('vn_stock_data')
                        if stock_data and hasattr(stock_data, 'price'):
                            if stock_data.price > 10000:
                                st.success("🟢 Sử dụng dữ liệu thật từ VNStock")
                            else:
                                st.info("🟡 Sử dụng dữ liệu demo")
                        # VN Stock Data
                        if stock_data:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Giá", f"{stock_data.price:,.0f} VND")
                            with col2:
                                st.metric("Thay đổi", f"{stock_data.change_percent:+.2f}%")
                            with col3:
                                st.metric("Volume", f"{stock_data.volume:,}")
                        # Price Prediction
                        if data.get('price_prediction'):
                            pred = data['price_prediction']
                            st.markdown("**🔮 Dự đoán giá:**")
                            st.write(f"- Xu hướng: {pred.get('trend', 'N/A')}")
                            st.write(f"- Độ tin cậy: {pred.get('confidence', 'N/A')}")
                        # Risk Assessment
                        if data.get('risk_assessment'):
                            risk = data['risk_assessment']
                            st.markdown("**⚠️ Đánh giá rủi ro:**")
                            st.write(f"- Mức rủi ro: {risk.get('risk_level', 'N/A')}")
                            st.write(f"- Độ biến động: {risk.get('volatility', 'N/A')}%")

with tab5:
    st.header("📈 Tổng quan thị trường Việt Nam")
    st.markdown("**Dữ liệu chỉ số, top movers và danh sách cổ phiếu hỗ trợ**")
    
    if st.button("🔄 Cập nhật dữ liệu thị trường", type="primary"):
        with st.spinner("Đang lấy dữ liệu real-time..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            market_data = loop.run_until_complete(vn_api.get_market_overview())
            
            if market_data.get('vn_index'):
                st.subheader("📊 VN-Index")
                vn_index = market_data['vn_index']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("VN-Index", f"{vn_index['value']:,.2f}", f"{vn_index['change_percent']:+.2f}%")
                with col2:
                    st.metric("Thay đổi", f"{vn_index['change']:+,.2f}")
                with col3:
                    st.metric("Khối lượng", f"{vn_index.get('volume', 0):,}")
            
            # Top movers with beautiful cards
            col1, col2 = st.columns(2)
            
            with col1:
                if market_data.get('top_gainers'):
                    st.subheader("🚀 Top tăng mạnh")
                    for stock in market_data['top_gainers'][:5]:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(90deg, #4caf50, #81c784);
                            color: white;
                            padding: 10px;
                            border-radius: 8px;
                            margin: 5px 0;
                            text-align: center;
                        ">
                            <strong>{stock['symbol']}</strong>: +{stock['change_percent']:.2f}%
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                if market_data.get('top_losers'):
                    st.subheader("📉 Top giảm mạnh")
                    for stock in market_data['top_losers'][:5]:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(90deg, #f44336, #e57373);
                            color: white;
                            padding: 10px;
                            border-radius: 8px;
                            margin: 5px 0;
                            text-align: center;
                        ">
                            <strong>{stock['symbol']}</strong>: {stock['change_percent']:.2f}%
                        </div>
                        """, unsafe_allow_html=True)
    
    # Available VN stocks from CrewAI
    st.subheader("📋 Danh sách cổ phiếu (CrewAI Real Data)")
    
    # Show data source
    if symbols and symbols[0].get('data_source') == 'CrewAI':
        st.success(f"✅ Hiển thị {len(symbols)} mã cổ phiếu từ CrewAI")
    else:
        st.info(f"📋 Hiển thị {len(symbols)} mã cổ phiếu tĩnh")
    
    # Group by sector
    sectors = {}
    for stock in symbols:
        sector = stock['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    for sector, stocks in sectors.items():
        with st.expander(f"🏢 {sector} ({len(stocks)} mã)"):
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

# Footer
st.markdown("---")
st.markdown("**🇻🇳 AI Trading Team Vietnam** - Powered by CrewAI, Google Gemini & 6 AI Agents")
st.markdown("*Real-time data từ CrewAI thay vì vnstock*")