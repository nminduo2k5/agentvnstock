# 🇻🇳 AI Trading Team Vietnam

Hệ thống phân tích đầu tư chứng khoán Việt Nam với 3 AI Agents chuyên nghiệp, sử dụng Google GenAI để mô phỏng cuộc thảo luận thực tế của một investment team.

![AI Trading Team Vietnam](https://img.shields.io/badge/Vietnam-Stock%20Market-red?style=for-the-badge&logo=vietnam)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Google AI](https://img.shields.io/badge/Google_AI-Gemini-4285F4?style=for-the-badge&logo=google)

## 🌟 Tính năng chính

### 👥 3 AI Agents chuyên nghiệp
- **🔍 Nguyễn Minh Anh** - Senior Market Analyst (CFA, 8 năm kinh nghiệm)
- **⚠️ Trần Quốc Bảo** - Senior Risk Manager (FRM, 12 năm kinh nghiệm)  
- **💼 Lê Thị Mai** - Portfolio Manager (MBA INSEAD, 10 năm quản lý fund)

### 🚀 Tính năng nổi bật
- ✅ **Real-time Analysis**: Phân tích real-time với dữ liệu thị trường VN
- ✅ **Multi-Agent Discussion**: Agents tương tác và tranh luận như team thật
- ✅ **Vietnamese Market Focus**: Tối ưu hoá cho HOSE, HNX, UPCOM
- ✅ **Risk Management**: Tích hợp position sizing và risk assessment
- ✅ **Beautiful UI**: Giao diện đẹp với Streamlit
- ✅ **Export Results**: Xuất phân tích dưới dạng JSON

## 🏗️ Hình ảnh minh họa

![alt text](image.png)

## 🚀 Quick Start

### 1. Cài đặt Dependencies

```bash
# Clone repository
git https://github.com/huudatscience/Agent-to-agent-ai-trading-vietnam
cd Agent-to-agent-ai-trading-vietnam

# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Lấy Google GenAI API Key

1. Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Đăng nhập với Google account
3. Tạo API key mới
4. Copy và giữ bí mật API key

### 3. Chạy ứng dụng

```bash
streamlit run app.py
```

### 4. Sử dụng

1. Mở browser tại `http://localhost:8501`
2. Nhập Google GenAI API key ở sidebar
3. Chọn cổ phiếu muốn phân tích
4. Thiết lập số tiền và mức độ rủi ro
5. Bấm "🚀 Bắt đầu phân tích"
6. Xem cuộc thảo luận của AI team

## 📊 Supported Stocks

Hệ thống hỗ trợ các bluechips chính của thị trường Việt Nam:

### 🏦 Banking
- **VCB** - Vietcombank
- **BID** - BIDV  
- **CTG** - VietinBank
- **TCB** - Techcombank
- **ACB** - ACB

### 🏢 Real Estate
- **VIC** - Vingroup
- **VHM** - Vinhomes
- **VRE** - Vincom Retail
- **DXG** - Dat Xanh Group

### 🛒 Consumer
- **MSN** - Masan Group
- **MWG** - Mobile World
- **VNM** - Vinamilk
- **SAB** - Sabeco

### 🏭 Industrial & Utilities
- **HPG** - Hoa Phat Group
- **GAS** - PetroVietnam Gas
- **PLX** - Petrolimex

### 💻 Technology  
- **Phenikaa** - Trường Công nghệ thông tin, Phenikaa University

## 🆘 Support & Contact

- **GitHub Issues**: [Report bugs và feature requests](https://github.com/huudatscience)
- **Email**: dat.nguyenhuu@phenikaa-uni.edu.vn
- **Documentation**: [Xem docs đầy đủ](https://huudatscience.github.io/)