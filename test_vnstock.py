#!/usr/bin/env python3
"""
Test vnstock integration
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.vn_stock_api import VNStockAPI

async def test_vnstock():
    """Test vnstock integration"""
    print("Testing vnstock integration...")
    
    api = VNStockAPI()
    
    # Test single stock
    print("\nTesting single stock data (VCB)...")
    vcb_data = await api.get_stock_data('VCB')
    if vcb_data:
        print(f"SUCCESS VCB: {vcb_data.price:,.0f} VND ({vcb_data.change_percent:+.2f}%)")
        print(f"   Volume: {vcb_data.volume:,}")
        print(f"   Market Cap: {vcb_data.market_cap:,.1f}B VND")
    else:
        print("FAILED to get VCB data")
    
    # Test market overview
    print("\nTesting market overview...")
    market_data = await api.get_market_overview()
    if market_data:
        vn_index = market_data['vn_index']
        print(f"SUCCESS VN-Index: {vn_index['value']:,.2f} ({vn_index['change_percent']:+.2f}%)")
        
        print("Top Gainers:")
        for stock in market_data['top_gainers'][:3]:
            print(f"   {stock['symbol']}: {stock['change_percent']:+.2f}%")
    else:
        print("FAILED to get market overview")
    
    # Test historical data
    print("\nTesting historical data (HPG)...")
    hist_data = await api.get_historical_data('HPG', days=5)
    if hist_data:
        print(f"SUCCESS Got {len(hist_data)} days of historical data for HPG")
        for day in hist_data[-3:]:  # Show last 3 days
            print(f"   {day['date']}: {day['price']:,.0f} VND ({day['change_percent']:+.2f}%)")
    else:
        print("FAILED to get historical data")

if __name__ == "__main__":
    asyncio.run(test_vnstock())