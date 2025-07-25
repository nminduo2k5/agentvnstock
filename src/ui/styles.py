# src/ui/styles.py
"""
Modern CSS Styles for AI Trading Team Vietnam
"""

import streamlit as st

def load_custom_css():
    """Load Bootstrap-integrated professional CSS"""
    css = """
    <!-- Bootstrap 5.3 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        /* Bootstrap Integration */
        --bs-primary: #2a5298;
        --bs-primary-rgb: 42, 82, 152;
        --bs-secondary: #667eea;
        --bs-success: #28a745;
        --bs-danger: #dc3545;
        --bs-warning: #ffc107;
        --bs-info: #17a2b8;
        
        /* Custom Variables */
        --primary-gradient: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        --secondary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Bootstrap Font Integration */
    * {
        font-family: 'Inter', var(--bs-font-sans-serif);
    }
    
    body {
        background: linear-gradient(135deg, var(--bs-gray-100) 0%, var(--bs-gray-200) 100%);
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Bootstrap Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bs-primary);
        border-radius: 4px;
    }
    
    /* Bootstrap Enhanced Header */
    .main-header {
        background: var(--primary-gradient);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        position: relative;
    }
    
    .header-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.95;
        margin-bottom: 1.5rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Bootstrap Card Enhancements */
    .card {
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    /* Professional Metrics */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card-pro {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
    }
    
    .metric-card-pro:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-left-color: var(--primary-dark);
    }
    
    .metric-title-pro {
        font-size: 0.85rem;
        color: #666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value-pro {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.3rem;
    }
    
    .metric-change-pro {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Professional Badges */
    .feature-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem;
        justify-content: center;
        margin-top: 1.5rem;
        position: relative;
        z-index: 1;
    }
    
    .feature-badge {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        backdrop-filter: blur(15px);
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .feature-badge:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Bootstrap Button Enhancements */
    .stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(42, 82, 152, 0.3) !important;
    }
    
    .btn-secondary {
        background: var(--secondary-gradient);
    }
    
    .btn-success {
        background: var(--success-gradient);
    }
    
    .btn-danger {
        background: var(--danger-gradient);
    }
    
    .btn-warning {
        background: var(--warning-gradient);
        color: var(--dark-color);
    }
    
    /* Professional Status Indicators */
    .status-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .status-active {
        background: var(--success-color);
        animation: pulse-pro 2s infinite;
    }
    
    .status-inactive {
        background: var(--danger-color);
    }
    
    .status-warning {
        background: var(--warning-color);
    }
    
    @keyframes pulse-pro {
        0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
        100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
    }
    
    /* Professional Analysis Container */
    .analysis-container-pro {
        background: white;
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
    }
    
    .analysis-container-pro::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
    }
    
    /* Professional Stock Header */
    .stock-header-pro {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        gap: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 2px solid #f8f9fa;
    }
    
    .stock-symbol-pro {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    .stock-meta-pro {
        display: flex;
        gap: 1rem;
        margin-top: 0.8rem;
        flex-wrap: wrap;
    }
    
    .sector-tag, .exchange-tag {
        background: var(--light-color);
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #666;
        border: 1px solid #e9ecef;
    }
    
    .price-container-pro {
        text-align: right;
        min-width: 200px;
    }
    
    .current-price-pro {
        font-size: 2.8rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .currency-pro {
        font-size: 1.1rem;
        opacity: 0.7;
        font-weight: 400;
        color: #666;
    }
    
    .price-change-pro {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 0.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .price-change-pro.positive {
        color: var(--success-color);
    }
    
    .price-change-pro.negative {
        color: var(--danger-color);
    }
    
    .price-change-pro.neutral {
        color: #6c757d;
    }
    
    /* Professional Metrics Grid */
    .metrics-grid-pro {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card-grid {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .metric-card-grid:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-left-color: var(--primary-dark);
    }
    
    .metric-icon-pro {
        font-size: 2.2rem;
        opacity: 0.8;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .metric-label-pro {
        font-size: 0.85rem;
        color: #666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value-grid {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.3rem;
    }
    
    /* Professional Recommendation Cards */
    .recommendation-card-pro {
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        margin: 1.5rem 0;
        color: white;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .recommendation-card-pro:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
    }
    
    .recommendation-card-pro::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.15) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .rec-header-pro {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 1;
    }
    
    .rec-icon-pro {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .rec-title-pro {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .rec-subtitle-pro {
        font-size: 1rem;
        font-weight: 500;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        letter-spacing: 1px;
        position: relative;
        z-index: 1;
    }
    
    .rec-reason-pro {
        font-size: 1.1rem;
        line-height: 1.6;
        opacity: 0.95;
        margin: 1rem 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    .confidence-bar-pro {
        background: rgba(255, 255, 255, 0.2);
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
        margin: 1rem 0;
        position: relative;
        z-index: 1;
    }
    
    .confidence-fill-pro {
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 3px;
        transition: width 1.5s ease;
    }
    
    .confidence-text-pro {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Streamlit Button Overrides */
    .stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-sm) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-sm) !important;
        position: relative !important;
        overflow: hidden !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
        background: var(--primary-dark) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Professional Loading */
    .loading-container-pro {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 3rem;
        background: var(--primary-gradient);
        border-radius: var(--border-radius-lg);
        margin: 2rem 0;
        color: white;
        text-align: center;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .loading-container-pro::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .loading-content-pro {
        max-width: 400px;
        position: relative;
        z-index: 1;
    }
    
    .loading-spinner-pro {
        position: relative;
        width: 60px;
        height: 60px;
        margin: 0 auto 1.5rem auto;
    }
    
    .spinner-ring-pro {
        position: absolute;
        width: 100%;
        height: 100%;
        border: 3px solid transparent;
        border-top: 3px solid rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        animation: spin-pro 1.2s linear infinite;
    }
    
    .spinner-ring-pro:nth-child(2) {
        width: 75%;
        height: 75%;
        top: 12.5%;
        left: 12.5%;
        animation-delay: -0.4s;
        border-top-color: rgba(255, 255, 255, 0.7);
    }
    
    .spinner-ring-pro:nth-child(3) {
        width: 50%;
        height: 50%;
        top: 25%;
        left: 25%;
        animation-delay: -0.8s;
        border-top-color: rgba(255, 255, 255, 0.5);
    }
    
    @keyframes spin-pro {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-title-pro {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .loading-subtitle-pro {
        opacity: 0.9;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
        position: relative;
        z-index: 1;
    }
    
    .agents-status-pro {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.8rem;
        margin-top: 1.5rem;
        position: relative;
        z-index: 1;
    }
    
    .agent-status-pro {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 0.6rem 1rem;
        border-radius: var(--border-radius-sm);
        font-size: 0.85rem;
        backdrop-filter: blur(15px);
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s ease;
    }
    
    .agent-status-pro:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-1px);
    }
    
    .agent-status-pro.working {
        animation: pulse-agent-pro 1.8s infinite;
    }
    
    @keyframes pulse-agent-pro {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Professional Alerts */
    .alert-pro {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        margin: 1.5rem 0;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid;
        background: white;
    }
    
    .alert-pro.success {
        border-left-color: var(--success-color);
        background: #d4edda;
        color: #155724;
    }
    
    .alert-pro.danger {
        border-left-color: var(--danger-color);
        background: #f8d7da;
        color: #721c24;
    }
    
    .alert-pro.warning {
        border-left-color: var(--warning-color);
        background: #fff3cd;
        color: #856404;
    }
    
    .alert-pro.info {
        border-left-color: var(--info-color);
        background: #d1ecf1;
        color: #0c5460;
    }
    
    .alert-icon-pro {
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    
    .alert-title-pro {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    .alert-subtitle-pro {
        opacity: 0.9;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    /* Professional Chart Container */
    .chart-container-pro {
        background: white;
        padding: 2rem;
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        margin: 2rem 0;
        border: 1px solid rgba(0, 0, 0, 0.05);
        position: relative;
    }
    
    .chart-container-pro::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
    }
    
    .chart-title-pro {
        color: var(--primary-color);
        font-weight: 600;
        margin-bottom: 1.5rem;
        font-size: 1.3rem;
        padding-top: 0.5rem;
    }
    
    /* Professional Responsive Design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2.2rem;
        }
        
        .header-subtitle {
            font-size: 1rem;
        }
        
        .feature-badges {
            justify-content: center;
        }
        
        .stock-header-pro {
            flex-direction: column;
            text-align: center;
            gap: 1.5rem;
        }
        
        .price-container-pro {
            text-align: center;
            min-width: auto;
        }
        
        .current-price-pro {
            font-size: 2.2rem;
        }
        
        .stock-symbol-pro {
            font-size: 2.5rem;
        }
        
        .metrics-grid-pro {
            grid-template-columns: 1fr;
        }
        
        .rec-header-pro {
            gap: 1rem;
        }
        
        .rec-title-pro {
            font-size: 2rem;
        }
        
        .agents-status-pro {
            grid-template-columns: 1fr;
        }
        
        .metric-container {
            grid-template-columns: 1fr;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            padding: 1.5rem 1rem;
        }
        
        .header-title {
            font-size: 1.8rem;
        }
        
        .analysis-container-pro {
            padding: 1.5rem;
        }
        
        .recommendation-card-pro {
            padding: 1.5rem;
        }
        
        .loading-container-pro {
            padding: 2rem 1rem;
        }
    }
    
    /* Professional Utilities */
    .text-center { text-align: center; }
    .text-left { text-align: left; }
    .text-right { text-align: right; }
    
    .font-weight-bold { font-weight: 700; }
    .font-weight-semibold { font-weight: 600; }
    .font-weight-medium { font-weight: 500; }
    .font-weight-normal { font-weight: 400; }
    
    .text-primary { color: var(--primary-color); }
    .text-success { color: var(--success-color); }
    .text-danger { color: var(--danger-color); }
    .text-warning { color: var(--warning-color); }
    .text-info { color: var(--info-color); }
    .text-muted { color: #6c757d; }
    
    .bg-primary { background-color: var(--primary-color); }
    .bg-success { background-color: var(--success-color); }
    .bg-danger { background-color: var(--danger-color); }
    .bg-warning { background-color: var(--warning-color); }
    .bg-info { background-color: var(--info-color); }
    .bg-light { background-color: var(--light-color); }
    
    .rounded { border-radius: var(--border-radius); }
    .rounded-sm { border-radius: var(--border-radius-sm); }
    .rounded-lg { border-radius: var(--border-radius-lg); }
    
    .shadow-sm { box-shadow: var(--shadow-sm); }
    .shadow-md { box-shadow: var(--shadow-md); }
    .shadow-lg { box-shadow: var(--shadow-lg); }
    .shadow-xl { box-shadow: var(--shadow-xl); }
    
    .mb-1 { margin-bottom: 0.25rem; }
    .mb-2 { margin-bottom: 0.5rem; }
    .mb-3 { margin-bottom: 1rem; }
    .mb-4 { margin-bottom: 1.5rem; }
    .mb-5 { margin-bottom: 3rem; }
    
    .mt-1 { margin-top: 0.25rem; }
    .mt-2 { margin-top: 0.5rem; }
    .mt-3 { margin-top: 1rem; }
    .mt-4 { margin-top: 1.5rem; }
    .mt-5 { margin-top: 3rem; }
    
    .p-1 { padding: 0.25rem; }
    .p-2 { padding: 0.5rem; }
    .p-3 { padding: 1rem; }
    .p-4 { padding: 1.5rem; }
    .p-5 { padding: 3rem; }
    
    .d-flex { display: flex; }
    .d-block { display: block; }
    .d-inline { display: inline; }
    .d-inline-block { display: inline-block; }
    .d-none { display: none; }
    
    .justify-content-center { justify-content: center; }
    .justify-content-between { justify-content: space-between; }
    .justify-content-around { justify-content: space-around; }
    .justify-content-start { justify-content: flex-start; }
    .justify-content-end { justify-content: flex-end; }
    
    .align-items-center { align-items: center; }
    .align-items-start { align-items: flex-start; }
    .align-items-end { align-items: flex-end; }
    
    .flex-column { flex-direction: column; }
    .flex-row { flex-direction: row; }
    
    .w-100 { width: 100%; }
    .h-100 { height: 100%; }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    </style>
    
    <!-- Bootstrap JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    """
    st.markdown(css, unsafe_allow_html=True)