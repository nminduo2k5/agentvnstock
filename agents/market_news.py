import requests
import yfinance as yf

class MarketNews:
    def __init__(self):
        self.name = "Market News Agent"
    
    def get_market_news(self, category: str = "general"):
        try:
            # Get news from major indices
            indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
            all_news = []
            
            for index in indices:
                ticker = yf.Ticker(index)
                news = ticker.news
                
                for item in news[:3]:  # Top 3 news per index
                    all_news.append({
                        "title": item.get("title", ""),
                        "publisher": item.get("publisher", ""),
                        "link": item.get("link", ""),
                        "published": item.get("providerPublishTime", ""),
                        "source_index": index
                    })
            
            return {
                "category": category,
                "news_count": len(all_news),
                "news": all_news[:10]  # Return top 10
            }
        except Exception as e:
            return {"error": str(e)}