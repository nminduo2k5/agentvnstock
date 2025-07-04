# src/utils/helpers.py
"""
Helper Functions cho AI Trading Team Vietnam
Các utility functions được sử dụng xuyên suốt ứng dụng
"""

import re
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
import logging
import hashlib
import time
from functools import wraps

logger = logging.getLogger(__name__)

# ============================================================================
# FORMATTING UTILITIES
# ============================================================================

def format_vnd(amount: Union[int, float], include_symbol: bool = True) -> str:
    """
    Format số tiền VND với đơn vị phù hợp
    
    Args:
        amount: Số tiền cần format
        include_symbol: Có include ký hiệu VND không
        
    Returns:
        str: Formatted currency string
    """
    try:
        if amount >= 1_000_000_000_000:  # Nghìn tỷ
            formatted = f"{amount/1_000_000_000_000:.1f} nghìn tỷ"
        elif amount >= 1_000_000_000:  # Tỷ
            formatted = f"{amount/1_000_000_000:.1f} tỷ"
        elif amount >= 1_000_000:  # Triệu
            formatted = f"{amount/1_000_000:.1f} triệu"
        elif amount >= 1_000:  # Nghìn
            formatted = f"{amount/1_000:.1f} nghìn"
        else:
            formatted = f"{amount:,.0f}"
        
        return f"{formatted} VND" if include_symbol else formatted
        
    except (TypeError, ValueError):
        return "N/A"

def format_percentage(value: Union[int, float], decimal_places: int = 2) -> str:
    """
    Format percentage với sign và color indicator
    
    Args:
        value: Percentage value
        decimal_places: Số chữ số thập phân
        
    Returns:
        str: Formatted percentage
    """
    try:
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.{decimal_places}f}%"
    except (TypeError, ValueError):
        return "N/A"

def format_number(number: Union[int, float], decimal_places: int = 0) -> str:
    """
    Format number với thousand separators
    
    Args:
        number: Number to format
        decimal_places: Decimal places
        
    Returns:
        str: Formatted number
    """
    try:
        if decimal_places == 0:
            return f"{number:,.0f}"
        else:
            return f"{number:,.{decimal_places}f}"
    except (TypeError, ValueError):
        return "N/A"

def format_market_cap(market_cap: float) -> str:
    """
    Format market cap cho Vietnamese stocks
    
    Args:
        market_cap: Market cap in billions VND
        
    Returns:
        str: Formatted market cap
    """
    return format_vnd(market_cap * 1_000_000_000)

# ============================================================================
# CALCULATION UTILITIES
# ============================================================================

def calculate_change_percentage(current: float, previous: float) -> float:
    """
    Calculate percentage change
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        float: Percentage change
    """
    try:
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    except (TypeError, ValueError, ZeroDivisionError):
        return 0

