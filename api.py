from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.concurrency import run_in_threadpool
from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI
from dataclasses import asdict
from typing import Optional, List, Dict, Any
import asyncio
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Professional FastAPI configuration
app = FastAPI(
    title="DUONG AI TRADING PRO API",
    description="Professional AI-powered stock analysis system with 6 specialized agents",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Professional CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize system with error handling
try:
    vn_api = VNStockAPI()
    main_agent = MainAgent(vn_api)
    logger.info("✅ API system initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize API system: {e}")
    vn_api = None
    main_agent = None

# Professional Pydantic models
class APIKeyRequest(BaseModel):
    api_key: str = Field(..., description="API key for authentication")

class CrewAIKeyRequest(BaseModel):
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    serper_api_key: Optional[str] = Field(None, description="Serper API key for news")

class QueryRequest(BaseModel):
    query: str = Field(..., description="User query for AI analysis")
    symbol: Optional[str] = Field("", description="Stock symbol for context")

class AnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to analyze")
    time_horizon: Optional[str] = Field("medium", description="Investment time horizon")
    risk_tolerance: Optional[int] = Field(50, description="Risk tolerance (0-100)")
    investment_amount: Optional[int] = Field(100000000, description="Investment amount in VND")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    agents: Dict[str, str]
    features: Dict[str, str]

# Professional startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting DUONG AI TRADING PRO API v2.0")
    logger.info(f"📊 VN API Status: {'✅ Ready' if vn_api else '❌ Failed'}")
    logger.info(f"🤖 Main Agent Status: {'✅ Ready' if main_agent else '❌ Failed'}")
    logger.info(f"🧠 Gemini Status: {'✅ Ready' if main_agent and main_agent.gemini_agent else '🔴 Not Configured'}")
    logger.info(f"🤖 CrewAI Status: {'✅ Ready' if main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else '🔴 Not Configured'}")
    logger.info("📚 API Documentation: http://127.0.0.1:8000/api/docs")
    logger.info("🌐 Web Interface: http://127.0.0.1:8000")

# Mount static files for professional web interface
app.mount("/static", StaticFiles(directory="static"), name="static")

# Professional root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the professional web interface"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>DUONG AI TRADING PRO</h1><p>Web interface not found. Please ensure static files are available.</p>",
            status_code=404
        )

# Professional health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive system health check"""
    agents_status = {
        "price_predictor": "ready",
        "ticker_news": "ready", 
        "market_news": "ready",
        "investment_expert": "ready",
        "risk_expert": "ready",
        "gemini_agent": "ready" if main_agent and main_agent.gemini_agent else "not_configured",
        "crewai_integration": "ready" if main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "not_configured"
    }
    
    features_status = {
        "real_news_collection": "enabled" if main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "disabled",
        "market_sentiment": "enhanced" if main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "basic",
        "ai_chatbot": "enabled" if main_agent and main_agent.gemini_agent else "disabled",
        "real_time_data": "enabled" if vn_api else "disabled"
    }
    
    return HealthResponse(
        status="healthy" if main_agent and vn_api else "degraded",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        agents=agents_status,
        features=features_status
    )

