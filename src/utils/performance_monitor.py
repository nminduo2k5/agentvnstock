# src/utils/performance_monitor.py
"""
Performance Monitor and Rate Limiter
Giám sát hiệu suất và giới hạn tốc độ API calls
"""

import time
import asyncio
from typing import Dict, Optional
from collections import defaultdict, deque
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter cho API calls"""
    
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(deque)
    
    def is_allowed(self, key: str) -> bool:
        """Kiểm tra xem có được phép gọi API không"""
        now = time.time()
        call_times = self.calls[key]
        
        # Remove old calls outside time window
        while call_times and call_times[0] <= now - self.time_window:
            call_times.popleft()
        
        # Check if under limit
        if len(call_times) < self.max_calls:
            call_times.append(now)
            return True
        
        return False
    
    def get_wait_time(self, key: str) -> float:
        """Lấy thời gian cần chờ"""
        call_times = self.calls[key]
        if not call_times:
            return 0
        
        oldest_call = call_times[0]
        wait_time = self.time_window - (time.time() - oldest_call)
        return max(0, wait_time)

class PerformanceMonitor:
    """Monitor hiệu suất hệ thống"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
    
    def record_api_call(self, endpoint: str, duration: float, success: bool):
        """Ghi lại thông tin API call"""
        self.metrics[endpoint].append({
            'timestamp': time.time(),
            'duration': duration,
            'success': success
        })
        
        # Keep only last 1000 records per endpoint
        if len(self.metrics[endpoint]) > 1000:
            self.metrics[endpoint] = self.metrics[endpoint][-1000:]
    
    def get_stats(self, endpoint: str) -> Dict:
        """Lấy thống kê cho endpoint"""
        calls = self.metrics.get(endpoint, [])
        if not calls:
            return {'total_calls': 0, 'avg_duration': 0, 'success_rate': 0}
        
        recent_calls = [c for c in calls if time.time() - c['timestamp'] < 3600]  # Last hour
        
        total_calls = len(recent_calls)
        avg_duration = sum(c['duration'] for c in recent_calls) / total_calls if total_calls > 0 else 0
        success_rate = sum(1 for c in recent_calls if c['success']) / total_calls if total_calls > 0 else 0
        
        return {
            'total_calls': total_calls,
            'avg_duration': round(avg_duration, 3),
            'success_rate': round(success_rate * 100, 1)
        }

class CircuitBreaker:
    """Circuit breaker pattern cho API calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = defaultdict(int)
        self.last_failure_time = defaultdict(float)
        self.state = defaultdict(lambda: 'CLOSED')  # CLOSED, OPEN, HALF_OPEN
    
    def call_allowed(self, service: str) -> bool:
        """Kiểm tra xem có được phép gọi service không"""
        current_state = self.state[service]
        
        if current_state == 'CLOSED':
            return True
        elif current_state == 'OPEN':
            if time.time() - self.last_failure_time[service] > self.timeout:
                self.state[service] = 'HALF_OPEN'
                return True
            return False
        elif current_state == 'HALF_OPEN':
            return True
        
        return False
    
    def record_success(self, service: str):
        """Ghi lại thành công"""
        self.failure_count[service] = 0
        self.state[service] = 'CLOSED'
    
    def record_failure(self, service: str):
        """Ghi lại thất bại"""
        self.failure_count[service] += 1
        self.last_failure_time[service] = time.time()
        
        if self.failure_count[service] >= self.failure_threshold:
            self.state[service] = 'OPEN'
            logger.warning(f"Circuit breaker OPEN for {service}")

# Decorators
def rate_limit(max_calls: int = 60, time_window: int = 60):
    """Decorator cho rate limiting"""
    limiter = RateLimiter(max_calls, time_window)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}_{id(args[0]) if args else 'global'}"
            
            if not limiter.is_allowed(key):
                wait_time = limiter.get_wait_time(key)
                logger.warning(f"Rate limit exceeded for {func.__name__}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def monitor_performance(service_name: str):
    """Decorator cho performance monitoring"""
    monitor = PerformanceMonitor()
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                monitor.record_api_call(service_name, duration, success)
        
        return wrapper
    return decorator

# Singleton instances
_performance_monitor = PerformanceMonitor()
_rate_limiter = RateLimiter()

def get_performance_monitor() -> PerformanceMonitor:
    return _performance_monitor

def get_rate_limiter() -> RateLimiter:
    return _rate_limiter