def calculate_compound_return(returns: List[float]) -> float:
    """
    Calculate compound return từ list of returns
    
    Args:
        returns: List of period returns (as decimals)
        
    Returns:
        float: Compound return
    """
    try:
        compound = 1.0
        for r in returns:
            compound *= (1 + r)
        return compound - 1
    except:
        return 0

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: List of returns
        risk_free_rate: Risk-free rate (annual)
        
    Returns:
        float: Sharpe ratio
    """
    try:
        if len(returns) < 2:
            return 0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]  # Daily risk-free rate
        mean_excess = np.mean(excess_returns)
        std_excess = np.std(excess_returns)
        
        if std_excess == 0:
            return 0
        
        return (mean_excess / std_excess) * np.sqrt(252)  # Annualized
    except:
        return 0

def calculate_max_drawdown(values: List[float]) -> float:
    """
    Calculate maximum drawdown
    
    Args:
        values: List of portfolio values
        
    Returns:
        float: Maximum drawdown (as decimal)
    """
    try:
        if len(values) < 2:
            return 0
        
        peak = values[0]
        max_dd = 0
        
        for value in values[1:]:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_dd = max(max_dd, drawdown)
        
        return max_dd
    except:
        return 0

def calculate_volatility(returns: List[float], annualized: bool = True) -> float:
    """
    Calculate volatility (standard deviation of returns)
    
    Args:
        returns: List of returns
        annualized: Whether to annualize the volatility
        
    Returns:
        float: Volatility
    """
    try:
        if len(returns) < 2:
            return 0
        
        std = np.std(returns)
        
        if annualized:
            return std * np.sqrt(252)  # Assuming daily returns
        
        return std
    except:
        return 0

def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> float:
    """
    Calculate beta coefficient
    
    Args:
        stock_returns: Stock returns
        market_returns: Market returns
        
    Returns:
        float: Beta coefficient
    """
    try:
        if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
            return 1.0
        
        stock_returns = np.array(stock_returns)
        market_returns = np.array(market_returns)
        
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        return covariance / market_variance
    except:
        return 1.0

# ============================================================================
# RISK MANAGEMENT UTILITIES
# ============================================================================

def calculate_position_size_kelly(win_rate: float, avg_win: float, avg_loss: float, 
                                 max_position: float = 0.25) -> float:
    """
    Calculate optimal position size using Kelly Criterion
    
    Args:
        win_rate: Historical win rate (0-1)
        avg_win: Average winning return
        avg_loss: Average losing return (positive number)
        max_position: Maximum allowed position size
        
    Returns:
        float: Optimal position size (0-1)
    """
    try:
        if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
            return 0.01  # Minimum position
        
        # Kelly formula: f = (bp - q) / b
        # where b = avg_win/avg_loss, p = win_rate, q = 1-win_rate
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate
        
        kelly_fraction = (b * p - q) / b
        
        # Apply constraints
        kelly_fraction = max(0, kelly_fraction)  # No negative positions
        kelly_fraction = min(kelly_fraction, max_position)  # Max position limit
        kelly_fraction = min(kelly_fraction, 0.25)  # Conservative cap at 25%
        
        return kelly_fraction
    except:
        return 0.05  # Default 5% position

def calculate_var(returns: List[float], confidence_level: float = 0.05) -> float:
    """
    Calculate Value at Risk (VaR)
    
    Args:
        returns: Historical returns
        confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
        
    Returns:
        float: VaR value
    """
    try:
        if len(returns) < 10:
            return 0
        
        sorted_returns = sorted(returns)
        index = int(confidence_level * len(sorted_returns))
        
        return abs(sorted_returns[index])
    except:
        return 0

def calculate_risk_metrics(returns: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive risk metrics
    
    Args:
        returns: List of returns
        
    Returns:
        Dict: Risk metrics dictionary
    """
    try:
        if len(returns) < 2:
            return {
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'var_95': 0,
                'skewness': 0,
                'kurtosis': 0
            }
        
        returns_array = np.array(returns)
        
        metrics = {
            'volatility': calculate_volatility(returns),
            'sharpe_ratio': calculate_sharpe_ratio(returns),
            'max_drawdown': calculate_max_drawdown([sum(returns[:i+1]) for i in range(len(returns))]),
            'var_95': calculate_var(returns, 0.05),
            'skewness': float(pd.Series(returns).skew()),
            'kurtosis': float(pd.Series(returns).kurtosis())
        }
        
        return metrics
    except:
        return {}

# ============================================================================
# DATA PROCESSING UTILITIES
# ============================================================================

def clean_text(text: str) -> str:
    """
    Clean và normalize text cho analysis
    
    Args:
        text: Raw text
        
    Returns:
        str: Cleaned text
    """
    try:
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep Vietnamese
        text = re.sub(r'[^\w\s\-\.,%\(\)àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', '', text)
        
        return text
    except:
        return text

def extract_numbers_from_text(text: str) -> List[float]:
    """
    Extract numbers từ text
    
    Args:
        text: Input text
        
    Returns:
        List[float]: List of extracted numbers
    """
    try:
        # Pattern để match numbers (including Vietnamese number format)
        pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        
        return numbers
    except:
        return []

