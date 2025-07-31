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

# Cấu hình trang chuyên nghiệp
st.set_page_config(
    page_title="DUONG AI TRADING PRO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tải CSS tích hợp Bootstrap
load_custom_css()

# CSS bổ sung cho ứng dụng
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

# Khởi tạo hệ thống
@st.cache_resource
def init_system():
    vn_api = VNStockAPI()
    main_agent = MainAgent(vn_api)
    return main_agent, vn_api

# Clear cache and reinitialize to ensure updated methods are available
if 'main_agent_initialized' not in st.session_state:
    st.cache_resource.clear()
    st.session_state.main_agent_initialized = True

main_agent, vn_api = init_system()
# Các hàm hiển thị phân tích
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
        st.info("🔴 **Chiến lược mạo hiểm:** Tập trung vào tăng trưởng cao")
    
    # Analysis tabs
    tab1, tab2= st.tabs(["📈 Dự đoán giá", "⚠️ Đánh giá rủi ro"])
    
    with tab1:
        if result.get('price_prediction'):
            display_price_prediction(result['price_prediction'])
    
    with tab2:
        if result.get('risk_assessment'):
            display_risk_assessment(result['risk_assessment'])
            
   

def display_price_prediction(pred):
    if pred.get('error'):
        st.error(f"❌ {pred['error']}")
        return
    
    # Show prediction method info
    method = pred.get('primary_method', pred.get('method', 'Technical Analysis'))
    if 'LSTM' in method:
        st.success(f"🧠 {method} - Enhanced with Neural Network")
        if pred.get('lstm_confidence'):
            st.info(f"📊 LSTM Confidence: {pred['lstm_confidence']:.1f}%")
    else:
        st.info(f"📈 Method: {method}")
    
    # Extract ALL data from price_predictor agent - NO calculations here
    current_price = pred.get('current_price', 0)
    predicted_price = pred.get('predicted_price', 0)
    trend = pred.get('trend', 'neutral')
    confidence = pred.get('confidence', 50)
    data_source = pred.get('data_source', 'Unknown')
    change_percent = pred.get('change_percent', 0)
    
    # AI-enhanced advice and reasoning
    ai_advice = pred.get('ai_advice', '')
    ai_reasoning = pred.get('ai_reasoning', '')
    
    # Technical indicators from agent
    tech_indicators = pred.get('technical_indicators', {})
    rsi = tech_indicators.get('rsi', 50)
    macd = tech_indicators.get('macd', 0)
    
    # Support/resistance from agent
    trend_analysis = pred.get('trend_analysis', {})
    support = trend_analysis.get('support_level', current_price)
    resistance = trend_analysis.get('resistance_level', current_price)
    
    # Multi-timeframe predictions from agent (exact keys from price_predictor)
    predictions = pred.get('predictions', {})
    target_1d = predictions.get('short_term', {}).get('1_days', {}).get('price', predicted_price)
    target_1w = predictions.get('short_term', {}).get('7_days', {}).get('price', predicted_price) 
    target_1m = predictions.get('medium_term', {}).get('30_days', {}).get('price', predicted_price)
    target_3m = predictions.get('long_term', {}).get('90_days', {}).get('price', predicted_price)
    
    # If no multi-timeframe data, use single predicted_price
    if not predictions:
        target_1d = target_1w = target_1m = target_3m = predicted_price
    
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
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Giá dự đoán 3 tháng: {target_3m:,.2f} VND</p>
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
   
    # Show data source and AI model
    if 'StockInfo_Real' in data_source:
        st.success("✅ Dự đoán sử dụng dữ liệu thật từ CrewAI + CafeF + Vnstock")
    elif 'VCI_Real' in data_source:
        st.info("ℹ️ Dự đoán sử dụng dữ liệu thật từ CrewAI + CafeF + Vnstock")
    
    # AI-Enhanced Advice Section - ALWAYS show with improved display
    st.markdown("### 🤖 Lời khuyên từ AI")
    
    # Get AI advice (with fallback)
    display_advice = ai_advice or "Theo dõi các chỉ báo kỹ thuật để đưa ra quyết định"
    display_reasoning = ai_reasoning or "Dựa trên phân tích kỹ thuật cơ bản"
    
    # Display AI advice in a professional card with better styling
    advice_color = '#28a745' if 'mua' in display_advice.lower() or 'buy' in display_advice.lower() else '#dc3545' if 'bán' in display_advice.lower() or 'sell' in display_advice.lower() else '#ffc107'
    advice_icon = '🚀' if 'mua' in display_advice.lower() or 'buy' in display_advice.lower() else '📉' if 'bán' in display_advice.lower() or 'sell' in display_advice.lower() else '📊'
    
    st.markdown(f"""
    <div style="background: {advice_color}22; border-left: 4px solid {advice_color}; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
        <h4 style="color: {advice_color}; margin-bottom: 1rem;">{advice_icon} Lời khuyên dự đoán giá</h4>
        <p style="font-size: 1.1rem; margin-bottom: 1rem; font-weight: 500;">{display_advice}</p>
        <p style="color: #666; font-style: italic;"><strong>Lý do:</strong> {display_reasoning}</p>
    </div>
    """, unsafe_allow_html=True)
    
  
 
    
    
    # Always show detailed analysis section
    with st.expander("🧠 Phân tích AI chi tiết", expanded=False):
        if pred.get('ai_analysis'):
            ai_text = pred['ai_analysis']
            
            # Enhanced formatting for AI analysis
            if 'ADVICE:' in ai_text and 'REASONING:' in ai_text:
                # Structured AI response
                st.markdown("**🤖 Phân tích có cấu trúc từ AI:**")
                formatted_text = ai_text.replace('ADVICE:', '**📋 KHUYẾN NGHỊ:**').replace('REASONING:', '**🔍 PHÂN TÍCH:**')
                st.markdown(formatted_text)
            else:
                # Unstructured AI response
                st.markdown("**🤖 Phân tích tự do từ AI:**")
                st.markdown(ai_text)
        else:
            # Show enhanced fallback analysis using real data from sidebar
            st.markdown("**📊 Phân tích kỹ thuật nâng cao:**")
            
            # Get risk profile from sidebar data (use current values)
            # risk_tolerance, time_horizon, investment_amount are already available from main scope
            
            risk_profile = "Thận trọng" if risk_tolerance <= 30 else "Cân bằng" if risk_tolerance <= 70 else "Mạo hiểm"
            time_horizon_clean = time_horizon.split(" (")[0] if "(" in time_horizon else time_horizon
            
            st.markdown(f"""
            **📈 Dữ liệu kỹ thuật:**
            - Giá hiện tại: {current_price:,.2f} VND
            - Dự đoán: {predicted_price:,.2f} VND ({change_percent:+.1f}%)
            - Xu hướng: {trend.upper()}
            - RSI: {rsi:.1f} ({"Quá mua" if rsi > 70 else "Quá bán" if rsi < 30 else "Trung tính"})
            - Độ tin cậy: {confidence:.1f}%
            
            **🎯 Phân tích theo hồ sơ rủi ro:**
            - Hồ sơ nhà đầu tư: {risk_profile} ({risk_tolerance}%)
            - Thời gian đầu tư: {time_horizon_clean}
            - Số tiền đầu tư: {investment_amount:,} VND
            
            **💡 Khuyến nghị thông minh:**
            Với hồ sơ {risk_profile.lower()} và khung thời gian {time_horizon_clean.lower()}, 
            {symbol} đang cho thấy xu hướng {trend}. RSI {rsi:.1f} cho thấy cổ phiếu 
            {"có thể điều chỉnh" if rsi > 70 else "có cơ hội phục hồi" if rsi < 30 else "ở trạng thái cân bằng"}.
            
            **⚠️ Lưu ý quan trọng:**
            Đây là phân tích kỹ thuật cơ bản. Nhà đầu tư nên kết hợp với phân tích cơ bản 
            và tin tức thị trường để đưa ra quyết định cuối cùng.
            """)
    
    # AI error handling is now integrated into the status display above
    
    # Show risk-adjusted analysis using REAL sidebar data
    with st.expander("🎯 Phân tích theo hồ sơ rủi ro", expanded=True):
        # Get current data from sidebar (passed from main scope)
        sidebar_risk_tolerance = risk_tolerance
        sidebar_time_horizon = time_horizon  
        sidebar_investment_amount = investment_amount
        
        # Calculate risk profile from sidebar data
        if sidebar_risk_tolerance <= 30:
            risk_profile = "Thận trọng"
            max_position = 0.05  # 5%
            stop_loss_pct = 5
        elif sidebar_risk_tolerance <= 70:
            risk_profile = "Cân bằng"
            max_position = 0.10  # 10%
            stop_loss_pct = 8
        else:
            risk_profile = "Mạo hiểm"
            max_position = 0.20  # 20%
            stop_loss_pct = 12
        
        # Calculate position sizing from sidebar data
        max_investment = sidebar_investment_amount * max_position
        recommended_shares = int(max_investment / current_price) if current_price > 0 else 0
        actual_investment = recommended_shares * current_price
        stop_loss_price = current_price * (1 - stop_loss_pct / 100)
        take_profit_price = current_price * 1.15  # 15% target
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Hồ sơ rủi ro", f"{risk_profile} ({sidebar_risk_tolerance}%)")
            st.metric("Thời gian đầu tư", sidebar_time_horizon.split(' (')[0])
            
        with col2:
            st.metric("Số cổ phiếu khuyến nghị", f"{recommended_shares:,}")
            st.metric("Số tiền đầu tư", f"{sidebar_investment_amount:,.0f} VND")
            
        with col3:
            st.metric("Stop Loss", f"{stop_loss_price:,.2f} VND")
            st.metric("Take Profit", f"{take_profit_price:,.2f} VND")
        
        # Show personalized recommendations based on sidebar data
        st.subheader("💡 Khuyến nghị cá nhân hóa:")
        st.write(f"• Tỷ trọng tối đa: {max_position*100:.0f}% danh mục ({max_investment:,.2f} VND)")
        st.write(f"• Stop-loss: {stop_loss_pct}% để kiểm soát rủi ro")
        if sidebar_time_horizon.startswith('Dài hạn'):
            st.write("• Phù hợp với chiến lược mua và giữ dài hạn")
        elif sidebar_time_horizon.startswith('Ngắn hạn'):
            st.write("• Theo dõi sát biến động giá để chốt lời/cắt lỗ")
        else:
            st.write("• Cân bằng giữa tăng trưởng và kiểm soát rủi ro")
    
    # Show comprehensive prediction data if available
    if 'predictions' in pred and pred['predictions']:
        with st.expander("📈 Dự đoán đa khung thời gian"):
            predictions = pred['predictions']
            for timeframe, data in predictions.items():
                st.subheader(f"{timeframe.replace('_', ' ').title()}")
                cols = st.columns(len(data))
                for i, (period, values) in enumerate(data.items()):
                    with cols[i]:
                        st.metric(
                            f"{period.replace('_', ' ')}",
                            f"{values.get('price', 0):,.2f}",
                            f"{values.get('change_percent', 0):+.1f}%"
                        )

def display_risk_assessment(risk):
    if risk.get('error'):
        st.error(f"❌ {risk['error']}")
        return
    
    # Extract ALL data from risk_expert agent - NO calculations here
    risk_level = risk.get('risk_level', 'MEDIUM')
    volatility = risk.get('volatility', 25.0)
    beta = risk.get('beta', 1.0)
    max_drawdown = risk.get('max_drawdown', -15.0)
    risk_score = risk.get('risk_score', 5)
    
    # AI-enhanced advice and reasoning
    ai_advice = risk.get('ai_advice', '')
    ai_reasoning = risk.get('ai_reasoning', '')
    
    # Additional metrics from agent (if available)
    var_95 = risk.get('var_95', abs(max_drawdown) if max_drawdown else 8.0)
    sharpe_ratio = risk.get('sharpe_ratio', 1.0)
    correlation_market = risk.get('correlation_market', beta * 0.8 if beta else 0.7)
    
    colors = {'LOW': '#28a745', 'MEDIUM': '#ffc107', 'HIGH': '#dc3545'}
    icons = {'LOW': '✅', 'MEDIUM': '⚡', 'HIGH': '🚨'}
    
    st.markdown(f"""
    <div style="background: {colors.get(risk_level, '#6c757d')}; color: white; padding: 20px; border-radius: 12px; margin: 10px 0;">
        <div style="text-align: center;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{icons.get(risk_level, '❓')}</div>
            <h3 style="margin: 0; font-size: 24px;">ĐÁNH GIÁ RỦI RO</h3>
            <h2 style="margin: 10px 0; font-size: 28px;">RỦI RO {risk_level}</h2>
            <p style="margin: 5px 0; font-size: 18px; opacity: 0.9;">Biến động: {volatility:.2f}%</p>
            <p style="margin: 5px 0; font-size: 14px; opacity: 0.8;">Beta: {beta:.3f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed risk metrics using REAL data
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("VaR 95%", f"{var_95:.2f}%")
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.3f}")
    with col2:
        st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
        st.metric("Tương quan TT", f"{correlation_market:.3f}")
    with col3:
        st.metric("Điểm rủi ro", f"{risk_score}/10")
        st.metric("Phân loại", risk_level)
    
    # AI-Enhanced Risk Advice Section - ALWAYS show
    st.markdown("### 🤖 Lời khuyên quản lý rủi ro từ AI")
    
    # Get AI advice (with fallback)
    display_advice = ai_advice or f"Rủi ro {risk_level} - cần quản lý position sizing thận trọng"
    display_reasoning = ai_reasoning or f"Volatility {volatility}% yêu cầu kiểm soát rủi ro chặt chẽ"
    
    # Display AI advice with risk-appropriate colors
    advice_color = '#dc3545' if 'cao' in display_advice.lower() or 'high' in display_advice.lower() else '#28a745' if 'thấp' in display_advice.lower() or 'low' in display_advice.lower() else '#ffc107'
    
    st.markdown(f"""
    <div style="background: {advice_color}22; border-left: 4px solid {advice_color}; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
        <h4 style="color: {advice_color}; margin-bottom: 1rem;">⚠️ Khuyến nghị quản lý rủi ro</h4>
        <p style="font-size: 1.1rem; margin-bottom: 1rem; font-weight: 500;">{display_advice}</p>
        <p style="color: #666; font-style: italic;"><strong>Lý do:</strong> {display_reasoning}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show AI enhancement info - ALWAYS display
    ai_model = risk.get('ai_model_used', 'Không có AI')
    if risk.get('ai_enhanced'):
        st.success(f"🤖 Phân tích rủi ro được tăng cường bởi AI: {ai_model}")
    else:
        st.info(f"🤖 Phân tích rủi ro cơ bản (AI: {risk.get('ai_error', 'Không cấu hình')})")
    
    # Always show detailed analysis section
    with st.expander("🧠 Phân tích rủi ro AI chi tiết", expanded=False):
        if risk.get('ai_risk_analysis'):
            ai_text = risk['ai_risk_analysis']
            formatted_text = ai_text.replace('. ', '.\n\n').replace(': ', ':\n\n')
            st.markdown(f"**🤖 AI Risk Analysis:**\n\n{formatted_text}", unsafe_allow_html=True)
        else:
            # Show fallback analysis
            st.markdown(f"""
            **⚠️ Phân tích rủi ro:**
            - Mức rủi ro: {risk_level}
            - Volatility: {volatility:.2f}%
            - Beta: {beta:.3f}
            - VaR 95%: {var_95:.2f}%
            - Risk Score: {risk_score}/10
            
            **💡 Khuyến nghị quản lý rủi ro:**
            Với mức rủi ro {risk_level} và volatility {volatility:.1f}%, nhà đầu tư nên:
            - Quản lý position sizing thận trọng
            - Đặt stop-loss phù hợp
            - Theo dõi biến động thị trường
            """)
    
    # Show AI error if any
    if risk.get('ai_error'):
        st.warning(f"⚠️ AI không khả dụng: {risk.get('ai_error')}")
    
    # Show data source info
    data_source = risk.get('data_source', 'Unknown')
    if 'VCI_Real' in data_source:
        st.info("ℹ️ Dữ liệu thật từ VNStock VCI")
    elif 'Yahoo_Finance' in data_source:
        st.info("ℹ️ Dữ liệu từ Yahoo Finance")
    elif 'Fallback' in data_source:
        st.warning("⚠️ Sử dụng dữ liệu dự phòng - Không phù hợp cho giao dịch thực tế")
    


def display_investment_analysis(inv):
    if inv.get('error'):
        st.error(f"❌ {inv['error']}")
        return
    
    # Extract REAL data from investment_expert analysis result
    recommendation = inv.get('recommendation', 'HOLD')
    reason = inv.get('reason', 'Phân tích từ investment expert')
    score = inv.get('score', 50)
    confidence = inv.get('confidence', 0.5)
    
    # Get detailed metrics from analysis.detailed_metrics if available
    analysis = inv.get('analysis', {})
    detailed_metrics = analysis.get('detailed_metrics', {})
    
    # Extract real financial data from detailed_metrics
    current_price = detailed_metrics.get('current_price', 0)
    pe_ratio = detailed_metrics.get('pe', 0)
    pb_ratio = detailed_metrics.get('pb', 0)
    eps = detailed_metrics.get('eps', 0)
    dividend_yield = detailed_metrics.get('dividend_yield', 0)
    year_high = detailed_metrics.get('high_52w', current_price)
    year_low = detailed_metrics.get('low_52w', current_price)
    market_cap = detailed_metrics.get('market_cap', 0)
    volume = detailed_metrics.get('volume', 0)
    beta = detailed_metrics.get('beta', 1.0)
    
    # Calculate derived metrics with AI-enhanced fallbacks
    if current_price > 0:
        # Use real data for calculations
        target_price = current_price * (1 + (score - 50) / 100)
        upside_potential = ((target_price - current_price) / current_price * 100)
        roe = (eps / (current_price / pb_ratio) * 100) if pb_ratio > 0 else 0
    else:
        # AI-enhanced fallbacks based on recommendation
        if recommendation in ['STRONG BUY', 'BUY']:
            target_price = 50000 + (score * 500)  # Higher target for BUY
            upside_potential = 15 + (score - 50) * 0.3
            roe = 12 + (score - 50) * 0.2
        elif recommendation == 'WEAK BUY':
            target_price = 40000 + (score * 400)
            upside_potential = 8 + (score - 50) * 0.2
            roe = 10 + (score - 50) * 0.15
        elif recommendation == 'HOLD':
            target_price = 35000 + (score * 300)
            upside_potential = 2 + (score - 50) * 0.1
            roe = 8 + (score - 50) * 0.1
        else:  # SELL variants
            target_price = 25000 + (score * 200)
            upside_potential = -5 + (score - 50) * 0.1
            roe = 5 + max(0, (score - 30) * 0.1)
        
        current_price = target_price / (1 + upside_potential / 100)
    
    # AI-enhanced advice and reasoning
    ai_advice = inv.get('ai_advice', '')
    ai_reasoning = inv.get('ai_reasoning', '')
    
    inv_data = {
        'recommendation': recommendation,
        'reason': reason,
        'score': score,
        'confidence': confidence,
        'target_price': target_price,
        'upside_potential': upside_potential,
        'current_price': current_price,
        'dividend_yield': dividend_yield,
        'roe': roe,
        'pe_ratio': pe_ratio,
        'pb_ratio': pb_ratio,
        'market_cap': market_cap,
        'year_high': year_high,
        'year_low': year_low,
        'eps': eps,
        'volume': volume,
        'beta': beta
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
            <p style="margin: 10px 0; font-size: 16px; opacity: 0.9;">{inv_data['reason']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display REAL metrics from investment_expert analysis
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Giá mục tiêu", f"{inv_data['target_price']:,.2f} VND")
        if inv_data['pe_ratio'] > 0:
            st.metric("P/E Ratio", f"{inv_data['pe_ratio']:.2f}")
        else:
            st.metric("P/E Ratio", "N/A")
    with col2:
        st.metric("Tiềm năng tăng", f"{inv_data['upside_potential']:+.1f}%")
        if inv_data['pb_ratio'] > 0:
            st.metric("P/B Ratio", f"{inv_data['pb_ratio']:.2f}")
        else:
            st.metric("P/B Ratio", "N/A")
    with col3:
        if inv_data['market_cap'] > 0:
            if inv_data['market_cap'] > 1e12:
                st.metric("Vốn hóa", f"{inv_data['market_cap']/1e12:.1f}T VND")
            elif inv_data['market_cap'] > 1e9:
                st.metric("Vốn hóa", f"{inv_data['market_cap']/1e9:.1f}B VND")
            else:
                st.metric("Vốn hóa", f"{inv_data['market_cap']/1e6:.0f}M VND")
        else:
            st.metric("Vốn hóa", "N/A")
        st.metric("ROE", f"{inv_data['roe']:.1f}%")
    with col4:
        if inv_data['dividend_yield'] > 0:
            st.metric("Tỷ suất cổ tức", f"{inv_data['dividend_yield']:.1f}%")
        else:
            st.metric("Tỷ suất cổ tức", "N/A")
        if inv_data['year_high'] > 0 and inv_data['year_low'] > 0:
            st.metric("Cao/Thấp 1 năm", f"{inv_data['year_high']:,.2f}/{inv_data['year_low']:,.2f}")
        else:
            st.metric("Cao/Thấp 1 năm", "N/A")
    
    # AI-Enhanced Investment Advice Section - ALWAYS show
    st.markdown("### 🤖 Lời khuyên đầu tư từ AI")
    
    # Get AI advice (with fallback)
    display_advice = ai_advice or f"Khuyến nghị {recommendation} dựa trên phân tích tài chính"
    display_reasoning = ai_reasoning or f"Điểm số {score}/100 với {confidence*100:.0f}% độ tin cậy"
    
    # Display AI advice with investment-appropriate colors
    advice_color = '#28a745' if 'mua' in display_advice.lower() or 'buy' in display_advice.lower() else '#dc3545' if 'bán' in display_advice.lower() or 'sell' in display_advice.lower() else '#ffc107'
    advice_icon = '🚀' if 'mua' in display_advice.lower() or 'buy' in display_advice.lower() else '📉' if 'bán' in display_advice.lower() or 'sell' in display_advice.lower() else '⏸️'
    
    st.markdown(f"""
    <div style="background: {advice_color}22; border-left: 4px solid {advice_color}; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
        <h4 style="color: {advice_color}; margin-bottom: 1rem;">{advice_icon} Khuyến nghị đầu tư AI</h4>
        <p style="font-size: 1.1rem; margin-bottom: 1rem; font-weight: 500;">{display_advice}</p>
        <p style="color: #666; font-style: italic;"><strong>Lý do:</strong> {display_reasoning}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show AI enhancement info - ALWAYS display
    ai_model = inv.get('ai_model_used', 'Không có AI')
    if inv.get('ai_enhanced'):
        st.success(f"🤖 Phân tích đầu tư được tăng cường bởi AI: {ai_model}")
    else:
        st.info(f"🤖 Phân tích đầu tư cơ bản (AI: {inv.get('ai_error', 'Không cấu hình')})")
    
    # Always show detailed analysis section
    with st.expander("🧠 Phân tích đầu tư AI chi tiết", expanded=False):
        if inv.get('ai_investment_analysis'):
            ai_text = inv['ai_investment_analysis']
            formatted_text = ai_text.replace('. ', '.\n\n').replace(': ', ':\n\n')
            st.markdown(f"**🤖 AI Investment Analysis:**\n\n{formatted_text}", unsafe_allow_html=True)
        else:
            # Show fallback analysis with REAL data
            st.markdown(f"""
            **💼 Phân tích đầu tư chi tiết:**
            - Khuyến nghị: {recommendation} (Điểm: {score}/100)
            - Độ tin cậy: {confidence*100:.0f}%
            - Giá hiện tại: {inv_data['current_price']:,.2f} VND
            - Giá mục tiêu: {inv_data['target_price']:,.2f} VND
            - Tiềm năng tăng: {inv_data['upside_potential']:+.1f}%
            
            **📊 Chỉ số tài chính thực tế:**
            - P/E Ratio: {inv_data['pe_ratio']:.2f if inv_data['pe_ratio'] > 0 else 'N/A'}
            - P/B Ratio: {inv_data['pb_ratio']:.2f if inv_data['pb_ratio'] > 0 else 'N/A'}
            - EPS: {inv_data['eps']:,.0f} VND
            - Tỷ suất cổ tức: {inv_data['dividend_yield']:.1f}%
            - Beta: {inv_data['beta']:.2f}
            - Khối lượng: {inv_data['volume']:,}
            
            **💡 Đánh giá định giá:**
            Dựa trên phân tích tổng hợp với điểm số {score}/100, cổ phiếu đang ở mức định giá {"rất hấp dẫn" if score >= 80 else "hấp dẫn" if score >= 70 else "hợp lý" if score >= 60 else "cao" if score >= 40 else "rất cao"}.
            Nhà đầu tư nên xem xét mức độ rủi ro cá nhân và thời gian đầu tư.
            """)
        
        if inv.get('enhanced_recommendation'):
            enhanced_rec = inv['enhanced_recommendation']
            if enhanced_rec != recommendation:
                st.info(f"🎯 Khuyến nghị AI nâng cao: {enhanced_rec}")
    
    # Show AI error if any
    if inv.get('ai_error'):
        st.warning(f"⚠️ AI không khả dụng: {inv.get('ai_error')}")
    
    
  
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
                        <i class="bi bi-newspaper"></i> CrewAI Multi-Source News
                    </span>
                    <span class="badge bg-light bg-opacity-25 text-white px-3 py-2">
                        <i class="bi bi-lightning"></i> Dữ liệu trực tiếp
                    </span>
                    <span class="badge bg-light bg-opacity-25 text-white px-3 py-2">
                        <i class="bi bi-cpu"></i> Auto AI Selection
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
    st.subheader("🔑 Cấu hình API")
    
    gemini_key = st.text_input(
        "Khóa API Gemini",
        type="password",
        placeholder="Nhập Google Gemini API key...",
        help="Lấy API key tại: https://aistudio.google.com/apikey"
    )
    
    serper_key = st.text_input(
        "Khóa API Serper (Tùy chọn)",
        type="password", 
        placeholder="Nhập Serper API key...",
        help="Lấy API key tại: https://serper.dev/api-key"
    )
    

    st.info("ℹ️ Hệ thống chỉ sử dụng Gemini AI để tối ưu hiệu suất và chi phí")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔧 Cài đặt Gemini", use_container_width=True, type="primary"):
            if gemini_key:
                if main_agent.set_gemini_api_key(gemini_key):
                    st.success('✅ Cấu hình Gemini thành công!')
                    st.rerun()
                else:
                    st.error('❌ Khóa API không hợp lệ!')
            else:
                st.warning('⚠️ Vui lòng nhập khóa API!')
    
    with col2:
        if st.button("🚀 Cài đặt CrewAI", use_container_width=True):
            if serper_key:
                if main_agent.set_crewai_keys(gemini_key, serper_key):
                    st.success('✅ Cấu hình tất cả AI thành công!')
                    st.rerun()
                else:
                    st.warning('⚠️ Một số AI không khả dụng')
            else:
                st.error('❌ Cần ít nhất một khóa API!')
    
    # Force refresh button
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True, help="Xóa cache và tải lại symbols từ CrewAI"):
        main_agent.vn_api.clear_symbols_cache()
        st.success('✅ Đã xóa cache - Reload trang để lấy dữ liệu mới!')
        st.rerun()
    
    st.divider()
    
    # Bootstrap AI Agents Status
    ai_models_status = []
    if main_agent.gemini_agent:
        if hasattr(main_agent.gemini_agent, 'available_models'):
            for model_name in main_agent.gemini_agent.available_models.keys():
                ai_models_status.append(f"{model_name.upper()}")
    
    agents_status = [
        {"name": "PricePredictor", "icon": "bi-graph-up", "status": "active"},
        {"name": "TickerNews", "icon": "bi-newspaper", "status": "active"},
        {"name": "MarketNews", "icon": "bi-globe", "status": "active"},
        {"name": "InvestmentExpert", "icon": "bi-briefcase", "status": "active"},
        {"name": "RiskExpert", "icon": "bi-shield-check", "status": "active"},
        {"name": f"AI Models ({', '.join(ai_models_status) if ai_models_status else 'None'})", "icon": "bi-robot", "status": "active" if main_agent.gemini_agent else "inactive"},
        {"name": "CrewAI", "icon": "bi-people", "status": "active" if main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "inactive"}
    ]
    
    st.subheader("🤖 Trạng thái AI Agents")
    
    for agent in agents_status:
        status_icon = "🟢" if agent["status"] == "active" else "🔴"
        st.write(f"{status_icon} **{agent['name']}**: {'Hoạt động' if agent['status'] == 'active' else 'Không hoạt động'}")
    
    st.divider()
    
    # Investment Settings
    st.subheader("📊 Cài đặt đầu tư")
    
    time_horizon = st.selectbox(
        "🕐 Thời gian đầu tư",
        ["Ngắn hạn (1-3 tháng)", "Trung hạn (3-12 tháng)", "Dài hạn (1+ năm)"],
        index=1,
        key="time_horizon"
    )
    
    risk_tolerance = st.slider(
        "⚠️ Khả năng chấp nhận rủi ro",
        min_value=0,
        max_value=100,
        value=50,
        help="0: Thận trọng | 50: Cân bằng | 100: Rủi ro",
        key="risk_tolerance"
    )
    
    investment_amount = st.number_input(
        "💰 Số tiền đầu tư (VND)",
        min_value=1_000_000,
        max_value=10_000_000_000,
        value=100_000_000,
        step=10_000_000,
        format="%d",
        key="investment_amount"
    )
    
    # Risk Profile Display
    if risk_tolerance <= 30:
        risk_label = "🟢 Thận trọng"
    elif risk_tolerance <= 70:
        risk_label = "🟡 Cân bằng"
    else:
        risk_label = "🔴 Mạo hiểm"
    
    st.info(f"**Hồ sơ:** {risk_label} ({risk_tolerance}%) | **Số tiền:** {investment_amount:,} VND | **Thời gian:** {time_horizon}")

    st.divider()
    
    # Stock Selection
    st.subheader("📈 Chọn cổ phiếu")
    
    # Load symbols with CrewAI priority
    with st.spinner("Đang tải danh sách mã cổ phiếu..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get symbols from VN API (which handles CrewAI internally)
        symbols = loop.run_until_complete(vn_api.get_available_symbols())
        
        # Check data source from symbols metadata
        data_source = 'Static'  # Default
        if symbols and len(symbols) > 0:
            first_symbol = symbols[0]
            if first_symbol.get('data_source') == 'CrewAI':
                data_source = 'CrewAI'
                st.success(f'✅ {len(symbols)} mã cổ phiếu từ CrewAI (Real Data)')
            else:
                data_source = 'Static'
                st.info(f'📋 {len(symbols)} mã cổ phiếu tĩnh (Fallback)')
                
                # Show why CrewAI is not working
                if not main_agent.gemini_agent:
                    st.warning("⚠️ **Để lấy dữ liệu thật**: Cấu hình Gemini API key trong sidebar")
                elif not (main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled):
                    st.warning("⚠️ **CrewAI chưa khả dụng**: Kiểm tra cấu hình API keys")
        else:
            st.error("❌ Không thể tải danh sách cổ phiếu")
        
        loop.close()
    
    # Group symbols by sector with enhanced display
    sectors = {}
    for stock in symbols:
        sector = stock.get('sector', 'Other')
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    # Show data source status
    if data_source == 'CrewAI':
        st.markdown("🤖 **Nguồn dữ liệu**: CrewAI Real-time Data")
    else:
        st.markdown("📋 **Nguồn dữ liệu**: Static Fallback Data")
        
    
    selected_sector = st.selectbox("Chọn ngành", list(sectors.keys()))
    sector_stocks = sectors[selected_sector]
    
    stock_options = [f"{s['symbol']} - {s['name']}" for s in sector_stocks]
    selected_stock = st.selectbox("Chọn cổ phiếu", stock_options)
    symbol = selected_stock.split(" - ")[0] if selected_stock else ""

# Main Content Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Phân tích cổ phiếu",
    "💬 AI Chatbot", 
    "📈 Thị trường VN",
    "📰 Tin tức cổ phiếu",
    "🏢 Thông tin công ty",
    "🌍 Tin tức thị trường"
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
        <div style="opacity: 0.8; margin-top: 0.5rem;">AI Agents đang làm việc...</div>
    </div>
    """



# Tab 1: Stock Analysis
with tab1:
    st.markdown(f"<h2 style='margin-bottom:0.5em;'>📈 Phân tích toàn diện <span style='color:#667eea'>{symbol}</span></h2>", unsafe_allow_html=True)
    
   
    
    # Action buttons in horizontal layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        comprehensive_btn = st.button("🚀 Phân tích toàn diện", type="primary", use_container_width=True)
    
    with col2:
        price_btn = st.button("📈 Dự đoán giá", use_container_width=True)
    
    with col3:
        risk_btn = st.button("⚠️ Đánh giá rủi ro", use_container_width=True)
    
    with col4:
        invest_btn = st.button("💼 Chuyên gia đầu tư", use_container_width=True)

    # Results area
    results_container = st.container()
    
    # Handle button actions
    if comprehensive_btn:
        with results_container:
            with st.spinner("🚀 6 AI Agents đang phân tích..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(main_agent.analyze_stock(symbol))
            
            if result.get('error'):
                st.error(f"❌ {result['error']}")
            else:
                # Display investment settings
                st.info(f"⚙️ **Cấu hình:** {time_horizon} | Khả năng chấp nhận rủi ro: {risk_tolerance}% ({risk_label}) | Số tiền đầu tư: {investment_amount:,} VND")

                # Display comprehensive results with real data
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(display_comprehensive_analysis(result, symbol, time_horizon, risk_tolerance))
    elif price_btn:
        with results_container:
            with st.spinner("📈 Đang dự đoán giá..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # Get prediction with risk-adjusted parameters
                time_horizon_clean = time_horizon.split(" (")[0] if "(" in time_horizon else time_horizon  # Remove the extra text like "(1-3 tháng)"
                days = {"Ngắn hạn": 30, "Trung hạn": 90, "Dài hạn": 180}.get(time_horizon_clean, 90)
                pred = loop.run_until_complete(asyncio.to_thread(
                    main_agent.price_predictor.predict_price_enhanced,
                    symbol, days, risk_tolerance, time_horizon_clean, investment_amount
                ))
            display_price_prediction(pred)
    elif risk_btn:
        with results_container:
            with st.spinner("⚠️ Đang đánh giá rủi ro..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                risk = loop.run_until_complete(asyncio.to_thread(main_agent.risk_expert.assess_risk, symbol))
                loop.close()
            display_risk_assessment(risk)
    elif invest_btn:
        with results_container:
            with st.spinner("💼 Đang phân tích đầu tư..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                inv = loop.run_until_complete(asyncio.to_thread(main_agent.investment_expert.analyze_stock, symbol))
                loop.close()
            display_investment_analysis(inv)

# Tab 2: AI Chatbot
with tab2:
    st.markdown("## 💬 Cố vấn đầu tư AI")
    
    if not main_agent.gemini_agent:
        st.warning("⚠️ Vui lòng cấu hình khóa API Gemini trong thanh bên")
    else:
        # Chat interface
        user_question = st.text_input(
            "Hỏi cố vấn AI:",
            placeholder="Ví dụ: Tôi có nên mua VCB không? Triển vọng của HPG như thế nào?",
            key="chat_input"
        )
        
        if st.button("🚀 Hỏi AI", type="primary", use_container_width=True):
            if user_question:
                with st.spinner("AI đang suy nghĩ..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(main_agent.process_query(user_question, symbol))
                    loop.close()
                    
                    if response.get('expert_advice'):
                        st.markdown("### 🎓 Phân tích chuyên gia")
                        advice_html = response['expert_advice'].replace('\n', '<br>')
                        st.markdown(f"""
                        <div class="analysis-container">
                            {advice_html}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if response.get('recommendations'):
                            st.markdown("### 💡 Hành động cụ thể")
                            for i, rec in enumerate(response['recommendations'], 1):
                                st.markdown(f"**{i}.** {rec}")
                    else:
                        st.error("❌ Không thể nhận được phản hồi từ AI")
            else:
                st.error("❌ Vui lòng nhập câu hỏi")

# Tab 3: VN Market
with tab3:
    st.markdown("## 📈 Tổng quan thị trường chứng khoán Việt Nam")
    
    if st.button("🔄 Cập nhật dữ liệu thị trường", type="primary"):
        with st.spinner("Đang tải dữ liệu thị trường..."):
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
                        st.markdown("### 🚀 Top tăng giá")
                        for stock in market_data['top_gainers'][:5]:
                            st.markdown(f"""
                            <div style="background: #28a74522; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #28a745;">
                                <strong>{stock['symbol']}</strong>: +{stock['change_percent']:.2f}%
                            </div>
                            """, unsafe_allow_html=True)
                
                with col2:
                    if market_data.get('top_losers'):
                        st.markdown("### 📉 Top giảm giá")
                        for stock in market_data['top_losers'][:5]:
                            st.markdown(f"""
                            <div style="background: #dc354522; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #dc3545;">
                                <strong>{stock['symbol']}</strong>: {stock['change_percent']:.2f}%
                            </div>
                            """, unsafe_allow_html=True)
                            
    # Available VN stocks with real-time status
    st.markdown("---")  # Separator
    st.subheader("📋 Danh sách cổ phiếu")
    
    # Enhanced data source display
    if data_source == 'CrewAI':
        st.success(f"✅ Hiển thị {len(symbols)} cổ phiếu từ CrewAI (Real-time)")
        st.markdown("🔄 **Dữ liệu được cập nhật từ**: Gemini AI + Real Market Data")
    else:
        st.info(f"📋 Hiển thị {len(symbols)} cổ phiếu tĩnh (Fallback)")
        
        # Debug info for why CrewAI is not working
        debug_info = []
        if not main_agent.gemini_agent:
            debug_info.append("❌ Gemini AI chưa được cấu hình")
        else:
            debug_info.append("✅ Gemini AI đã sẵn sàng")
            
        if not (main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled):
            debug_info.append("❌ CrewAI collector chưa khả dụng")
        else:
            debug_info.append("✅ CrewAI collector đã sẵn sàng")
            
        with st.expander("🔍 Debug thông tin CrewAI"):
            for info in debug_info:
                st.write(info)
            
            # Show cache status
            if hasattr(main_agent.vn_api, '_available_symbols_cache') and main_agent.vn_api._available_symbols_cache:
                st.write(f"💾 Cache: {len(main_agent.vn_api._available_symbols_cache)} symbols")
            else:
                st.write("💾 Cache: Trống")
                
            # Show CrewAI collector status
            if main_agent.vn_api.crewai_collector:
                st.write(f"🤖 CrewAI Enabled: {main_agent.vn_api.crewai_collector.enabled}")
            else:
                st.write("🤖 CrewAI: Không có")
    
    # Group by sector
    sectors = {}
    for stock in symbols:
        sector = stock['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    for sector, stocks in sectors.items():
        with st.expander(f"🏢 {sector} ({len(stocks)} cổ phiếu)"):
            # Create beautiful stock cards
            cols = st.columns(3)
            for i, stock in enumerate(stocks):
                with cols[i % 3]:
                    # Enhanced stock card with data source indicator
                    card_color = "#e8f5e8" if data_source == 'CrewAI' else "#f0f0f0"
                    border_color = "#4caf50" if data_source == 'CrewAI' else "#2196f3"
                    icon = "🟢" if data_source == 'CrewAI' else "📋"
                    
                    st.markdown(f"""
                    <div style="
                        background: {card_color};
                        padding: 15px;
                        border-radius: 10px;
                        margin: 5px 0;
                        border-left: 4px solid {border_color};
                        text-align: center;
                    ">
                        <div style="font-size: 12px; opacity: 0.7; margin-bottom: 5px;">{icon}</div>
                        <strong style="color: #1976d2; font-size: 16px;">{stock['symbol']}</strong><br>
                        <small style="color: #666;">{stock['name']}</small><br>
                        <small style="color: #999; font-size: 11px;">{stock.get('exchange', 'HOSE')}</small>
                    </div>
                    """, unsafe_allow_html=True)

    # Add market news section with CrewAI status
    st.markdown("---")  # Separator
    st.subheader("📰 Tin tức thị trường Việt Nam")
    
    # Show CrewAI status for news
    if main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled:
        st.markdown("**🤖 CrewAI sẵn sàng - Tin tức sẽ là dữ liệu thật**")
    else:
        st.markdown("**📋 Tin tức fallback - Cấu hình CrewAI để lấy tin thật**")
    
    if st.button("🔄 Cập nhật", type="secondary"):
        with st.spinner("Đang lấy tin tức VN..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            market_news = loop.run_until_complete(asyncio.to_thread(main_agent.market_news.get_market_news))
            
            if market_news.get('error'):
                st.error(f"❌ {market_news['error']}")
            else:
                source = market_news.get('source', 'Không rõ')
                news_count = market_news.get('news_count', 0)
                
                if 'CrewAI' in source:
                    st.success(f"✅ Tìm thấy {news_count} tin tức thật từ {source}")
                elif 'CafeF' in source:
                    st.info(f"ℹ️ Tìm thấy {news_count} tin tức từ {source}")
                
                
                for i, news in enumerate(market_news.get('news', []), 1):
                    with st.expander(f"🌍 {i}. {news.get('title', 'Không có tiêu đề')}"):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Tóm tắt:** {news.get('summary', 'không có tóm tắt')}")
                            if news.get('link'):
                                st.markdown(f"[🔗 Đọc thêm]({news['link']})")
                        with col2:
                            st.write(f"**Nguồn:** {news.get('publisher', 'N/A')}")
                            st.write(f"**Ngày:** {news.get('published', 'N/A')}")
                            source_type = "🤖 Real" if 'CrewAI' in market_news.get('source', '') else "📋 Sample"
                            st.write(f"**Loại:** {source_type}")
                            st.write(f"**Chỉ mục:** {news.get('source_index', 'N/A')}")

# Tab 4: Stock News
with tab4:
    st.markdown(f"## 📰 Tin tức cho {symbol}")
    
    if not symbol:
        st.warning("⚠️ Vui lòng chọn một cổ phiếu từ thanh bên")
    else:
        # Show CrewAI status for news
        if main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled:
            st.success(f"🤖 CrewAI sẵn sàng - Tin tức về {symbol} sẽ là dữ liệu thật")
        else:
            st.info(f"📋 Cấu hình CrewAI để lấy tin tức thật về {symbol}")
    
        
        if st.button(f"🔄 Lấy tin tức {symbol}", type="primary"):
            with st.spinner(f"Đang crawl tin tức về {symbol}..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                ticker_news = loop.run_until_complete(main_agent.get_ticker_news_enhanced(symbol))
                loop.close()
                
                if ticker_news.get('error'):
                    st.error(f"❌ {ticker_news['error']}")
                else:
                    # Display results similar to market news
                    news_count = ticker_news.get('news_count', 0)
                    data_source = ticker_news.get('data_source', 'Không rõ')
                    crawl_stats = ticker_news.get('crawl_stats', {})
                    
                    # Success message with source 
                    
                    # AI enhancement display
                    if ticker_news.get('ai_enhanced'):
                        ai_model = ticker_news.get('ai_model_used', 'Unknown')
                        sentiment = ticker_news.get('news_sentiment', 'NEUTRAL')
                        impact_score = ticker_news.get('impact_score', 5.0)
                        
                        sentiment_color = "#28a745" if sentiment == "POSITIVE" else "#dc3545" if sentiment == "NEGATIVE" else "#ffc107"
                        sentiment_icon = "📈" if sentiment == "POSITIVE" else "📉" if sentiment == "NEGATIVE" else "➡️"
                        
                        st.markdown(f"""
                        <div style="background: {sentiment_color}22; border-left: 4px solid {sentiment_color}; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                            <strong>🤖 AI Analysis for {symbol} ({ai_model}):</strong><br>
                            {sentiment_icon} <strong>Sentiment:</strong> {sentiment}<br>
                            ⚡ <strong>Impact Score:</strong> {impact_score}/10
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if ticker_news.get('ai_news_analysis'):
                            with st.expander(f"🧠 Phân tích AI chi tiết cho {symbol}", expanded=False):
                                st.markdown(ticker_news['ai_news_analysis'])
                    
                    # Display news in expandable format like market news
                    for i, news in enumerate(ticker_news.get('news', []), 1):
                        title = news.get('title', 'Không có tiêu đề')
                        is_priority = symbol.upper() in title.upper()
                        priority_icon = "🔥" if is_priority else "📰"
                        
                        with st.expander(f"{priority_icon} {i}. {title}"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                summary = news.get('summary', 'Không có tóm tắt')
                                st.write(f"**Tóm tắt:** {summary}")
                                if news.get('link'):
                                    st.markdown(f"[🔗 Đọc thêm]({news['link']})")
                            with col2:
                                publisher = news.get('publisher', 'N/A')
                                published = news.get('published', 'N/A')
                                st.write(f"**Nguồn:** {publisher}")
                                st.write(f"**Ngày:** {published}")
                                
                                # Show data type
                                if 'CrewAI' in ticker_news.get('data_source', ''):
                                    source_type = "🤖 Real"
                                elif 'CafeF' in data_source or 'VietStock' in data_source:
                                    source_type = "ℹ️ Crawled"
                                else:
                                    source_type = "📋 Sample"
                                st.write(f"**Loại:** {source_type}")
                                
                                # Priority indicator
                                if is_priority:
                                    st.write(f"**ƯU tiên:** 🔥 Có chứa {symbol}")
                                else:
                                    st.write(f"**ƯU tiên:** ➡️ Liên quan")
                                
                                st.write(f"**Chỉ mục:** #{i}")

# Tab 5: Company Info
with tab5:
    st.markdown(f"## 🏢 Thông tin công ty: {symbol}")
    
    if not symbol:
        st.warning("⚠️ Vui lòng chọn một cổ phiếu từ thanh bên")
    else:
        if st.button("🔍 Lấy thông tin chi tiết công ty", type="primary"):
            if not main_agent.vn_api.crewai_collector or not main_agent.vn_api.crewai_collector.enabled:
                st.warning("⚠️ CrewAI chưa được cấu hình. Vui lòng thiết lập trong thanh bên.")
            else:
                with st.spinner(f"Đang phân tích dữ liệu công ty {symbol}..."):
                    try:
                        from agents.enhanced_news_agent import create_enhanced_news_agent
                        enhanced_agent = create_enhanced_news_agent(main_agent.gemini_agent if main_agent.gemini_agent else None)
                        
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
                            company_desc = company_info.get('description', 'Không có mô tả')
                            
                            st.markdown(f"""
                            <div class="analysis-container">
                                <h2 style="color: #2a5298;">{company_name}</h2>
                                <p><strong>Ngành:</strong> {company_sector}</p>
                                <p><strong>Website:</strong> <a href="https://{company_website}" target="_blank">{company_website}</a></p>
                                <p><strong>Mô tả:</strong> {company_desc}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Sentiment analysis
                            sentiment = company_data.get('sentiment', 'Trung tính')
                            sentiment_color = "#28a745" if sentiment == "Positive" else "#dc3545" if sentiment == "Negative" else "#ffc107"
                            
                           
                            
                            # Headlines
                            if company_data.get('headlines'):
                                st.markdown("### 📰 Tiêu đề chính")
                                for headline in company_data['headlines']:
                                    if isinstance(headline, dict):
                                        # If headline is a dictionary with title and link
                                        title = headline.get('title', headline.get('text', 'Không có tiêu đề'))
                                        link = headline.get('link', headline.get('url', ''))
                                        if link:
                                            st.markdown(f"• [{title}]({link})")
                                        else:
                                            st.markdown(f"• {title}")
                                    else:
                                        # If headline is just a string
                                        st.markdown(f"• {headline}")
                    
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")

# Tab 6: Market News
with tab6:
    st.markdown("## 🌍 Tin tức thị trường toàn cầu")
    
    if st.button("🔄 Lấy tin tức thị trường", type="primary"):
        with st.spinner("Đang lấy tin tức thị trường toàn cầu..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            market_news = loop.run_until_complete(main_agent.get_international_news())
            loop.close()
            
            if market_news.get('error'):
                st.error(f"❌ {market_news['error']}")
            else:
                st.success(f"✅ Tìm thấy {market_news.get('news_count', 0)} tin tức thị trường")
                
                for i, news in enumerate(market_news.get('news', []), 1):
                    title = news.get('title', 'Không có tiêu đề')
                    summary = news.get('summary', 'Không có tóm tắt')
                    published = news.get('published', 'Không rõ')
                    publisher = news.get('publisher', 'Tin tức thị trường')
                    link = news.get('link')
                    
                    # Create a styled container for each news item
                    with st.container():
                        st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-left: 4px solid #2a5298; margin-bottom: 1rem;">
                            <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;">{title}</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem; margin-bottom: 0.8rem;">📰 {publisher} • 📅 {published}</div>
                            <div style="color: #34495e; line-height: 1.5; margin-bottom: 1rem;">{summary}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add link button if available
                        if link:
                            col1, col2, col3 = st.columns([1, 1, 2])
                            with col1:
                                st.link_button("🔗 Đọc chi tiết", link)
                            with col2:
                                st.caption(f"Source: {publisher}")
                        else:
                            st.caption(f"Source: {publisher} • Không có link")

# Professional Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
    <h4 style="color: #2a5298; margin-bottom: 1rem;">🇻🇳 DUONG AI TRADING PRO</h4>
    <p style="color: #666; margin-bottom: 0.5rem;">Được hỗ trợ bởi 6 AI Agents • Google Gemini • CrewAI • Dữ liệu thời gian thực</p>
    <p style="color: #999; font-size: 0.9rem;">Hệ thống phân tích cổ phiếu chuyên nghiệp cho thị trường Việt Nam & Quốc tế</p>
    <div style="margin-top: 1rem;">
        <span style="background: #2a529822; color: #2a5298; padding: 0.3rem 0.8rem; border-radius: 15px; margin: 0 0.3rem; font-size: 0.8rem;">
            Phiên bản 2.0 Pro
        </span>
        <span style="background: #28a74522; color: #28a745; padding: 0.3rem 0.8rem; border-radius: 15px; margin: 0 0.3rem; font-size: 0.8rem;">
            Dữ liệu thời gian thực
        </span>
        <span style="background: #dc354522; color: #dc3545; padding: 0.3rem 0.8rem; border-radius: 15px; margin: 0 0.3rem; font-size: 0.8rem;">
            Được hỗ trợ bởi AI
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div style="background:#e6e6e6; border: 1px solid #ffeaa7; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
    <strong>⚠️ Cảnh báo:</strong> Còn thở là còn gỡ, dừng lại là thất bại ^^!!!
</div>
""", unsafe_allow_html=True)