# src/ui/styles.py
"""
Modern CSS Styles for AI Trading Team Vietnam
"""

import streamlit as st

def load_custom_css():
    """Load modern CSS styles for the application"""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --success-gradient: linear-gradient(135deg, #00C851 0%, #007E33 100%);
        --danger-gradient: linear-gradient(135deg, #FF4444 0%, #CC0000 100%);
        --warning-gradient: linear-gradient(135deg, #FF8800 0%, #FF6600 100%);
        --shadow-light: 0 8px 32px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        background: var(--primary-gradient);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-medium);
        position: relative;
        overflow: hidden;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 1;
        flex-wrap: wrap;
        gap: 2rem;
    }
    
    .header-left h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .flag {
        font-size: 3.2rem;
        margin-right: 1rem;
        animation: wave 3s ease-in-out infinite;
    }
    
    @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-8deg); }
        75% { transform: rotate(8deg); }
    }
    
    .subtitle {
        font-size: 1.3rem;
        opacity: 0.95;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    .highlight {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 0.7rem;
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .agent-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
        margin-top: 1.5rem;
    }
    
    .badge {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        backdrop-filter: blur(15px);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .badge:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .live-indicator {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.8rem 1.5rem;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(15px);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .pulse {
        width: 12px;
        height: 12px;
        background: #00ff88;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(0, 255, 136, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }
    
    .stock-overview-modern {
        background: white;
        border-radius: 20px;
        box-shadow: var(--shadow-light);
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
    }
    
    .stock-overview-modern::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
    }
    
    .stock-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .stock-symbol {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stock-meta {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
    }
    
    .sector, .exchange {
        background: #f8f9fa;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #666;
    }
    
    .price-container {
        text-align: right;
    }
    
    .current-price {
        font-size: 2.5rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .currency {
        font-size: 1.2rem;
        opacity: 0.7;
        font-weight: 400;
    }
    
    .price-change {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .price-change.positive {
        color: #00C851;
    }
    
    .price-change.negative {
        color: #FF4444;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-light);
    }
    
    .metric-icon {
        font-size: 2rem;
        opacity: 0.8;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #333;
    }
    
    .recommendation-card-modern {
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        color: white;
        box-shadow: var(--shadow-medium);
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    
    .recommendation-card-modern::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.2) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .rec-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .rec-icon {
        font-size: 4rem;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .rec-title h2 {
        font-size: 1rem;
        font-weight: 500;
        margin: 0;
        opacity: 0.9;
        letter-spacing: 2px;
    }
    
    .rec-title h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0.5rem 0 0 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .rec-reason {
        font-size: 1.1rem;
        line-height: 1.6;
        opacity: 0.95;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    .confidence-bar {
        background: rgba(255, 255, 255, 0.2);
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .confidence-fill {
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 4px;
        transition: width 1s ease;
    }
    
    .confidence-text {
        font-size: 0.9rem;
        opacity: 0.8;
        font-weight: 500;
    }
    
    .stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-light) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: var(--shadow-medium) !important;
    }
    
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem;
        background: var(--primary-gradient);
        border-radius: 20px;
        margin: 2rem 0;
        color: white;
        text-align: center;
        box-shadow: var(--shadow-medium);
    }
    
    .loading-content {
        max-width: 400px;
    }
    
    .loading-spinner {
        position: relative;
        width: 80px;
        height: 80px;
        margin: 0 auto 2rem auto;
    }
    
    .spinner-ring {
        position: absolute;
        width: 100%;
        height: 100%;
        border: 3px solid transparent;
        border-top: 3px solid rgba(255, 255, 255, 0.8);
        border-radius: 50%;
        animation: spin 1.5s linear infinite;
    }
    
    .spinner-ring:nth-child(2) {
        width: 60px;
        height: 60px;
        top: 10px;
        left: 10px;
        animation-delay: -0.5s;
        border-top-color: rgba(255, 255, 255, 0.6);
    }
    
    .spinner-ring:nth-child(3) {
        width: 40px;
        height: 40px;
        top: 20px;
        left: 20px;
        animation-delay: -1s;
        border-top-color: rgba(255, 255, 255, 0.4);
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .loading-subtitle {
        opacity: 0.9;
        margin-bottom: 1.5rem;
    }
    
    .agents-status {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .agent-status {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 0.5rem 0.8rem;
        border-radius: 10px;
        font-size: 0.85rem;
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .agent-status.working {
        animation: pulse-agent 1.5s infinite;
    }
    
    @keyframes pulse-agent {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .alert-modern {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        color: white;
        box-shadow: var(--shadow-light);
    }
    
    .alert-icon {
        font-size: 2rem;
        flex-shrink: 0;
    }
    
    .alert-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    .alert-subtitle {
        opacity: 0.9;
        font-size: 0.95rem;
    }
    
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: var(--shadow-light);
        margin: 2rem 0;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .chart-container h4 {
        color: #333;
        font-weight: 600;
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
    }
    
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            text-align: center;
            gap: 1.5rem;
        }
        
        .header-left h1 {
            font-size: 2rem;
        }
        
        .stock-header {
            flex-direction: column;
            text-align: center;
        }
        
        .price-container {
            text-align: center;
        }
        
        .current-price {
            font-size: 2rem;
        }
        
        .stock-symbol {
            font-size: 2.5rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .rec-header {
            flex-direction: column;
            gap: 1rem;
        }
        
        .rec-title h1 {
            font-size: 2.5rem;
        }
        
        .agent-badges {
            justify-content: center;
        }
    }
    
    html {
        scroll-behavior: smooth;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-gradient);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)