def parse_vietnamese_date(date_str: str) -> Optional[datetime]:
    """
    Parse Vietnamese date formats
    
    Args:
        date_str: Date string in Vietnamese format
        
    Returns:
        datetime: Parsed datetime object
    """
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y", 
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None

def normalize_stock_symbol(symbol: str) -> str:
    """
    Normalize Vietnamese stock symbol
    
    Args:
        symbol: Raw stock symbol
        
    Returns:
        str: Normalized symbol
    """
    try:
        # Convert to uppercase và remove whitespace
        symbol = symbol.strip().upper()
        
        # Remove exchange suffix if present
        symbol = re.sub(r'\.(HM|HN|UP)$', '', symbol)
        
        return symbol
    except:
        return symbol

# ============================================================================
# CACHING UTILITIES
# ============================================================================

def create_cache_key(*args, **kwargs) -> str:
    """
    Create cache key từ arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        str: MD5 hash cache key
    """
    try:
        # Combine all arguments
        key_data = str(args) + str(sorted(kwargs.items()))
        
        # Create MD5 hash
        return hashlib.md5(key_data.encode()).hexdigest()
    except:
        return str(time.time())

def timing_decorator(func):
    """
    Decorator để measure function execution time
    
    Args:
        func: Function to decorate
        
    Returns:
        function: Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"⏱️ {func.__name__} executed in {execution_time:.3f}s")
        
        return result
    return wrapper

def async_timing_decorator(func):
    """
    Decorator để measure async function execution time
    
    Args:
        func: Async function to decorate
        
    Returns:
        function: Decorated async function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"⏱️ {func.__name__} executed in {execution_time:.3f}s")
        
        return result
    return wrapper

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate Vietnamese stock symbol format
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        bool: True if valid
    """
    try:
        # Vietnamese stock symbols: 3-4 characters, letters only
        pattern = r'^[A-Z]{3,4}$'
        return bool(re.match(pattern, symbol.upper().strip()))
    except:
        return False

def validate_price(price: Union[int, float]) -> bool:
    """
    Validate stock price
    
    Args:
        price: Price to validate
        
    Returns:
        bool: True if valid
    """
    try:
        price = float(price)
        return 0 < price < 10_000_000  # Reasonable price range for VN stocks
    except:
        return False

def validate_percentage(percentage: Union[int, float]) -> bool:
    """
    Validate percentage value
    
    Args:
        percentage: Percentage to validate
        
    Returns:
        bool: True if valid
    """
    try:
        percentage = float(percentage)
        return -100 <= percentage <= 1000  # Reasonable range
    except:
        return False

def validate_api_key(api_key: str) -> bool:
    """
    Basic validation cho API key format
    
    Args:
        api_key: API key to validate
        
    Returns:
        bool: True if format looks valid
    """
    try:
        # Basic checks: not empty, reasonable length, alphanumeric
        if not api_key or len(api_key) < 10:
            return False
        
        # Check for basic alphanumeric pattern
        pattern = r'^[A-Za-z0-9_\-\.]+$'
        return bool(re.match(pattern, api_key))
    except:
        return False

# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """
    Safe division với default value
    
    Args:
        numerator: Numerator
        denominator: Denominator 
        default: Default value if division fails
        
    Returns:
        float: Result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default

