# 🇻🇳 Duong AI Trading SIUUUUU

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev)

> **Hệ thống phân tích đầu tư chứng khoán thông minh với 6 AI Agents + Gemini Chatbot**

## 🎯 Tổng quan

**Duong AI Trading SIUUUUU** là một hệ thống phân tích đầu tư chứng khoán hoàn chỉnh, tích hợp 6 AI Agents chuyên nghiệp và Gemini Chatbot để cung cấp phân tích toàn diện cho thị trường chứng khoán Việt Nam.

### ✨ Tính năng chính

- 🤖 **6 AI Agents chuyên nghiệp**
- 🧠 **Gemini AI Chatbot** tương tác tự nhiên
- 📊 **Dữ liệu real-time** từ thị trường VN
- 🚀 **FastAPI Backend** + **Streamlit Frontend**
- 📈 **Phân tích kỹ thuật & cơ bản**
- ⚠️ **Quản lý rủi ro thông minh**

## 🤖 Đội ngũ 6 AI Agents

| Agent | Chức năng | Mô tả |
|-------|-----------|-------|
| 📈 **PricePredictor** | Dự đoán giá | Phân tích xu hướng và dự báo giá cổ phiếu |
| 📰 **TickerNews** | Tin tức cổ phiếu | Thu thập và phân tích tin tức theo mã |
| 🌍 **MarketNews** | Tin tức thị trường | Cập nhật tin tức thị trường tổng thể |
| 💼 **InvestmentExpert** | Chuyên gia đầu tư | Phân tích cơ bản và khuyến nghị đầu tư |
| ⚠️ **RiskExpert** | Quản lý rủi ro | Đánh giá và quản lý rủi ro đầu tư |
| 🧠 **GeminiAgent** | AI Chatbot | Tương tác tự nhiên với Gemini AI |

## 🏗️ Kiến trúc hệ thống

```
agentvnstock/
├── agents/                 # 6 AI Agents
│   ├── price_predictor.py
│   ├── ticker_news.py
│   ├── market_news.py
│   ├── investment_expert.py
│   ├── risk_expert.py
│   
├── src/
│   ├── data/              # Data layer
│   │   └── vn_stock_api.py
│   ├── ui/                # UI components
│   │   ├── dashboard.py
│   │   ├── components.py
│   │   └── agent_widgets.py
│   └── utils/             # Utilities
├── gemini_agent.py        # Gemini AI integration
├── main_agent.py          # Main orchestrator
├── api.py                 # FastAPI backend
├── app.py                 # Streamlit app
└── streamlit_app.py       # New entry point
```

## 🚀 Cài đặt & Chạy

### 1. Clone repository

```bash
git clone https://github.com/nminduo2k5/agentvnstock.git
cd agentvnstock
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình API Keys (Tùy chọn)

Bạn có thể tạo file `.env` (không bắt buộc):

```env
# Optional - có thể nhập trực tiếp trong app
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

**Hoặc nhập API key trực tiếp khi chạy app:**
- Streamlit: Nhập API key ở sidebar
- FastAPI: Sử dụng endpoint `/set-gemini-key`
LINK:https://aistudio.google.com/apikey
### 4. Chạy ứng dụng

#### Option 1: Streamlit App (Recommended)

```bash
streamlit run app.py
```

#### Option 2: FastAPI Backend

```bash
# Start API server
python api.py

# Test API
python test_api.py
```

## 📡 API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/health` | GET | Health check |
| `/analyze` | POST | Phân tích toàn diện |
| `/query` | POST | Gemini chatbot |
| `/vn-stock/{symbol}` | GET | Dữ liệu cổ phiếu VN |
| `/vn-market` | GET | Tổng quan thị trường |
| `/predict/{symbol}` | GET | Dự đoán giá |
| `/news/{symbol}` | GET | Tin tức cổ phiếu |
| `/risk/{symbol}` | GET | Đánh giá rủi ro |

## 💻 Sử dụng

### 1. Phân tích cổ phiếu

```python
from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI

# Initialize
vn_api = VNStockAPI()
main_agent = MainAgent(vn_api)

# Analyze stock
result = await main_agent.analyze_stock('VCB')
print(result)
```

