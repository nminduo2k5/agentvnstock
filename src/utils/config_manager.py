# src/utils/config_manager.py
"""
Configuration Manager for AI Trading System
Quản lý cấu hình tập trung cho hệ thống AI Trading
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """API Configuration"""
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    vnstock_source: str = "VCI"
    timeout_seconds: int = 30
    max_retries: int = 3

@dataclass
class SystemConfig:
    """System Configuration"""
    debug_mode: bool = False
    log_level: str = "INFO"
    cache_duration: int = 60  # seconds
    max_concurrent_requests: int = 10
    enable_real_data: bool = True

@dataclass
class UIConfig:
    """UI Configuration"""
    page_title: str = "DUONG AI TRADING SIUUUU"
    page_icon: str = "🤖"
    layout: str = "wide"
    theme: str = "light"

class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self):
        self.api = APIConfig()
        self.system = SystemConfig()
        self.ui = UIConfig()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # API Config
        self.api.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.api.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        self.api.vnstock_source = os.getenv('VNSTOCK_SOURCE', 'VCI')
        self.api.timeout_seconds = int(os.getenv('API_TIMEOUT', '30'))
        self.api.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # System Config
        self.system.debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        self.system.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.system.cache_duration = int(os.getenv('CACHE_DURATION', '60'))
        self.system.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
        self.system.enable_real_data = os.getenv('ENABLE_REAL_DATA', 'True').lower() == 'true'
        
        # UI Config
        self.ui.page_title = os.getenv('PAGE_TITLE', 'DUONG AI TRADING SIUUUU')
        self.ui.page_icon = os.getenv('PAGE_ICON', '🤖')
        self.ui.layout = os.getenv('UI_LAYOUT', 'wide')
        self.ui.theme = os.getenv('UI_THEME', 'light')
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration"""
        return self.api
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return self.system
    
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration"""
        return self.ui
    
    def update_api_key(self, api_key: str):
        """Update Google API key"""
        self.api.google_api_key = api_key
    
    def is_gemini_configured(self) -> bool:
        """Check if Gemini is properly configured"""
        return bool(self.api.google_api_key)
    
    def get_vnstock_config(self) -> Dict[str, Any]:
        """Get VNStock configuration"""
        return {
            'source': self.api.vnstock_source,
            'timeout': self.api.timeout_seconds,
            'max_retries': self.api.max_retries,
            'enable_real_data': self.system.enable_real_data
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': self.system.log_level,
            'debug_mode': self.system.debug_mode,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'api': {
                'google_api_key': '***' if self.api.google_api_key else None,
                'gemini_model': self.api.gemini_model,
                'vnstock_source': self.api.vnstock_source,
                'timeout_seconds': self.api.timeout_seconds,
                'max_retries': self.api.max_retries
            },
            'system': {
                'debug_mode': self.system.debug_mode,
                'log_level': self.system.log_level,
                'cache_duration': self.system.cache_duration,
                'max_concurrent_requests': self.system.max_concurrent_requests,
                'enable_real_data': self.system.enable_real_data
            },
            'ui': {
                'page_title': self.ui.page_title,
                'page_icon': self.ui.page_icon,
                'layout': self.ui.layout,
                'theme': self.ui.theme
            }
        }

# Global configuration instance
config = ConfigManager()

# Vietnamese stock symbols configuration
VN_STOCK_SYMBOLS = {
    # Banking
    'VCB': {'name': 'Vietcombank', 'sector': 'Banking', 'exchange': 'HOSE'},
    'BID': {'name': 'BIDV', 'sector': 'Banking', 'exchange': 'HOSE'},
    'CTG': {'name': 'VietinBank', 'sector': 'Banking', 'exchange': 'HOSE'},
    'TCB': {'name': 'Techcombank', 'sector': 'Banking', 'exchange': 'HOSE'},
    'ACB': {'name': 'ACB', 'sector': 'Banking', 'exchange': 'HOSE'},
    'MBB': {'name': 'MB Bank', 'sector': 'Banking', 'exchange': 'HOSE'},
    'VPB': {'name': 'VPBank', 'sector': 'Banking', 'exchange': 'HOSE'},
    'STB': {'name': 'Sacombank', 'sector': 'Banking', 'exchange': 'HOSE'},
    
    # Real Estate
    'VIC': {'name': 'Vingroup', 'sector': 'Real Estate', 'exchange': 'HOSE'},
    'VHM': {'name': 'Vinhomes', 'sector': 'Real Estate', 'exchange': 'HOSE'},
    'VRE': {'name': 'Vincom Retail', 'sector': 'Real Estate', 'exchange': 'HOSE'},
    'DXG': {'name': 'Dat Xanh Group', 'sector': 'Real Estate', 'exchange': 'HOSE'},
    'NVL': {'name': 'Novaland', 'sector': 'Real Estate', 'exchange': 'HOSE'},
    'PDR': {'name': 'Phat Dat Real Estate', 'sector': 'Real Estate', 'exchange': 'HOSE'},
    
    # Consumer
    'MSN': {'name': 'Masan Group', 'sector': 'Consumer', 'exchange': 'HOSE'},
    'MWG': {'name': 'Mobile World', 'sector': 'Consumer', 'exchange': 'HOSE'},
    'VNM': {'name': 'Vinamilk', 'sector': 'Consumer', 'exchange': 'HOSE'},
    'SAB': {'name': 'Sabeco', 'sector': 'Consumer', 'exchange': 'HOSE'},
    'VCF': {'name': 'Vinacafe Bien Hoa', 'sector': 'Consumer', 'exchange': 'HOSE'},
    
    # Industrial
    'HPG': {'name': 'Hoa Phat Group', 'sector': 'Industrial', 'exchange': 'HOSE'},
    'HSG': {'name': 'Hoa Sen Group', 'sector': 'Industrial', 'exchange': 'HOSE'},
    'NKG': {'name': 'Nam Kim Group', 'sector': 'Industrial', 'exchange': 'HOSE'},
    
    # Utilities
    'GAS': {'name': 'PetroVietnam Gas', 'sector': 'Utilities', 'exchange': 'HOSE'},
    'PLX': {'name': 'Petrolimex', 'sector': 'Utilities', 'exchange': 'HOSE'},
    'POW': {'name': 'PetroVietnam Power', 'sector': 'Utilities', 'exchange': 'HOSE'},
    
    # Technology
    'FPT': {'name': 'FPT Corporation', 'sector': 'Technology', 'exchange': 'HOSE'},
    'CMG': {'name': 'CMC Group', 'sector': 'Technology', 'exchange': 'HOSE'},
    
    # Healthcare
    'DHG': {'name': 'Hau Giang Pharma', 'sector': 'Healthcare', 'exchange': 'HOSE'},
    'IMP': {'name': 'Imexpharm', 'sector': 'Healthcare', 'exchange': 'HOSE'},
    
    # Transportation
    'HVN': {'name': 'Vietnam Airlines', 'sector': 'Transportation', 'exchange': 'HOSE'},
    'VJC': {'name': 'VietJet Air', 'sector': 'Transportation', 'exchange': 'HOSE'},
}

# Agent configuration
AGENT_CONFIG = {
    'price_predictor': {
        'name': 'PricePredictor',
        'description': 'Dự đoán giá cổ phiếu',
        'icon': '📈',
        'enabled': True
    },
    'ticker_news': {
        'name': 'TickerNews', 
        'description': 'Tin tức cổ phiếu',
        'icon': '📰',
        'enabled': True
    },
    'market_news': {
        'name': 'MarketNews',
        'description': 'Tin tức thị trường',
        'icon': '🌍', 
        'enabled': True
    },
    'investment_expert': {
        'name': 'InvestmentExpert',
        'description': 'Chuyên gia đầu tư',
        'icon': '💼',
        'enabled': True
    },
    'risk_expert': {
        'name': 'RiskExpert',
        'description': 'Quản lý rủi ro',
        'icon': '⚠️',
        'enabled': True
    },
    'gemini_agent': {
        'name': 'GeminiAgent',
        'description': 'AI Chatbot',
        'icon': '🧠',
        'enabled': True
    }
}

# API endpoints configuration
API_ENDPOINTS = {
    'health': '/health',
    'analyze': '/analyze',
    'query': '/query', 
    'market': '/market',
    'predict': '/predict/{symbol}',
    'news': '/news/{symbol}',
    'risk': '/risk/{symbol}',
    'vn_stock': '/vn-stock/{symbol}',
    'vn_market': '/vn-market',
    'vn_symbols': '/vn-symbols',
    'set_gemini_key': '/set-gemini-key'
}

# Export main components
__all__ = [
    'ConfigManager',
    'APIConfig',
    'SystemConfig', 
    'UIConfig',
    'config',
    'VN_STOCK_SYMBOLS',
    'AGENT_CONFIG',
    'API_ENDPOINTS'
]