def safe_float(value: Any, default: float = 0) -> float:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default if conversion fails
        
    Returns:
        float: Converted value or default
    """
    try:
        return float(value)
    except:
        return default

def safe_percentage(value: Any, default: float = 0) -> float:
    """
    Safely convert và validate percentage
    
    Args:
        value: Value to convert
        default: Default if invalid
        
    Returns:
        float: Valid percentage or default
    """
    try:
        pct = float(value)
        if -100 <= pct <= 1000:
            return pct
        return default
    except:
        return default

# ============================================================================
# MARKET SPECIFIC UTILITIES
# ============================================================================

def get_trading_session(time_str: str) -> str:
    """
    Determine trading session for VN market
    
    Args:
        time_str: Time string (HH:MM format)
        
    Returns:
        str: Trading session (morning/afternoon/closed)
    """
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        
        morning_start = datetime.strptime("09:00", "%H:%M").time()
        morning_end = datetime.strptime("11:30", "%H:%M").time()
        afternoon_start = datetime.strptime("13:00", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()
        
        if morning_start <= time_obj <= morning_end:
            return "morning"
        elif afternoon_start <= time_obj <= afternoon_end:
            return "afternoon"
        else:
            return "closed"
    except:
        return "unknown"

def is_trading_day(date: datetime) -> bool:
    """
    Check if date is a trading day in Vietnam
    
    Args:
        date: Date to check
        
    Returns:
        bool: True if trading day
    """
    try:
        # Basic check: Monday to Friday
        return date.weekday() < 5
    except:
        return False

def calculate_vn_price_step(price: float) -> float:
    """
    Calculate minimum price step for Vietnamese stocks
    
    Args:
        price: Current stock price
        
    Returns:
        float: Minimum price step
    """
    try:
        if price < 10_000:
            return 10
        elif price < 50_000:
            return 50
        elif price < 100_000:
            return 100
        elif price < 500_000:
            return 500
        else:
            return 1_000
    except:
        return 100  # Default step

# ============================================================================
# UTILITY FUNCTIONS FOR AGENTS
# ============================================================================

def extract_sentiment_from_text(text: str) -> Dict[str, Any]:
    """
    Extract sentiment indicators từ Vietnamese text
    
    Args:
        text: Vietnamese text to analyze
        
    Returns:
        Dict: Sentiment analysis results
    """
    try:
        positive_words = [
            'tăng', 'tốt', 'mạnh', 'tích cực', 'khả quan', 'lạc quan',
            'tăng trưởng', 'phát triển', 'cải thiện', 'thuận lợi'
        ]
        
        negative_words = [
            'giảm', 'xấu', 'yếu', 'tiêu cực', 'bi quan', 'khó khăn',
            'suy giảm', 'giảm sút', 'rủi ro', 'bất lợi'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment = "Neutral"
            score = 0.5
        elif positive_count > negative_count:
            sentiment = "Positive"
            score = 0.5 + (positive_count / (total_sentiment_words * 2))
        elif negative_count > positive_count:
            sentiment = "Negative"
            score = 0.5 - (negative_count / (total_sentiment_words * 2))
        else:
            sentiment = "Neutral"
            score = 0.5
        
        return {
            'sentiment': sentiment,
            'score': max(0, min(1, score)),
            'positive_indicators': positive_count,
            'negative_indicators': negative_count
        }
    except:
        return {
            'sentiment': 'Neutral',
            'score': 0.5,
            'positive_indicators': 0,
            'negative_indicators': 0
        }

def prioritize_recommendations(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prioritize recommendations based on confidence và consensus
    
    Args:
        recommendations: List of recommendation dictionaries
        
    Returns:
        List: Sorted recommendations by priority
    """
    try:
        def priority_score(rec):
            confidence = rec.get('confidence_level', 0)
            consensus = 1 if rec.get('recommendation') in ['BUY', 'SELL'] else 0.5
            agent_weight = {
                'Portfolio Manager': 3,
                'Risk Manager': 2,
                'Market Analyst': 1
            }.get(rec.get('agent_role', ''), 1)
            
            return confidence * consensus * agent_weight
        
        return sorted(recommendations, key=priority_score, reverse=True)
    except:
        return recommendations

# Export commonly used functions
__all__ = [
    'format_vnd', 'format_percentage', 'format_number', 'format_market_cap',
    'calculate_change_percentage', 'calculate_sharpe_ratio', 'calculate_max_drawdown',
    'calculate_position_size_kelly', 'calculate_var', 'calculate_risk_metrics',
    'clean_text', 'extract_numbers_from_text', 'normalize_stock_symbol',
    'validate_stock_symbol', 'validate_price', 'validate_api_key',
    'safe_divide', 'safe_float', 'safe_percentage',
    'get_trading_session', 'is_trading_day', 'calculate_vn_price_step',
    'extract_sentiment_from_text', 'prioritize_recommendations',
    'timing_decorator', 'async_timing_decorator'
]