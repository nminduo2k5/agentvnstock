import streamlit as st
import asyncio
from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI
import json

# Page config
st.set_page_config(
    page_title="DUONG AI TRADING SIUUUU",
    page_icon="🤖",
    layout="wide"
)

# Initialize
@st.cache_resource
def init_agents():
    vn_api = VNStockAPI()
    main_agent = MainAgent(vn_api)  # Initialize without Gemini API key
    return main_agent, vn_api

main_agent, vn_api = init_agents()

# Header
st.title("🇻🇳 AI Trading Team Vietnam")
st.markdown("**Hệ thống phân tích đầu tư chứng khoán với 6 AI Agents chuyên nghiệp + Gemini Chatbot**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Cài đặt")
    
    # Gemini API Key Input
    st.subheader("🔑 Gemini API Key")
    api_key = st.text_input(
        "Google Gemini API Key:",
        type="password",
        help="Nhập API key từ Google AI Studio"
    )
    
    gemini_status = "🟢" if main_agent.gemini_agent else "🔴"
    
    if api_key and st.button("⚙️ Cài đặt API Key"):
        if main_agent.set_gemini_api_key(api_key):
            st.success("✅ API key đã được cài đặt!")
            st.rerun()
        else:
            st.error("❌ API key không hợp lệ!")
    
    if not api_key and not main_agent.gemini_agent:
        st.warning("⚠️ Vui lòng nhập API key để sử dụng Gemini!")
        st.info("💡 Lấy API key miễn phí tại: https://makersuite.google.com/app/apikey")
    
    st.divider()
    
    # 6 AI Agents Status
    st.subheader("🤖 6 AI Agents")
    agents_info = [
        {"name": "📈 PricePredictor", "desc": "Dự đoán giá", "status": "🟢"},
        {"name": "📰 TickerNews", "desc": "Tin tức cổ phiếu", "status": "🟢"},
        {"name": "🌍 MarketNews", "desc": "Tin tức thị trường", "status": "🟢"},
        {"name": "💼 InvestmentExpert", "desc": "Phân tích đầu tư", "status": "🟢"},
        {"name": "⚠️ RiskExpert", "desc": "Quản lý rủi ro", "status": "🟢"},
        {"name": "🧠 GeminiAgent", "desc": "AI Chatbot", "status": gemini_status}
    ]
    
    for agent in agents_info:
        st.write(f"{agent['status']} **{agent['name']}**: {agent['desc']}")
    
    st.divider()
    
    # Stock selection
    st.subheader("📊 Chọn cổ phiếu")
    symbols = vn_api.get_available_symbols()
    symbol_options = ["-- Chọn mã cổ phiếu --"] + [f"{s['symbol']} - {s['name']}" for s in symbols]
    selected_symbol = st.selectbox("Mã cổ phiếu:", symbol_options)
    symbol = selected_symbol.split(" - ")[0] if selected_symbol and not selected_symbol.startswith("--") else None

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📊 Phân tích cổ phiếu", "💬 AI Chatbot", "📈 Thị trường VN"])

