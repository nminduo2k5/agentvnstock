# 🔥 HỆ THỐNG TIN TỨC NGẦM QUỐC TẾ - DUONG AI TRADING PRO

## 📋 TỔNG QUAN

Hệ thống tin tức ngầm quốc tế được thiết kế để cung cấp thông tin đầu tư từ nhiều nguồn khác nhau, được phân loại theo hồ sơ rủi ro của nhà đầu tư.

## 🎯 PHÂN LOẠI THEO HỒ SƠ RỦI RO

### 🛡️ THẬN TRỌNG (≤ 30%)
- **Loại tin:** Chỉ tin tức chính thống
- **Nguồn:** Bloomberg, Financial Times, Reuters, CafeF
- **Đặc điểm:** Tin tức đã được xác minh từ các tổ chức tài chính uy tín
- **Cảnh báo:** Không hiển thị tin ngầm

### ⚖️ CÂN BẰNG (31-70%)
- **Loại tin:** Chỉ tin tức chính thống
- **Nguồn:** Bloomberg, Financial Times, Reuters, CafeF
- **Đặc điểm:** Tập trung vào phân tích cơ bản và xu hướng dài hạn
- **Cảnh báo:** Không hiển thị tin ngầm

### 🚀 MẠO HIỂM (> 70%)
- **Loại tin:** Tin ngầm + Tin chính thống
- **Nguồn:** Reddit, Twitter, Bloomberg, Financial Times, Reuters
- **Đặc điểm:** Bao gồm cả thông tin từ cộng đồng và tin chính thống
- **Cảnh báo:** Luôn xác minh thông tin trước khi đầu tư

## 🌍 NGUỒN TIN NGẦM QUỐC TẾ

### 📱 REDDIT SOURCES
- **r/stocks** - Thảo luận về cổ phiếu cá nhân
- **r/investing** - Chiến lược đầu tư dài hạn
- **r/financialindependence** - Độc lập tài chính
- **r/worldnews** - Tin tức thế giới ảnh hưởng thị trường
- **r/geopolitics** - Địa chính trị và tác động kinh tế

### 🐦 TWITTER SOURCES
- **@unusual_whales** - Phân tích dòng tiền và options
- **@zerohedge** - Tin tức tài chính và cảnh báo rủi ro
- **@chigrl** - Phân tích kỹ thuật và momentum

### 📰 TIN CHÍNH THỐNG
- **Bloomberg** - Tin tức tài chính hàng đầu
- **Financial Times** - Phân tích kinh tế toàn cầu
- **Reuters Business** - Tin tức doanh nghiệp quốc tế
- **CafeF International** - Tin tức quốc tế bằng tiếng Việt

## 🔧 KIẾN TRÚC HỆ THỐNG

### 📁 Files Chính
```
agents/
├── international_underground_news.py  # Agent crawl tin ngầm quốc tế
├── international_news.py              # Agent tin tức quốc tế chính
├── risk_based_news.py                 # Agent tin ngầm Việt Nam
└── market_news.py                     # Agent tin tức VN chính
```

### 🔄 Luồng Xử Lý
1. **Nhận hồ sơ rủi ro** từ sidebar
2. **Xác định loại tin** cần hiển thị
3. **Crawl dữ liệu** từ các nguồn phù hợp
4. **AI phân tích** sentiment và risk assessment
5. **Hiển thị** với màu sắc và cảnh báo phù hợp

## 🎨 GIAO DIỆN NGƯỜI DÙNG

### 📊 Tab 3: Tin tức Việt Nam
- Hiển thị tin tức VN theo hồ sơ rủi ro
- Nguồn: F319, F247, CafeF, VnEconomy
- Màu sắc: 🔥 Đỏ (ngầm), 📰 Xanh (chính thống)

### 🌍 Tab 6: Tin tức Quốc tế
- Hiển thị tin tức quốc tế theo hồ sơ rủi ro
- Nguồn: Reddit, Twitter, Bloomberg, Reuters
- Màu sắc: 🔥 Đỏ (ngầm), 📰 Xanh (premium), 🌍 Tím (quốc tế)

