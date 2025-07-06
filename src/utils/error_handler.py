# src/utils/error_handler.py
"""
Centralized Error Handling for AI Trading System
Xử lý lỗi tập trung cho hệ thống AI Trading
"""

import logging
import traceback
from typing import Dict, Any, Optional
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class TradingSystemError(Exception):
    """Base exception for trading system"""
    pass

class DataFetchError(TradingSystemError):
    """Error when fetching data"""
    pass

class APIError(TradingSystemError):
    """Error with external APIs"""
    pass

class ValidationError(TradingSystemError):
    """Error with data validation"""
    pass

def handle_errors(default_return=None, log_error=True):
    """Decorator để handle errors một cách đồng nhất"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                # Return structured error response
                if default_return is not None:
                    return default_return
                else:
                    return {
                        "error": True,
                        "message": str(e),
                        "function": func.__name__
                    }
        return wrapper
    return decorator

def handle_async_errors(default_return=None, log_error=True):
    """Decorator để handle async errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                if default_return is not None:
                    return default_return
                else:
                    return {
                        "error": True,
                        "message": str(e),
                        "function": func.__name__
                    }
        return wrapper
    return decorator

def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Basic validation
    symbol = symbol.strip().upper()
    if len(symbol) < 2 or len(symbol) > 10:
        return False
    
    # Check for valid characters
    if not symbol.isalnum():
        return False
    
    return True

def format_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """Format error response consistently"""
    return {
        "success": False,
        "error": True,
        "message": str(error),
        "context": context,
        "type": type(error).__name__
    }

def format_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Format success response consistently"""
    return {
        "success": True,
        "error": False,
        "message": message,
        "data": data
    }

# Specific error handlers for different components
class AgentErrorHandler:
    """Error handler cho AI Agents"""
    
    @staticmethod
    def handle_prediction_error(symbol: str, error: Exception) -> Dict[str, Any]:
        logger.error(f"Prediction error for {symbol}: {error}")
        return {
            "symbol": symbol,
            "error": f"Không thể dự đoán giá cho {symbol}: {str(error)}",
            "predicted_price": "N/A",
            "trend": "Unknown",
            "confidence": "Low"
        }
    
    @staticmethod
    def handle_news_error(symbol: str, error: Exception) -> Dict[str, Any]:
        logger.error(f"News fetch error for {symbol}: {error}")
        return {
            "symbol": symbol,
            "error": f"Không thể lấy tin tức cho {symbol}: {str(error)}",
            "news": [],
            "sentiment": "Neutral"
        }
    
    @staticmethod
    def handle_risk_error(symbol: str, error: Exception) -> Dict[str, Any]:
        logger.error(f"Risk assessment error for {symbol}: {error}")
        return {
            "symbol": symbol,
            "error": f"Không thể đánh giá rủi ro cho {symbol}: {str(error)}",
            "risk_level": "UNKNOWN",
            "volatility": 0,
            "beta": 0
        }

class DataErrorHandler:
    """Error handler cho data layer"""
    
    @staticmethod
    def handle_vnstock_error(symbol: str, error: Exception) -> Dict[str, Any]:
        logger.error(f"VNStock error for {symbol}: {error}")
        return {
            "symbol": symbol,
            "error": f"Lỗi lấy dữ liệu VN cho {symbol}: {str(error)}",
            "data_source": "Error",
            "fallback_used": True
        }
    
    @staticmethod
    def handle_api_timeout(symbol: str, timeout_seconds: int) -> Dict[str, Any]:
        logger.warning(f"API timeout for {symbol} after {timeout_seconds}s")
        return {
            "symbol": symbol,
            "error": f"Timeout lấy dữ liệu cho {symbol} sau {timeout_seconds}s",
            "timeout": True,
            "retry_suggested": True
        }

# Context managers for error handling
class ErrorContext:
    """Context manager để handle errors trong blocks"""
    
    def __init__(self, operation_name: str, default_return=None):
        self.operation_name = operation_name
        self.default_return = default_return
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Error in {self.operation_name}: {exc_val}")
            return False  # Don't suppress the exception
        return True

# Utility functions
def safe_float(value, default=0.0) -> float:
    """Safely convert to float"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0) -> int:
    """Safely convert to int"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_get(dictionary: dict, key: str, default=None):
    """Safely get value from dictionary"""
    try:
        return dictionary.get(key, default) if dictionary else default
    except (AttributeError, TypeError):
        return default

# Export main components
__all__ = [
    'TradingSystemError',
    'DataFetchError', 
    'APIError',
    'ValidationError',
    'handle_errors',
    'handle_async_errors',
    'validate_symbol',
    'format_error_response',
    'format_success_response',
    'AgentErrorHandler',
    'DataErrorHandler',
    'ErrorContext',
    'safe_float',
    'safe_int',
    'safe_get'
]