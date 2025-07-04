# src/utils/config.py
"""
Configuration Management cho AI Trading Team Vietnam
Quản lý settings, constants và environment variables
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API configuration settings"""
    google_genai_api_key: Optional[str] = None
    vietstock_api_key: Optional[str] = None
    cafef_api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

@dataclass
class AgentConfig:
    """AI Agent configuration"""
    model_name: str = "gemini-pro"
    max_tokens: int = 2048
    temperature: float = 0.7
    conversation_memory: int = 5  # Number of previous messages to remember

@dataclass
class UIConfig:
    """UI configuration settings"""
    theme: str = "light"
    page_title: str = "🇻🇳 AI Trading Team Vietnam"
    page_icon: str = "📈"
    layout: str = "wide"
    sidebar_state: str = "expanded"

@dataclass
class TradingConfig:
    """Trading and market configuration"""
    default_currency: str = "VND"
    market_hours_start: str = "09:00"
    market_hours_end: str = "15:00"
    trading_days: list = None
    max_position_size: float = 0.10  # 10% max position
    max_sector_exposure: float = 0.30  # 30% max sector
    min_cash_reserve: float = 0.15  # 15% min cash

    def __post_init__(self):
        if self.trading_days is None:
            self.trading_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

@dataclass
class AppConfig:
    """Main application configuration"""
    api: APIConfig
    agents: AgentConfig
    ui: UIConfig
    trading: TradingConfig
    
    # Paths
    data_dir: str = "data"
    cache_dir: str = "data/cache"
    logs_dir: str = "logs"
    
    # Performance
    cache_duration: int = 300  # 5 minutes
    enable_caching: bool = True
    debug_mode: bool = False

