# 🇻🇳 Duong AI Trading Pro

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.117+-purple.svg)](https://crewai.com)

> **Hệ thống phân tích đầu tư chứng khoán thông minh với 6 AI Agents + Gemini AI + CrewAI + LSTM Neural Network**

## 🎯 Tổng quan

**Duong AI Trading Pro** là hệ thống phân tích đầu tư chứng khoán hoàn chỉnh, tích hợp 6 AI Agents chuyên nghiệp, Gemini AI, và mạng neural LSTM để cung cấp phân tích toàn diện cho thị trường chứng khoán Việt Nam và quốc tế.

### ✨ Tính năng nổi bật

- 🤖 **6 AI Agents chuyên nghiệp** với phân tích cá nhân hóa
- 🧠 **Gemini AI Chatbot** với khả năng offline fallback
- 🔮 **LSTM Neural Network** cho dự đoán giá nâng cao
- 📊 **Dữ liệu real-time** từ VNStock API và CrewAI
- 🚀 **FastAPI Backend** + **Streamlit Frontend** với 6 tabs chuyên nghiệp
- 📈 **Phân tích kỹ thuật & cơ bản** với số liệu chính xác
- ⚙️ **Cài đặt đầu tư cá nhân** (thời gian + mức độ rủi ro)
- 🎨 **Giao diện đẹp mắt** với Bootstrap integration

## 🤖 Đội ngũ 6 AI Agents

| Agent | Chức năng | Mô tả | Tính năng đặc biệt |
|-------|-----------|-------|-------------------|
| 📈 **PricePredictor** | Dự đoán giá | LSTM + Technical Analysis cho dự báo giá | LSTM Neural Network, Multi-timeframe |
| 💼 **InvestmentExpert** | Chuyên gia đầu tư | Phân tích cơ bản và khuyến nghị BUY/SELL/HOLD | Real financial ratios, AI-enhanced |
| ⚠️ **RiskExpert** | Quản lý rủi ro | Đánh giá rủi ro với VaR, Beta, Sharpe ratio | Advanced risk metrics, AI advice |
| 📰 **TickerNews** | Tin tức cổ phiếu | Crawl tin tức từ CafeF, VietStock | Multi-source crawling, Sentiment analysis |
| 🌍 **MarketNews** | Tin tức thị trường | Risk-based news filtering | Underground news, Risk-adjusted content |
| 🏢 **StockInfo** | Thông tin chi tiết | Hiển thị metrics và charts chuyên nghiệp | Real-time data, Interactive charts |

## 🏗️ Kiến trúc hệ thống

```
agentvnstock/
├── agents/                           # 6 AI Agents + LSTM
│   ├── price_predictor.py           # LSTM + Technical Analysis
│   ├── lstm_price_predictor.py      # Neural Network predictor
│   ├── investment_expert.py         # BUY/SELL recommendations
│   ├── risk_expert.py               # Risk assessment with VaR
│   ├── ticker_news.py               # Multi-source news crawling
│   ├── market_news.py               # Risk-based market news
│   ├── stock_info.py                # Professional data display
│   └── risk_based_news.py           # Underground news agent
├── src/
│   ├── data/                        # Data layer
│   │   ├── vn_stock_api.py          # VNStock + CrewAI integration
│   │   ├── crewai_collector.py      # Real news collection
│   │   └── company_search_api.py    # Company information
│   ├── ui/                          # UI components
│   │   ├── styles.py                # Bootstrap + Custom CSS
│   │   └── components.py            # Reusable UI components
│   └── utils/                       # Utilities
│       ├── error_handler.py         # Comprehensive error handling
│       ├── market_schedule.py       # Market timing logic
│       ├── performance_monitor.py   # System monitoring
│       └── security_manager.py      # Security utilities
├── deep-learning/                   # LSTM Research & Development
│   ├── 1.lstm.ipynb                # Basic LSTM implementation
│   ├── 16.attention-is-all-you-need.ipynb # Transformer models
│   └── [18 Jupyter notebooks]      # Various ML approaches
├── static/                          # Web interface
│   ├── index.html                   # Professional web UI
│   ├── script.js                    # Interactive features
│   └── styles.css                   # Web styling
├── gemini_agent.py                  # Unified AI with offline fallback
├── main_agent.py                    # Main orchestrator
├── api.py                           # FastAPI backend (20+ endpoints)
└── app.py                           # Streamlit frontend (6 tabs)
```

## 🚀 Cài đặt nhanh

### 1. Clone repository
```bash
git clone https://github.com/nminduo2k5/agentvnstock.git
cd agentvnstock
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

#### Streamlit Frontend (Khuyến nghị)
```bash
streamlit run app.py
```

#### FastAPI Backend (Tùy chọn)
```bash
python api.py
# Hoặc
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Cấu hình API (trong ứng dụng)
- Mở sidebar trong Streamlit
- Nhập **Gemini API key** (miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey))
- Nhập **Serper API key** (tùy chọn, tại [Serper.dev](https://serper.dev/api-key))
- Click **"🔧 Cài đặt Gemini"** hoặc **"🚀 Cài đặt CrewAI"**

## 📱 Giao diện 6 Tabs chuyên nghiệp

### **Tab 1: 📊 Phân tích cổ phiếu**
- **🚀 Phân tích toàn diện**: Tất cả 6 agents + LSTM
- **📈 Dự đoán giá**: LSTM Neural Network + Technical Analysis
- **💼 Phân tích đầu tư**: BUY/SELL/HOLD với real financial ratios
- **⚠️ Đánh giá rủi ro**: VaR, Beta, Sharpe ratio, Max Drawdown

### **Tab 2: 💬 AI Chatbot**
- **Gemini AI**: Phân tích chuyên sâu với ngôn ngữ tự nhiên
- **Offline Fallback**: Vẫn hoạt động khi hết quota API
- **Gợi ý câu hỏi**: 5 câu hỏi mẫu thông dụng
- **Phản hồi thông minh**: Format tự động với màu sắc và icon

### **Tab 3: 📈 Thị trường VN**
- **VN-Index Real-time**: Dữ liệu từ VNStock API
- **Top movers**: Tăng/giảm mạnh với styling đẹp
- **37+ cổ phiếu VN**: CrewAI tìm kiếm real-time hoặc static fallback
- **Market overview**: Tin tức và sentiment analysis

### **Tab 4: 📰 Tin tức cổ phiếu**
- **Multi-source crawling**: CafeF, VietStock, VCI
- **AI sentiment analysis**: Phân tích tâm lý thị trường
- **Priority highlighting**: Tin quan trọng được đánh dấu
- **Real-time updates**: CrewAI integration

### **Tab 5: 🏢 Thông tin công ty**
- **Company overview**: Thông tin chi tiết từ CrewAI
- **Financial metrics**: P/E, P/B, EPS, Dividend yield
- **Interactive charts**: Price history với Plotly
- **Enhanced display**: Professional styling

### **Tab 6: 🌍 Tin tức thị trường**
- **Risk-based filtering**: Tin tức theo hồ sơ rủi ro
- **Underground news**: Tin nội gián từ F319, F247, FB Groups
- **Official news**: CafeF, VnEconomy, DanTri
- **Smart categorization**: Tự động phân loại theo risk profile

## 🧠 LSTM Neural Network

### **Tính năng LSTM nâng cao:**
- **18 mô hình ML**: Từ basic LSTM đến Transformer
- **Multi-timeframe prediction**: 1 ngày đến 1 năm
- **Confidence scoring**: Đánh giá độ tin cậy dự đoán
- **AI enhancement**: Kết hợp với Gemini AI
- **Real-time training**: Cập nhật mô hình liên tục

### **Các mô hình có sẵn:**
```
1. LSTM Basic                    11. Bidirectional LSTM Seq2Seq
2. Bidirectional LSTM           12. LSTM Seq2Seq VAE
3. LSTM 2-Path                  13. GRU Seq2Seq
4. GRU                          14. Bidirectional GRU Seq2Seq
5. Bidirectional GRU            15. GRU Seq2Seq VAE
6. GRU 2-Path                   16. Attention (Transformer)
7. Vanilla RNN                  17. CNN Seq2Seq
8. Bidirectional Vanilla        18. Dilated CNN Seq2Seq
9. Vanilla 2-Path
10. LSTM Seq2Seq
```

## ⚙️ Cài đặt đầu tư cá nhân

### **🕐 Thời gian đầu tư:**
- **Ngắn hạn**: 1-3 tháng (Focus: Technical analysis)
- **Trung hạn**: 3-12 tháng (Balance: Technical + Fundamental)
- **Dài hạn**: 1+ năm (Focus: Fundamental analysis)

### **⚠️ Mức độ rủi ro (0-100):**
- **0-30**: 🟢 Thận trọng (Blue-chip, dividend stocks)
- **31-70**: 🟡 Cân bằng (Mixed portfolio)
- **71-100**: 🔴 Mạo hiểm (Growth stocks, underground news)

### **💰 Số tiền đầu tư:**
- **Từ 1 triệu đến 10 tỷ VND**
- **Position sizing**: Tự động tính toán tỷ trọng
- **Risk management**: Stop-loss và take-profit thông minh

## 🛡️ Tính năng Offline Fallback

### **Khi hết quota Gemini API:**
- ✅ Hệ thống **KHÔNG crash**
- ✅ Vẫn trả lời câu hỏi với nội dung hữu ích
- ✅ Thông báo rõ ràng về tình trạng
- ✅ Hướng dẫn user cách xử lý

### **Phản hồi offline thông minh:**
```
📈 PHÂN TÍCH OFFLINE:
Do Gemini API đã hết quota, hệ thống chuyển sang chế độ offline...

💡 Nguyên tắc đầu tư cơ bản:
- P/E < 15 thường được coi là hấp dẫn
- Đa dạng hóa danh mục để giảm rủi ro
- Chỉ đầu tư số tiền có thể chấp nhận mất

⏰ Quota thường reset sau 24 giờ
```

## 📊 Cổ phiếu được hỗ trợ

### 🏦 Ngân hàng (7 mã)
**VCB** • **BID** • **CTG** • **TCB** • **ACB** • **MBB** • **VPB**

### 🏢 Bất động sản (5 mã)
**VIC** • **VHM** • **VRE** • **DXG** • **NVL**

### 🛒 Tiêu dùng (5 mã)
**MSN** • **MWG** • **VNM** • **SAB** • **PNJ**

### 🏭 Công nghiệp (3 mã)
**HPG** • **HSG** • **NKG**

### ⚡ Tiện ích (3 mã)
**GAS** • **PLX** • **POW**

### 💻 Công nghệ (2 mã)
**FPT** • **CMG**

### 🚁 Vận tải (2 mã)
**VJC** • **HVN**

### 💊 Y tế (2 mã)
**DHG** • **IMP**

**Tổng cộng: 37+ cổ phiếu VN **

## 💻 Sử dụng API

### FastAPI Endpoints (20+ endpoints)

#### Phân tích cổ phiếu
```python
# POST /analyze
{
  "symbol": "VCB",
  "time_horizon": "medium",
  "risk_tolerance": 50,
  "investment_amount": 100000000
}
```

#### AI Chatbot
```python
# POST /query
{
  "query": "Phân tích VCB có nên mua không?",
  "symbol": "VCB"
}
```

#### Dự đoán giá
```python
# GET /predict/VCB
# Response: LSTM + Technical analysis
```

#### Đánh giá rủi ro
```python
# GET /risk/VCB
# Response: VaR, Beta, Sharpe ratio
```

### Python SDK
```python
from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI

# Initialize
vn_api = VNStockAPI()
main_agent = MainAgent(vn_api, gemini_api_key="your_key")

# Comprehensive analysis
result = await main_agent.analyze_stock('VCB')

# AI Chatbot
response = await main_agent.process_query("Phân tích VCB", "VCB")
```

## 📋 Requirements chính

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
aiohttp>=3.8.0

# Visualization
plotly>=5.17.0
matplotlib>=3.7.0
beautifulsoup4>=4.12.0
```

## 🔧 Cấu hình nâng cao

### Dynamic API Key (Không cần .env file)
```python
# Trong Streamlit sidebar
gemini_key = st.text_input("Gemini API Key", type="password")
if st.button("🔧 Cài đặt"):
    main_agent.set_gemini_api_key(gemini_key)
```

### FastAPI Health Check
```bash
curl http://localhost:8000/health
# Response: System status + agents status
```

### CrewAI Real Data
```python
# Tự động lấy symbols từ CrewAI
symbols = await vn_api.get_available_symbols()
# Fallback to static nếu CrewAI fail
```

## 🎨 Giao diện mới

### **Bootstrap Integration:**
- **Professional styling**: Card-based layout
- **Responsive design**: Mobile-friendly
- **Color-coded metrics**: Green/Red/Yellow indicators
- **Interactive charts**: Plotly integration
- **Gradient backgrounds**: Modern UI/UX

### **Enhanced Features:**
- **Real-time updates**: Auto-refresh data
- **Error handling**: Graceful fallbacks
- **Loading states**: Professional spinners
- **Tooltips**: Helpful explanations
- **Keyboard shortcuts**: Power user features

## 🔍 Troubleshooting

### **Lỗi thường gặp:**

**1. Gemini API Error:**
```bash
# Kiểm tra API key tại: https://aistudio.google.com/apikey
# Đảm bảo API key có quyền truy cập Gemini 2.0 Flash
```

**2. VNStock Error:**
```bash
pip install vnstock --upgrade
# Hoặc sử dụng fallback data
```

**3. CrewAI Error:**
```bash
pip install crewai[tools] --upgrade
# Kiểm tra Serper API key (optional)
```

**4. LSTM Error:**
```bash
pip install tensorflow scikit-learn --upgrade
# LSTM sẽ fallback to traditional methods
```

## 🚀 Roadmap

### **Version 2.0 (Current)**
- ✅ 6 AI Agents hoàn chỉnh
- ✅ LSTM Neural Network
- ✅ Gemini AI với offline fallback
- ✅ CrewAI real data integration
- ✅ 37+ VN stocks support

### **Version 2.2 (Planned)**
- 🔄 Transformer models (GPT-style)
- 🔄 Real-time alerts system
- 🔄 Portfolio management
- 🔄 Backtesting engine
- 🔄 Mobile app

### **Version 3.0 (Future)**
- 🔮 Multi-market support (US, EU, Asia)
- 🔮 Options & Derivatives analysis
- 🔮 Social sentiment integration
- 🔮 Automated trading signals

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📞 Hỗ trợ

- 🐛 **Issues**: [GitHub Issues](https://github.com/nminduo2k5/agentvnstock/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/nminduo2k5/agentvnstock/discussions)
- 📧 **Email**: duongnguyenminh808@gmail.com or 23010441@st.phenikaa-uni.edu.vn


## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev) - AI chatbot với offline fallback
- [CrewAI](https://crewai.com) - Multi-agent framework
- [vnstock](https://github.com/thinh-vu/vnstock) - Vietnamese stock data
- [Streamlit](https://streamlit.io) - Beautiful web framework
- [FastAPI](https://fastapi.tiangolo.com) - Modern API framework
- [TensorFlow](https://tensorflow.org) - LSTM Neural Networks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**🇻🇳 Made with ❤️ for Vietnamese investors**

[![Star this repo](https://img.shields.io/github/stars/nminduo2k5/agentvnstock?style=social)](https://github.com/nminduo2k5/agentvnstock)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**🚀 Version 2.0 - Professional AI Trading System**

*"Đầu tư thông minh với sức mạnh của AI và Machine Learning!"* 💪

### ⚠️ Disclaimer

**Cảnh báo quan trọng**: Đây là công cụ hỗ trợ phân tích, **KHÔNG PHẢI lời khuyên đầu tư tuyệt đối**.

- Dữ liệu có thể không chính xác 100%
- Luôn thực hiện nghiên cứu riêng (DYOR)
- Chỉ đầu tư số tiền có thể chấp nhận mất
- Tác giả không chịu trách nhiệm về tổn thất tài chính

**"Còn thở là còn gỡ, dừng lại là thất bại!"** 🚀

</div>