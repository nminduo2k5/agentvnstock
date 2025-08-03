from agents.price_predictor import PricePredictor
from agents.ticker_news import TickerNews
from agents.market_news import MarketNews
from agents.investment_expert import InvestmentExpert
from agents.risk_expert import RiskExpert
from agents.stock_info import StockInfoDisplay
from agents.international_news import InternationalMarketNews
from gemini_agent import UnifiedAIAgent
from src.data.vn_stock_api import VNStockAPI
from src.utils.error_handler import handle_async_errors, AgentErrorHandler, validate_symbol
from fastapi.concurrency import run_in_threadpool
import asyncio
import logging

logger = logging.getLogger(__name__)

class MainAgent:
    def __init__(self, vn_api: VNStockAPI, gemini_api_key: str = None, serper_api_key: str = None):
        self.vn_api = vn_api
        self.stock_info = StockInfoDisplay(vn_api)
        self.price_predictor = PricePredictor(vn_api, self.stock_info)
        self.ticker_news = TickerNews()
        self.market_news = MarketNews()
        self.investment_expert = InvestmentExpert(vn_api)
        self.risk_expert = RiskExpert(vn_api)
        self.international_news = InternationalMarketNews()
        
        # Initialize Unified AI Agent with user-provided API key
        self.gemini_agent = None
        if gemini_api_key:
            try:
                self.gemini_agent = UnifiedAIAgent(
                    gemini_api_key=gemini_api_key
                )
                connection_results = self.gemini_agent.test_connection()
                active_models = [model for model, status in connection_results.items() if status]
                model_info = self.gemini_agent.get_model_info()
                print(f"✅ AI Models initialized: {', '.join(active_models)} ({model_info.get('current_model', 'Unknown')})")
            except Exception as e:
                print(f"⚠️ AI initialization failed: {e}")
                self.gemini_agent = None
        
        # Update VN API with CrewAI keys
        if gemini_api_key or serper_api_key:
            try:
                self.vn_api.set_crewai_keys(gemini_api_key, serper_api_key)
                print("✅ CrewAI integration enabled for real news")
            except Exception as e:
                print(f"⚠️ CrewAI setup failed: {e}")
        
        # Pass AI agent to other agents for enhanced capabilities
        self._integrate_ai_with_agents()
    
    def _integrate_ai_with_agents(self):
        """Integrate AI capabilities with all agents"""
        if self.gemini_agent:
            # Pass AI agent to agents that can benefit from it
            if hasattr(self.price_predictor, 'set_ai_agent'):
                self.price_predictor.set_ai_agent(self.gemini_agent)
            if hasattr(self.investment_expert, 'set_ai_agent'):
                self.investment_expert.set_ai_agent(self.gemini_agent)
            if hasattr(self.risk_expert, 'set_ai_agent'):
                self.risk_expert.set_ai_agent(self.gemini_agent)
            if hasattr(self.ticker_news, 'set_ai_agent'):
                self.ticker_news.set_ai_agent(self.gemini_agent)
            if hasattr(self.market_news, 'set_ai_agent'):
                self.market_news.set_ai_agent(self.gemini_agent)
            if hasattr(self.international_news, 'set_ai_agent'):
                self.international_news.set_ai_agent(self.gemini_agent)
    
    def set_gemini_api_key(self, api_key: str):
        """Set or update Gemini API key"""
        try:
            # Create new agent
            self.gemini_agent = UnifiedAIAgent(gemini_api_key=api_key)
            
            connection_results = self.gemini_agent.test_connection()
            model_info = self.gemini_agent.get_model_info()
            
            if model_info['is_active']:
                print(f"✅ Gemini API key updated successfully ({model_info['current_model']})")
                self._integrate_ai_with_agents()
                return True
            else:
                print("❌ Gemini API key invalid or model not available")
                self.gemini_agent = None
                return False
        except Exception as e:
            print(f"❌ Failed to set Gemini API key: {e}")
            self.gemini_agent = None
            return False
    

    
    def set_crewai_keys(self, gemini_api_key: str, serper_api_key: str = None):
        """Set CrewAI API keys for real news collection with Gemini AI"""
        try:
            # Update AI agents (only Gemini)
            if gemini_api_key:
                if self.gemini_agent:
                    # Update existing agent with new key
                    current_gemini = getattr(self.gemini_agent, 'gemini_api_key', None)
                    
                    self.gemini_agent = UnifiedAIAgent(
                        gemini_api_key=gemini_api_key or current_gemini
                    )
                else:
                    # Create new agent
                    self.gemini_agent = UnifiedAIAgent(
                        gemini_api_key=gemini_api_key
                    )
                
                connection_results = self.gemini_agent.test_connection()
                active_models = [model for model, status in connection_results.items() if status]
                model_info = self.gemini_agent.get_model_info()
                print(f"✅ AI Models updated: {', '.join(active_models)} ({model_info.get('current_model', 'Unknown')})")
                self._integrate_ai_with_agents()
            
            # Update VN API CrewAI integration
            success = self.vn_api.set_crewai_keys(gemini_api_key, serper_api_key)
            
            if success:
                print("✅ CrewAI integration updated successfully")
                return True
            else:
                print("⚠️ CrewAI integration not available")
                return False
                
        except Exception as e:
            print(f"❌ Failed to set CrewAI keys: {e}")
            return False
    
    @handle_async_errors(default_return={"error": "Lỗi hệ thống khi phân tích cổ phiếu"})
    async def analyze_stock(self, symbol: str):
        """Phân tích toàn diện một mã cổ phiếu"""
        if not symbol or not validate_symbol(symbol):
            return {"error": "Mã cổ phiếu không hợp lệ"}
            
        symbol = symbol.upper().strip()
        logger.info(f"Starting comprehensive analysis for {symbol}")
        
        tasks = {}
        results = {"symbol": symbol}

        try:
            # Check if VN stock first
            if self.vn_api.is_vn_stock(symbol):
                logger.info(f"{symbol} is Vietnamese stock, using VN API")
                tasks['vn_stock_data'] = self.vn_api.get_stock_data(symbol)
                tasks['ticker_news'] = self.vn_api.get_news_sentiment(symbol)
                tasks['detailed_stock_info'] = self.stock_info.get_detailed_stock_data(symbol)
                market_type = 'Vietnam'
            else:
                # Kiểm tra xem có phải là mã hợp lệ cho international market không
                if self._is_valid_international_symbol(symbol):
                    logger.info(f"{symbol} is international stock, using international APIs")
                    tasks['ticker_news'] = run_in_threadpool(self._safe_get_ticker_news, symbol)
                    tasks['investment_analysis'] = run_in_threadpool(self._safe_get_investment_analysis, symbol)
                    market_type = 'International'
                else:
                    logger.warning(f"{symbol} is not a valid stock symbol")
                    return {"error": f"Mã {symbol} không hợp lệ hoặc không được hỗ trợ"}

            # Các tác vụ chung cho cả hai thị trường
            tasks['price_prediction'] = run_in_threadpool(self._safe_get_price_prediction, symbol)
            tasks['risk_assessment'] = run_in_threadpool(self._safe_get_risk_assessment, symbol)

            # Thực thi tất cả các tác vụ song song
            task_results = await asyncio.gather(*tasks.values(), return_exceptions=True)

            # Ánh xạ kết quả với error handling
            for key, result in zip(tasks.keys(), task_results):
                if isinstance(result, Exception):
                    logger.error(f"Error in {key} for {symbol}: {result}")
                    results[key] = self._get_error_fallback(key, symbol, result)
                else:
                    results[key] = result
            
            results['market_type'] = market_type
            results['analysis_timestamp'] = asyncio.get_event_loop().time()
            
            logger.info(f"Completed analysis for {symbol}")
            return results
            
        except Exception as e:
            logger.error(f"Critical error in analyze_stock for {symbol}: {e}")
            return {"error": f"Lỗi nghiêm trọng khi phân tích {symbol}: {str(e)}"}
    
    @handle_async_errors(default_return={"error": "Lỗi khi lấy tổng quan thị trường"})
    async def get_market_overview(self):
        """Lấy tổng quan thị trường"""
        logger.info("Getting market overview")
        
        try:
            # Chạy tác vụ đồng bộ và bất đồng bộ song song với error handling
            international_task = run_in_threadpool(self._safe_get_international_market_news)
            vietnam_task = self.vn_api.get_market_overview()

            international_result, vietnam_result = await asyncio.gather(
                international_task, vietnam_task, return_exceptions=True
            )
            
            # Handle results with error checking
            results = {}
            
            if isinstance(international_result, Exception):
                logger.error(f"International market error: {international_result}")
                results['international_market'] = {"error": "Lỗi lấy tin tức thị trường quốc tế"}
            else:
                results['international_market'] = international_result
            
            if isinstance(vietnam_result, Exception):
                logger.error(f"Vietnam market error: {vietnam_result}")
                results['vietnam_market'] = {"error": "Lỗi lấy dữ liệu thị trường Việt Nam"}
            else:
                results['vietnam_market'] = vietnam_result
            
            results['timestamp'] = asyncio.get_event_loop().time()
            return results
            
        except Exception as e:
            logger.error(f"Critical error in get_market_overview: {e}")
            return {"error": f"Lỗi nghiêm trọng khi lấy tổng quan thị trường: {str(e)}"}
    
    @handle_async_errors(default_return={"error": "Lỗi xử lý truy vấn"})
    async def process_query(self, query: str, symbol: str = ""):
        """Xử lý truy vấn từ người dùng với AI response"""
        if not query or not query.strip():
            return {"error": "Vui lòng nhập câu hỏi"}
        
        query = query.strip()
        symbol = symbol.strip().upper() if symbol else ""
        
        logger.info(f"Processing query: '{query}' for symbol: '{symbol}'")
        
        try:
            # Get relevant data first with error handling
            data = None
            if symbol and validate_symbol(symbol):
                if self.vn_api.is_vn_stock(symbol):
                    logger.info(f"Getting VN data for {symbol}")
                    # Chạy song song các tác vụ với error handling
                    tasks = [
                        self.vn_api.get_stock_data(symbol),
                        run_in_threadpool(self._safe_get_price_prediction, symbol),
                        run_in_threadpool(self._safe_get_risk_assessment, symbol)
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    data = {
                        "vn_stock_data": results[0] if not isinstance(results[0], Exception) else None,
                        "price_prediction": results[1] if not isinstance(results[1], Exception) else None,
                        "risk_assessment": results[2] if not isinstance(results[2], Exception) else None
                    }
                else:
                    logger.info(f"Getting international data for {symbol}")
                    tasks = [
                        run_in_threadpool(self._safe_get_price_prediction, symbol),
                        run_in_threadpool(self._safe_get_investment_analysis, symbol),
                        run_in_threadpool(self._safe_get_risk_assessment, symbol)
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    data = {
                        "price_prediction": results[0] if not isinstance(results[0], Exception) else None,
                        "investment_analysis": results[1] if not isinstance(results[1], Exception) else None,
                        "risk_assessment": results[2] if not isinstance(results[2], Exception) else None
                    }
            
            # Use Gemini to generate expert advice
            if self.gemini_agent:
                try:
                    gemini_response = await run_in_threadpool(
                        self.gemini_agent.generate_expert_advice, query, symbol, data
                    )
                except Exception as e:
                    logger.error(f"Gemini error: {e}")
                    gemini_response = {
                        "expert_advice": f"Lỗi Gemini AI: {str(e)}",
                        "recommendations": ["Thử lại sau", "Kiểm tra API key"]
                    }
            else:
                gemini_response = {
                    "expert_advice": "Gemini AI chưa được khởi tạo. Vui lòng nhập API key.",
                    "recommendations": ["Nhập Google API key để sử dụng Gemini AI"]
                }

            response = {
                "query": query,
                "symbol": symbol,
                "response_type": "conversational",
                "expert_advice": gemini_response.get("expert_advice", "Không có phân tích từ chuyên gia."),
                "recommendations": gemini_response.get("recommendations", []),
                "data": data,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            logger.info(f"Successfully processed query for {symbol}")
            return response
            
        except Exception as e:
            logger.error(f"Critical error in process_query: {e}")
            return {"error": f"Lỗi nghiêm trọng khi xử lý truy vấn: {str(e)}"}

    
    # Helper methods với error handling
    def _safe_get_price_prediction(self, symbol: str):
        """Safely get price prediction with LSTM enhancement"""
        try:
            # Use LSTM-enhanced prediction if available
            if hasattr(self.price_predictor, 'lstm_predictor') and self.price_predictor.lstm_predictor:
                return self.price_predictor.predict_price_enhanced(symbol)
            else:
                return self.price_predictor.predict_price(symbol)
        except Exception as e:
            return AgentErrorHandler.handle_prediction_error(symbol, e)
    
    def _safe_get_ticker_news(self, symbol: str, limit: int = 10):
        """Safely get ticker news"""
        try:
            return self.ticker_news.get_ticker_news(symbol, limit)
        except Exception as e:
            return AgentErrorHandler.handle_news_error(symbol, e)
    
    @handle_async_errors(default_return={"error": "Lỗi hệ thống khi lấy tin tức cổ phiếu"})
    async def get_ticker_news_enhanced(self, symbol: str, limit: int = 15):
        """Get enhanced ticker news with detailed stats"""
        try:
            result = await run_in_threadpool(self._safe_get_ticker_news, symbol, limit)
            return result
        except Exception as e:
            logger.error(f"Ticker news enhanced error: {e}")
            return {"error": f"Lỗi lấy tin tức cổ phiếu {symbol}: {str(e)}"}
    
    def _safe_get_investment_analysis(self, symbol: str):
        """Safely get investment analysis"""
        try:
            return self.investment_expert.analyze_stock(symbol)
        except Exception as e:
            return {"error": f"Lỗi phân tích đầu tư cho {symbol}: {str(e)}"}
    
    def _safe_get_risk_assessment(self, symbol: str):
        """Safely get risk assessment"""
        try:
            return self.risk_expert.assess_risk(symbol)
        except Exception as e:
            return AgentErrorHandler.handle_risk_error(symbol, e)
    
    def _safe_get_market_news(self):
        """Safely get market news"""
        try:
            return self.market_news.get_market_news()
        except Exception as e:
            logger.error(f"Market news error: {e}")
            return {"error": f"Lỗi lấy tin tức thị trường: {str(e)}"}
    
    def _safe_get_international_market_news(self):
        """Safely get international market news"""
        try:
            return self.international_news.get_international_news()
        except Exception as e:
            logger.error(f"International market news error: {e}")
            return {"error": f"Lỗi lấy tin tức thị trường quốc tế: {str(e)}"}
    
    @handle_async_errors(default_return={"error": "Lỗi hệ thống khi lấy tin tức quốc tế"})
    async def get_international_news(self):
        """Get international market news"""
        try:
            result = await run_in_threadpool(self._safe_get_international_market_news)
            return result
        except Exception as e:
            logger.error(f"International news async error: {e}")
            return {"error": f"Lỗi lấy tin tức thị trường quốc tế: {str(e)}"}
    
    def _get_error_fallback(self, task_name: str, symbol: str, error: Exception):
        """Get appropriate error fallback based on task type"""
        fallbacks = {
            'price_prediction': AgentErrorHandler.handle_prediction_error(symbol, error),
            'ticker_news': AgentErrorHandler.handle_news_error(symbol, error),
            'risk_assessment': AgentErrorHandler.handle_risk_error(symbol, error),
            'investment_analysis': {"error": f"Lỗi phân tích đầu tư: {str(error)}"},
            'vn_stock_data': {"error": f"Lỗi dữ liệu VN: {str(error)}"},
            'detailed_stock_info': {"error": f"Lỗi thông tin chi tiết: {str(error)}"}
        }
        return fallbacks.get(task_name, {"error": f"Lỗi {task_name}: {str(error)}"})
    
    def _is_valid_international_symbol(self, symbol: str) -> bool:
        """Kiểm tra xem có phải là mã international hợp lệ không"""
        if not symbol or len(symbol) < 1:
            return False
        
        symbol = symbol.upper().strip()
        
        # Loại bỏ các mã không hợp lệ
        invalid_patterns = [
            'X20', 'X21', 'X22', 'X23', 'X24', 'X25',  # Các mã lạ
            'TEST', 'DEMO', 'NULL', 'NONE'
        ]
        
        if symbol in invalid_patterns:
            return False
        
        # Kiểm tra pattern hợp lệ cho US stocks
        if len(symbol) >= 1 and len(symbol) <= 5:
            # Chấp nhận các mã có chữ và số
            if symbol.replace('.', '').replace('-', '').isalnum():
                return True
        
        return False
    
    async def get_detailed_stock_info(self, symbol: str):
        """Lấy thông tin chi tiết cổ phiếu từ stock_info module"""
        try:
            return await self.stock_info.get_detailed_stock_data(symbol)
        except Exception as e:
            logger.error(f"Error getting detailed stock info for {symbol}: {e}")
            return {"error": f"Lỗi lấy thông tin chi tiết: {str(e)}"}
    
    def display_stock_header(self, stock_data, current_time: str):
        """Display stock header - delegate to stock_info"""
        return self.stock_info.display_stock_header(stock_data, current_time)
    
    def display_detailed_metrics(self, detailed_data):
        """Display detailed metrics - delegate to stock_info"""
        return self.stock_info.display_detailed_metrics(detailed_data)
    
    def display_financial_ratios(self, detailed_data):
        """Display financial ratios - delegate to stock_info"""
        return self.stock_info.display_financial_ratios(detailed_data)
    
    def display_price_chart(self, price_history, symbol):
        """Display price chart - delegate to stock_info"""
        return self.stock_info.display_price_chart(price_history, symbol)
