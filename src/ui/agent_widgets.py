# src/ui/agent_widgets.py
"""
Specialized widgets for 6 AI Agents
"""

import streamlit as st
from typing import Dict, Any, List
from datetime import datetime

def render_agent_status_panel():
    """Render 6 AI agents status panel"""
    st.subheader("🤖 AI Agents Status")
    
    agents = [
        {"name": "PricePredictor", "icon": "📈", "status": "active", "desc": "Dự đoán giá cổ phiếu"},
        {"name": "TickerNews", "icon": "📰", "status": "active", "desc": "Tin tức cổ phiếu"},
        {"name": "MarketNews", "icon": "🌍", "status": "active", "desc": "Tin tức thị trường"},
        {"name": "InvestmentExpert", "icon": "💼", "status": "active", "desc": "Phân tích đầu tư"},
        {"name": "RiskExpert", "icon": "⚠️", "status": "active", "desc": "Quản lý rủi ro"},
        {"name": "GeminiAgent", "icon": "🧠", "status": "active", "desc": "AI Chatbot"}
    ]
    
    cols = st.columns(3)
    for i, agent in enumerate(agents):
        with cols[i % 3]:
            status_color = "🟢" if agent["status"] == "active" else "🔴"
            st.markdown(f"""
            <div style="
                background: white;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #2196f3;
                margin: 5px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 20px; margin-right: 8px;">{agent['icon']}</span>
                    <div>
                        <strong>{agent['name']}</strong><br>
                        <small style="color: #666;">{agent['desc']}</small><br>
                        <span style="font-size: 12px;">{status_color} Active</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_price_predictor_widget(prediction_data: Dict[str, Any]):
    """Render PricePredictor results widget"""
    st.subheader("📈 Price Prediction")
    
    if not prediction_data:
        st.info("Chưa có dự đoán giá")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trend = prediction_data.get('trend', 'Unknown')
        trend_color = "🟢" if trend == "Bullish" else "🔴" if trend == "Bearish" else "🟡"
        st.metric("Xu hướng", f"{trend_color} {trend}")
    
    with col2:
        predicted_price = prediction_data.get('predicted_price', 0)
        st.metric("Giá dự đoán", f"{predicted_price:,.0f} VND")
    
    with col3:
        confidence = prediction_data.get('confidence', 0)
        st.metric("Độ tin cậy", f"{confidence}%")
    
    # Additional details
    if prediction_data.get('reasoning'):
        with st.expander("Chi tiết dự đoán"):
            st.write(prediction_data['reasoning'])

def render_risk_expert_widget(risk_data: Dict[str, Any]):
    """Render RiskExpert results widget"""
    st.subheader("⚠️ Risk Assessment")
    
    if not risk_data:
        st.info("Chưa có đánh giá rủi ro")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_level = risk_data.get('risk_level', 'UNKNOWN')
        risk_colors = {
            'LOW': '🟢',
            'MEDIUM': '🟡', 
            'HIGH': '🔴'
        }
        risk_color = risk_colors.get(risk_level, '⚪')
        st.metric("Mức rủi ro", f"{risk_color} {risk_level}")
    
    with col2:
        volatility = risk_data.get('volatility', 0)
        st.metric("Độ biến động", f"{volatility:.1f}%")
    
    with col3:
        beta = risk_data.get('beta', 0)
        st.metric("Beta", f"{beta:.2f}")
    
    # Risk breakdown
    if risk_data.get('risk_factors'):
        with st.expander("Phân tích rủi ro chi tiết"):
            for factor, score in risk_data['risk_factors'].items():
                st.write(f"**{factor}**: {score}")

def render_investment_expert_widget(investment_data: Dict[str, Any]):
    """Render InvestmentExpert results widget"""
    st.subheader("💼 Investment Analysis")
    
    if not investment_data:
        st.info("Chưa có phân tích đầu tư")
        return
    
    recommendation = investment_data.get('recommendation', 'HOLD')
    rec_colors = {
        'BUY': '#4caf50',
        'SELL': '#f44336',
        'HOLD': '#ff9800'
    }
    rec_color = rec_colors.get(recommendation, '#757575')
    
    st.markdown(f"""
    <div style="
        background: {rec_color};
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 15px 0;
    ">
        <h3 style="margin: 0;">Khuyến nghị: {recommendation}</h3>
        <p style="margin: 10px 0 0 0;">{investment_data.get('reason', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pe_ratio = investment_data.get('pe_ratio', 0)
        st.metric("P/E Ratio", f"{pe_ratio:.1f}")
    
    with col2:
        dividend_yield = investment_data.get('dividend_yield', 0)
        st.metric("Dividend Yield", f"{dividend_yield:.1f}%")
    
    with col3:
        target_price = investment_data.get('target_price', 0)
        st.metric("Target Price", f"{target_price:,.0f} VND")

def render_news_widgets(ticker_news: List[Dict], market_news: List[Dict]):
    """Render TickerNews and MarketNews widgets"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📰 Tin tức cổ phiếu")
        if ticker_news:
            for news in ticker_news[:3]:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #2196f3;
                    margin: 10px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <strong>{news.get('title', 'No title')}</strong><br>
                    <small style="color: #666;">{news.get('summary', 'No summary')}</small><br>
                    <small style="color: #999;">{news.get('timestamp', '')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Chưa có tin tức cổ phiếu")
    
    with col2:
        st.subheader("🌍 Tin tức thị trường")
        if market_news:
            for news in market_news[:3]:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #ff9800;
                    margin: 10px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <strong>{news.get('title', 'No title')}</strong><br>
                    <small style="color: #666;">{news.get('summary', 'No summary')}</small><br>
                    <small style="color: #999;">{news.get('timestamp', '')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Chưa có tin tức thị trường")

def render_gemini_chat_widget():
    """Render Gemini chatbot widget"""
    st.subheader("🧠 Gemini AI Assistant")
    
    # Chat history display
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages[-5:]:  # Show last 5 messages
            if message['role'] == 'user':
                st.markdown(f"""
                <div style="
                    background: #e3f2fd;
                    padding: 10px;
                    border-radius: 10px;
                    margin: 5px 0;
                    text-align: right;
                ">
                    <strong>Bạn:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: #f3e5f5;
                    padding: 10px;
                    border-radius: 10px;
                    margin: 5px 0;
                ">
                    <strong>🧠 Gemini:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    return st.text_input("💭 Hỏi Gemini AI:", key="gemini_input")

def render_analysis_summary_widget(analysis_results: Dict[str, Any]):
    """Render comprehensive analysis summary"""
    st.subheader("📋 Tổng kết phân tích")
    
    if not analysis_results:
        st.info("Chưa có kết quả phân tích")
        return
    
    # Extract recommendations from all agents
    recommendations = []
    confidences = []
    
    for agent_name, result in analysis_results.items():
        if isinstance(result, dict) and 'recommendation' in result:
            recommendations.append(result['recommendation'])
            confidences.append(result.get('confidence', 5))
    
    if not recommendations:
        st.warning("Không có khuyến nghị từ các agents")
        return
    
    # Calculate consensus
    buy_count = recommendations.count('BUY')
    sell_count = recommendations.count('SELL')
    hold_count = recommendations.count('HOLD')
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Determine final recommendation
    if buy_count > max(sell_count, hold_count):
        final_rec = "BUY"
        rec_color = "#4caf50"
        rec_icon = "📈"
    elif sell_count > max(buy_count, hold_count):
        final_rec = "SELL"
        rec_color = "#f44336"
        rec_icon = "📉"
    else:
        final_rec = "HOLD"
        rec_color = "#ff9800"
        rec_icon = "⏸️"
    
    # Display final recommendation
    st.markdown(f"""
    <div style="
        background: {rec_color};
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    ">
        <div style="font-size: 48px; margin-bottom: 10px;">{rec_icon}</div>
        <h2 style="margin: 0; font-size: 36px;">{final_rec}</h2>
        <p style="margin: 10px 0; font-size: 18px;">Team Recommendation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display consensus metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        consensus_strength = max(buy_count, sell_count, hold_count)
        st.metric("Consensus", f"{consensus_strength}/{len(recommendations)}")
    
    with col2:
        st.metric("Avg Confidence", f"{avg_confidence:.1f}/10")
    
    with col3:
        consensus_level = "Strong" if consensus_strength == len(recommendations) else "Moderate"
        st.metric("Agreement Level", consensus_level)

def render_quick_actions_panel(symbol: str):
    """Render quick actions panel"""
    st.subheader("⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Quick Price Check", use_container_width=True):
            return {"action": "price_check", "symbol": symbol}
        
        if st.button("📰 Latest News", use_container_width=True):
            return {"action": "news_check", "symbol": symbol}
    
    with col2:
        if st.button("⚠️ Risk Alert", use_container_width=True):
            return {"action": "risk_check", "symbol": symbol}
        
        if st.button("💼 Investment Advice", use_container_width=True):
            return {"action": "investment_advice", "symbol": symbol}
    
    return None