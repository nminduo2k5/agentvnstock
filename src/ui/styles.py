# src/ui/styles.py
"""
CSS Styles cho AI Trading Team Vietnam
Custom styling cho Streamlit components
"""

import streamlit as st

def load_custom_css():
    """Load custom CSS styles for the application"""
    
    css = """
    <style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .header-container p {
        margin: 1rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Agent cards styling */
    .agent-card {
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .analyst-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left-color: #2196f3;
    }
    
    .risk-manager-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left-color: #ff9800;
    }
    
    .portfolio-manager-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left-color: #9c27b0;
    }
    
    /* Stock overview card */
    .stock-overview {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Recommendation cards */
    .recommendation-card {
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    
    .buy-recommendation {
        background: linear-gradient(135deg, #4caf50 0%, #81c784 100%);
    }
    
    .sell-recommendation {
        background: linear-gradient(135deg, #f44336 0%, #e57373 100%);
    }
    
    .hold-recommendation {
        background: linear-gradient(135deg, #ff9800 0%, #ffb74d 100%);
    }
    
    /* Metrics cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
    }
    
    .metric-card h3 {
        margin: 0;
        color: #333;
        font-size: 1.8rem;
    }
    
    .metric-card p {
        margin: 5px 0 0 0;
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .stError {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    
    .stWarning {
        background-color: #fff3cd;
        border-color: #ffeaa7;
        color: #856404;
    }
    
    /* Market ticker styling */
    .market-ticker {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        border: 1px solid #dee2e6;
    }
    
    /* Loading animation */
    .loading-container {
        text-align: center;
        padding: 40px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 10px;
        color: white;
        margin: 20px 0;
    }
    
    .loading-spinner {
        border: 4px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top: 4px solid white;
        width: 40px;
        height: 40px;
        animation: spin 2s linear infinite;
        margin: 0 auto 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .dataframe th {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        text-align: center;
    }
    
    .dataframe td {
        text-align: center;
        padding: 10px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .header-container h1 {
            font-size: 2rem;
        }
        
        .header-container p {
            font-size: 1rem;
        }
        
        .agent-card {
            padding: 15px;
            margin: 10px 0;
        }
        
        .stock-overview {
            padding: 20px;
        }
        
        .metric-card {
            padding: 15px;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom footer */
    .custom-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 0.8rem;
        z-index: 999;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def get_agent_colors():
    """Get color scheme for agents"""
    return {
        "analyst": {
            "primary": "#2196f3",
            "background": "#e3f2fd",
            "gradient": "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)"
        },
        "risk_manager": {
            "primary": "#ff9800", 
            "background": "#fff3e0",
            "gradient": "linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)"
        },
        "portfolio_manager": {
            "primary": "#9c27b0",
            "background": "#f3e5f5", 
            "gradient": "linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)"
        }
    }

def get_recommendation_colors():
    """Get color scheme for recommendations"""
    return {
        "BUY": {
            "color": "#4caf50",
            "background": "#e8f5e8",
            "gradient": "linear-gradient(135deg, #4caf50 0%, #81c784 100%)"
        },
        "SELL": {
            "color": "#f44336",
            "background": "#ffebee", 
            "gradient": "linear-gradient(135deg, #f44336 0%, #e57373 100%)"
        },
        "HOLD": {
            "color": "#ff9800",
            "background": "#fff3e0",
            "gradient": "linear-gradient(135deg, #ff9800 0%, #ffb74d 100%)"
        }
    }

def apply_custom_theme():
    """Apply custom theme to Streamlit"""
    
    # Custom CSS for Vietnamese market theme
    vn_theme = """
    <style>
    /* Vietnamese flag colors theme */
    .vn-red { color: #da020e; }
    .vn-yellow { color: #ffff00; }
    
    /* Vietnam-specific styling */
    .vn-market-card {
        background: linear-gradient(135deg, #da020e 0%, #ffff00 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    /* Currency formatting for VND */
    .vnd-amount {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        color: #2e7d32;
    }
    
    /* Stock ticker styling */
    .stock-ticker {
        background: #f5f5f5;
        padding: 5px 10px;
        border-radius: 5px;
        font-family: monospace;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }
    
    /* Vietnamese text styling */
    .vietnamese-text {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }
    </style>
    """
    
    st.markdown(vn_theme, unsafe_allow_html=True)

def show_loading_animation(message: str = "Đang xử lý..."):
    """Show loading animation with Vietnamese text"""
    
    loading_html = f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <h3>{message}</h3>
        <p>Vui lòng chờ trong giây lát...</p>
    </div>
    """
    
    return st.markdown(loading_html, unsafe_allow_html=True)

def format_stock_symbol(symbol: str) -> str:
    """Format stock symbol with styling"""
    
    return f'<span class="stock-ticker">{symbol}</span>'

def format_vnd_amount(amount: float) -> str:
    """Format VND amount with styling"""
    
    if amount >= 1_000_000_000:
        formatted = f"{amount/1_000_000_000:.1f} tỷ VND"
    elif amount >= 1_000_000:
        formatted = f"{amount/1_000_000:.1f} triệu VND"
    else:
        formatted = f"{amount:,.0f} VND"
    
    return f'<span class="vnd-amount">{formatted}</span>'

# CSS Constants
AGENT_CARD_CSS = """
    border-radius: 10px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-left: 5px solid;
"""

RECOMMENDATION_CARD_CSS = """
    padding: 25px;
    border-radius: 15px;
    margin: 20px 0;
    text-align: center;
    color: white;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
"""

METRIC_CARD_CSS = """
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    text-align: center;
    margin: 10px 0;
    border: 1px solid #e0e0e0;
"""