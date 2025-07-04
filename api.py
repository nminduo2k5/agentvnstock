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

app = FastAPI(title="Stock Analysis Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vn_api = VNStockAPI()
main_agent = MainAgent(vn_api=vn_api) # Dependency Injection: Dùng chung 1 instance vn_api

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str
    symbol: str = ""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/analyze")
async def analyze_stock(symbol: str):
    try:
        result = await main_agent.analyze_stock(symbol.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        # Gọi đúng hàm nếu không có tham số model
        result = await main_agent.process_query(request.query, request.symbol.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market")
async def get_market_overview():
    try:
        result = await main_agent.get_market_overview()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/{symbol}")
async def predict_price(symbol: str):
    try:
        result = await run_in_threadpool(main_agent.price_predictor.predict_price, symbol.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/{symbol}")
async def get_ticker_news(symbol: str):
    try:
        result = await run_in_threadpool(main_agent.ticker_news.get_ticker_news, symbol.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/risk/{symbol}")
async def assess_risk(symbol: str):
    try:
        result = await run_in_threadpool(main_agent.risk_expert.assess_risk, symbol.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vn-stock/{symbol}")
async def get_vn_stock(symbol: str):
    try:
        result = await vn_api.get_stock_data(symbol.upper())
        if result:
            return asdict(result)  # Real data available
        else:
            # No real data available, generate mock for demo
            mock_data = vn_api._generate_mock_data(symbol.upper())
            return asdict(mock_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vn-market")
async def get_vn_market():
    try:
        result = await vn_api.get_market_overview() # Sử dụng instance vn_api đã được tạo
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vn-symbols")
async def get_vn_symbols():
    try:
        result = vn_api.get_available_symbols() # Sử dụng instance vn_api đã được tạo
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)