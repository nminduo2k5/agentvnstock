# src/data/company_search_api.py
"""
Company Search API - Tìm kiếm thông tin công ty
Input: Tên công ty
Output: Thông tin chi tiết công ty
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class CompanySearchAPI:
    def __init__(self):
        self.name = "Company Search API"
        
        # Database công ty VN
        self.vn_companies = {
            'vietcombank': {
                'symbol': 'VCB',
                'full_name': 'Ngân hàng TMCP Ngoại thương Việt Nam',
                'sector': 'Banking',
                'description': 'Ngân hàng thương mại cổ phần lớn nhất Việt Nam',
                'headquarters': 'Hà Nội',
                'employees': 25000,
                'founded': 1963,
                'website': 'vietcombank.com.vn',
                'exchange': 'HOSE'
            },
            'bidv': {
                'symbol': 'BID',
                'full_name': 'Ngân hàng TMCP Đầu tư và Phát triển Việt Nam',
                'sector': 'Banking',
                'description': 'Ngân hàng đầu tư và phát triển Việt Nam',
                'headquarters': 'Hà Nội',
                'employees': 22000,
                'founded': 1957,
                'website': 'bidv.com.vn',
                'exchange': 'HOSE'
            },
            'vingroup': {
                'symbol': 'VIC',
                'full_name': 'Tập đoàn Vingroup',
                'sector': 'Real Estate',
                'description': 'Tập đoàn kinh doanh đa ngành lớn nhất Việt Nam',
                'headquarters': 'Hà Nội',
                'employees': 50000,
                'founded': 1993,
                'website': 'vingroup.net',
                'exchange': 'HOSE'
            },
            'fpt': {
                'symbol': 'FPT',
                'full_name': 'Công ty Cổ phần FPT',
                'sector': 'Technology',
                'description': 'Tập đoàn công nghệ thông tin hàng đầu Việt Nam',
                'headquarters': 'Hà Nội',
                'employees': 40000,
                'founded': 1988,
                'website': 'fpt.com.vn',
                'exchange': 'HOSE'
            },
            'hoa phat': {
                'symbol': 'HPG',
                'full_name': 'Tập đoàn Hòa Phát',
                'sector': 'Industrial',
                'description': 'Tập đoàn sản xuất thép hàng đầu Việt Nam',
                'headquarters': 'Hà Nội',
                'employees': 15000,
                'founded': 1992,
                'website': 'hoaphat.com.vn',
                'exchange': 'HOSE'
            },
            'masan': {
                'symbol': 'MSN',
                'full_name': 'Tập đoàn Masan',
                'sector': 'Consumer',
                'description': 'Tập đoàn tiêu dùng và tài nguyên',
                'headquarters': 'TP.HCM',
                'employees': 30000,
                'founded': 2000,
                'website': 'masangroup.com',
                'exchange': 'HOSE'
            }
        }
        
        # International companies database
        self.international_companies = {
            'apple': {
                'symbol': 'AAPL',
                'full_name': 'Apple Inc.',
                'sector': 'Technology',
                'description': 'Consumer electronics and software company',
                'headquarters': 'Cupertino, CA',
                'employees': 164000,
                'founded': 1976,
                'website': 'apple.com',
                'exchange': 'NASDAQ'
            },
            'microsoft': {
                'symbol': 'MSFT',
                'full_name': 'Microsoft Corporation',
                'sector': 'Technology',
                'description': 'Software and cloud computing company',
                'headquarters': 'Redmond, WA',
                'employees': 221000,
                'founded': 1975,
                'website': 'microsoft.com',
                'exchange': 'NASDAQ'
            },
            'tesla': {
                'symbol': 'TSLA',
                'full_name': 'Tesla, Inc.',
                'sector': 'Automotive',
                'description': 'Electric vehicle and clean energy company',
                'headquarters': 'Austin, TX',
                'employees': 140000,
                'founded': 2003,
                'website': 'tesla.com',
                'exchange': 'NASDAQ'
            }
        }
    
    async def search_company(self, company_name: str) -> Dict[str, Any]:
        """
        Tìm kiếm thông tin công ty
        Input: Tên công ty (VD: "Vietcombank", "FPT Corporation", "Apple")
        Output: Thông tin chi tiết công ty
        """
        try:
            if not company_name or not company_name.strip():
                return {"error": "Vui lòng nhập tên công ty"}
            
            company_name = company_name.lower().strip()
            
            # Search in VN companies first
            vn_result = self._search_vn_companies(company_name)
            if vn_result:
                return {
                    "search_query": company_name,
                    "found": True,
                    "market": "Vietnam",
                    "company_info": vn_result,
                    "data_source": "VN_Database",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Search in international companies
            intl_result = self._search_international_companies(company_name)
            if intl_result:
                return {
                    "search_query": company_name,
                    "found": True,
                    "market": "International",
                    "company_info": intl_result,
                    "data_source": "International_Database",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Try fuzzy search
            fuzzy_result = self._fuzzy_search(company_name)
            if fuzzy_result:
                return {
                    "search_query": company_name,
                    "found": True,
                    "market": fuzzy_result.get('market', 'Unknown'),
                    "company_info": fuzzy_result,
                    "data_source": "Fuzzy_Match",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Not found
            return {
                "search_query": company_name,
                "found": False,
                "error": f"Không tìm thấy công ty '{company_name}'",
                "suggestions": self._get_suggestions(company_name),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Company search error: {e}")
            return {
                "error": f"Lỗi tìm kiếm công ty: {str(e)}",
                "search_query": company_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _search_vn_companies(self, query: str) -> Optional[Dict[str, Any]]:
        """Tìm kiếm trong database công ty VN"""
        for key, company in self.vn_companies.items():
            if (query in key or 
                query in company['full_name'].lower() or
                query in company['symbol'].lower()):
                return company
        return None
    
    def _search_international_companies(self, query: str) -> Optional[Dict[str, Any]]:
        """Tìm kiếm trong database công ty quốc tế"""
        for key, company in self.international_companies.items():
            if (query in key or 
                query in company['full_name'].lower() or
                query in company['symbol'].lower()):
                return company
        return None
    
    def _fuzzy_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Tìm kiếm mờ"""
        all_companies = {**self.vn_companies, **self.international_companies}
        
        for key, company in all_companies.items():
            # Check partial matches
            if (any(word in key for word in query.split()) or
                any(word in company['full_name'].lower() for word in query.split())):
                company['market'] = 'Vietnam' if key in self.vn_companies else 'International'
                return company
        
        return None
    
    def _get_suggestions(self, query: str) -> List[str]:
        """Đưa ra gợi ý tìm kiếm"""
        suggestions = []
        all_companies = {**self.vn_companies, **self.international_companies}
        
        for key, company in all_companies.items():
            if len(suggestions) >= 5:
                break
            suggestions.append(f"{company['full_name']} ({company['symbol']})")
        
        return suggestions[:5]
    
    async def get_company_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """Lấy thông tin công ty theo mã cổ phiếu"""
        try:
            symbol = symbol.upper().strip()
            
            # Search VN companies
            for company in self.vn_companies.values():
                if company['symbol'] == symbol:
                    return {
                        "symbol": symbol,
                        "found": True,
                        "market": "Vietnam",
                        "company_info": company,
                        "data_source": "VN_Database"
                    }
            
            # Search international companies
            for company in self.international_companies.values():
                if company['symbol'] == symbol:
                    return {
                        "symbol": symbol,
                        "found": True,
                        "market": "International", 
                        "company_info": company,
                        "data_source": "International_Database"
                    }
            
            return {
                "symbol": symbol,
                "found": False,
                "error": f"Không tìm thấy công ty với mã {symbol}"
            }
            
        except Exception as e:
            return {
                "error": f"Lỗi tìm kiếm theo symbol: {str(e)}",
                "symbol": symbol
            }
    
    async def search_companies_by_sector(self, sector: str) -> Dict[str, Any]:
        """Tìm kiếm công ty theo ngành"""
        try:
            sector = sector.lower().strip()
            results = []
            
            all_companies = {**self.vn_companies, **self.international_companies}
            
            for key, company in all_companies.items():
                if sector in company['sector'].lower():
                    results.append({
                        'symbol': company['symbol'],
                        'name': company['full_name'],
                        'sector': company['sector'],
                        'market': 'Vietnam' if key in self.vn_companies else 'International'
                    })
            
            return {
                "sector_query": sector,
                "found_count": len(results),
                "companies": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Lỗi tìm kiếm theo ngành: {str(e)}",
                "sector_query": sector
            }

# Singleton instance
_company_search_instance = None

def get_company_search_api() -> CompanySearchAPI:
    """Get singleton CompanySearchAPI instance"""
    global _company_search_instance
    
    if _company_search_instance is None:
        _company_search_instance = CompanySearchAPI()
    
    return _company_search_instance