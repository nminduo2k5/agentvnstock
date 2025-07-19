from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
from main_agent import MainAgent
import sys
import os
from src.data.vn_stock_api import VNStockAPI
from dataclasses import asdict

# Thêm dòng này để lấy model từ biến môi trường
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

app = FastAPI(
    title="AI Trading Team Vietnam API",
    description="6 AI Agents + Gemini Chatbot API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize with error handling (without Gemini API key)
try:
    vn_api = VNStockAPI()
    main_agent = MainAgent(vn_api=vn_api)  # No Gemini API key initially
    print("✅ API initialized successfully (Gemini not configured)")
except Exception as e:
    print(f"❌ Failed to initialize API: {e}")
    vn_api = None
    main_agent = None

# API key management
class APIKeyRequest(BaseModel):
    api_key: str

class CrewAIKeyRequest(BaseModel):
    gemini_api_key: str
    serper_api_key: str = None

@app.post("/set-gemini-key")
async def set_gemini_key(request: APIKeyRequest):
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = main_agent.set_gemini_api_key(request.api_key)
        if success:
            return {"status": "success", "message": "Gemini API key set successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid API key")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/set-crewai-keys")
async def set_crewai_keys(request: CrewAIKeyRequest):
    """Set CrewAI keys for real news collection"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = main_agent.set_crewai_keys(request.gemini_api_key, request.serper_api_key)
        if success:
            return {
                "status": "success", 
                "message": "CrewAI integration enabled for real news collection",
                "features": ["Real stock news", "Market overview news", "Sentiment analysis"]
            }
        else:
            return {
                "status": "partial",
                "message": "CrewAI not available, using fallback methods"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str
    symbol: str = ""

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting AI Trading Team Vietnam API...")
    print(f"📊 VN API Status: {'✅ Ready' if vn_api else '❌ Failed'}")
    print(f"🤖 Main Agent Status: {'✅ Ready' if main_agent else '❌ Failed'}")
    print(f"🧠 Gemini Status: {'✅ Ready' if main_agent and main_agent.gemini_agent else '🔴 Not Configured'}")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("🔑 Set Gemini Key: POST /set-gemini-key")
    print("🤖 Set CrewAI Keys: POST /set-crewai-keys")
    print("📰 CrewAI enables real news collection from Vietnamese sources")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "vn_api": "ready" if vn_api else "failed",
        "main_agent": "ready" if main_agent else "failed",
        "agents": {
            "price_predictor": "ready",
            "ticker_news": "ready", 
            "market_news": "ready",
            "investment_expert": "ready",
            "risk_expert": "ready",
            "gemini_agent": "ready" if main_agent and main_agent.gemini_agent else "not_configured",
            "crewai_integration": "ready" if main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "not_configured"
        },
        "features": {
            "real_news_collection": "enabled" if main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "disabled",
            "market_sentiment": "enhanced" if main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "basic"
        }
    }

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/analyze")
async def analyze_stock(symbol: str):
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await main_agent.analyze_stock(symbol.upper())
        return result
    except Exception as e:
        print(f"Error in analyze_stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def process_query(request: QueryRequest):
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        symbol = request.symbol.upper() if request.symbol else ""
        result = await main_agent.process_query(request.query, symbol)
        return result
    except Exception as e:
        print(f"Error in process_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market")
async def get_market_overview():
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await main_agent.get_market_overview()
        return result
    except Exception as e:
        print(f"Error in get_market_overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/{symbol}")
async def predict_price(symbol: str):
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await run_in_threadpool(main_agent.price_predictor.predict_price, symbol.upper())
        return result
    except Exception as e:
        print(f"Error in predict_price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/{symbol}")
async def get_ticker_news(symbol: str):
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await run_in_threadpool(main_agent.ticker_news.get_ticker_news, symbol.upper())
        return result
    except Exception as e:
        print(f"Error in get_ticker_news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/risk/{symbol}")
async def assess_risk(symbol: str):
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await run_in_threadpool(main_agent.risk_expert.assess_risk, symbol.upper())
        return result
    except Exception as e:
        print(f"Error in assess_risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vn-stock/{symbol}")
async def get_vn_stock(symbol: str):
    if not vn_api:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await vn_api.get_stock_data(symbol.upper())
        if result:
            return asdict(result)
        else:
            mock_data = vn_api._generate_mock_data(symbol.upper())
            return asdict(mock_data)
    except Exception as e:
        print(f"Error in get_vn_stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vn-market")
async def get_vn_market():
    if not vn_api:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await vn_api.get_market_overview()
        return result
    except Exception as e:
        print(f"Error in get_vn_market: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vn-symbols")
async def get_vn_symbols():
    if not vn_api:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await vn_api.get_available_symbols()
        return result
    except Exception as e:
        print(f"Error in get_vn_symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Company Search API endpoints
@app.get("/search/company/{company_name}")
async def search_company(company_name: str):
    """Search company by name"""
    try:
        from src.data.company_search_api import get_company_search_api
        company_api = get_company_search_api()
        result = await company_api.search_company(company_name)
        return result
    except Exception as e:
        print(f"Error in search_company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/symbol/{symbol}")
async def search_by_symbol(symbol: str):
    """Get company info by symbol"""
    try:
        from src.data.company_search_api import get_company_search_api
        company_api = get_company_search_api()
        result = await company_api.get_company_by_symbol(symbol)
        return result
    except Exception as e:
        print(f"Error in search_by_symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/sector/{sector}")
async def search_by_sector(sector: str):
    """Search companies by sector"""
    try:
        from src.data.company_search_api import get_company_search_api
        company_api = get_company_search_api()
        result = await company_api.search_companies_by_sector(sector)
        return result
    except Exception as e:
        print(f"Error in search_by_sector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# International News API endpoints
@app.get("/international-news/{keyword}")
async def get_international_news(keyword: str, country: str = "US", limit: int = 5):
    """Get international news by keyword"""
    try:
        from src.data.crewai_collector import get_crewai_collector
        collector = get_crewai_collector()
        result = await collector.get_international_news(keyword, country, limit)
        return result
    except Exception as e:
        print(f"Error in get_international_news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/enhanced-news/{symbol}")
async def get_enhanced_news(symbol: str, limit: int = 5):
    """Get enhanced news using CrewAI"""
    try:
        from src.data.crewai_collector import get_crewai_collector
        collector = get_crewai_collector()
        result = await collector.get_stock_news(symbol, limit)
        return result
    except Exception as e:
        print(f"Error in get_enhanced_news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-overview-news")
async def get_market_overview_news():
    """Get market overview news using CrewAI"""
    try:
        from src.data.crewai_collector import get_crewai_collector
        collector = get_crewai_collector()
        result = await collector.get_market_overview_news()
        return result
    except Exception as e:
        print(f"Error in get_market_overview_news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-report/{symbol}")
async def generate_investment_report(symbol: str, time_horizon: str = "Trung hạn", risk_tolerance: int = 50):
    """Generate comprehensive investment report"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        # First analyze the stock
        analysis_result = await main_agent.analyze_stock(symbol.upper(), time_horizon, risk_tolerance)
        
        if analysis_result.get('error'):
            raise HTTPException(status_code=400, detail=analysis_result['error'])
        
        # Generate report files
        report_result = await main_agent.generate_and_save_report(analysis_result, symbol.upper(), time_horizon, risk_tolerance)
        
        return report_result
    except Exception as e:
        print(f"Error in generate_investment_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/company-news/{symbol}")
async def get_company_news(symbol: str):
    """Get company information and news by stock symbol"""
    try:
        from agents.enhanced_news_agent import create_enhanced_news_agent
        enhanced_agent = create_enhanced_news_agent()
        result = await enhanced_agent.get_stock_news(symbol.upper())
        return result
    except Exception as e:
        print(f"Error in get_company_news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sector-companies/{sector}")
async def get_sector_companies(sector: str):
    """Get companies by sector"""
    try:
        from agents.enhanced_news_agent import create_enhanced_news_agent
        enhanced_agent = create_enhanced_news_agent()
        result = await enhanced_agent.get_company_by_sector(sector)
        return result
    except Exception as e:
        print(f"Error in get_sector_companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)