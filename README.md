# 🇻🇳 Duong AI Trading Pro

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.117+-purple.svg)](https://crewai.com)

> **Hệ thống phân tích đầu tư chứng khoán thông minh với 6 AI Agents + Gemini AI + Offline Fallback**

## 🎯 Tổng quan

**Duong AI Trading Pro** là hệ thống phân tích đầu tư chứng khoán hoàn chỉnh, tích hợp 6 AI Agents chuyên nghiệp và Gemini AI với khả năng hoạt động offline khi hết quota API, cung cấp phân tích toàn diện cho thị trường chứng khoán Việt Nam và quốc tế.

### ✨ Tính năng nổi bật

- 🤖 **6 AI Agents chuyên nghiệp** với phân tích cá nhân hóa
- 🧠 **Gemini AI Chatbot** với giao diện đẹp mắt và tương tác thông minh
- 🛡️ **Offline Fallback** - Vẫn hoạt động khi hết quota API
- 📊 **Dữ liệu real-time** từ VNStock API
- 🚀 **FastAPI Backend** + **Streamlit Frontend** với 6 tabs chuyên nghiệp
- 📈 **Phân tích kỹ thuật & cơ bản** với số liệu chính xác
- ⚙️ **Cài đặt đầu tư cá nhân** (thời gian + mức độ rủi ro)
- 🎨 **Giao diện đẹp mắt** với gradient, animation và UX tối ưu

## 🤖 Đội ngũ 6 AI Agents

| Agent | Chức năng | Mô tả | Tab |
|-------|-----------|-------|-----|
| 📈 **PricePredictor** | Dự đoán giá | Phân tích xu hướng và dự báo giá cổ phiếu | Tab 1 |
| 📰 **TickerNews** | Tin tức cổ phiếu | Thu thập và phân tích tin tức theo mã | Tab 4 |
| 🌍 **MarketNews** | Tin tức thị trường | Crawl tin tức từ CafeF.vn | Tab 6 |
| 💼 **InvestmentExpert** | Chuyên gia đầu tư | Phân tích cơ bản và khuyến nghị đầu tư | Tab 1 |
| ⚠️ **RiskExpert** | Quản lý rủi ro | Đánh giá và quản lý rủi ro đầu tư | Tab 1 |
| 🧠 **GeminiAgent** | AI Chatbot | Tương tác tự nhiên với Gemini AI | Tab 2 |

## 🏗️ Kiến trúc hệ thống

```
agentvnstock/
├── agents/                    # 6 AI Agents
│   ├── price_predictor.py     # Dự đoán giá với AI enhancement
│   ├── ticker_news.py         # Tin tức cổ phiếu VN + International
│   ├── market_news.py         # Crawl CafeF.vn với fallback
│   ├── investment_expert.py   # Phân tích đầu tư cá nhân hóa
│   ├── risk_expert.py         # Đánh giá rủi ro thông minh
│   └── stock_info.py          # Hiển thị thông tin chi tiết
├── src/
│   ├── data/                  # Data layer
│   │   ├── vn_stock_api.py    # VNStock API integration
│   │   └── crewai_collector.py # CrewAI real news
│   ├── ui/                    # UI components
│   │   ├── styles.py          # Custom CSS với Bootstrap
│   │   └── components.py      # UI components
│   └── utils/                 # Utilities
│       ├── error_handler.py   # Error handling
│       └── helpers.py         # Helper functions
├── gemini_agent.py           # Gemini AI với offline fallback
├── main_agent.py             # Main orchestrator
├── api.py                    # FastAPI backend
└── app.py                    # Streamlit frontend (6 tabs)
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
```bash
streamlit run app.py
```

### 4. Cấu hình API (trong ứng dụng)
- Mở sidebar
- Nhập **Gemini API key** (miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey))
- Nhập **Serper API key** (tùy chọn, tại [Serper.dev](https://serper.dev/api-key))
- Click **"🔧 Cài đặt Gemini"**

## 📱 Giao diện 6 Tabs chuyên nghiệp

### **Tab 1: 📊 Phân tích cổ phiếu**
- **🚀 Phân tích toàn diện**: Tất cả 6 agents
- **📈 Dự đoán giá**: PricePredictor với AI enhancement
- **⚠️ Đánh giá rủi ro**: RiskExpert với phân tích thông minh
- **💼 Phân tích đầu tư**: InvestmentExpert với khuyến nghị cá nhân hóa

### **Tab 2: 💬 AI Chatbot** ⭐ **MỚI CẢI TIẾN**
- **Giao diện đẹp mắt**: Gradient header, card styling chuyên nghiệp
- **Gợi ý câu hỏi**: 5 câu hỏi mẫu thông dụng
- **Phản hồi thông minh**: Format tự động với màu sắc và icon
- **Offline fallback**: Vẫn trả lời khi hết quota API
- **Timestamp & disclaimer**: Thông tin minh bạch

### **Tab 3: 📈 Thị trường VN**
- **VN-Index**: Dữ liệu real-time với color coding
- **Top movers**: Tăng/giảm mạnh với styling đẹp
- **Danh sách cổ phiếu**: CrewAI real-time hoặc static fallback

### **Tab 4: 📰 Tin tức cổ phiếu**
- **TickerNews Agent**: Tin tức theo mã cổ phiếu
- **AI sentiment analysis**: Phân tích tâm lý thị trường
- **Priority highlighting**: Tin quan trọng được đánh dấu

### **Tab 5: 🏢 Thông tin công ty**
- **Company overview**: Thông tin chi tiết công ty
- **CrewAI integration**: Dữ liệu thật từ AI
- **Enhanced display**: Styling chuyên nghiệp

### **Tab 6: 🌍 Tin tức thị trường**
- **MarketNews Agent**: Crawl từ CafeF.vn
- **Risk-based filtering**: Tin tức theo hồ sơ rủi ro
- **Underground news**: Tin nội gián cho trader mạo hiểm

## ⚙️ Cài đặt đầu tư cá nhân

### **🕐 Thời gian đầu tư:**
- **Ngắn hạn**: 1-3 tháng
- **Trung hạn**: 3-12 tháng  
- **Dài hạn**: 1+ năm

### **⚠️ Mức độ rủi ro (0-100):**
- **0-30**: 🟢 Thận trọng
- **31-70**: 🟡 Cân bằng
- **71-100**: 🔴 Mạo hiểm

### **💰 Số tiền đầu tư:**
- Từ 1 triệu đến 10 tỷ VND
- Tự động tính toán position sizing
- Stop-loss và take-profit thông minh

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

### 🏦 Ngân hàng
**VCB** • **BID** • **CTG** • **TCB** • **ACB**

### 🏢 Bất động sản  
**VIC** • **VHM** • **VRE** • **DXG**

### 🛒 Tiêu dùng
**MSN** • **MWG** • **VNM** • **SAB**

### 🏭 Công nghiệp
**HPG** • **GAS** • **PLX**

### 💻 Công nghệ
**FPT**

## 💻 Sử dụng API

### Phân tích cổ phiếu
```python
from main_agent import MainAgent
from src.data.vn_stock_api import VNStockAPI

# Initialize
vn_api = VNStockAPI()
main_agent = MainAgent(vn_api, gemini_api_key="your_key")

# Analyze
result = await main_agent.analyze_stock('VCB')
```

### Gemini Chatbot
```python
from gemini_agent import UnifiedAIAgent

# Initialize với fallback
gemini = UnifiedAIAgent(gemini_api_key="your_key")

# Chat với offline fallback
response = gemini.generate_expert_advice("Phân tích VCB")
```

## 📋 Requirements chính

```
streamlit>=1.28.0
fastapi>=0.104.0
google-generativeai>=0.3.0
vnstock>=3.2.0
crewai[tools]>=0.117.0
plotly>=5.17.0
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

### FastAPI Endpoints
```bash
# Set API key
curl -X POST "http://localhost:8000/set-gemini-key" \
     -d '{"api_key": "your_key"}'

# Analyze stock
curl -X POST "http://localhost:8000/analyze" \
     -d '{"symbol": "VCB"}'
```

## 🎨 Giao diện mới

### Cải tiến Tab 2 (AI Chatbot):
- **Header gradient** với typography đẹp
- **Sample questions** để hướng dẫn user
- **Text area** thay vì input box
- **Color-coded responses** với icon
- **Enhanced error handling** với styling đẹp
- **Timestamp & model info** minh bạch

### Styling chuyên nghiệp:
- Bootstrap integration
- Gradient backgrounds
- Card-based layout
- Responsive design
- Professional color scheme

## ⚠️ Disclaimer

> **Cảnh báo quan trọng**: Đây là công cụ hỗ trợ phân tích, **KHÔNG PHẢI lời khuyên đầu tư**.

- Dữ liệu có thể không chính xác 100%
- Luôn thực hiện nghiên cứu riêng (DYOR)
- Chỉ đầu tư số tiền có thể chấp nhận mất
- Tác giả không chịu trách nhiệm về tổn thất tài chính

## 🔍 Troubleshooting

### Lỗi thường gặp:

**1. Gemini API Error:**
```bash
# Kiểm tra API key tại: https://aistudio.google.com/apikey
# Đảm bảo API key có quyền truy cập Gemini
```

**2. Hết quota API:**
```
✅ Hệ thống tự động chuyển sang offline mode
✅ Vẫn nhận được phản hồi hữu ích
⏰ Quota reset sau 24 giờ
```

**3. Import Error:**
```bash
pip install -r requirements.txt --force-reinstall
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes  
4. Push và tạo Pull Request

## 📞 Hỗ trợ

- 🐛 **Issues**: [GitHub Issues](https://github.com/nminduo2k5/agentvnstock/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/nminduo2k5/agentvnstock/discussions)

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev) - AI chatbot với offline fallback
- [vnstock](https://github.com/thinh-vu/vnstock) - Vietnamese stock data
- [Streamlit](https://streamlit.io) - Beautiful web framework
- [FastAPI](https://fastapi.tiangolo.com) - Modern API framework

---

<div align="center">

**🇻🇳 Made with ❤️ for Vietnamese investors**

[![Star this repo](https://img.shields.io/github/stars/nminduo2k5/agentvnstock?style=social)](https://github.com/nminduo2k5/agentvnstock)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**🚀 Version 2.1 - Enhanced AI Trading System with Offline Fallback**

*"Còn thở là còn gỡ, dừng lại là thất bại!"* 💪

</div>