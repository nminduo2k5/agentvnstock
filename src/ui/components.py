# src/ui/components.py
"""
Reusable UI Components cho Streamlit Dashboard
Các component có thể tái sử dụng trong UI
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

def render_agent_card(agent_name: str, role: str, status: str = "ready", response: str = ""):
    """
    Render card cho từng AI agent
    
    Args:
        agent_name: Tên agent
        role: Vai trò của agent
        status: Trạng thái (ready, thinking, done)
        response: Response từ agent
    """
    
    # Determine colors và icons
    colors = {
        "Nguyễn Minh Anh": {"bg": "#e3f2fd", "border": "#2196f3", "icon": "🔍"},
        "Trần Quốc Bảo": {"bg": "#fff3e0", "border": "#ff9800", "icon": "⚠️"},
        "Lê Thị Mai": {"bg": "#f3e5f5", "border": "#9c27b0", "icon": "💼"}
    }
    
    agent_colors = colors.get(agent_name, {"bg": "#f5f5f5", "border": "#757575", "icon": "🤖"})
    
    # Status indicators
    status_indicators = {
        "ready": "⏳ Sẵn sàng",
        "thinking": "🤔 Đang phân tích...", 
        "done": "✅ Hoàn thành"
    }
    
    status_text = status_indicators.get(status, "❓ Unknown")
    
    # Render card
    st.markdown(f"""
    <div style="
        background-color: {agent_colors['bg']};
        border-left: 5px solid {agent_colors['border']};
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 24px; margin-right: 10px;">{agent_colors['icon']}</span>
            <div>
                <h4 style="margin: 0; color: #333;">{agent_name}</h4>
                <p style="margin: 0; color: #666; font-size: 14px;">{role}</p>
                <p style="margin: 5px 0 0 0; color: #999; font-size: 12px;">{status_text}</p>
            </div>
        </div>
        {f'<div style="background-color: white; padding: 15px; border-radius: 5px; margin-top: 10px;"><p style="margin: 0;">{response}</p></div>' if response else ''}
    </div>
    """, unsafe_allow_html=True)

def render_stock_overview_card(stock_data, news_sentiment: Optional[Dict] = None):
    """
    Render overview card cho stock
    
    Args:
        stock_data: VNStockData object
        news_sentiment: News sentiment data
    """
    
    # Determine price color
    price_color = "green" if stock_data.change >= 0 else "red"
    change_symbol = "▲" if stock_data.change >= 0 else "▼"
    
    # News sentiment color
    sentiment_colors = {
        "Positive": "#4caf50",
        "Negative": "#f44336", 
        "Neutral": "#ff9800"
    }
    
    sentiment_color = sentiment_colors.get(
        news_sentiment.get('sentiment', 'Neutral') if news_sentiment else 'Neutral',
        "#ff9800"
    )
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
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
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px;">
            <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                <p style="margin: 0; font-size: 12px; opacity: 0.8;">VOLUME</p>
                <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold;">{stock_data.volume:,}</p>
            </div>
            <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                <p style="margin: 0; font-size: 12px; opacity: 0.8;">P/E RATIO</p>
                <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold;">{stock_data.pe_ratio:.1f if stock_data.pe_ratio else 'N/A'}</p>
            </div>
            <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                <p style="margin: 0; font-size: 12px; opacity: 0.8;">MARKET CAP</p>
                <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold;">{stock_data.market_cap:,.0f}B</p>
            </div>
            {f'''<div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                <p style="margin: 0; font-size: 12px; opacity: 0.8;">NEWS SENTIMENT</p>
                <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: {sentiment_color};">{news_sentiment.get('sentiment', 'Neutral')}</p>
            </div>''' if news_sentiment else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recommendation_summary(responses: List, investment_amount: float):
    """
    Render tổng kết recommendation từ AI team
    
    Args:
        responses: List of AgentResponse objects
        investment_amount: Số tiền đầu tư
    """
    
    # Calculate consensus
    recommendations = [r.recommendation for r in responses]
    confidences = [r.confidence_level for r in responses]
    
    buy_count = recommendations.count('BUY')
    sell_count = recommendations.count('SELL') 
    hold_count = recommendations.count('HOLD')
    
    avg_confidence = sum(confidences) / len(confidences)
    
    # Determine final recommendation
    if buy_count > max(sell_count, hold_count):
        final_rec = "BUY"
        rec_color = "#4caf50"
        rec_icon = "📈"
        consensus_strength = buy_count
    elif sell_count > max(buy_count, hold_count):
        final_rec = "SELL"
        rec_color = "#f44336"
        rec_icon = "📉"
        consensus_strength = sell_count
    else:
        final_rec = "HOLD"
        rec_color = "#ff9800"
        rec_icon = "⏸️"
        consensus_strength = hold_count
    
    consensus_level = "Strong" if consensus_strength == 3 else "Moderate" if consensus_strength == 2 else "Weak"
    
    # Render summary card
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {rec_color} 0%, {rec_color}cc 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 25px 0;
        text-align: center;
    ">
        <div style="font-size: 48px; margin-bottom: 10px;">{rec_icon}</div>
        <h2 style="margin: 0; font-size: 36px; font-weight: bold;">{final_rec}</h2>
        <p style="margin: 10px 0; font-size: 18px; opacity: 0.9;">Team Recommendation</p>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 25px;">
            <div style="background-color: rgba(255,255,255,0.15); padding: 20px; border-radius: 10px;">
                <h4 style="margin: 0; font-size: 24px;">{consensus_strength}/3</h4>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Agents Agreement</p>
            </div>
            <div style="background-color: rgba(255,255,255,0.15); padding: 20px; border-radius: 10px;">
                <h4 style="margin: 0; font-size: 24px;">{avg_confidence:.1f}/10</h4>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Avg Confidence</p>
            </div>
            <div style="background-color: rgba(255,255,255,0.15); padding: 20px; border-radius: 10px;">
                <h4 style="margin: 0; font-size: 24px;">{consensus_level}</h4>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Consensus Level</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action recommendations
    if final_rec == "BUY":
        render_action_plan("BUY", investment_amount, avg_confidence)
    elif final_rec == "SELL":
        render_action_plan("SELL", investment_amount, avg_confidence)
    else:
        render_action_plan("HOLD", investment_amount, avg_confidence)

def render_action_plan(recommendation: str, amount: float, confidence: float):
    """
    Render action plan based on recommendation
    
    Args:
        recommendation: Final recommendation (BUY/SELL/HOLD)
        amount: Investment amount
        confidence: Confidence level
    """
    
    actions = {
        "BUY": {
            "color": "#4caf50",
            "icon": "✅",
            "title": "Action Plan - MUA",
            "steps": [
                f"💰 Prepare {amount:,.0f} VND for investment",
                "📊 Set stop-loss at recommended levels",
                "⏰ Execute order during market hours",
                "📱 Set price alerts for key levels",
                "📅 Schedule 2-week review"
            ]
        },
        "SELL": {
            "color": "#f44336",
            "icon": "🚫",
            "title": "Action Plan - TRÁNH",
            "steps": [
                "⛔ Avoid investment at current levels",
                "👀 Monitor for better entry points",
                "📈 Wait for technical improvement",
                "📰 Watch for positive catalysts",
                "🔄 Re-evaluate in 2-4 weeks"
            ]
        },
        "HOLD": {
            "color": "#ff9800", 
            "icon": "⏸️",
            "title": "Action Plan - QUAN SÁT",
            "steps": [
                "👁️ Continue monitoring closely",
                "📊 Wait for clearer signals",
                "💼 Maintain current position if any",
                "📅 Review weekly for updates",
                "🔔 Set alerts for breakout levels"
            ]
        }
    }
    
    action = actions[recommendation]
    
    st.markdown(f"""
    <div style="
        border: 2px solid {action['color']};
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        background-color: {action['color']}08;
    ">
        <h3 style="color: {action['color']}; margin: 0 0 15px 0;">
            {action['icon']} {action['title']}
        </h3>
        <div style="background-color: white; padding: 15px; border-radius: 8px;">
            {''.join([f'<p style="margin: 8px 0;"><strong>{step}</strong></p>' for step in action['steps']])}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_stock_chart(historical_data: List[Dict], symbol: str):
    """
    Render stock chart với technical indicators
    """
    if not historical_data:
        st.warning("⚠️ Không có dữ liệu lịch sử")
        return
    
    df = pd.DataFrame(historical_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['price'],
        mode='lines', name=f'{symbol} Price',
        line=dict(color='#2196f3', width=3)
    ))
    
    fig.update_layout(
        title=f'📈 {symbol} - Price Chart',
        xaxis_title="Date", yaxis_title="Price (VND)",
        height=400, template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_performance_metrics(metrics: Dict[str, float]):
    """
    Render performance metrics
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_return = metrics.get('total_return', 0) * 100
        st.metric("Total Return", f"{total_return:+.2f}%")
    
    with col2:
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
    
    with col3:
        max_drawdown = metrics.get('max_drawdown', 0) * 100
        st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
    
    with col4:
        win_rate = metrics.get('win_rate', 0) * 100
        st.metric("Win Rate", f"{win_rate:.1f}%")

def render_loading_animation(message: str = "Đang xử lý..."):
    """
    Render loading animation
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: linear-gradient(45deg, #667eea, #764ba2); 
                border-radius: 10px; color: white; margin: 20px 0;">
        <div style="border: 4px solid rgba(255,255,255,0.3); border-radius: 50%; border-top: 4px solid white;
                    width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 0 auto 20px auto;"></div>
        <h3 style="margin: 0;">{message}</h3>
    </div>
    <style>
    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
    """, unsafe_allow_html=True)

def render_error_message(error: str, suggestion: str = ""):
    """
    Render error message
    """
    st.markdown(f"""
    <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 8px; 
                padding: 20px; margin: 15px 0;">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 24px; margin-right: 10px;">⚠️</span>
            <h4 style="margin: 0; color: #d32f2f;">Có lỗi xảy ra</h4>
        </div>
        <p style="margin: 10px 0; color: #666;">{error}</p>
        {f'<p style="margin: 10px 0; color: #1976d2;"><strong>💡 Gợi ý:</strong> {suggestion}</p>' if suggestion else ''}
    </div>
    """, unsafe_allow_html=True)ce level
    """
    
    actions = {
        "BUY": {
            "color": "#4caf50",
            "icon": "✅",
            "title": "Action Plan - MUA",
            "steps": [
                f"💰 Prepare {amount:,.0f} VND for investment",
                "📊 Set stop-loss at recommended levels",
                "⏰ Execute order during market hours",
                "📱 Set price alerts for key levels",
                "📅 Schedule 2-week review"
            ]
        },
        "SELL": {
            "color": "#f44336",
            "icon": "🚫",
            "title": "Action Plan - TRÁNH",
            "steps": [
                "⛔ Avoid investment at current levels",
                "👀 Monitor for better entry points",
                "📈 Wait for technical improvement",
                "📰 Watch for positive catalysts",
                "🔄 Re-evaluate in 2-4 weeks"
            ]
        },
        "HOLD": {
            "color": "#ff9800", 
            "icon": "⏸️",
            "title": "Action Plan - QUAN SÁT",
            "steps": [
                "👁️ Continue monitoring closely",
                "📊 Wait for clearer signals",
                "💼 Maintain current position if any",
                "📅 Review weekly for updates",
                "🔔 Set alerts for breakout levels"
            ]
        }
    }
    
    action = actions[recommendation]
    
    st.markdown(f"""
    <div style="
        border: 2px solid {action['color']};
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        background-color: {action['color']}08;
    ">
        <h3 style="color: {action['color']}; margin: 0 0 15px 0;">
            {action['icon']} {action['title']}
        </h3>
        <div style="background-color: white; padding: 15px; border-radius: 8px;">
            {''.join([f'<p style="margin: 8px 0;"><strong>{step}</strong></p>' for step in action['steps']])}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_stock_chart(historical_data: List[Dict], symbol: str):
    """
    Render advanced stock chart với technical indicators
    
    Args:
        historical_data: Historical price data
        symbol: Stock symbol
    """
    
    if not historical_data:
        st.warning("⚠️ Không có dữ liệu lịch sử để hiển thị biểu đồ")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(historical_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Calculate technical indicators
    df['sma_5'] = df['price'].rolling(window=5).mean()
    df['sma_20'] = df['price'].rolling(window=20).mean()
    
    # Create subplots
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['price'],
        mode='lines',
        name=f'{symbol} Price',
        line=dict(color='#2196f3', width=3),
        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Price: %{y:,.0f} VND<extra></extra>'
    ))
    
    # Moving averages
    if len(df) >= 5:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['sma_5'],
            mode='lines',
            name='SMA 5',
            line=dict(color='#ff9800', width=2, dash='dash'),
            opacity=0.7
        ))
    
    if len(df) >= 20:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['sma_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='#4caf50', width=2, dash='dot'),
            opacity=0.7
        ))
    
    # Volume bars (secondary y-axis)
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['volume'],
        name='Volume',
        yaxis='y2',
        opacity=0.3,
        marker_color='gray'
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'📈 {symbol} - Price Chart & Technical Analysis',
            'x': 0.5,
            'font': {'size': 20}
        },
        xaxis_title="Thời gian",
        yaxis_title="Giá (VND)",
        yaxis2=dict(
            title="Volume",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        height=500,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Add range selector
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="7D", step="day", stepmode="backward"),
                    dict(count=14, label="14D", step="day", stepmode="backward"),
                    dict(count=30, label="30D", step="day", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_performance_metrics(metrics: Dict[str, float]):
    """
    Render performance metrics cards
    
    Args:
        metrics: Dictionary of performance metrics
    """
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_return = metrics.get('total_return', 0) * 100
        st.metric(
            "Total Return",
            f"{total_return:+.2f}%",
            delta=f"{'📈' if total_return > 0 else '📉'} Performance"
        )
    
    with col2:
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        st.metric(
            "Sharpe Ratio", 
            f"{sharpe_ratio:.2f}",
            delta="Risk-adjusted return"
        )
    
    with col3:
        max_drawdown = metrics.get('max_drawdown', 0) * 100
        st.metric(
            "Max Drawdown",
            f"{max_drawdown:.2f}%",
            delta="Maximum loss"
        )
    
    with col4:
        win_rate = metrics.get('win_rate', 0) * 100
        st.metric(
            "Win Rate",
            f"{win_rate:.1f}%",
            delta="Successful trades"
        )

def render_market_heatmap(sector_performance: Dict[str, float]):
    """
    Render sector performance heatmap
    
    Args:
        sector_performance: Dictionary of sector returns
    """
    
    if not sector_performance:
        return
    
    # Prepare data
    sectors = list(sector_performance.keys())
    returns = list(sector_performance.values())
    
    # Create color scale
    colors = ['red' if r < 0 else 'green' for r in returns]
    
    # Create bar chart
    fig = px.bar(
        x=sectors,
        y=returns,
        color=returns,
        color_continuous_scale=['red', 'white', 'green'],
        title="📊 Sector Performance Today"
    )
    
    fig.update_layout(
        xaxis_title="Sectors",
        yaxis_title="Change (%)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_news_sentiment_widget(news_data: Dict[str, Any]):
    """
    Render news sentiment widget
    
    Args:
        news_data: News sentiment data
    """
    
    sentiment = news_data.get('sentiment', 'Neutral')
    score = news_data.get('sentiment_score', 0.5)
    headlines = news_data.get('headlines', [])
    
    # Sentiment color
    sentiment_colors = {
        'Positive': '#4caf50',
        'Negative': '#f44336',
        'Neutral': '#ff9800'
    }
    
    color = sentiment_colors.get(sentiment, '#ff9800')
    
    # Render widget
    st.markdown(f"""
    <div style="
        border: 2px solid {color};
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: {color}08;
    ">
        <h4 style="color: {color}; margin: 0 0 10px 0;">📰 News Sentiment: {sentiment}</h4>
        <div style="background-color: {color}; height: 8px; border-radius: 4px; width: {score*100}%; margin-bottom: 15px;"></div>
        <div style="background-color: white; padding: 10px; border-radius: 5px;">
            <strong>Recent Headlines:</strong>
            {''.join([f'<p style="margin: 5px 0; font-size: 14px;">• {headline}</p>' for headline in headlines[:3]])}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_download_button(data: Dict, filename: str, button_text: str = "📥 Download"):
    """
    Create download button for data export
    
    Args:
        data: Data to download
        filename: Filename for download
        button_text: Button text
    """
    
    import json
    
    json_data = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    
    st.download_button(
        label=button_text,
        data=json_data,
        file_name=filename,
        mime="application/json"
    )

def render_loading_animation(message: str = "Đang xử lý..."):
    """
    Render loading animation
    
    Args:
        message: Loading message
    """
    
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 40px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 10px;
        color: white;
        margin: 20px 0;
    ">
        <div style="
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid white;
            width: 40px;
            height: 40px;
            animation: spin 2s linear infinite;
            margin: 0 auto 20px auto;
        "></div>
        <h3 style="margin: 0;">{message}</h3>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def render_error_message(error: str, suggestion: str = ""):
    """
    Render user-friendly error message
    
    Args:
        error: Error message
        suggestion: Suggested solution
    """
    
    st.markdown(f"""
    <div style="
        background-color: #ffebee;
        border: 1px solid #f44336;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 24px; margin-right: 10px;">⚠️</span>
            <h4 style="margin: 0; color: #d32f2f;">Oops! Có lỗi xảy ra</h4>
        </div>
        <p style="margin: 10px 0; color: #666;">{error}</p>
        {f'<p style="margin: 10px 0; color: #1976d2;"><strong>💡 Gợi ý:</strong> {suggestion}</p>' if suggestion else ''}
    </div>
    """, unsafe_allow_html=True)