### 2. Gemini Chatbot

```python
from gemini_agent import GeminiAgent

# Initialize
gemini = GeminiAgent()

# Ask question
response = gemini.generate_expert_advice(
    "Phân tích VCB có nên mua không?", 
    symbol="VCB"
)
print(response['expert_advice'])
```

### 3. VN Stock Data

```python
from src.data.vn_stock_api import VNStockAPI

# Initialize
api = VNStockAPI()

# Get stock data
stock_data = await api.get_stock_data('VCB')
print(f"Price: {stock_data.price:,} VND")
```

## 📊 Cổ phiếu được hỗ trợ

### 🏦 Ngân hàng
- **VCB** - Vietcombank
- **BID** - BIDV  
- **CTG** - VietinBank
- **TCB** - Techcombank
- **ACB** - ACB

### 🏢 Bất động sản
- **VIC** - Vingroup
- **VHM** - Vinhomes
- **VRE** - Vincom Retail
- **DXG** - Dat Xanh Group

### 🛒 Tiêu dùng
- **MSN** - Masan Group
- **MWG** - Mobile World
- **VNM** - Vinamilk
- **SAB** - Sabeco

### 🏭 Công nghiệp
- **HPG** - Hoa Phat Group
- **GAS** - PetroVietnam Gas
- **PLX** - Petrolimex

### 💻 Công nghệ
- **FPT** - FPT Corporation

## 🧪 Testing

```bash
# Test vnstock integration
python test_vnstock.py

# Test API endpoints
python test_api.py

# Test Gemini integration
python test_gemini.py
```

## 📋 Requirements

```
streamlit>=1.28.0
google-generativeai>=0.3.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
plotly>=5.17.0
python-dotenv>=1.0.0
asyncio-mqtt>=0.11.0
aiohttp>=3.8.0
vnstock>=3.2.0
fastapi>=0.104.0
uvicorn>=0.24.0
yfinance>=0.2.0
python-multipart>=0.0.6
```

## 🔧 Cấu hình

### Environment Variables

```env
# Optional - có thể nhập trực tiếp trong app
GOOGLE_API_KEY=your_gemini_api_key

# Optional
GEMINI_MODEL=gemini-1.5-flash
```

### Dynamic API Key Setup

**Streamlit:**
- Mở sidebar
- Nhập Google Gemini API key
- Click "Cài đặt API Key"

**FastAPI:**
```bash
curl -X POST "http://localhost:8000/set-gemini-key" \
     -H "Content-Type: application/json" \
     -d '{"api_key": "your_api_key_here"}'
```

### API Configuration

```python
# In api.py
app = FastAPI(
    title="AI Trading Team Vietnam API",
    description="6 AI Agents + Gemini Chatbot API",
    version="1.0.0"
)
```

## 📈 Screenshots

### Streamlit Dashboard
![Dashboard](image.png)

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## ⚠️ Disclaimer

> **Cảnh báo quan trọng**: Đây là công cụ hỗ trợ phân tích, **KHÔNG PHẢI lời khuyên đầu tư**. 

- Dữ liệu có thể không chính xác 100%
- Luôn thực hiện nghiên cứu riêng
- Chỉ đầu tư số tiền có thể chấp nhận mất
- Tác giả không chịu trách nhiệm về tổn thất tài chính

## 📄 License

Dự án này được phát hành dưới [Custom License](LICENSE.md) - chỉ dành cho mục đích cá nhân và nghiên cứu.

## 📞 Liên hệ & Hỗ trợ

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/agentvnstock/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/agentvnstock/discussions)
- 📧 **Email**: your-email@example.com

## 🙏 Acknowledgments

- [vnstock](https://github.com/thinh-vu/vnstock) - Vietnamese stock data
- [Google Gemini](https://ai.google.dev) - AI chatbot
- [Streamlit](https://streamlit.io) - Web framework
- [FastAPI](https://fastapi.tiangolo.com) - API framework

---

<div align="center">

**🇻🇳 Made with ❤️ for Vietnamese investors**

[![Star this repo](https://img.shields.io/github/stars/your-username/agentvnstock?style=social)](https://github.com/your-username/agentvnstock)

</div>