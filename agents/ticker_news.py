import yfinance as yf
import requests

class TickerNews:
    def __init__(self):
        self.name = "Ticker News Agent"
    
    def get_ticker_news(self, symbol: str, limit: int = 5):
        try:
            # Logic kiểm tra cổ phiếu VN đã được chuyển ra MainAgent.
            # Agent này giờ chỉ tập trung vào cổ phiếu quốc tế qua Yahoo Finance.
            # US/International stocks - use Yahoo Finance
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return {"error": f"No news found for {symbol}"}
            
            formatted_news = []
            for item in news[:limit]:
                formatted_news.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", ""),
                    "published": item.get("providerPublishTime", "")
                })
            
            return {
                "symbol": symbol,
                "news_count": len(formatted_news),
                "news": formatted_news,
                "market": "International"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_vn_mock_news(self, symbol: str, limit: int = 5):
        """Generate mock news for VN stocks"""
        import random
        from datetime import datetime, timedelta
        
        # Sample VN news templates
        news_templates = [
            f"{symbol} công bố kết quả kinh doanh quý III tăng trưởng tích cực",
            f"Cổ đông lớn của {symbol} đăng ký mua thêm 5 triệu cổ phiếu",
            f"{symbol} được chấp thuận tăng vốn điều lệ lên 50,000 tỷ đồng",
            f"Dự án mới của {symbol} tại TP.HCM chính thức khởi công",
            f"{symbol} ký kết hợp tác chiến lược với đối tác nước ngoài",
            f"HĐQT {symbol} thông qua phương án trả cổ tức 15% bằng tiền mặt",
            f"{symbol} dự kiến phát hành 100 triệu cổ phiếu để tăng vốn",
            f"Lợi nhuận 9 tháng của {symbol} đạt 8,500 tỷ đồng, tăng 12%"
        ]
        
        # Generate random news
        selected_news = random.sample(news_templates, min(limit, len(news_templates)))
        
        formatted_news = []
        for i, title in enumerate(selected_news):
            pub_time = datetime.now() - timedelta(hours=random.randint(1, 72))
            formatted_news.append({
                "title": title,
                "publisher": random.choice(["CafeF", "VnExpress", "Đầu tư", "VietStock", "Báo Kinh tế"]),
                "link": f"https://example-vn-news.com/{symbol.lower()}-news-{i+1}",
                "published": pub_time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": f"Tin tức mới nhất về {symbol} từ thị trường chứng khoán Việt Nam"
            })
        
        return {
            "symbol": symbol,
            "news_count": len(formatted_news),
            "news": formatted_news,
            "market": "Vietnam",
            "source": "VN Financial News"
        }