# Professional API key management
@app.post("/set-gemini-key")
async def set_gemini_key(request: APIKeyRequest):
    """Configure Gemini API key for AI chatbot functionality"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = main_agent.set_gemini_api_key(request.api_key)
        if success:
            logger.info("✅ Gemini API key configured successfully")
            return {
                "status": "success", 
                "message": "Gemini API key configured successfully",
                "features_enabled": ["AI Chatbot", "Enhanced Analysis", "Natural Language Queries"]
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid or expired API key")
    except Exception as e:
        logger.error(f"❌ Gemini API key configuration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/set-crewai-keys")
async def set_crewai_keys(request: CrewAIKeyRequest):
    """Configure CrewAI keys for real news collection and enhanced analysis"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = main_agent.set_crewai_keys(request.gemini_api_key, request.serper_api_key)
        if success:
            logger.info("✅ CrewAI integration enabled successfully")
            return {
                "status": "success", 
                "message": "CrewAI integration enabled for real news collection",
                "features": [
                    "Real stock news collection",
                    "Market overview news", 
                    "Enhanced sentiment analysis",
                    "Company information lookup",
                    "Dynamic stock symbols loading"
                ]
            }
        else:
            logger.warning("⚠️ CrewAI not available, using fallback methods")
            return {
                "status": "partial",
                "message": "CrewAI not available, using fallback methods",
                "features": ["Basic news collection", "Static stock symbols"]
            }
    except Exception as e:
        logger.error(f"❌ CrewAI configuration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Professional stock analysis endpoints
@app.post("/analyze")
async def analyze_stock(request: AnalysisRequest):
    """Comprehensive stock analysis with 6 AI agents"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(f"🔍 Starting comprehensive analysis for {request.symbol}")
        
        # Enhanced analysis with investment parameters
        result = await main_agent.analyze_stock(
            symbol=request.symbol.upper(),
            time_horizon=request.time_horizon,
            risk_tolerance=request.risk_tolerance
        )
        
        # Add metadata
        result["analysis_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "agents_used": ["PricePredictor", "TickerNews", "MarketNews", "InvestmentExpert", "RiskExpert", "StockInfo"],
            "investment_profile": {
                "time_horizon": request.time_horizon,
                "risk_tolerance": request.risk_tolerance,
                "investment_amount": request.investment_amount
            }
        }
        
        logger.info(f"✅ Analysis completed for {request.symbol}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Analysis failed for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/query")
async def process_query(request: QueryRequest):
    """AI-powered natural language query processing"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if not main_agent.gemini_agent:
        raise HTTPException(status_code=400, detail="Gemini AI not configured. Please set API key first.")
    
    try:
        logger.info(f"💬 Processing query: {request.query[:50]}...")
        
        symbol = request.symbol.upper() if request.symbol else ""
        result = await main_agent.process_query(request.query, symbol)
        
        # Add metadata
        result["query_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "processed_by": "Gemini AI",
            "context_symbol": symbol,
            "response_type": "conversational"
        }
        
        logger.info("✅ Query processed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

# Individual agent endpoints
@app.get("/predict/{symbol}")
async def predict_price(symbol: str):
    """Price prediction using PricePredictor agent"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(f"📈 Predicting price for {symbol}")
        result = await run_in_threadpool(main_agent.price_predictor.predict_price, symbol.upper())
        
        result["prediction_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "PricePredictor",
            "version": "2.0.0"
        }
        
        return result
    except Exception as e:
        logger.error(f"❌ Price prediction failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/{symbol}")
async def get_ticker_news(symbol: str, limit: int = 10):
    """Get news for specific stock ticker"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(f"📰 Fetching news for {symbol}")
        result = await run_in_threadpool(main_agent.ticker_news.get_ticker_news, symbol.upper(), limit)
        
        result["news_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "TickerNews",
            "symbol": symbol.upper(),
            "limit": limit
        }
        
        return result
    except Exception as e:
        logger.error(f"❌ News fetching failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/risk/{symbol}")
async def assess_risk(symbol: str):
    """Risk assessment using RiskExpert agent"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(f"⚠️ Assessing risk for {symbol}")
        result = await run_in_threadpool(main_agent.risk_expert.assess_risk, symbol.upper())
        
        result["risk_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "RiskExpert",
            "version": "2.0.0"
        }
        
        return result
    except Exception as e:
        logger.error(f"❌ Risk assessment failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Vietnamese market endpoints
@app.get("/vn-stock/{symbol}")
async def get_vn_stock(symbol: str):
    """Get Vietnamese stock data"""
    if not vn_api:
        raise HTTPException(status_code=503, detail="VN Stock API not initialized")
    
    try:
        logger.info(f"🇻🇳 Fetching VN stock data for {symbol}")
        result = await vn_api.get_stock_data(symbol.upper())
        
        if result:
            data = asdict(result)
            data["data_metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "source": "VNStock API",
                "market": "Vietnam"
            }
            return data
        else:
            # Return mock data with clear indication
            mock_data = vn_api._generate_mock_data(symbol.upper())
            data = asdict(mock_data)
            data["data_metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "source": "Mock Data",
                "market": "Vietnam",
                "warning": "This is demo data for testing purposes"
            }
            return data
            
    except Exception as e:
        logger.error(f"❌ VN stock data failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vn-market")
async def get_vn_market():
    """Get Vietnamese market overview"""
    if not vn_api:
        raise HTTPException(status_code=503, detail="VN Stock API not initialized")
    
    try:
        logger.info("🇻🇳 Fetching VN market overview")
        result = await vn_api.get_market_overview()
        
        result["market_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "source": "VNStock API",
            "market": "Vietnam",
            "indices": ["VN-Index", "VN30-Index", "HN-Index"]
        }
        
        return result
    except Exception as e:
        logger.error(f"❌ VN market overview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vn-symbols")
async def get_vn_symbols():
    """Get available Vietnamese stock symbols"""
    if not vn_api:
        raise HTTPException(status_code=503, detail="VN Stock API not initialized")
    
    try:
        logger.info("📋 Fetching available VN symbols")
        result = await vn_api.get_available_symbols()
        
        # Add metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "total_symbols": len(result),
            "data_source": result[0].get('data_source', 'Unknown') if result else 'Unknown',
            "sectors": list(set(s.get('sector', 'Other') for s in result))
        }
        
        return {
            "symbols": result,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"❌ VN symbols fetching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market news endpoints
@app.get("/market-news")
async def get_market_news():
    """Get general market news"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("🌍 Fetching market news")
        result = await run_in_threadpool(main_agent.market_news.get_market_news)
        
        result["news_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "MarketNews",
            "type": "market_overview"
        }
        
        return result
    except Exception as e:
        logger.error(f"❌ Market news fetching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/international-news")
async def get_international_news():
    """Get international market news"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("🌏 Fetching international news")
        result = await main_agent.get_international_news()
        
        result["news_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "InternationalMarketNews",
            "type": "international_market"
        }
        
        return result
    except Exception as e:
        logger.error(f"❌ International news fetching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced company information endpoint
@app.get("/company/{symbol}")
async def get_company_info(symbol: str):
    """Get detailed company information using CrewAI"""
    if not main_agent:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if not (main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled):
        raise HTTPException(status_code=400, detail="CrewAI not configured. Enhanced company info not available.")
    
    try:
        logger.info(f"🏢 Fetching company info for {symbol}")
        
        from agents.enhanced_news_agent import create_enhanced_news_agent
        enhanced_agent = create_enhanced_news_agent(
            main_agent.gemini_agent.api_key if main_agent.gemini_agent else None
        )
        
        result = await enhanced_agent.get_stock_news(symbol.upper())
        
        result["company_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "EnhancedNewsAgent",
            "data_source": "CrewAI",
            "symbol": symbol.upper()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Company info failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System status endpoint
@app.get("/status")
async def get_system_status():
    """Get detailed system status"""
    return {
        "system": {
            "status": "operational",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        },
        "services": {
            "main_agent": "ready" if main_agent else "failed",
            "vn_api": "ready" if vn_api else "failed",
            "gemini_ai": "ready" if main_agent and main_agent.gemini_agent else "not_configured",
            "crewai": "ready" if main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled else "not_configured"
        },
        "agents": {
            "price_predictor": "active",
            "ticker_news": "active",
            "market_news": "active", 
            "investment_expert": "active",
            "risk_expert": "active",
            "stock_info": "active"
        },
        "features": {
            "real_time_data": vn_api is not None,
            "ai_chatbot": main_agent and main_agent.gemini_agent is not None,
            "real_news": main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled,
            "company_analysis": main_agent and hasattr(main_agent.vn_api, 'crewai_collector') and main_agent.vn_api.crewai_collector and main_agent.vn_api.crewai_collector.enabled
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "timestamp": datetime.now().isoformat(),
            "available_endpoints": [
                "/health", "/analyze", "/query", "/predict/{symbol}",
                "/news/{symbol}", "/risk/{symbol}", "/vn-market", "/vn-symbols"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Professional shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down DUONG AI TRADING PRO API")
    logger.info("👋 Thank you for using our professional trading system!")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting DUONG AI TRADING PRO API Server...")
    print("📚 API Documentation: http://127.0.0.1:8000/api/docs")
    print("🌐 Web Interface: http://127.0.0.1:8000")
    print("⚡ Professional trading system ready!")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )