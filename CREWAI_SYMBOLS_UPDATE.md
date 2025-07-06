# 🤖 CrewAI Stock Symbols Integration

## 📋 Tổng quan thay đổi

Đã cập nhật hệ thống để **sử dụng CrewAI lấy danh sách cổ phiếu thật** thay vì phụ thuộc vào vnstock.

## 🔧 Các thay đổi chính

### 1. CrewAI Data Collector (`src/data/crewai_collector.py`)
- ✅ Thêm method `get_available_symbols()` 
- ✅ Sử dụng CrewAI agents để tìm kiếm cổ phiếu thật từ cafef.vn, vneconomy.vn
- ✅ Cache kết quả 1 giờ để tối ưu performance
- ✅ Fallback sang danh sách tĩnh nếu CrewAI fail

### 2. VN Stock API (`src/data/vn_stock_api.py`)
- ✅ Cập nhật `get_available_symbols()` để ưu tiên CrewAI
- ✅ Mở rộng danh sách cổ phiếu tĩnh từ 18 lên 40+ mã
- ✅ Thêm nhiều ngành: Healthcare, Transportation, Food & Beverage
- ✅ Tên công ty đầy đủ bằng tiếng Việt

### 3. User Interface Updates
- ✅ `app.py`: Hiển thị "CrewAI Real Data" trong tiêu đề
- ✅ `dashboard.py`: Cập nhật UI indicators
- ✅ Thêm status indicators cho data source
- ✅ Footer cập nhật: "Powered by CrewAI" thay vì "vnstock"

## 🎯 Cách hoạt động

### Khi có API keys:
1. CrewAI tìm kiếm top 50 cổ phiếu có thanh khoản cao
2. Ưu tiên blue-chip: VCB, BID, VIC, HPG, FPT
3. Lấy thông tin: Mã, Tên, Ngành, Sàn giao dịch
4. Cache kết quả 1 giờ

### Khi không có API keys:
1. Sử dụng danh sách tĩnh mở rộng (40+ mã)
2. Hiển thị thông báo khuyến khích nhập API key
3. Vẫn đảm bảo ứng dụng hoạt động bình thường

## 📊 Danh sách cổ phiếu mở rộng

### 🏦 Banking (8 mã)
VCB, BID, CTG, TCB, ACB, MBB, VPB, STB

### 🏢 Real Estate (6 mã)  
VIC, VHM, VRE, DXG, NVL, KDH

### 🛒 Consumer & Retail (6 mã)
MSN, MWG, VNM, SAB, PNJ, FRT

### 🏭 Industrial & Materials (4 mã)
HPG, HSG, NKG, SMC

### ⚡ Utilities & Energy (4 mã)
GAS, PLX, POW, NT2

### 💻 Technology (3 mã)
FPT, CMG, ELC

### 🚁 Transportation (3 mã)
VJC, HVN, GMD

### 🏥 Healthcare & Pharma (3 mã)
DHG, IMP, DBD

## 🧪 Testing

Chạy test script:
```bash
python test_crewai_symbols.py
```

## 🔑 API Keys cần thiết

### Bắt buộc:
- **GOOGLE_API_KEY**: Gemini API từ https://aistudio.google.com/apikey

### Tùy chọn:
- **SERPER_API_KEY**: Serper API từ https://serper.dev/api-key

## 🎨 UI Improvements

### Status Indicators:
- 🟢 **CrewAI Real Data**: Khi có API keys và CrewAI hoạt động
- 📋 **Static List**: Khi không có API keys hoặc CrewAI fail
- ⚠️ **Warning**: Khi có lỗi tải danh sách

### User Experience:
- Hiển thị rõ nguồn dữ liệu
- Khuyến khích nhập API key để có dữ liệu thật
- Graceful fallback khi CrewAI không khả dụng

## 🚀 Benefits

1. **Real Data**: Danh sách cổ phiếu cập nhật từ nguồn thật
2. **Performance**: Cache 1 giờ giảm API calls
3. **Reliability**: Fallback đảm bảo ứng dụng luôn hoạt động
4. **User-friendly**: UI rõ ràng về nguồn dữ liệu
5. **Scalable**: Dễ mở rộng thêm nguồn dữ liệu khác

## 📝 Notes

- CrewAI cần cả Gemini và Serper API keys để hoạt động tối ưu
- Nếu chỉ có Gemini key, vẫn có thể hoạt động nhưng hạn chế
- Danh sách tĩnh đã được mở rộng đáng kể so với trước
- Tất cả thay đổi backward compatible

---

**🇻🇳 Made with ❤️ for Vietnamese investors**