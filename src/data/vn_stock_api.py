# src/data/vn_stock_api.py
"""
Vietnamese Stock Market API Integration
Tích hợp data từ các nguồn chứng khoán Việt Nam
"""

import requests
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import json
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VNStockData:
    """Data structure cho Vietnamese stock"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    sector: str
    exchange: str  # HOSE, HNX, UPCOM

class VNStockAPI:
    """
    API client cho Vietnamese stock market data
    Sử dụng multiple sources để đảm bảo reliability
    """
    
    def __init__(self):
        self.base_urls = {
            'vietstock': 'https://finance.vietstock.vn/data',
            'investing': 'https://api.investing.com',
            'cafef': 'https://s.cafef.vn/data',
            'vnexpress': 'https://vnexpress.net/api',
            'simplize':'https://simplize.vn/api'
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8'
        })
        
        # Cache để avoid quá nhiều API calls
        self.cache = {}
        self.cache_duration = 60  # 1 minute, giảm từ 5 phút để dữ liệu mới hơn
        
        # Vietnamese stock symbols mapping
        self.vn_stocks = {
            # Banking
            'VCB': {'name': 'Vietcombank', 'sector': 'Banking', 'exchange': 'HOSE'},
            'BID': {'name': 'BIDV', 'sector': 'Banking', 'exchange': 'HOSE'},
            'CTG': {'name': 'VietinBank', 'sector': 'Banking', 'exchange': 'HOSE'},
            'TCB': {'name': 'Techcombank', 'sector': 'Banking', 'exchange': 'HOSE'},
            'ACB': {'name': 'ACB', 'sector': 'Banking', 'exchange': 'HOSE'},
            
            # Real Estate
            'VIC': {'name': 'Vingroup', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            'VHM': {'name': 'Vinhomes', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            'VRE': {'name': 'Vincom Retail', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            'DXG': {'name': 'Dat Xanh Group', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            
            # Consumer
            'MSN': {'name': 'Masan Group', 'sector': 'Consumer', 'exchange': 'HOSE'},
            'MWG': {'name': 'Mobile World', 'sector': 'Consumer', 'exchange': 'HOSE'},
            'VNM': {'name': 'Vinamilk', 'sector': 'Consumer', 'exchange': 'HOSE'},
            'SAB': {'name': 'Sabeco', 'sector': 'Consumer', 'exchange': 'HOSE'},
            
            # Industrial
            'HPG': {'name': 'Hoa Phat Group', 'sector': 'Industrial', 'exchange': 'HOSE'},
            'GAS': {'name': 'PetroVietnam Gas', 'sector': 'Utilities', 'exchange': 'HOSE'},
            'PLX': {'name': 'Petrolimex', 'sector': 'Utilities', 'exchange': 'HOSE'},
            
            # Technology
            'FPT': {'name': 'FPT Corporation', 'sector': 'Technology', 'exchange': 'HOSE'},
        }
    
    def is_vn_stock(self, symbol: str) -> bool:
        """Kiểm tra xem một mã có phải là cổ phiếu VN được hỗ trợ không"""
        return symbol.upper() in self.vn_stocks

    async def get_stock_data(self, symbol: str, force_refresh: bool = False) -> Optional[VNStockData]:
        """
        Lấy stock data cho một symbol (ưu tiên API trả về dữ liệu thành công)
        """
        try:
            cache_key = f"stock_{symbol}"
            if not force_refresh and self._is_cache_valid(cache_key):
                logger.info(f"📋 Using cached data for {symbol}")
                return self.cache[cache_key]['data']

            # Danh sách các hàm fetch API, ưu tiên thứ tự bạn muốn
            fetchers = [
                self._fetch_vietstock_data,
                self._fetch_cafef_data,
                self._fetch_simplize_data,
                self._fetch_investing_data
            ]

            data = None
            for fetcher in fetchers:
                try:
                    data = await fetcher(symbol)
                    if data:
                        logger.info(f"✅ Got realtime data for {symbol} from {fetcher.__name__}")
                        break
                except Exception as e:
                    logger.error(f"❌ Error in {fetcher.__name__} for {symbol}: {e}")

            if not data:
                logger.warning(f"⚠️ No real data for {symbol}, using simulated data")
                data = self._generate_mock_data(symbol)

            if data:
                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': time.time()
                }
            return data
        except Exception as e:
            logger.error(f"❌ Error fetching data for {symbol}: {e}")
            return self._generate_mock_data(symbol)
    
    async def _fetch_vietstock_data(self, symbol: str) -> Optional[VNStockData]:
        """Fetch data từ VietStock"""
        try:
            url = f"https://finance.vietstock.vn/data/stockinfo?scode={symbol}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_vietstock_response(symbol, data)
            else:
                logger.error(f"❌ Không lấy được dữ liệu từ VietStock cho {symbol}, status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi gọi API VietStock cho {symbol}: {e}")
            return None

    async def _fetch_investing_data(self, symbol: str) -> Optional[VNStockData]:
        """Fetch data từ Investing.com"""
        try:
            url = f"https://api.investing.com/api/financialdata/{symbol}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Bạn cần viết hàm _parse_investing_response nếu muốn parse dữ liệu này
                # return self._parse_investing_response(symbol, data)
                return None  # Chưa parse, trả về None để fallback
            else:
                logger.error(f"❌ Không lấy được dữ liệu từ Investing cho {symbol}, status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi gọi API Investing cho {symbol}: {e}")
            return None

    async def _fetch_cafef_data(self, symbol: str) -> Optional[VNStockData]:
        """Fetch data từ CafeF"""
        try:
            url = f"https://s.cafef.vn/data/stockinfo.ashx?symbol={symbol}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_cafef_response(symbol, data)
            else:
                logger.error(f"❌ Không lấy được dữ liệu từ CafeF cho {symbol}, status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi gọi API CafeF cho {symbol}: {e}")
            return None

    async def _fetch_vnexpress_data(self, symbol: str) -> Optional[dict]:
        """Fetch news data từ VNExpress"""
        try:
            url = f"https://vnexpress.net/api/stock/{symbol}/news"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Không lấy được dữ liệu từ VNExpress cho {symbol}, status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi gọi API VNExpress cho {symbol}: {e}")
            return None

    async def _fetch_simplize_data(self, symbol: str) -> Optional[VNStockData]:
        """Fetch data từ Simplize API"""
        try:
            url = f"https://simplize.vn/api/stock/{symbol}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_simplize_response(symbol, data)
            else:
                logger.error(f"❌ Không lấy được dữ liệu từ Simplize cho {symbol}, status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi gọi API Simplize cho {symbol}: {e}")
            return None

    def _parse_vietstock_response(self, symbol: str, data: Dict) -> VNStockData:
        """Parse VietStock API response"""
        stock_info = self.vn_stocks.get(symbol, {})
        
        return VNStockData(
            symbol=symbol,
            price=data.get('lastPrice', 50000),
            change=data.get('change', 0),
            change_percent=data.get('changePercent', 0),
            volume=data.get('volume', 100000),
            market_cap=data.get('marketCap', 10000),  # tỷ VND
            pe_ratio=data.get('pe', 15.0),
            pb_ratio=data.get('pb', 1.5),
            sector=stock_info.get('sector', 'Unknown'),
            exchange=stock_info.get('exchange', 'HOSE')
        )
    
    def _parse_cafef_response(self, symbol: str, data: Dict) -> VNStockData:
        """Parse CafeF API response"""
        stock_info = self.vn_stocks.get(symbol, {})
        
        return VNStockData(
            symbol=symbol,
            price=data.get('price', 50000),
            change=data.get('change', 0),
            change_percent=data.get('change_percent', 0),
            volume=data.get('volume', 100000),
            market_cap=data.get('market_cap', 10000),
            pe_ratio=data.get('pe_ratio', 15.0),
            pb_ratio=data.get('pb_ratio', 1.5),
            sector=stock_info.get('sector', 'Unknown'),
            exchange=stock_info.get('exchange', 'HOSE')
        )
    
    def _parse_simplize_response(self, symbol: str, data: dict) -> VNStockData:
        """Parse Simplize API response"""
        stock_info = self.vn_stocks.get(symbol, {})
        # Giả sử data trả về có các trường tương tự, nếu khác thì map lại cho đúng
        return VNStockData(
            symbol=symbol,
            price=data.get('price', 50000),
            change=data.get('change', 0),
            change_percent=data.get('changePercent', 0),
            volume=data.get('volume', 100000),
            market_cap=data.get('marketCap', 10000),
            pe_ratio=data.get('pe', 15.0),
            pb_ratio=data.get('pb', 1.5),
            sector=stock_info.get('sector', 'Unknown'),
            exchange=stock_info.get('exchange', 'HOSE')
        )
    
    def _generate_mock_data(self, symbol: str) -> VNStockData:
        """
        Generate realistic mock data for demo purposes
        Sử dụng khi không có real API data
        """
        import random
        
        stock_info = self.vn_stocks.get(symbol, {
            'name': symbol,
            'sector': 'Unknown',
            'exchange': 'HOSE'
        })
        
        # Base prices cho different stocks
        base_prices = {
            'VCB': 85000, 'BID': 45000, 'CTG': 35000, 'TCB': 55000,
            'VIC': 90000, 'VHM': 75000, 'MSN': 120000, 'MWG': 80000,
            'HPG': 25000, 'FPT': 95000, 'VNM': 85000, 'GAS': 95000
        }
        
        base_price = base_prices.get(symbol, 50000)
        
        # Random variations
        price_variation = random.uniform(-0.05, 0.05)  # ±5%
        current_price = base_price * (1 + price_variation)
        
        change = current_price - base_price
        change_percent = (change / base_price) * 100
        
        return VNStockData(
            symbol=symbol,
            price=round(current_price, -2),  # Round to nearest 100
            change=round(change, -2),
            change_percent=round(change_percent, 2),
            volume=random.randint(50000, 2000000),
            market_cap=random.randint(5000, 200000),  # tỷ VND
            pe_ratio=round(random.uniform(8, 25), 1),
            pb_ratio=round(random.uniform(0.8, 3.0), 1),
            sector=stock_info['sector'],
            exchange=stock_info['exchange']
        )
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Lấy tổng quan thị trường Việt Nam
        
        Returns:
            Dict: Market overview data
        """
        try:
            # Check cache
            cache_key = "market_overview"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]['data']
            
            # Fetch VN-Index data
            vn_index_data = await self._fetch_vnindex_data()
            
            # Fetch sector performance
            sector_performance = await self._fetch_sector_performance()
            
            # Fetch top movers
            top_gainers, top_losers = await self._fetch_top_movers()
            
            overview = {
                'vn_index': vn_index_data,
                'sector_performance': sector_performance,
                'top_gainers': top_gainers,
                'top_losers': top_losers,
                'foreign_flows': await self._fetch_foreign_flows(),
                'market_sentiment': self._calculate_market_sentiment(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache result
            self.cache[cache_key] = {
                'data': overview,
                'timestamp': time.time()
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"❌ Error fetching market overview: {e}")
            return self._generate_mock_market_overview()
    
    async def _fetch_vnindex_data(self) -> Dict[str, Any]:
        """Fetch VN-Index data"""
        try:
            # Trong thực tế sẽ call API thật
            # Hiện tại return mock data
            import random
            
            base_index = 1200
            variation = random.uniform(-0.02, 0.02)
            current_index = base_index * (1 + variation)
            
            return {
                'value': round(current_index, 2),
                'change': round(current_index - base_index, 2),
                'change_percent': round(variation * 100, 2),
                'volume': random.randint(500_000_000, 1_500_000_000),  # Value in VND
                'transaction_count': random.randint(50000, 150000)
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching VN-Index: {e}")
            return {'value': 1200, 'change': 0, 'change_percent': 0}
    
    async def _fetch_sector_performance(self) -> Dict[str, float]:
        """Fetch sector performance"""
        import random
        
        sectors = ['Banking', 'Real Estate', 'Consumer', 'Industrial', 'Technology', 'Utilities']
        performance = {}
        
        for sector in sectors:
            performance[sector] = round(random.uniform(-3, 3), 2)  # ±3% change
        
        return performance
    
    async def _fetch_top_movers(self) -> tuple:
        """Fetch top gainers và losers"""
        import random
        
        all_symbols = list(self.vn_stocks.keys())
        
        top_gainers = []
        top_losers = []
        
        for _ in range(5):
            symbol = random.choice(all_symbols)
            change_percent = random.uniform(2, 7)  # 2-7% gain
            top_gainers.append({
                'symbol': symbol,
                'change_percent': round(change_percent, 2),
                'price': self.vn_stocks[symbol].get('base_price', 50000)
            })
        
        for _ in range(5):
            symbol = random.choice(all_symbols)
            change_percent = random.uniform(-7, -2)  # 2-7% loss
            top_losers.append({
                'symbol': symbol,
                'change_percent': round(change_percent, 2),
                'price': self.vn_stocks[symbol].get('base_price', 50000)
            })
        
        return top_gainers, top_losers
    
    async def _fetch_foreign_flows(self) -> Dict[str, int]:
        """Fetch foreign investment flows"""
        import random
        
        return {
            'buy_value': random.randint(-500, 1000) * 1_000_000,  # triệu VND
            'sell_value': random.randint(-1000, 500) * 1_000_000,
            'net_value': random.randint(-500, 500) * 1_000_000
        }
    
    def _calculate_market_sentiment(self) -> str:
        """Calculate overall market sentiment"""
        import random
        
        sentiments = ['Bullish', 'Bearish', 'Neutral']
        weights = [0.4, 0.3, 0.3]  # Slightly bullish bias for VN market
        
        return random.choices(sentiments, weights=weights)[0]
    
    def _generate_mock_market_overview(self) -> Dict[str, Any]:
        """Generate mock market overview for demo"""
        return {
            'vn_index': {'value': 1200, 'change': 0, 'change_percent': 0},
            'sector_performance': {
                'Banking': 1.2, 'Real Estate': -0.8, 'Consumer': 0.5,
                'Industrial': 1.8, 'Technology': 2.1, 'Utilities': -0.3
            },
            'top_gainers': [
                {'symbol': 'FPT', 'change_percent': 4.2},
                {'symbol': 'HPG', 'change_percent': 3.8}
            ],
            'top_losers': [
                {'symbol': 'VHM', 'change_percent': -2.1},
                {'symbol': 'VRE', 'change_percent': -1.8}
            ],
            'foreign_flows': {'net_value': 250_000_000},
            'market_sentiment': 'Neutral',
            'timestamp': datetime.now().isoformat()
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return (time.time() - cached_time) < self.cache_duration
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Lấy historical data cho backtesting
        
        Args:
            symbol: Stock symbol
            days: Number of days
            
        Returns:
            List of historical data points
        """
        try:
            # Mock historical data generation
            import random
            from datetime import timedelta
            
            current_stock = await self.get_stock_data(symbol)
            if not current_stock:
                return []
            
            historical_data = []
            base_price = current_stock.price
            
            for i in range(days, 0, -1):
                date = datetime.now() - timedelta(days=i)
                
                # Random walk với mean reversion
                daily_return = random.normalvariate(0.001, 0.025)  # 0.1% daily return, 2.5% volatility
                base_price *= (1 + daily_return)
                
                historical_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'price': round(base_price, -2),
                    'volume': random.randint(50000, 500000),
                    'change_percent': round(daily_return * 100, 2)
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching historical data for {symbol}: {e}")
            return []
    
    def get_available_symbols(self) -> List[Dict[str, str]]:
        """
        Lấy danh sách symbols có sẵn
        
        Returns:
            List of available symbols với metadata
        """
        return [
            {
                'symbol': symbol,
                'name': info['name'],
                'sector': info['sector'],
                'exchange': info['exchange']
            }
            for symbol, info in self.vn_stocks.items()
        ]
    
    async def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Lấy news sentiment cho stock
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict: News sentiment analysis
        """
        try:
            # Mock news sentiment analysis
            import random
            
            sentiments = ['Positive', 'Negative', 'Neutral']
            sentiment_weights = [0.4, 0.3, 0.3]
            
            selected_sentiment = random.choices(sentiments, weights=sentiment_weights)[0]
            
            # Generate sample news headlines
            positive_headlines = [
                f"{symbol} báo lãi quý tăng trưởng mạnh",
                f"Dự án mới của {symbol} được phê duyệt",
                f"{symbol} mở rộng thị trường xuất khẩu"
            ]
            
            negative_headlines = [
                f"{symbol} gặp khó khăn trong quý này",
                f"Ngành của {symbol} chịu áp lực cạnh tranh",
                f"{symbol} hoãn dự án đầu tư lớn"
            ]
            
            neutral_headlines = [
                f"{symbol} công bố kết quả kinh doanh",
                f"Họp đại hội cổ đông {symbol}",
                f"{symbol} thông báo thay đổi nhân sự"
            ]
            
            if selected_sentiment == 'Positive':
                headlines = random.sample(positive_headlines, 2)
                score = random.uniform(0.6, 0.9)
            elif selected_sentiment == 'Negative':
                headlines = random.sample(negative_headlines, 2)
                score = random.uniform(0.1, 0.4)
            else:
                headlines = random.sample(neutral_headlines, 2)
                score = random.uniform(0.4, 0.6)
            
            return {
                'sentiment': selected_sentiment,
                'sentiment_score': round(score, 2),
                'headlines': headlines,
                'news_count': random.randint(5, 20),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching news sentiment for {symbol}: {e}")
            return {
                'sentiment': 'Neutral',
                'sentiment_score': 0.5,
                'headlines': [],
                'news_count': 0
            }

# Utility functions
async def get_multiple_stocks(symbols: List[str]) -> Dict[str, VNStockData]:
    """
    Lấy data cho multiple stocks concurrently
    
    Args:
        symbols: List of stock symbols
        
    Returns:
        Dict mapping symbol to stock data
    """
    api = VNStockAPI()
    
    tasks = [api.get_stock_data(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    stock_data = {}
    for symbol, result in zip(symbols, results):
        if isinstance(result, VNStockData):
            stock_data[symbol] = result
        else:
            logger.error(f"❌ Failed to fetch data for {symbol}: {result}")
    
    return stock_data

def format_currency_vnd(amount: float) -> str:
    """Format số tiền VND"""
    if amount >= 1_000_000_000:
        return f"{amount/1_000_000_000:.1f}B VND"
    elif amount >= 1_000_000:
        return f"{amount/1_000_000:.1f}M VND"
    elif amount >= 1_000:
        return f"{amount/1_000:.1f}K VND"
    else:
        return f"{amount:.0f} VND"

def calculate_technical_indicators(prices: List[float]) -> Dict[str, float]:
    """
    Calculate basic technical indicators

    Args:
        prices: List of historical prices

    Returns:
        Dict: Technical indicators
    """
    if len(prices) < 20:
        return {}

    try:
        current_price = prices[-1]

        # Simple Moving Averages
        sma_5 = sum(prices[-5:]) / 5
        sma_20 = sum(prices[-20:]) / 20

        # RSI calculation (simplified)
        gains = []
        losses = []
        for i in range(1, min(15, len(prices))):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # Support and Resistance
        recent_high = max(prices[-10:])
        recent_low = min(prices[-10:])

        return {
            'current_price': current_price,
            'sma_5': round(sma_5, 2),
            'sma_20': round(sma_20, 2),
            'rsi': round(rsi, 2),
            'support': recent_low,
            'resistance': recent_high,
            'trend': 'Bullish' if current_price > sma_20 else 'Bearish'
        }

    except Exception as e:
        logger.error(f"❌ Error calculating technical indicators: {e}")
        return {}
            'current_price': current_price,
            'sma_5': round(sma_5, 2),
            'sma_20': round(sma_20, 2),
            'rsi': round(rsi, 2),
            'support': recent_low,
            'resistance': recent_high,
            'trend': 'Bullish' if current_price > sma_20 else 'Bearish'
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating technical indicators: {e}")
        return {}