with tab1:
    if symbol:
        st.header(f"📈 Phân tích toàn diện {symbol}")
    else:
        st.header("📈 Phân tích toàn diện")
        st.info("📝 Vui lòng chọn mã cổ phiếu ở sidebar để bắt đầu phân tích!")
        st.stop()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Phân tích toàn diện", type="primary"):
            if not symbol:
                st.error("❌ Vui lòng chọn mã cổ phiếu trước!")
            else:
                with st.spinner("6 AI Agents đang phân tích..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(main_agent.analyze_stock(symbol))
                
                    if result.get('error'):
                        st.error(f"❌ {result['error']}")
                    else:
                        # Hiển thị cảnh báo nếu có warning (mock data)
                        if result.get('vn_stock_data') and isinstance(result['vn_stock_data'], dict) and result['vn_stock_data'].get('warning'):
                            st.warning(result['vn_stock_data']['warning'])
                            stock_data = result['vn_stock_data']['data']
                        else:
                            stock_data = result.get('vn_stock_data')
                        # VN Stock Data với card đẹp
                        if stock_data:
                            price_color = "#4caf50" if stock_data.change >= 0 else "#f44336"
                            change_symbol = "▲" if stock_data.change >= 0 else "▼"
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white;
                                padding: 25px;
                                border-radius: 15px;
                                margin: 20px 0;
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                                    <div>
                                        <h2 style="margin: 0; font-size: 28px;">{stock_data.symbol}</h2>
                                        <p style="margin: 5px 0; opacity: 0.9;">{stock_data.sector} • {stock_data.exchange}</p>
                                    </div>
                                    <div style="text-align: right;">
                                        <h3 style="margin: 0; font-size: 24px;">{stock_data.price:,.0f} VND</h3>
                                        <p style="margin: 5px 0; color: {price_color};">
                                            {change_symbol} {stock_data.change:+,.0f} ({stock_data.change_percent:+.2f}%)
                                        </p>
                                    </div>
                                </div>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                                    <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                                        <p style="margin: 0; font-size: 12px; opacity: 0.8;">VOLUME</p>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold;">{stock_data.volume:,}</p>
                                    </div>
                                    <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                                        <p style="margin: 0; font-size: 12px; opacity: 0.8;">P/E RATIO</p>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold;">{stock_data.pe_ratio if stock_data.pe_ratio else 'N/A'}</p>
                                    </div>
                                    <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                                        <p style="margin: 0; font-size: 12px; opacity: 0.8;">MARKET CAP</p>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold;">{stock_data.market_cap:,.0f}B VND</p>
                                    </div>
                                    <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                                        <p style="margin: 0; font-size: 12px; opacity: 0.8;">P/B RATIO</p>
                                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold;">{stock_data.pb_ratio if stock_data.pb_ratio else 'N/A'}</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Thêm biểu đồ giá cổ phiếu
                            import pandas as pd
                            import numpy as np
                            from datetime import datetime, timedelta

                            # Nếu có hàm lấy lịch sử giá thực tế, thay thế đoạn này
                            # price_history = vn_api.get_price_history(stock_data.symbol)
                            # if price_history is not None:
                            #     df = pd.DataFrame(price_history)
                            # else:
                            #     # Demo: tạo dữ liệu giả lập
                            #     ...

                            # Demo: tạo dữ liệu giá giả lập 30 ngày gần nhất
                            np.random.seed(0)
                            days = 30
                            today = datetime.now()
                            dates = [today - timedelta(days=i) for i in range(days)][::-1]
                            base_price = stock_data.price
                            prices = [base_price]
                            for _ in range(1, days):
                                prices.append(prices[-1] * (1 + np.random.normal(0, 0.01)))
                            df = pd.DataFrame({
                                "Ngày": [d.strftime("%d/%m") for d in dates],
                                "Giá đóng cửa": np.round(prices, 2)
                            })

                            st.markdown("#### 📉 Biểu đồ giá 30 ngày gần nhất")
                            st.line_chart(df.set_index("Ngày"))
                
                        # Price Prediction với card đẹp
                        if result.get('price_prediction'):
                            pred = result['price_prediction']
                            trend = pred.get('trend', 'Unknown')
                            trend_color = "#4caf50" if trend == "Bullish" else "#f44336" if trend == "Bearish" else "#ff9800"
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, {trend_color}, {trend_color}cc);
                                color: white;
                                padding: 20px;
                                border-radius: 15px;
                                margin: 15px 0;
                            ">
                                <h3 style="margin: 0 0 15px 0;">🔮 PricePredictor Agent</h3>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                    <div>
                                        <strong>Xu hướng:</strong> {trend}<br>
                                        <strong>Giá dự đoán:</strong> {pred.get('predicted_price', 'N/A')}
                                    </div>
                                    <div>
                                        <strong>Độ tin cậy:</strong> {pred.get('confidence', 'N/A')}<br>
                                        <strong>Thời gian:</strong> {pred.get('timeframe', 'N/A')}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
                        # Risk Assessment với card đẹp
                        if result.get('risk_assessment'):
                            risk = result['risk_assessment']
                            risk_level = risk.get('risk_level', 'UNKNOWN')
                            risk_bg_color = "#f44336" if risk_level == 'HIGH' else "#ff9800" if risk_level == 'MEDIUM' else "#4caf50"
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, {risk_bg_color}, {risk_bg_color}cc);
                                color: white;
                                padding: 20px;
                                border-radius: 15px;
                                margin: 15px 0;
                            ">
                                <h3 style="margin: 0 0 15px 0;">⚠️ RiskExpert Agent</h3>
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                                    <div style="text-align: center;">
                                        <strong>Mức rủi ro</strong><br>
                                        <span style="font-size: 1.5em;">{risk_level}</span>
                                    </div>
                                    <div style="text-align: center;">
                                        <strong>Độ biến động</strong><br>
                                        <span style="font-size: 1.5em;">{risk.get('volatility', 'N/A')}%</span>
                                    </div>
                                    <div style="text-align: center;">
                                        <strong>Beta</strong><br>
                                        <span style="font-size: 1.5em;">{risk.get('beta', 'N/A')}</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
                        # Investment Analysis với card đẹp
                        if result.get('investment_analysis'):
                            inv = result['investment_analysis']
                            recommendation = inv.get('recommendation', 'HOLD')
                            rec_bg_color = "#4caf50" if recommendation == 'BUY' else "#f44336" if recommendation == 'SELL' else "#ff9800"
                            rec_icon = "📈" if recommendation == 'BUY' else "📉" if recommendation == 'SELL' else "⏸️"
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, {rec_bg_color}, {rec_bg_color}cc);
                                color: white;
                                padding: 20px;
                                border-radius: 15px;
                                margin: 15px 0;
                                text-align: center;
                            ">
                                <h3 style="margin: 0 0 15px 0;">💼 InvestmentExpert Agent</h3>
                                <div style="font-size: 2em; margin: 10px 0;">{rec_icon}</div>
                                <h2 style="margin: 10px 0; font-size: 2.5em;">{recommendation}</h2>
                                <p style="margin: 15px 0; font-size: 1.1em; opacity: 0.9;">{inv.get('reason', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        ">
            <h3 style="margin: 0; text-align: center;">🎯 Quick Actions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Price Prediction Button
        if st.button("📈 Dự đoán giá", use_container_width=True):
            if not symbol:
                st.error("❌ Chọn mã cổ phiếu trước!")
            else:
                with st.spinner("🔮 Đang dự đoán..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    pred = loop.run_until_complete(asyncio.to_thread(main_agent.price_predictor.predict_price, symbol))
                
                trend = pred.get('trend', 'Unknown')
                trend_bg = "#4caf50" if trend == "Bullish" else "#f44336" if trend == "Bearish" else "#ff9800"
                
                st.markdown(f"""
                <div style="
                    background: {trend_bg};
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0;">🔮 {trend}</h4>
                    <p style="margin: 5px 0; font-size: 18px;">{pred.get('predicted_price', 'N/A')}</p>
                    <small>Tin cậy: {pred.get('confidence', 0)}%</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Risk Assessment Button
        if st.button("⚠️ Đánh giá rủi ro", use_container_width=True):
            if not symbol:
                st.error("❌ Chọn mã cổ phiếu trước!")
            else:
                with st.spinner("⚠️ Đang đánh giá..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    risk = loop.run_until_complete(asyncio.to_thread(main_agent.risk_expert.assess_risk, symbol))
                
                risk_level = risk.get('risk_level', 'UNKNOWN')
                risk_bg = "#f44336" if risk_level == 'HIGH' else "#ff9800" if risk_level == 'MEDIUM' else "#4caf50"
                
                st.markdown(f"""
                <div style="
                    background: {risk_bg};
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0;">⚠️ {risk_level}</h4>
                    <p style="margin: 5px 0;">Biến động: {risk.get('volatility', 0):.1f}%</p>
                    <small>Beta: {risk.get('beta', 0):.2f}</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Investment Analysis Button
        if st.button("💼 Phân tích đầu tư", use_container_width=True):
            if not symbol:
                st.error("❌ Chọn mã cổ phiếu trước!")
            else:
                with st.spinner("💼 Đang phân tích..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    inv = loop.run_until_complete(asyncio.to_thread(main_agent.investment_expert.analyze_stock, symbol))
                
                recommendation = inv.get('recommendation', 'HOLD')
                rec_bg = "#4caf50" if recommendation == 'BUY' else "#f44336" if recommendation == 'SELL' else "#ff9800"
                rec_icon = "📈" if recommendation == 'BUY' else "📉" if recommendation == 'SELL' else "⏸️"
                
                st.markdown(f"""
                <div style="
                    background: {rec_bg};
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0;">{rec_icon} {recommendation}</h4>
                    <p style="margin: 5px 0; font-size: 14px;">{inv.get('reason', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

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
                        # Hiển thị cảnh báo nếu có warning (mock data)
                        if data.get('vn_stock_data') and isinstance(data['vn_stock_data'], dict) and data['vn_stock_data'].get('warning'):
                            st.warning(data['vn_stock_data']['warning'])
                            stock_data = data['vn_stock_data']['data']
                        else:
                            stock_data = data.get('vn_stock_data')
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

with tab3:
    st.header("📈 Tổng quan thị trường Việt Nam")
    
    if st.button("🔄 Cập nhật thị trường", type="primary"):
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
    
    # Available VN stocks
    st.subheader("📋 Danh sách cổ phiếu hỗ trợ")
    symbols = vn_api.get_available_symbols()
    
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
st.markdown("**🇻🇳 AI Trading Team Vietnam** - Powered by vnstock, Google Gemini & 6 AI Agents")
st.markdown("*Real-time data từ thị trường chứng khoán Việt Nam*")