#!/usr/bin/env python3
"""
Market Schedule Utility for Vietnamese Stock Market
Handles trading hours, holidays, and weekend detection
"""

from datetime import datetime, time, timedelta
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class VNMarketSchedule:
    """Vietnamese Stock Market Schedule Manager"""
    
    def __init__(self):
        # VN Stock Market trading hours (GMT+7)
        self.market_open = time(9, 0)   # 9:00 AM
        self.market_close = time(15, 0)  # 3:00 PM
        
        # Vietnamese holidays (approximate - should be updated yearly)
        self.holidays_2024 = [
            "2024-01-01",  # New Year
            "2024-02-10",  # Tet Holiday start
            "2024-02-11",  # Tet Holiday
            "2024-02-12",  # Tet Holiday
            "2024-02-13",  # Tet Holiday
            "2024-02-14",  # Tet Holiday
            "2024-04-18",  # Hung Kings Day
            "2024-04-30",  # Liberation Day
            "2024-05-01",  # Labor Day
            "2024-09-02",  # National Day
        ]
    
    def is_market_open(self, check_time: datetime = None) -> Dict[str, Any]:
        """Check if Vietnamese stock market is currently open"""
        if check_time is None:
            check_time = datetime.now()
        
        # Check if weekend
        is_weekend = check_time.weekday() >= 5  # Saturday (5) or Sunday (6)
        
        # Check if holiday
        date_str = check_time.strftime("%Y-%m-%d")
        is_holiday = date_str in self.holidays_2024
        
        # Check trading hours
        current_time = check_time.time()
        is_trading_hours = self.market_open <= current_time <= self.market_close
        
        # Market is open if: not weekend, not holiday, and within trading hours
        is_open = not is_weekend and not is_holiday and is_trading_hours
        
        return {
            'is_open': is_open,
            'is_weekend': is_weekend,
            'is_holiday': is_holiday,
            'is_trading_hours': is_trading_hours,
            'current_time': check_time.strftime("%Y-%m-%d %H:%M:%S"),
            'day_of_week': check_time.strftime("%A"),
            'next_open': self._get_next_market_open(check_time),
            'reason': self._get_closure_reason(is_weekend, is_holiday, is_trading_hours)
        }
    
    def _get_next_market_open(self, current_time: datetime) -> str:
        """Get next market opening time"""
        # If it's weekend, next open is Monday 9AM
        if current_time.weekday() >= 5:
            days_until_monday = 7 - current_time.weekday()
            next_monday = current_time + timedelta(days=days_until_monday)
            next_open = datetime.combine(next_monday.date(), self.market_open)
            return next_open.strftime("%Y-%m-%d %H:%M:%S")
        
        # If it's after market hours on weekday, next open is tomorrow 9AM
        if current_time.time() > self.market_close:
            next_day = current_time + timedelta(days=1)
            # Skip weekend
            if next_day.weekday() >= 5:
                days_until_monday = 7 - next_day.weekday()
                next_monday = next_day + timedelta(days=days_until_monday)
                next_open = datetime.combine(next_monday.date(), self.market_open)
            else:
                next_open = datetime.combine(next_day.date(), self.market_open)
            return next_open.strftime("%Y-%m-%d %H:%M:%S")
        
        # If it's before market hours on weekday, next open is today 9AM
        if current_time.time() < self.market_open:
            next_open = datetime.combine(current_time.date(), self.market_open)
            return next_open.strftime("%Y-%m-%d %H:%M:%S")
        
        # Market is currently open
        return "Market is currently open"
    
    def _get_closure_reason(self, is_weekend: bool, is_holiday: bool, is_trading_hours: bool) -> str:
        """Get reason why market is closed"""
        if is_weekend:
            return "Market closed: Weekend"
        elif is_holiday:
            return "Market closed: Public holiday"
        elif not is_trading_hours:
            return "Market closed: Outside trading hours (9AM-3PM)"
        else:
            return "Market is open"
    
    def get_data_freshness_expectation(self) -> Dict[str, Any]:
        """Get expectation for data freshness based on market status"""
        market_status = self.is_market_open()
        
        if market_status['is_open']:
            return {
                'expectation': 'real_time',
                'description': 'Expect real-time data and fresh news',
                'recommended_source': 'crewai_live',
                'cache_duration': 300,  # 5 minutes
                'confidence': 'high'
            }
        elif market_status['is_weekend']:
            return {
                'expectation': 'cached_fallback',
                'description': 'Weekend: Use cached data from last trading day',
                'recommended_source': 'fallback_with_cache',
                'cache_duration': 3600,  # 1 hour
                'confidence': 'medium'
            }
        elif market_status['is_holiday']:
            return {
                'expectation': 'cached_fallback',
                'description': 'Holiday: Use cached data from last trading day',
                'recommended_source': 'fallback_with_cache',
                'cache_duration': 3600,  # 1 hour
                'confidence': 'medium'
            }
        else:
            return {
                'expectation': 'limited_real_time',
                'description': 'After hours: Limited real-time data available',
                'recommended_source': 'crewai_with_fallback',
                'cache_duration': 1800,  # 30 minutes
                'confidence': 'low'
            }
    
    def should_use_crewai(self) -> Dict[str, Any]:
        """Determine if CrewAI should be used based on market conditions"""
        market_status = self.is_market_open()
        freshness = self.get_data_freshness_expectation()
        
        # Use CrewAI during trading hours and shortly after
        use_crewai = (
            market_status['is_open'] or 
            (not market_status['is_weekend'] and not market_status['is_holiday'])
        )
        
        return {
            'use_crewai': use_crewai,
            'reason': freshness['description'],
            'fallback_priority': 'high' if market_status['is_weekend'] else 'medium',
            'cache_strategy': freshness['recommended_source']
        }

# Global instance
market_schedule = VNMarketSchedule()

def get_market_status() -> Dict[str, Any]:
    """Get current market status - convenience function"""
    return market_schedule.is_market_open()

def should_expect_fresh_data() -> bool:
    """Check if we should expect fresh data"""
    status = market_schedule.is_market_open()
    return status['is_open'] or (not status['is_weekend'] and not status['is_holiday'])

def get_recommended_data_source() -> str:
    """Get recommended data source based on market conditions"""
    recommendation = market_schedule.should_use_crewai()
    if recommendation['use_crewai']:
        return 'crewai'
    else:
        return 'fallback'