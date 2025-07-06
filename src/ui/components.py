import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

def render_main_header():
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div class="header-left">
                <h1><span class="flag">🇻🇳</span> AI Trading Team Vietnam</h1>
                <p class="subtitle">Hệ thống phân tích đầu tư chứng khoán với <span class="highlight">6 AI Agents</span> + <span class="highlight">Gemini Chatbot</span></p>
                <div class="agent-badges">
                    <span class="badge">📈 PricePredictor</span>
                    <span class="badge">📰 NewsAnalyzer</span>
                    <span class="badge">💼 InvestmentExpert</span>
                    <span class="badge">⚠️ RiskManager</span>
                    <span class="badge">🌍 MarketInsights</span>
                    <span class="badge">🧠 GeminiAI</span>
                </div>
            </div>
            <div class="header-right">
                <div class="live-indicator">
                    <div class="pulse"></div>
                    <span>LIVE DATA</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_stock_overview_card(stock_data):
    price_color = "#00C851" if stock_data.change >= 0 else "#FF4444"
    change_symbol = "▲" if stock_data.change >= 0 else "▼"
    trend_class = "positive" if stock_data.change >= 0 else "negative"
    
    st.markdown(f"""
    <div class="stock-overview-modern">
        <div class="stock-header">
            <div class="stock-info">
                <div class="symbol-container">
                    <h1 class="stock-symbol">{stock_data.symbol}</h1>
                    <div class="stock-meta">
                        <span class="sector">{stock_data.sector}</span>
                        <span class="exchange">{stock_data.exchange}</span>
                    </div>
                </div>
            </div>
            <div class="price-container">
                <div class="current-price">{stock_data.price:,.0f} <span class="currency">VND</span></div>
                <div class="price-change {trend_class}">
                    <span class="change-icon">{change_symbol}</span>
                    <span class="change-value">{stock_data.change:+,.0f}</span>
                    <span class="change-percent">({stock_data.change_percent:+.2f}%)</span>
                </div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-content">
                    <div class="metric-label">Volume</div>
                    <div class="metric-value">{stock_data.volume:,}</div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-content">
                    <div class="metric-label">P/E Ratio</div>
                    <div class="metric-value">{stock_data.pe_ratio if stock_data.pe_ratio else 'N/A'}</div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🏢</div>
                <div class="metric-content">
                    <div class="metric-label">Market Cap</div>
                    <div class="metric-value">{stock_data.market_cap:,.0f}B VND</div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-content">
                    <div class="metric-label">P/B Ratio</div>
                    <div class="metric-value">{stock_data.pb_ratio if stock_data.pb_ratio else 'N/A'}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recommendation_card(recommendation, reason, confidence=None):
    colors = {
        "BUY": {"bg": "linear-gradient(135deg, #00C851 0%, #007E33 100%)", "icon": "🚀", "action": "MUA"},
        "SELL": {"bg": "linear-gradient(135deg, #FF4444 0%, #CC0000 100%)", "icon": "📉", "action": "BÁN"},
        "HOLD": {"bg": "linear-gradient(135deg, #FF8800 0%, #FF6600 100%)", "icon": "⏸️", "action": "GIỮ"}
    }
    
    rec_data = colors.get(recommendation, colors["HOLD"])
    confidence_bar = f'<div class="confidence-bar"><div class="confidence-fill" style="width: {confidence or 75}%"></div></div>' if confidence else ''
    
    st.markdown(f"""
    <div class="recommendation-card-modern" style="background: {rec_data['bg']}">
        <div class="rec-header">
            <div class="rec-icon">{rec_data['icon']}</div>
            <div class="rec-title">
                <h2>KHUYẾN NGHỊ</h2>
                <h1>{rec_data['action']}</h1>
            </div>
        </div>
        <div class="rec-reason">{reason}</div>
        {confidence_bar}
        {f'<div class="confidence-text">Độ tin cậy: {confidence}%</div>' if confidence else ''}
    </div>
    """, unsafe_allow_html=True)

def render_chart_container(title, chart_func):
    st.markdown(f'<div class="chart-container"><h4 style="margin-bottom:1em;">{title}</h4>', unsafe_allow_html=True)
    chart_func()
    st.markdown('</div>', unsafe_allow_html=True)

def render_error_message(msg, submsg="", error_type="error"):
    icons = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
    colors = {
        "error": "linear-gradient(135deg, #FF4444 0%, #CC0000 100%)",
        "warning": "linear-gradient(135deg, #FF8800 0%, #FF6600 100%)", 
        "info": "linear-gradient(135deg, #2196F3 0%, #1976D2 100%)"
    }
    
    st.markdown(f"""
    <div class="alert-modern {error_type}" style="background: {colors.get(error_type, colors['error'])}">
        <div class="alert-icon">{icons.get(error_type, icons['error'])}</div>
        <div class="alert-content">
            <div class="alert-title">{msg}</div>
            {f'<div class="alert-subtitle">{submsg}</div>' if submsg else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_loading_animation(message="Đang xử lý...", agents_status=None):
    agents_html = ""
    if agents_status:
        agents_html = '<div class="agents-status">'
        for agent, status in agents_status.items():
            status_icon = "🔄" if status == "working" else "✅" if status == "done" else "⏳"
            agents_html += f'<div class="agent-status {status}"><span>{status_icon}</span> {agent}</div>'
        agents_html += '</div>'
    
    st.markdown(f"""
    <div class="loading-container">
        <div class="loading-content">
            <div class="loading-spinner">
                <div class="spinner-ring"></div>
                <div class="spinner-ring"></div>
                <div class="spinner-ring"></div>
            </div>
            <h3 class="loading-title">{message}</h3>
            <p class="loading-subtitle">AI Agents đang làm việc...</p>
            {agents_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