## 🤖 TÍCH HỢP AI

### 🧠 AI Analysis Features
- **Market Sentiment:** BULLISH/BEARISH/NEUTRAL
- **Risk Assessment:** HIGH_RISK/MODERATE_RISK/LOW_RISK
- **Impact Analysis:** Tác động đến thị trường VN
- **Recommendation:** Khuyến nghị theo hồ sơ rủi ro

### 📈 Enhanced Display
- **Crawl Summary:** Thống kê nguồn tin
- **AI Reasoning:** Giải thích logic phân tích
- **Risk Warnings:** Cảnh báo phù hợp với từng loại tin
- **Source Reliability:** Đánh giá độ tin cậy nguồn

## ⚠️ CẢNH BÁO VÀ LƯU Ý

### 🚨 Tin Ngầm (Underground)
- **Reddit/Twitter:** "Thông tin từ mạng xã hội - Luôn DYOR trước khi đầu tư!"
- **Độ tin cậy:** Medium - Community-driven
- **Khuyến nghị:** Chỉ dành cho nhà đầu tư có kinh nghiệm

### ✅ Tin Chính Thống (Official)
- **Bloomberg/Reuters:** "Nguồn tin uy tín từ tổ chức tài chính hàng đầu"
- **Độ tin cậy:** Very High
- **Khuyến nghị:** Phù hợp cho mọi nhà đầu tư

## 🔮 TÍNH NĂNG NÂNG CAO

### 📊 Real-time Crawling
- Crawl dữ liệu thời gian thực từ Reddit API
- Simulate Twitter data (do API restrictions)
- Cache và optimize performance

### 🎯 Personalization
- Lọc tin theo hồ sơ rủi ro
- Khuyến nghị đọc tin cá nhân hóa
- Cảnh báo phù hợp với từng nhóm đối tượng

### 📈 Analytics
- Thống kê nguồn tin
- Phân tích sentiment tổng thể
- Đánh giá tác động thị trường

## 🚀 HƯỚNG DẪN SỬ DỤNG

### 1. Thiết lập Hồ sơ Rủi ro
- Điều chỉnh thanh trượt "Mức độ rủi ro chấp nhận"
- Chọn thời gian đầu tư
- Nhập số tiền đầu tư

### 2. Xem Tin tức
- **Tab 3:** Tin tức Việt Nam
- **Tab 6:** Tin tức Quốc tế
- Click "🔄 Cập nhật tin tức" để tải dữ liệu mới

### 3. Phân tích AI
- Xem phân tích AI trong expander "🧠 Phân tích AI"
- Đọc khuyến nghị trong "💡 Khuyến nghị đọc tin"
- Kiểm tra "📊 Tóm tắt nguồn tin"

## 🔧 TECHNICAL DETAILS

### Dependencies
```python
import aiohttp          # Async HTTP requests
import asyncio          # Async programming
import BeautifulSoup    # HTML parsing
import requests         # HTTP requests
```

### API Integration
- **Reddit API:** JSON format crawling
- **Twitter API:** Simulated data (requires auth)
- **News APIs:** Direct HTML parsing
- **AI APIs:** Gemini integration

### Performance Optimization
- Async crawling for multiple sources
- Request rate limiting
- Error handling and fallbacks
- Caching mechanisms

## 📞 SUPPORT

Hệ thống được thiết kế để hoạt động tự động với fallback mechanisms. Nếu có lỗi:

1. **Crawling fails:** Sử dụng dữ liệu mô phỏng
2. **AI fails:** Hiển thị phân tích cơ bản
3. **Network issues:** Fallback to cached data

---

**🇻🇳 DUONG AI TRADING PRO - Phiên bản 2.0**
*Hệ thống phân tích cổ phiếu chuyên nghiệp với AI và dữ liệu thời gian thực*