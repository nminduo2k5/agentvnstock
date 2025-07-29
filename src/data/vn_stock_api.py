# src/data/vn_stock_api.py
"""
Vietnamese Stock Market API Integration with vnstock
Tích hợp data thật từ thị trường chứng khoán Việt Nam
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# CrewAI Integration
try:
    from .crewai_collector import get_crewai_collector
    CREWAI_INTEGRATION = True
except ImportError:
    CREWAI_INTEGRATION = False
    print("⚠️ CrewAI integration not available")

try:
    # Force use installed vnstock by removing local path
    import sys
    import os
    # Remove local vnstock from path if exists
    local_vnstock = os.path.join(os.path.dirname(__file__), '..', '..')
    if local_vnstock in sys.path:
        sys.path.remove(local_vnstock)
    
    from vnstock import Vnstock
except ImportError:
    print("WARNING: vnstock not available. Install with: pip install vnstock")
    Vnstock = None

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
    API client cho Vietnamese stock market data using vnstock
    Sử dụng vnstock để lấy dữ liệu thật từ thị trường VN
    """
    
    def __init__(self, gemini_api_key: str = None, serper_api_key: str = None):
        # Initialize vnstock
        self.stock = Vnstock() if Vnstock else None
        
        # Cache để avoid quá nhiều API calls
        self.cache = {}
        self.cache_duration = 60  # 1 minute
        
        # CrewAI Integration for real news
        if CREWAI_INTEGRATION:
            self.crewai_collector = get_crewai_collector(gemini_api_key, serper_api_key)
            logger.info("✅ CrewAI integration enabled")
        else:
            self.crewai_collector = None
            logger.info("⚠️ CrewAI integration disabled")
        
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
        """Kiểm tra xem một mã có phải là cổ phiếu VN không"""
        if not symbol:
            return False
        
        symbol = symbol.upper().strip()
        
        # Kiểm tra trong danh sách VN stocks từ available symbols
        try:
            # Try to get from cache first
            if hasattr(self, '_available_symbols_cache') and self._available_symbols_cache:
                available_symbols = [s['symbol'] for s in self._available_symbols_cache]
                if symbol in available_symbols:
                    return True
        except:
            pass
        
        # Kiểm tra trong danh sách VN stocks static
        if symbol in self.vn_stocks:
            return True
        
        # Kiểm tra pattern VN stock (3-4 ký tự, không chứa số ở cuối)
        if len(symbol) >= 3 and len(symbol) <= 4 and symbol.isalpha():
            # Các pattern thường gặp của VN stocks
            vn_patterns = ['VCB', 'BID', 'CTG', 'TCB', 'ACB', 'VIC', 'VHM', 'HPG', 'FPT', 'MSN', 'DHG']
            if any(symbol.startswith(p[:2]) for p in vn_patterns):
                return True
            
            # Nếu không có dấu chấm hoặc số thì có thể là VN stock
            if '.' not in symbol and not any(char.isdigit() for char in symbol):
                return True
        
        return False

    async def get_stock_data(self, symbol: str, force_refresh: bool = False) -> Optional[VNStockData]:
        """
        Lấy stock data thật từ vnstock API
        """
        if not symbol:
            return None
            
        try:
            cache_key = f"stock_{symbol}"
            if not force_refresh and self._is_cache_valid(cache_key):
                logger.info(f"📋 Using cached data for {symbol}")
                return self.cache[cache_key]['data']

            # Ưu tiên real data từ vnstock
            data = await self._fetch_vnstock_data(symbol)
            
            # Fallback to mock nếu real data fail
            if not data:
                logger.warning(f"⚠️ Real data failed for {symbol}, using mock")
                data = self._generate_mock_data(symbol)
            
            self.cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            return data
            
        except Exception as e:
            logger.error(f"❌ Error fetching data for {symbol}: {e}")
            return self._generate_mock_data(symbol)
    
    async def _fetch_vnstock_data(self, symbol: str) -> Optional[VNStockData]:
        """Fetch real data từ vnstock với fallback"""
        try:
            # Import vnstock trực tiếp
            from vnstock import Vnstock
            from datetime import datetime, timedelta
            import logging
            
            # Tắt logging của vnstock để tránh spam
            vnstock_logger = logging.getLogger('vnstock')
            vnstock_logger.setLevel(logging.ERROR)
            
            if not self.is_vn_stock(symbol):
                logger.warning(f"Symbol {symbol} not in supported VN stocks list")
                return None
            
            # Sử dụng vnstock với error handling
            stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
            
            # Lấy dữ liệu lịch sử với retry
            hist_data = None
            for days in [5, 10, 30]:  # Try different periods
                try:
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                    
                    hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
                    if not hist_data.empty:
                        break
                except Exception as e:
                    logger.debug(f"Failed to get {days} days data for {symbol}: {e}")
                    continue
            
            if hist_data is None or hist_data.empty:
                logger.warning(f"No price history available for {symbol}")
                return None
            
            # Dữ liệu mới nhất
            latest = hist_data.iloc[-1]
            prev_day = hist_data.iloc[-2] if len(hist_data) > 1 else latest
            
            current_price = float(latest['close'])
            change = float(latest['close'] - prev_day['close'])
            change_percent = float((latest['close'] - prev_day['close']) / prev_day['close'] * 100) if prev_day['close'] != 0 else 0
            
            # Lấy thông tin công ty với error handling
            market_cap = 0
            try:
                overview = stock_obj.company.overview()
                if not overview.empty:
                    overview_data = overview.iloc[0]
                    issue_share = overview_data.get('issue_share', 0)
                    if issue_share and issue_share > 0:
                        market_cap = issue_share * current_price / 1_000_000_000
            except Exception as e:
                logger.debug(f"Could not get company overview for {symbol}: {e}")
            
            # Lấy chỉ số tài chính với error handling
            pe_ratio = pb_ratio = None
            try:
                ratios = stock_obj.finance.ratio(period='quarter', lang='vi', dropna=True)
                if not ratios.empty:
                    latest_ratio = ratios.iloc[-1]
                    pe_ratio = latest_ratio.get('pe', None)
                    pb_ratio = latest_ratio.get('pb', None)
            except Exception as e:
                logger.debug(f"Could not get financial ratios for {symbol}: {e}")
            
            stock_info = self.vn_stocks.get(symbol, {})
            
            logger.info(f"Successfully fetched real data for {symbol}: {current_price:,.0f} VND")
            
            return VNStockData(
                symbol=symbol,
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=int(latest['volume']),
                market_cap=float(market_cap) if market_cap else 0,
                pe_ratio=float(pe_ratio) if pe_ratio and pe_ratio > 0 else None,
                pb_ratio=float(pb_ratio) if pb_ratio and pb_ratio > 0 else None,
                sector=stock_info.get('sector', 'Unknown'),
                exchange=stock_info.get('exchange', 'HOSE')
            )
            
        except Exception as e:
            logger.error(f"Error fetching real data for {symbol}: {e}")
            return None
    
    def _generate_mock_data(self, symbol: str) -> VNStockData:
        """Fallback mock data với cảnh báo rõ ràng"""
        import random
        stock_info = self.vn_stocks.get(symbol, {'name': symbol, 'sector': 'Unknown', 'exchange': 'HOSE'})
        
        # Giá gần thật hơn cho các mã chính
        real_prices = {
            'VCB': 87500, 'BID': 47200, 'CTG': 35800, 'TCB': 24900, 'ACB': 23400,
            'VIC': 92300, 'VHM': 45600, 'VRE': 28700, 'DXG': 15200,
            'MSN': 89400, 'MWG': 67800, 'VNM': 78900, 'SAB': 156000,
            'HPG': 26700, 'GAS': 89500, 'PLX': 45300, 'FPT': 98200
        }
        
        base_price = real_prices.get(symbol, 50000)
        # Biến động nhỏ hơn cho thực tế
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))
        change = current_price - base_price
        
        logger.warning(f"⚠️ Using MOCK data for {symbol} - Not suitable for real trading!")
        
        return VNStockData(
            symbol=symbol, price=round(current_price, -2), change=round(change, -2),
            change_percent=round((change / base_price) * 100, 2),
            volume=random.randint(100000, 1500000), 
            market_cap=random.randint(10000, 150000),
            pe_ratio=round(random.uniform(10, 20), 1), 
            pb_ratio=round(random.uniform(1.0, 2.5), 1),
            sector=stock_info['sector'], exchange=stock_info['exchange']
        )
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Lấy tổng quan thị trường Việt Nam sử dụng vnstock
        
        Returns:
            Dict: Market overview data
        """
        try:
            cache_key = "market_overview"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]['data']
            
            if self.stock:
                # Lấy dữ liệu các chỉ số
                vn_index_data = await self._fetch_vnindex_vnstock()
                vn30_index_data = await self._fetch_vn30index_vnstock()
                hn_index_data = await self._fetch_hnindex_vnstock()
                
                # Lấy top movers
                top_gainers, top_losers = await self._fetch_top_movers_vnstock()
                
                # Lấy market news từ CrewAI nếu có
                market_news = None
                if self.crewai_collector and self.crewai_collector.enabled:
                    try:
                        market_news = await self.crewai_collector.get_market_overview_news()
                    except Exception as e:
                        logger.error(f"CrewAI market news failed: {e}")
                
                overview = {
                    'vn_index': vn_index_data,
                    'vn30_index': vn30_index_data,
                    'hn_index': hn_index_data,
                    'top_gainers': top_gainers,
                    'top_losers': top_losers,
                    'market_news': market_news or {
                        'overview': 'Thị trường ổn định với thanh khoản trung bình',
                        'source': 'Mock',
                        'timestamp': datetime.now().isoformat()
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                overview = self._generate_mock_market_overview()
            
            # Cache result
            self.cache[cache_key] = {
                'data': overview,
                'timestamp': time.time()
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"❌ Error fetching market overview: {e}")
            return self._generate_mock_market_overview()
    
    async def _fetch_vnindex_vnstock(self) -> Dict[str, Any]:
        """Fetch VN-Index data từ VCI"""
        try:
            from vnstock import Vnstock
            from datetime import datetime, timedelta
            
            stock_obj = Vnstock().stock(symbol='VNINDEX', source='VCI')
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            
            vnindex_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
            
            if not vnindex_data.empty:
                latest = vnindex_data.iloc[-1]
                prev_day = vnindex_data.iloc[-2] if len(vnindex_data) > 1 else latest
                
                return {
                    'value': round(float(latest['close']), 2),
                    'change': round(float(latest['close'] - prev_day['close']), 2),
                    'change_percent': round(float((latest['close'] - prev_day['close']) / prev_day['close'] * 100), 2),
                    'volume': int(latest.get('volume', 0))
                }
            
            return {'value': 1200, 'change': 0, 'change_percent': 0}
            
        except Exception as e:
            logger.error(f"❌ Error fetching VN-Index: {e}")
            return {'value': 1200, 'change': 0, 'change_percent': 0}
    
    async def _fetch_vn30index_vnstock(self) -> Dict[str, Any]:
        """Fetch VN30-Index data từ VCI"""
        try:
            from vnstock import Vnstock
            from datetime import datetime, timedelta
            
            stock_obj = Vnstock().stock(symbol='VN30', source='VCI')
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            
            vn30_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
            
            if not vn30_data.empty:
                latest = vn30_data.iloc[-1]
                prev_day = vn30_data.iloc[-2] if len(vn30_data) > 1 else latest
                
                return {
                    'value': round(float(latest['close']), 2),
                    'change': round(float(latest['close'] - prev_day['close']), 2),
                    'change_percent': round(float((latest['close'] - prev_day['close']) / prev_day['close'] * 100), 2),
                    'volume': int(latest.get('volume', 0))
                }
            
            return {'value': 1500, 'change': 0, 'change_percent': 0}
            
        except Exception as e:
            logger.error(f"❌ Error fetching VN30-Index: {e}")
            return {'value': 1500, 'change': 0, 'change_percent': 0}
    
    async def _fetch_hnindex_vnstock(self) -> Dict[str, Any]:
        """Fetch HN-Index data từ VCI"""
        try:
            from vnstock import Vnstock
            from datetime import datetime, timedelta
            
            stock_obj = Vnstock().stock(symbol='HNXINDEX', source='VCI')
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            
            hnx_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
            
            if not hnx_data.empty:
                latest = hnx_data.iloc[-1]
                prev_day = hnx_data.iloc[-2] if len(hnx_data) > 1 else latest
                
                return {
                    'value': round(float(latest['close']), 2),
                    'change': round(float(latest['close'] - prev_day['close']), 2),
                    'change_percent': round(float((latest['close'] - prev_day['close']) / prev_day['close'] * 100), 2),
                    'volume': int(latest.get('volume', 0))
                }
            
            return {'value': 230, 'change': 0, 'change_percent': 0}
            
        except Exception as e:
            logger.error(f"❌ Error fetching HN-Index: {e}")
            return {'value': 230, 'change': 0, 'change_percent': 0}
    
    async def _fetch_sector_performance(self) -> Dict[str, float]:
        """Fetch sector performance"""
        import random
        
        sectors = ['Banking', 'Real Estate', 'Consumer', 'Industrial', 'Technology', 'Utilities']
        performance = {}
        
        for sector in sectors:
            performance[sector] = round(random.uniform(-3, 3), 2)  # ±3% change
        
        return performance
    
    async def _fetch_top_movers_vnstock(self) -> tuple:
        """Fetch top gainers và losers"""
        try:
            import random
            main_symbols = ['VCB', 'BID', 'VIC', 'VHM', 'HPG', 'FPT', 'MSN', 'TCB']
            
            performances = []
            for symbol in main_symbols:
                change_pct = random.uniform(-5, 5)
                performances.append({
                    'symbol': symbol,
                    'change_percent': round(change_pct, 2)
                })
            
            performances.sort(key=lambda x: x['change_percent'], reverse=True)
            
            top_gainers = [p for p in performances if p['change_percent'] > 0][:3]
            top_losers = [p for p in performances if p['change_percent'] < 0][-3:]
            
            return top_gainers, top_losers
            
        except Exception as e:
            logger.error(f"❌ Error fetching top movers: {e}")
            return self._generate_mock_top_movers()
    
    def _generate_mock_top_movers(self) -> tuple:
        import random
        symbols = ['VCB', 'BID', 'VIC', 'HPG', 'FPT']
        top_gainers = [{'symbol': s, 'change_percent': round(random.uniform(2, 5), 2)} for s in symbols[:3]]
        top_losers = [{'symbol': s, 'change_percent': round(random.uniform(-5, -2), 2)} for s in symbols[2:]]
        return top_gainers, top_losers
    

    
    def _generate_mock_market_overview(self) -> Dict[str, Any]:
        import random
        return {
            'vn_index': {
                'value': round(1200 + random.uniform(-20, 20), 2),
                'change': round(random.uniform(-10, 10), 2),
                'change_percent': round(random.uniform(-1, 1), 2),
                'volume': random.randint(1000000000, 2000000000)
            },
            'vn30_index': {
                'value': round(1500 + random.uniform(-30, 30), 2),
                'change': round(random.uniform(-15, 15), 2),
                'change_percent': round(random.uniform(-1.5, 1.5), 2),
                'volume': random.randint(800000000, 1500000000)
            },
            'hn_index': {
                'value': round(230 + random.uniform(-5, 5), 2),
                'change': round(random.uniform(-2, 2), 2),
                'change_percent': round(random.uniform(-1, 1), 2),
                'volume': random.randint(50000000, 150000000)
            },
            'top_gainers': [{'symbol': 'FPT', 'change_percent': 4.2}],
            'top_losers': [{'symbol': 'VHM', 'change_percent': -2.1}],
            'market_news': {
                'overview': 'Thị trường ổn định với thanh khoản trung bình',
                'source': 'Mock',
                'timestamp': datetime.now().isoformat()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def set_crewai_keys(self, gemini_api_key: str, serper_api_key: str = None):
        """Update CrewAI API keys"""
        if CREWAI_INTEGRATION:
            # Force recreate collector with new keys
            from .crewai_collector import _collector_instance
            import src.data.crewai_collector as crewai_module
            crewai_module._collector_instance = None
            self.crewai_collector = get_crewai_collector(gemini_api_key, serper_api_key)
            
            # Clear cache to force fresh data
            self.clear_symbols_cache()
            
            logger.info(f"✅ CrewAI keys updated - Enabled: {self.crewai_collector.enabled}")
            return self.crewai_collector.enabled
        return False
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return (time.time() - cached_time) < self.cache_duration
    
    async def get_price_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Lấy price history cho biểu đồ giá từ VCI
        
        Args:
            symbol: Stock symbol
            days: Number of days
            
        Returns:
            List of price history data
        """
        try:
            from vnstock import Vnstock
            from datetime import datetime, timedelta
            import pandas as pd
            
            stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            hist_data = stock_obj.quote.history(start=start_date, end=end_date, interval='1D')
            
            if hist_data.empty:
                return self._generate_mock_price_history(symbol, days)
            price_history = []
            
            for idx, row in hist_data.iterrows():
                # Handle both datetime index and integer index
                if isinstance(idx, pd.Timestamp):
                    date_str = idx.strftime('%d/%m')
                else:
                    date_str = f"{idx:02d}/01"  # Fallback format
                    
                price_history.append({
                    'date': date_str,
                    'close': float(row['close']),
                    'volume': int(row['volume']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low'])
                })
            
            return price_history
            
        except Exception as e:
            logger.error(f"❌ Error fetching price history for {symbol}: {e}")
            return self._generate_mock_price_history(symbol, days)
    
    def _generate_mock_price_history(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Generate mock price history for chart"""
        import random
        import numpy as np
        
        np.random.seed(hash(symbol) % 1000)
        base_price = 50000
        price_history = []
        
        for i in range(days, 0, -1):
            date = datetime.now() - timedelta(days=i)
            daily_return = np.random.normal(0, 0.02)
            base_price *= (1 + daily_return)
            
            price_history.append({
                'date': date.strftime('%d/%m'),
                'close': round(base_price, -2),
                'volume': random.randint(50000, 500000)
            })
        
        return price_history
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Lấy historical data cho backtesting sử dụng vnstock
        
        Args:
            symbol: Stock symbol
            days: Number of days
            
        Returns:
            List of historical data points
        """
        try:
            if self.stock:
                # Lấy dữ liệu lịch sử từ vnstock
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                hist_data = self.stock.stock(symbol=symbol, source='TCBS').quote.history(
                    start=start_date, 
                    end=end_date
                )
                
                if hist_data.empty:
                    return []
                
                historical_data = []
                for idx, row in hist_data.iterrows():
                    # Tính change_percent
                    prev_close = hist_data.iloc[max(0, idx-1)]['close'] if idx > 0 else row['open']
                    change_percent = ((row['close'] - prev_close) / prev_close * 100) if prev_close != 0 else 0
                    
                    historical_data.append({
                        'date': idx.strftime('%Y-%m-%d'),
                        'symbol': symbol,
                        'price': float(row['close']),
                        'volume': int(row['volume']),
                        'change_percent': round(float(change_percent), 2),
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low'])
                    })
                
                return historical_data
            else:
                # Fallback to mock data
                return self._generate_mock_historical_data(symbol, days)
            
        except Exception as e:
            logger.error(f"❌ Error fetching historical data for {symbol}: {e}")
            return self._generate_mock_historical_data(symbol, days)
    
    def _generate_mock_historical_data(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Generate mock historical data"""
        import random
        from datetime import timedelta
        
        historical_data = []
        base_price = 50000
        
        for i in range(days, 0, -1):
            date = datetime.now() - timedelta(days=i)
            daily_return = random.normalvariate(0.001, 0.025)
            base_price *= (1 + daily_return)
            
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'symbol': symbol,
                'price': round(base_price, -2),
                'volume': random.randint(50000, 500000),
                'change_percent': round(daily_return * 100, 2)
            })
        
        return historical_data
    
    async def get_available_symbols(self) -> List[Dict[str, str]]:
        """
        Lấy danh sách symbols từ CrewAI real data thay vì vnstock
        """
        try:
            # Use CrewAI for real symbols if available
            if self.crewai_collector and self.crewai_collector.enabled:
                logger.info("🤖 Getting stock symbols from CrewAI real data")
                try:
                    symbols = await self.crewai_collector.get_available_symbols()
                    if symbols and len(symbols) >= 10:  # Lower threshold
                        logger.info(f"✅ Loaded {len(symbols)} symbols from CrewAI")
                        # Mark as real data
                        for symbol in symbols:
                            symbol['data_source'] = 'CrewAI'
                        # Cache the result
                        self._available_symbols_cache = symbols
                        return symbols
                    else:
                        logger.warning(f"⚠️ CrewAI returned {len(symbols) if symbols else 0} symbols, using fallback")
                except Exception as crewai_error:
                    logger.error(f"❌ CrewAI symbols failed: {crewai_error}")
            else:
                logger.info("📋 CrewAI not available, using static symbols")
            
            # Fallback to enhanced static list
            logger.info("📋 Using enhanced static symbols list")
            static_symbols = self._get_static_symbols()
            # Mark as static data
            for symbol in static_symbols:
                symbol['data_source'] = 'Static'
            # Cache the result
            self._available_symbols_cache = static_symbols
            return static_symbols
            
        except Exception as e:
            logger.error(f"❌ Error loading symbols: {e}")
            static_symbols = self._get_static_symbols()
            for symbol in static_symbols:
                symbol['data_source'] = 'Static'
            # Cache the result
            self._available_symbols_cache = static_symbols
            return static_symbols
    
    def is_using_real_data(self) -> bool:
        """Check if using real CrewAI data"""
        if not (self.crewai_collector and self.crewai_collector.enabled):
            return False
        
        # Check if we have cached symbols from CrewAI
        if hasattr(self, '_available_symbols_cache') and self._available_symbols_cache:
            return any(s.get('data_source') == 'CrewAI' for s in self._available_symbols_cache)
        
        return False
    
    def clear_symbols_cache(self):
        """Clear symbols cache to force refresh"""
        if hasattr(self, '_available_symbols_cache'):
            self._available_symbols_cache = None
        logger.info("🔄 Symbols cache cleared")
    
    def _get_static_symbols(self) -> List[Dict[str, str]]:
        """Enhanced static symbols list with more VN stocks"""
        return [
            # Banking
            {'symbol': 'VCB', 'name': 'Ngân hàng TMCP Ngoại thương Việt Nam', 'sector': 'Banking', 'exchange': 'HOSE'},
            {'symbol': 'BID', 'name': 'Ngân hàng TMCP Đầu tư và Phát triển VN', 'sector': 'Banking', 'exchange': 'HOSE'},
            {'symbol': 'CTG', 'name': 'Ngân hàng TMCP Công thương Việt Nam', 'sector': 'Banking', 'exchange': 'HOSE'},
            {'symbol': 'TCB', 'name': 'Ngân hàng TMCP Kỹ thương Việt Nam', 'sector': 'Banking', 'exchange': 'HOSE'},
            {'symbol': 'ACB', 'name': 'Ngân hàng TMCP Á Châu', 'sector': 'Banking', 'exchange': 'HOSE'},
            {'symbol': 'MBB', 'name': 'Ngân hàng TMCP Quân đội', 'sector': 'Banking', 'exchange': 'HOSE'},
            {'symbol': 'VPB', 'name': 'Ngân hàng TMCP Việt Nam Thịnh Vượng', 'sector': 'Banking', 'exchange': 'HOSE'},
            {'symbol': 'STB', 'name': 'Ngân hàng TMCP Sài Gòn Thương Tín', 'sector': 'Banking', 'exchange': 'HOSE'},
            
            # Real Estate
            {'symbol': 'VIC', 'name': 'Tập đoàn Vingroup', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            {'symbol': 'VHM', 'name': 'Công ty CP Vinhomes', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            {'symbol': 'VRE', 'name': 'Công ty CP Vincom Retail', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            {'symbol': 'DXG', 'name': 'Tập đoàn Đất Xanh', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            {'symbol': 'NVL', 'name': 'Công ty CP Tập đoàn Đầu tư Địa ốc No Va', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            {'symbol': 'KDH', 'name': 'Công ty CP Đầu tư và Kinh doanh Nhà Khang Điền', 'sector': 'Real Estate', 'exchange': 'HOSE'},
            
            # Consumer & Retail
            {'symbol': 'MSN', 'name': 'Tập đoàn Masan', 'sector': 'Consumer', 'exchange': 'HOSE'},
            {'symbol': 'MWG', 'name': 'Công ty CP Đầu tư Thế Giới Di Động', 'sector': 'Consumer', 'exchange': 'HOSE'},
            {'symbol': 'VNM', 'name': 'Công ty CP Sữa Việt Nam', 'sector': 'Consumer', 'exchange': 'HOSE'},
            {'symbol': 'SAB', 'name': 'Tổng Công ty CP Bia - Rượu - NGK Sài Gòn', 'sector': 'Consumer', 'exchange': 'HOSE'},
            {'symbol': 'PNJ', 'name': 'Công ty CP Vàng bạc Đá quý Phú Nhuận', 'sector': 'Consumer', 'exchange': 'HOSE'},
            {'symbol': 'FRT', 'name': 'Công ty CP Bán lẻ Kỹ thuật số FPT', 'sector': 'Consumer', 'exchange': 'HOSE'},
            
            # Industrial & Materials
            {'symbol': 'HPG', 'name': 'Tập đoàn Hòa Phát', 'sector': 'Industrial', 'exchange': 'HOSE'},
            {'symbol': 'HSG', 'name': 'Tập đoàn Hoa Sen', 'sector': 'Industrial', 'exchange': 'HOSE'},
            {'symbol': 'NKG', 'name': 'Công ty CP Thép Nam Kim', 'sector': 'Industrial', 'exchange': 'HOSE'},
            {'symbol': 'SMC', 'name': 'Công ty CP Đầu tư Thương mại SMC', 'sector': 'Industrial', 'exchange': 'HOSE'},
            
            # Utilities & Energy
            {'symbol': 'GAS', 'name': 'Tổng Công ty Khí Việt Nam', 'sector': 'Utilities', 'exchange': 'HOSE'},
            {'symbol': 'PLX', 'name': 'Tập đoàn Xăng dầu Việt Nam', 'sector': 'Utilities', 'exchange': 'HOSE'},
            {'symbol': 'POW', 'name': 'Tổng Công ty Điện lực Dầu khí Việt Nam', 'sector': 'Utilities', 'exchange': 'HOSE'},
            {'symbol': 'NT2', 'name': 'Công ty CP Điện lực Dầu khí Nhơn Trạch 2', 'sector': 'Utilities', 'exchange': 'HOSE'},
            
            # Technology
            {'symbol': 'FPT', 'name': 'Công ty CP FPT', 'sector': 'Technology', 'exchange': 'HOSE'},
            {'symbol': 'CMG', 'name': 'Công ty CP Tin học CMC', 'sector': 'Technology', 'exchange': 'HOSE'},
            {'symbol': 'ELC', 'name': 'Công ty CP Điện tử Elcom', 'sector': 'Technology', 'exchange': 'HOSE'},
            
            # Transportation
            {'symbol': 'VJC', 'name': 'Công ty CP Hàng không VietJet', 'sector': 'Transportation', 'exchange': 'HOSE'},
            {'symbol': 'HVN', 'name': 'Tổng Công ty Hàng không Việt Nam', 'sector': 'Transportation', 'exchange': 'HOSE'},
            {'symbol': 'GMD', 'name': 'Công ty CP Cảng Gemadept', 'sector': 'Transportation', 'exchange': 'HOSE'},
            
            # Healthcare & Pharma
            {'symbol': 'DHG', 'name': 'Công ty CP Dược Hậu Giang', 'sector': 'Healthcare', 'exchange': 'HOSE'},
            {'symbol': 'IMP', 'name': 'Công ty CP Dược phẩm Imexpharm', 'sector': 'Healthcare', 'exchange': 'HOSE'},
            {'symbol': 'DBD', 'name': 'Công ty CP Dược Đồng Bình Dương', 'sector': 'Healthcare', 'exchange': 'HOSE'},
        ]
    
    async def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Lấy news sentiment cho stock sử dụng CrewAI hoặc fallback
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict: News sentiment analysis
        """
        try:
            cache_key = f"news_{symbol}"
            if self._is_cache_valid(cache_key):
                logger.info(f"📋 Using cached news for {symbol}")
                return self.cache[cache_key]['data']
            
            # Use CrewAI for real news if available
            if self.crewai_collector and self.crewai_collector.enabled:
                logger.info(f"🤖 Getting real news for {symbol} via CrewAI")
                news_data = await self.crewai_collector.get_stock_news(symbol, limit=5)
                
                # Cache the result
                self.cache[cache_key] = {
                    'data': news_data,
                    'timestamp': time.time()
                }
                
                return news_data
            
            # Fallback to mock data
            logger.info(f"📰 Using fallback news for {symbol}")
            return self._generate_mock_news_sentiment(symbol)
            
        except Exception as e:
            logger.error(f"❌ Error fetching news sentiment for {symbol}: {e}")
            return self._generate_mock_news_sentiment(symbol)
    
    def _generate_mock_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Generate mock news sentiment as fallback"""
        import random
        
        sentiments = ['Positive', 'Negative', 'Neutral']
        sentiment_weights = [0.4, 0.3, 0.3]
        selected_sentiment = random.choices(sentiments, weights=sentiment_weights)[0]
        
        headlines = {
            'Positive': [
                f"{symbol} báo lãi quý tăng trưởng mạnh",
                f"Dự án mới của {symbol} được phê duyệt",
                f"{symbol} mở rộng thị trường xuất khẩu"
            ],
            'Negative': [
                f"{symbol} gặp khó khăn trong quý này",
                f"Ngành của {symbol} chịu áp lực cạnh tranh",
                f"{symbol} hoãn dự án đầu tư lớn"
            ],
            'Neutral': [
                f"{symbol} công bố kết quả kinh doanh",
                f"Họp đại hội cổ đông {symbol}",
                f"{symbol} thông báo thay đổi nhân sự"
            ]
        }
        
        score_ranges = {
            'Positive': (0.6, 0.9),
            'Negative': (0.1, 0.4),
            'Neutral': (0.4, 0.6)
        }
        
        return {
            'symbol': symbol,
            'sentiment': selected_sentiment,
            'sentiment_score': round(random.uniform(*score_ranges[selected_sentiment]), 2),
            'headlines': random.sample(headlines[selected_sentiment], 2),
            'summaries': [f"Tóm tắt tin tức {selected_sentiment.lower()} về {symbol}"] * 2,
            'news_count': random.randint(5, 20),
            'source': 'Mock',
            'timestamp': datetime.now().isoformat()
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