class ConfigManager:
    """Configuration manager để load và manage settings"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()
        
    def _get_default_config_path(self) -> str:
        """Get default config file path"""
        current_dir = Path(__file__).parent.parent.parent
        return str(current_dir / "config.json")
    
    def _load_config(self) -> AppConfig:
        """Load configuration từ file và environment variables"""
        
        # Default configuration
        default_config = {
            "api": {
                "google_genai_api_key": None,
                "vietstock_api_key": None,
                "cafef_api_key": None,
                "timeout": 30,
                "max_retries": 3
            },
            "agents": {
                "model_name": "gemini-pro",
                "max_tokens": 2048,
                "temperature": 0.7,
                "conversation_memory": 5
            },
            "ui": {
                "theme": "light",
                "page_title": "🇻🇳 AI Trading Team Vietnam",
                "page_icon": "📈",
                "layout": "wide",
                "sidebar_state": "expanded"
            },
            "trading": {
                "default_currency": "VND",
                "market_hours_start": "09:00",
                "market_hours_end": "15:00",
                "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "max_position_size": 0.10,
                "max_sector_exposure": 0.30,
                "min_cash_reserve": 0.15
            },
            "data_dir": "data",
            "cache_dir": "data/cache",
            "logs_dir": "logs",
            "cache_duration": 300,
            "enable_caching": True,
            "debug_mode": False
        }
        
        # Load từ file nếu tồn tại
        file_config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                logger.info(f"✅ Loaded config from {self.config_file}")
            except Exception as e:
                logger.warning(f"⚠️ Could not load config file: {e}")
        
        # Merge với default config
        merged_config = self._deep_merge(default_config, file_config)
        
        # Override với environment variables
        env_config = self._load_from_env()
        merged_config = self._deep_merge(merged_config, env_config)
        
        # Create config objects
        try:
            api_config = APIConfig(**merged_config["api"])
            agent_config = AgentConfig(**merged_config["agents"])
            ui_config = UIConfig(**merged_config["ui"])
            trading_config = TradingConfig(**merged_config["trading"])
            
            app_config = AppConfig(
                api=api_config,
                agents=agent_config,
                ui=ui_config,
                trading=trading_config,
                data_dir=merged_config["data_dir"],
                cache_dir=merged_config["cache_dir"],
                logs_dir=merged_config["logs_dir"],
                cache_duration=merged_config["cache_duration"],
                enable_caching=merged_config["enable_caching"],
                debug_mode=merged_config["debug_mode"]
            )
            
            return app_config
            
        except Exception as e:
            logger.error(f"❌ Error creating config objects: {e}")
            # Return default config
            return AppConfig(
                api=APIConfig(),
                agents=AgentConfig(),
                ui=UIConfig(),
                trading=TradingConfig()
            )
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration từ environment variables"""
        
        env_config = {
            "api": {},
            "agents": {},
            "ui": {},
            "trading": {}
        }
        
        # API keys
        if os.getenv("GOOGLE_GENAI_API_KEY"):
            env_config["api"]["google_genai_api_key"] = os.getenv("GOOGLE_GENAI_API_KEY")
        
        if os.getenv("VIETSTOCK_API_KEY"):
            env_config["api"]["vietstock_api_key"] = os.getenv("VIETSTOCK_API_KEY")
        
        # Debug mode
        if os.getenv("DEBUG_MODE"):
            env_config["debug_mode"] = os.getenv("DEBUG_MODE").lower() == "true"
        
        # Cache settings
        if os.getenv("CACHE_DURATION"):
            try:
                env_config["cache_duration"] = int(os.getenv("CACHE_DURATION"))
            except ValueError:
                pass
        
        return env_config
    
    def _deep_merge(self, dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_dict = {
                "api": asdict(self.config.api),
                "agents": asdict(self.config.agents),
                "ui": asdict(self.config.ui),
                "trading": asdict(self.config.trading),
                "data_dir": self.config.data_dir,
                "cache_dir": self.config.cache_dir,
                "logs_dir": self.config.logs_dir,
                "cache_duration": self.config.cache_duration,
                "enable_caching": self.config.enable_caching,
                "debug_mode": self.config.debug_mode
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Config saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")
    
    def get_config(self) -> AppConfig:
        """Get current configuration"""
        return self.config
    
    def update_api_key(self, key_name: str, api_key: str):
        """Update API key in configuration"""
        if hasattr(self.config.api, key_name):
            setattr(self.config.api, key_name, api_key)
            logger.info(f"✅ Updated {key_name}")
        else:
            logger.warning(f"⚠️ Unknown API key: {key_name}")
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        from datetime import datetime, time
        
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%A")
        
        # Check if trading day
        if current_day not in self.config.trading.trading_days:
            return False
        
        # Check trading hours
        start_time = time.fromisoformat(self.config.trading.market_hours_start)
        end_time = time.fromisoformat(self.config.trading.market_hours_end)
        
        return start_time <= current_time <= end_time
    
    def get_cache_path(self, cache_name: str) -> str:
        """Get cache file path"""
        cache_dir = Path(self.config.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        return str(cache_dir / f"{cache_name}.json")
    
    def setup_directories(self):
        """Setup required directories"""
        directories = [
            self.config.data_dir,
            self.config.cache_dir,
            self.config.logs_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"📁 Directory ready: {directory}")

# Global config manager instance
_config_manager = None

def load_config(config_file: Optional[str] = None) -> AppConfig:
    """
    Load application configuration
    
    Args:
        config_file: Optional config file path
        
    Returns:
        AppConfig: Application configuration
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
        _config_manager.setup_directories()
    
    return _config_manager.get_config()

def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.setup_directories()
    
    return _config_manager

def update_api_key(key_name: str, api_key: str):
    """Update API key in global config"""
    config_manager = get_config_manager()
    config_manager.update_api_key(key_name, api_key)

def is_market_open() -> bool:
    """Check if VN market is currently open"""
    config_manager = get_config_manager()
    return config_manager.is_market_open()

# Vietnamese market specific constants
VN_MARKET_CONSTANTS = {
    "exchanges": ["HOSE", "HNX", "UPCOM"],
    "currency": "VND",
    "trading_unit": 100,  # Minimum trading unit
    "price_step": {
        "under_10k": 10,
        "10k_50k": 50, 
        "50k_100k": 100,
        "100k_500k": 500,
        "over_500k": 1000
    },
    "foreign_ownership_limits": {
        "banks": 0.30,
        "telecoms": 0.49,
        "airlines": 0.49,
        "securities": 0.49,
        "insurance": 0.49,
        "default": 0.49
    },
    "trading_hours": {
        "morning_session": {"start": "09:00", "end": "11:30"},
        "afternoon_session": {"start": "13:00", "end": "15:00"}
    },
    "settlement": {
        "t_plus": 2,  # T+2 settlement
        "trading_calendar": "vietnam"
    }
}

def get_vn_market_constants() -> Dict[str, Any]:
    """Get Vietnamese market constants"""
    return VN_MARKET_CONSTANTS.copy()

def get_price_step(price: float) -> float:
    """
    Get price step for Vietnamese stocks based on price level
    
    Args:
        price: Current stock price
        
    Returns:
        float: Minimum price step
    """
    steps = VN_MARKET_CONSTANTS["price_step"]
    
    if price < 10_000:
        return steps["under_10k"]
    elif price < 50_000:
        return steps["10k_50k"]
    elif price < 100_000:
        return steps["50k_100k"]
    elif price < 500_000:
        return steps["100k_500k"]
    else:
        return steps["over_500k"]

def get_foreign_ownership_limit(sector: str) -> float:
    """
    Get foreign ownership limit for a sector
    
    Args:
        sector: Sector name
        
    Returns:
        float: Foreign ownership limit (0-1)
    """
    limits = VN_MARKET_CONSTANTS["foreign_ownership_limits"]
    return limits.get(sector.lower(), limits["default"])

# Development và testing helpers
def create_sample_config() -> str:
    """Create sample configuration file"""
    sample_config = {
        "api": {
            "google_genai_api_key": "your-google-genai-api-key-here",
            "vietstock_api_key": "your-vietstock-api-key-here",
            "timeout": 30,
            "max_retries": 3
        },
        "agents": {
            "model_name": "gemini-pro",
            "max_tokens": 2048,
            "temperature": 0.7,
            "conversation_memory": 5
        },
        "ui": {
            "theme": "light",
            "page_title": "🇻🇳 AI Trading Team Vietnam",
            "page_icon": "📈",
            "layout": "wide",
            "sidebar_state": "expanded"
        },
        "trading": {
            "default_currency": "VND",
            "market_hours_start": "09:00",
            "market_hours_end": "15:00",
            "max_position_size": 0.10,
            "max_sector_exposure": 0.30,
            "min_cash_reserve": 0.15
        },
        "debug_mode": False,
        "enable_caching": True,
        "cache_duration": 300
    }
    
    config_path = "config.sample.json"
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    return config_path