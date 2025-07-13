# 🇻🇳 Duong AI Trading SIUUUUU

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.117+-purple.svg)](https://crewai.com)

> **Hệ thống phân tích đầu tư chứng khoán thông minh với 6 AI Agents + Gemini Chatbot + CrewAI Real News**

## 🎯 Tổng quan

**Duong AI Trading SIUUUUU** là hệ thống phân tích đầu tư chứng khoán hoàn chỉnh, tích hợp 6 AI Agents chuyên nghiệp, Gemini Chatbot và CrewAI để cung cấp phân tích toàn diện cho thị trường chứng khoán Việt Nam và quốc tế.

### ✨ Tính năng chính

- 🤖 **6 AI Agents chuyên nghiệp** với phân tích cá nhân hóa
- 🧠 **Gemini AI Chatbot** tương tác tự nhiên
- 📰 **CrewAI Real News** - Tin tức thật từ CafeF.vn
- 📊 **Dữ liệu real-time** từ VNStock API
- 🚀 **FastAPI Backend** + **Streamlit Frontend**
- 📈 **Phân tích kỹ thuật & cơ bản** với số thập phân chuyên nghiệp
- ⚙️ **Cài đặt đầu tư cá nhân** (thời gian + rủi ro)
- ⚠️ **Quản lý rủi ro thông minh**

## 🤖 Đội ngũ 6 AI Agents

| Agent | Chức năng | Mô tả | Tab |
|-------|-----------|-------|-----|
| 📈 **PricePredictor** | Dự đoán giá | Phân tích xu hướng và dự báo giá cổ phiếu | Tab 1 |
| 📰 **TickerNews** | Tin tức cổ phiếu | Thu thập và phân tích tin tức theo mã | Tab 4 |
| 🌍 **MarketNews** | Tin tức thị trường | Crawl tin tức từ CafeF.vn | Tab 5 |
| 💼 **InvestmentExpert** | Chuyên gia đầu tư | Phân tích cơ bản và khuyến nghị đầu tư | Tab 1 |
| ⚠️ **RiskExpert** | Quản lý rủi ro | Đánh giá và quản lý rủi ro đầu tư | Tab 1 |
| 🧠 **GeminiAgent** | AI Chatbot | Tương tác tự nhiên với Gemini AI | Tab 2 |
| 🤖 **CrewAI News** | Tin tức nâng cao | Thu thập tin tức thật với AI analysis | Tab 6 |

## 🏗️ Kiến trúc hệ thống

```
agentvnstock/
├── agents/                    # 6 AI Agents
│   ├── price_predictor.py     # Dự đoán giá với time horizon
│   ├── ticker_news.py         # Tin tức cổ phiếu VN + International
│   ├── market_news.py         # Crawl CafeF.vn + fallback
│   ├── investment_expert.py   # Phân tích đầu tư cá nhân hóa
│   ├── risk_expert.py         # Đánh giá rủi ro theo tolerance
│   ├── stock_info.py          # Hiển thị thông tin chi tiết
│   └── enhanced_news_agent.py # CrewAI integration
├── src/
│   ├── data/                  # Data layer
│   │   ├── vn_stock_api.py    # VNStock API integration
│   │   └── crewai_collector.py # CrewAI real news
│   ├── ui/                    # UI components
│   │   ├── dashboard.py       # Main dashboard
│   │   ├── components.py      # UI components
│   │   ├── agent_widgets.py   # Agent-specific widgets
│   │   └── styles.py          # Custom CSS
│   └── utils/                 # Utilities
│       ├── config_manager.py  # Configuration management
│       ├── error_handler.py   # Error handling
│       └── helpers.py         # Helper functions
├── gemini_agent.py           # Gemini AI integration
├── main_agent.py             # Main orchestrator
├── api.py                    # FastAPI backend
└── app.py                    # Streamlit frontend (6 tabs)
```

## 🚀 Cài đặt & Chạy

### 🎯 Cài đặt tự động (Khuyến nghị)

#### Windows:
```cmd
git clone https://github.com/nminduo2k5/agentvnstock.git
cd agentvnstock
install.bat
```

#### Linux/Mac:
```bash
git clone https://github.com/nminduo2k5/agentvnstock.git
cd agentvnstock
chmod +x install.sh
./install.sh
```

### 🔧 Cài đặt thủ công

#### 1. Clone repository
```bash
git clone https://github.com/nminduo2k5/agentvnstock.git
cd agentvnstock
```

#### 2. Tạo virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Cài đặt dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Cấu hình API Keys

Tạo file `.env`:
```env
# Required for Gemini AI
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# CrewAI Real News (Optional)
SERPER_API_KEY=your_serper_api_key_here

# VNStock Configuration
VNSTOCK_SOURCE=VCI
ENABLE_REAL_DATA=True

# System Configuration
DEBUG_MODE=False
LOG_LEVEL=INFO
CACHE_DURATION=60
MAX_CONCURRENT_REQUESTS=10

# UI Configuration
PAGE_TITLE=DUONG AI TRADING SIUUUU
PAGE_ICON=🤖
UI_LAYOUT=wide
```

**Lấy API keys tại:**
- **Gemini**: https://aistudio.google.com/apikey
- **Serper** (tin tức): https://serper.dev/api-key

#### 5. Chạy ứng dụng

```bash
# Chạy Streamlit App (Khuyến nghị)
streamlit run app.py

# Hoặc chạy FastAPI Backend
python api.py
```

## 📱 Giao diện 6 Tabs

### **Tab 1: 📊 Phân tích cổ phiếu**
- **🚀 Phân tích toàn diện**: Tất cả 6 agents
- **📈 Dự đoán giá**: PricePredictor only
- **⚠️ Đánh giá rủi ro**: RiskExpert only  
- **💼 Phân tích đầu tư**: InvestmentExpert only
- **Hiển thị**: Số thập phân chuyên nghiệp (26.00 VND, P/E: 15.875)

### **Tab 2: 💬 AI Chatbot**
- **GeminiAgent**: Chat tự nhiên với AI
- **Dữ liệu hỗ trợ**: Từ tất cả agents
- **Context-aware**: Hiểu ngữ cảnh đầu tư

### **Tab 3: 📈 Thị trường VN**
- **VN-Index**: Dữ liệu real-time
- **Top movers**: Tăng/giảm mạnh
- **Danh sách cổ phiếu**: CrewAI hoặc static

### **Tab 4: 📰 Tin tức cổ phiếu**
- **TickerNews Agent**: Tin theo mã cổ phiếu
- **VN stocks**: Từ VCI
- **International**: Từ Yahoo Finance
- **Format**: Expander với link gốc

### **Tab 5: 🌍 Tin tức thị trường**
- **MarketNews Agent**: Crawl từ CafeF.vn
- **URL**: https://cafef.vn/thi-truong-chung-khoan.chn
- **Fallback**: Mock VN news nếu lỗi
- **Smart extraction**: Title, summary, link, time

### **Tab 6: 🤖 Tin tức nâng cao**
- **EnhancedNewsAgent**: CrewAI integration
- **Sentiment analysis**: AI-powered
- **Impact assessment**: High/Medium/Low
- **Trading recommendations**: Dựa trên AI analysis

## ⚙️ Cài đặt đầu tư cá nhân

### **🕐 Thời gian đầu tư:**
- **Ngắn hạn**: 1-6 tháng (180 ngày)
- **Trung hạn**: 6-24 tháng (720 ngày)
- **Dài hạn**: 2+ năm (1095 ngày)

### **⚠️ Mức độ rủi ro (0-100):**
- **0-30**: 🟢 Thận trọng (PE<12, PB<1.7)
- **31-70**: 🟡 Cân bằng (PE<20, PB<2.5)
- **71-100**: 🔴 Tích cực (PE<30, PB<3.5)

### **🎯 Tác động lên Agents:**
- **PricePredictor**: Điều chỉnh multiplier (0.5x - 1.5x)
- **RiskExpert**: Thay đổi ngưỡng rủi ro
- **InvestmentExpert**: PE/PB thresholds linh hoạt

## 📡 API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/health` | GET | Health check |
| `/analyze` | POST | Phân tích toàn diện với investment params |
| `/query` | POST | Gemini chatbot |
| `/set-gemini-key` | POST | Cài đặt Gemini API key |
| `/set-crewai-keys` | POST | Cài đặt CrewAI keys |
| `/vn-stock/{symbol}` | GET | Dữ liệu cổ phiếu VN |
| `/vn-market` | GET | Tổng quan thị trường |
| `/predict/{symbol}` | GET | Dự đoán giá với time horizon |
| `/news/{symbol}` | GET | Tin tức cổ phiếu |
| `/market-news` | GET | Tin tức thị trường từ CafeF |
| `/risk/{symbol}` | GET | Đánh giá rủi ro với tolerance |

## 💻 Sử dụng

### 1. Phân tích cổ phiếu với investment settings

```python
from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI

# Initialize
vn_api = VNStockAPI()
main_agent = MainAgent(vn_api)

# Analyze with personal investment profile
result = await main_agent.analyze_stock(
    symbol='VCB',
    time_horizon='Dài hạn',  # Ngắn hạn/Trung hạn/Dài hạn
    risk_tolerance=80        # 0-100
)
print(result)
```

### 2. Gemini Chatbot

```python
from gemini_agent import GeminiAgent

# Initialize
gemini = GeminiAgent(api_key="your_key")

# Ask with context
response = gemini.generate_expert_advice(
    "Phân tích VCB có nên mua không?", 
    symbol="VCB"
)
print(response['expert_advice'])
```

### 3. Crawl tin tức thị trường

```python
from agents.market_news import MarketNews

# Initialize
market_news = MarketNews()

# Get news from CafeF
news = market_news.get_market_news()
print(f"Found {news['news_count']} news from {news['source']}")
```

## 📊 Cổ phiếu được hỗ trợ

### 🏦 Ngân hàng
- **VCB** - Vietcombank | **BID** - BIDV | **CTG** - VietinBank
- **TCB** - Techcombank | **ACB** - ACB

### 🏢 Bất động sản  
- **VIC** - Vingroup | **VHM** - Vinhomes
- **VRE** - Vincom Retail | **DXG** - Dat Xanh Group

### 🛒 Tiêu dùng
- **MSN** - Masan Group | **MWG** - Mobile World
- **VNM** - Vinamilk | **SAB** - Sabeco

### 🏭 Công nghiệp
- **HPG** - Hoa Phat Group | **GAS** - PetroVietnam Gas
- **PLX** - Petrolimex

### 💻 Công nghệ
- **FPT** - FPT Corporation

## 🧪 Testing

### Comprehensive System Test
```bash
python test_system.py
```

### Individual Component Tests
```bash
# Test vnstock integration
python test_vnstock.py

# Test API endpoints  
python test_api.py

# Test Gemini integration
python test_gemini.py

# Test CrewAI integration
python test_crewai_integration.py

# Test news crawling
python test_real_data.py
```

## 📋 Requirements

```
# Core Framework
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn>=0.24.0

# CrewAI Integration
crewai[tools]>=0.117.0
crewai-tools>=0.12.0

# AI & ML
google-generativeai>=0.3.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0

# Data Sources
vnstock>=3.2.0
yfinance>=0.2.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Visualization
plotly>=5.17.0
matplotlib>=3.7.0

# Utilities
python-dotenv>=1.0.0
python-multipart>=0.0.6
```

## 🔧 Cấu hình nâng cao

### Dynamic API Key Setup

**Streamlit App:**
1. Mở sidebar
2. Nhập Google Gemini API key
3. Nhập Serper API key (optional)
4. Click "⚙️ Cài đặt Gemini" và "🤖 Cài đặt CrewAI"

**FastAPI:**
```bash
curl -X POST "http://localhost:8000/set-gemini-key" \
     -H "Content-Type: application/json" \
     -d '{"api_key": "your_api_key_here"}'
```

### Investment Profile Configuration

```python
# Trong sidebar
time_horizon = st.selectbox("Thời gian đầu tư", ["Ngắn hạn", "Trung hạn", "Dài hạn"])
risk_tolerance = st.slider("Mức độ rủi ro", 0, 100, 50)

# Tự động áp dụng cho tất cả agents
result = main_agent.analyze_stock(symbol, time_horizon, risk_tolerance)
```

## 📈 Screenshots

### Main Dashboard
![Dashboard](image.png)

### 6 Tabs Interface
- **Tab 1**: Phân tích toàn diện với investment settings
- **Tab 2**: Gemini AI Chatbot
- **Tab 3**: Thị trường VN real-time
- **Tab 4**: Tin tức cổ phiếu
- **Tab 5**: Tin tức thị trường từ CafeF
- **Tab 6**: Tin tức nâng cao CrewAI

## 🚀 Deployment

### Docker (Coming Soon)
```bash
# Build image
docker build -t agentvnstock .

# Run container
docker run -p 8501:8501 -p 8000:8000 agentvnstock
```

### Cloud Deployment
- **Streamlit Cloud**: Deploy trực tiếp từ GitHub
- **Heroku**: Sử dụng Procfile có sẵn
- **AWS/GCP**: Container hoặc serverless

## ⚠️ Disclaimer

> **Cảnh báo quan trọng**: Đây là công cụ hỗ trợ phân tích, **KHÔNG PHẢI lời khuyên đầu tư**. 

- Dữ liệu có thể không chính xác 100%
- Luôn thực hiện nghiên cứu riêng
- Chỉ đầu tư số tiền có thể chấp nhận mất
- Tác giả không chịu trách nhiệm về tổn thất tài chính

## 🔍 Troubleshooting

### Lỗi thường gặp

**1. Import Error:**
```bash
pip install -r requirements.txt --force-reinstall
```

**2. VNStock Error:**
```bash
pip install --upgrade vnstock
```

**3. Gemini API Error:**
- Kiểm tra API key tại https://aistudio.google.com/apikey
- Đảm bảo API key có quyền truy cập Gemini

**4. CafeF Crawling Error:**
- Kiểm tra kết nối internet
- Website có thể thay đổi cấu trúc HTML

**5. CrewAI Error:**
```bash
pip install --upgrade crewai crewai-tools
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📞 Liên hệ & Hỗ trợ

- 🐛 **Issues**: [GitHub Issues](https://github.com/nminduo2k5/agentvnstock/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/nminduo2k5/agentvnstock/discussions)
- 📧 **Email**: support@agentvnstock.com

## 🙏 Acknowledgments

- [vnstock](https://github.com/thinh-vu/vnstock) - Vietnamese stock data
- [Google Gemini](https://ai.google.dev) - AI chatbot
- [CrewAI](https://crewai.com) - AI agents framework
- [CafeF.vn](https://cafef.vn) - Vietnamese financial news
- [Streamlit](https://streamlit.io) - Web framework
- [FastAPI](https://fastapi.tiangolo.com) - API framework

## 📄 License

Dự án này được phát hành dưới [MIT License](LICENSE) - tự do sử dụng cho mục đích cá nhân và thương mại.

---

<div align="center">

**🇻🇳 Made with ❤️ for Vietnamese investors**

[![Star this repo](https://img.shields.io/github/stars/nminduo2k5/agentvnstock?style=social)](https://github.com/nminduo2k5/agentvnstock)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**🚀 Version 2.0 - Complete AI Trading System**

</div>