# src/utils/connection_manager.py
"""
Connection Pool Manager for HTTP requests
Quản lý connection pool để tối ưu performance
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any
from aiohttp import TCPConnector, ClientTimeout, ClientSession
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Quản lý connection pool cho HTTP requests"""
    
    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._connector: Optional[TCPConnector] = None
        self._timeout = ClientTimeout(total=30, connect=10)
    
    async def get_session(self) -> ClientSession:
        """Lấy session với connection pooling"""
        if self._session is None or self._session.closed:
            await self._create_session()
        return self._session
    
    async def _create_session(self):
        """Tạo session mới với connection pool"""
        try:
            # Create connector with optimized settings
            self._connector = TCPConnector(
                limit=100,              # Total connection pool size
                limit_per_host=30,      # Max connections per host
                ttl_dns_cache=300,      # DNS cache TTL
                use_dns_cache=True,     # Enable DNS caching
                keepalive_timeout=30,   # Keep-alive timeout
                enable_cleanup_closed=True
            )
            
            # Create session with connector
            self._session = ClientSession(
                connector=self._connector,
                timeout=self._timeout,
                headers={
                    'User-Agent': 'DUONG-AI-TRADING/2.0 (Professional Trading System)',
                    'Accept': 'application/json, text/html, */*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
            )
            
            logger.info("✅ HTTP session created with connection pooling")
            
        except Exception as e:
            logger.error(f"❌ Failed to create HTTP session: {e}")
            raise
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """GET request với connection pooling"""
        session = await self.get_session()
        return await session.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """POST request với connection pooling"""
        session = await self.get_session()
        return await session.post(url, **kwargs)
    
    async def close(self):
        """Đóng session và connector"""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector:
            await self._connector.close()
        logger.info("🔒 HTTP session closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# Singleton instance
_connection_manager: Optional[ConnectionManager] = None

async def get_connection_manager() -> ConnectionManager:
    """Lấy singleton connection manager"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager

async def cleanup_connections():
    """Cleanup connections khi shutdown"""
    global _connection_manager
    if _connection_manager:
        await _connection_manager.close()
        _connection_manager = None