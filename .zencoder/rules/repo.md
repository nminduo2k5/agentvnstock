---
description: Repository Information Overview
alwaysApply: true
---

# Duong AI Trading SIUUUUU Information

## Summary
Duong AI Trading SIUUUUU is a comprehensive stock analysis system for the Vietnamese market, integrating 6 AI agents, Gemini Chatbot, and CrewAI for real-time news analysis. The system provides price predictions, risk assessment, investment analysis, and market news for Vietnamese and international stocks.

## Structure
- **agents/**: Contains 6 specialized AI agents (price predictor, ticker news, market news, investment expert, risk expert, stock info)
- **src/**: Core functionality organized in data, UI, and utilities modules
- **static/**: Frontend web interface files (HTML, CSS, JavaScript)
- **reports/**: Generated stock analysis reports
- **.zencoder/**: Configuration files for the Zencoder system
- **.vscode/**: VS Code editor configuration

## Language & Runtime
**Language**: Python 3.8+
**Version**: Python 3.8+ with FastAPI 0.104+ and Streamlit 1.28+
**Build System**: pip (Python package installer)
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- streamlit>=1.28.0: Web application framework for the frontend
- fastapi>=0.104.0: API framework for the backend
- crewai[tools]>=0.117.0: AI agents framework for news collection
- google-generativeai>=0.3.0: Gemini AI integration
- vnstock>=3.2.0: Vietnamese stock market data API
- pandas>=2.0.0: Data manipulation and analysis
- plotly>=5.17.0: Interactive data visualization

**Development Dependencies**:
- python-dotenv>=1.0.0: Environment variable management
- aiohttp>=3.8.0: Asynchronous HTTP client/server
- beautifulsoup4>=4.12.0: Web scraping library

## Build & Installation
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Main Entry Points
**Application Entry Points**:
- app.py: Streamlit frontend with 6 tabs for different analyses
- api.py: FastAPI backend with RESTful endpoints
- main_agent.py: Main orchestrator for all AI agents

**Key API Endpoints**:
- /analyze: Comprehensive stock analysis with 6 AI agents
- /query: AI-powered natural language query processing
- /predict/{symbol}: Price prediction using PricePredictor agent
- /news/{symbol}: Get news for specific stock ticker
- /risk/{symbol}: Risk assessment using RiskExpert agent

## Data Sources
**Stock Data**:
- vnstock: Vietnamese stock market data API
- yfinance: International stock data (Yahoo Finance)

**News Sources**:
- CafeF.vn: Vietnamese financial news
- CrewAI integration for real-time news collection and analysis

## Testing
**Test Files**:
- test_crewai_symbols.py: Tests for CrewAI integration
- test_symbols_simple.py: Simple tests for stock symbols

**Run Command**:
```bash
# Test CrewAI integration
python test_crewai_symbols.py

# Test simple symbols
python test_symbols_simple.py
```

## Configuration
**Environment Variables**:
- GOOGLE_API_KEY: Required for Gemini AI
- GEMINI_MODEL: Gemini model to use (default: gemini-1.5-flash)
- SERPER_API_KEY: Optional for CrewAI real news
- VNSTOCK_SOURCE: VNStock data source (default: VCI)
- ENABLE_REAL_DATA: Enable real data fetching (default: True)

**UI Configuration**:
- PAGE_TITLE: Application title
- PAGE_ICON: Application icon
- UI_LAYOUT: Layout style (default: wide)