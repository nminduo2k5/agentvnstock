from agents.price_predictor import PricePredictor
from agents.ticker_news import TickerNews
from agents.market_news import MarketNews
from agents.investment_expert import InvestmentExpert
from agents.risk_expert import RiskExpert
from gemini_agent import GeminiAgent
import sys
from fastapi.concurrency import run_in_threadpool
import os
from src.data.vn_stock_api import VNStockAPI
import asyncio

class MainAgent:
    def __init__(self, vn_api: VNStockAPI):
        self.price_predictor = PricePredictor()
        self.ticker_news = TickerNews()
        self.market_news = MarketNews()
        self.investment_expert = InvestmentExpert()
        self.risk_expert = RiskExpert()
        self.vn_api = vn_api # Sử dụng instance được truyền vào
        
        self.gemini_agent = GeminiAgent()
    
    async def analyze_stock(self, symbol: str):
        """Phân tích toàn diện một mã cổ phiếu"""
        tasks = {}

        # Check if VN stock first
        if self.vn_api.is_vn_stock(symbol.upper()):
            tasks['vn_stock_data'] = self.vn_api.get_stock_data(symbol)
            tasks['ticker_news'] = self.vn_api.get_news_sentiment(symbol)
            market_type = 'Vietnam'
        else:
            # Chạy các hàm đồng bộ trong thread pool
            tasks['ticker_news'] = run_in_threadpool(self.ticker_news.get_ticker_news, symbol)
            tasks['investment_analysis'] = run_in_threadpool(self.investment_expert.analyze_stock, symbol)
            market_type = 'International'

        # Các tác vụ chung cho cả hai thị trường, chạy trong thread pool
        tasks['price_prediction'] = run_in_threadpool(self.price_predictor.predict_price, symbol)
        tasks['risk_assessment'] = run_in_threadpool(self.risk_expert.assess_risk, symbol)

        # Thực thi tất cả các tác vụ bất đồng bộ và đồng bộ (trong thread pool) một cách song song
        task_results = await asyncio.gather(*tasks.values())

        # Ánh xạ kết quả trở lại
        results = dict(zip(tasks.keys(), task_results))
        results['market_type'] = market_type

        return results
    
    async def get_market_overview(self):
        """Lấy tổng quan thị trường"""
        # Chạy tác vụ đồng bộ và bất đồng bộ song song
        international_task = run_in_threadpool(self.market_news.get_market_news)
        vietnam_task = self.vn_api.get_market_overview()

        international_result, vietnam_result = await asyncio.gather(international_task, vietnam_task)

        results = {
            'international_market': international_result,
            'vietnam_market': vietnam_result
        }
        return results
    
    async def process_query(self, query: str, symbol: str = ""):
        """Xử lý truy vấn từ người dùng với AI response"""
        query_lower = query.lower()
        
        # Get relevant data first
        data = None
        if symbol and symbol.strip():
            if self.vn_api.is_vn_stock(symbol.upper()):
                # Chạy song song các tác vụ
                vn_data_task = self.vn_api.get_stock_data(symbol)
                prediction_task = run_in_threadpool(self.price_predictor.predict_price, symbol)
                risk_task = run_in_threadpool(self.risk_expert.assess_risk, symbol)
                vn_data, prediction, risk_data = await asyncio.gather(vn_data_task, prediction_task, risk_task)
                data = {"vn_stock_data": vn_data, "price_prediction": prediction, "risk_assessment": risk_data}
            else:
                prediction_task = run_in_threadpool(self.price_predictor.predict_price, symbol)
                analysis_task = run_in_threadpool(self.investment_expert.analyze_stock, symbol)
                risk_task = run_in_threadpool(self.risk_expert.assess_risk, symbol)
                prediction, analysis, risk_data = await asyncio.gather(prediction_task, analysis_task, risk_task)
                data = {"price_prediction": prediction, "investment_analysis": analysis, "risk_assessment": risk_data}
        
        # Use Gemini to generate expert advice
        gemini_response = await self.gemini_agent.generate_expert_advice(query, symbol, data)

        # Backend chỉ trả về dữ liệu JSON, không tạo HTML.
        # Frontend sẽ chịu trách nhiệm render.
        response = {
            "query": query,
            "symbol": symbol,
            "response_type": "conversational",
            # Truyền dữ liệu thô từ Gemini về frontend
            "expert_advice": gemini_response.get("expert_advice", "Không có phân tích từ chuyên gia."),
            "recommendations": gemini_response.get("recommendations", []),
            "data": data,
        }
        
        return response
