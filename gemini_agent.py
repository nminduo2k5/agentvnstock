import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiAgent:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        
        try:
            genai.configure(api_key=api_key)
            model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            self.model = genai.GenerativeModel(model_name)
            # Test the connection
            self.model.generate_content("Hello")
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini: {str(e)}")
    
    def generate_expert_advice(self, query: str, symbol: str = None, data: dict = None):
        """Generate expert financial advice using Gemini"""
        
        # Build context prompt
        # Enhanced context with comprehensive analysis
        context = f"""
Bạn là một chuyên gia tài chính hàng đầu với 20 năm kinh nghiệm đầu tư chứng khoán tại Việt Nam và quốc tế.
Hãy phân tích sâu sắc và đưa ra lời khuyên chuyên nghiệp nhất.

CÂU HỎI: {query}
MÃ CỔ PHIẾU: {symbol if symbol else 'Không có'}
"""
        
        if data:
            context += f"\nDỮ LIỆU PHÂN TÍCH CHI TIẾT:\n{self._format_data_for_ai(data)}\n"
        
        context += f"""
YÊU CẦU PHÂN TÍCH CHUYÊN SÂU:
1. 📊 PHÂN TÍCH KỸ THUẬT: Đánh giá xu hướng, momentum, support/resistance
2. 💰 PHÂN TÍCH CƠ BẢN: P/E, P/B, tăng trưởng, tài chính
3. 📈 PHÂN TÍCH THỊ TRƯỜNG: Vị thế ngành, triển vọng, rủi ro vĩ mô
4. ⚖️ ĐÁNH GIÁ RỦI RO: Mức độ rủi ro, khả năng chịu đựng
5. 🎯 CHIẾN LƯỢC ĐẦU TƯ: Ngắn hạn vs dài hạn, timing
6. 💡 KHUYẾN NGHỊ CỤ THỂ: Mua/Bán/Giữ với lý do rõ ràng

HÃY TRẢ LỜI THEO FORMAT SAU:

PHÂN TÍCH CHUYÊN SÂU:
[Phân tích toàn diện từ nhiều góc độ, sử dụng dữ liệu cụ thể]

KẾT LUẬN & KHUYẾN NGHỊ:
[Kết luận rõ ràng: NÊN/KHÔNG NÊN đầu tư với lý do thuyết phục]

HÀNH ĐỘNG CỤ THỂ:
- [Danh sách 4-5 hành động cụ thể]

CẢNH BÁO RỦI RO:
[Những rủi ro quan trọng cần lưu ý]

Lưu ý: Trả lời bằng tiếng Việt, dựa trên dữ liệu thực tế, không đưa lời khuyên tuyệt đối.
"""
        
        try:
            # Generate content with safety settings
            response = self.model.generate_content(
                context,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            if response.text:
                return self._parse_response(response.text)
            else:
                return {
                    "expert_advice": "Xin lỗi, tôi không thể tạo phản hồi cho câu hỏi này.",
                    "recommendations": ["Thử đặt câu hỏi khác", "Kiểm tra nội dung câu hỏi"]
                }
                
        except Exception as e:
            error_msg = str(e)
            if "API_KEY" in error_msg.upper():
                return {
                    "expert_advice": "Lỗi API Key: Vui lòng kiểm tra GOOGLE_API_KEY trong file .env",
                    "recommendations": ["Kiểm tra API key", "Thử tạo API key mới"]
                }
            elif "QUOTA" in error_msg.upper() or "LIMIT" in error_msg.upper():
                return {
                    "expert_advice": "Lỗi giới hạn API: Đã vượt quá giới hạn sử dụng",
                    "recommendations": ["Chờ vài phút rồi thử lại", "Kiểm tra quota API"]
                }
            else:
                return {
                    "expert_advice": f"Lỗi hệ thống: {error_msg}",
                    "recommendations": ["Thử lại sau", "Liên hệ hỗ trợ nếu vấn đề tiếp tục"]
                }
    
    def _parse_response(self, response_text: str):
        """Parse enhanced Gemini response"""
        try:
            # Parse different sections
            sections = {
                'analysis': '',
                'conclusion': '',
                'actions': [],
                'risks': ''
            }
            
            # Split by sections
            if "PHÂN TÍCH CHUYÊN SÂU:" in response_text:
                parts = response_text.split("PHÂN TÍCH CHUYÊN SÂU:")
                if len(parts) > 1:
                    remaining = parts[1]
                    
                    # Extract analysis
                    if "KẾT LUẬN & KHUYẾN NGHỊ:" in remaining:
                        analysis_part = remaining.split("KẾT LUẬN & KHUYẾN NGHỊ:")[0].strip()
                        sections['analysis'] = analysis_part
                        remaining = remaining.split("KẾT LUẬN & KHUYẾN NGHỊ:")[1]
                    
                    # Extract conclusion
                    if "HÀNH ĐỘNG CỤ THỂ:" in remaining:
                        conclusion_part = remaining.split("HÀNH ĐỘNG CỤ THỂ:")[0].strip()
                        sections['conclusion'] = conclusion_part
                        remaining = remaining.split("HÀNH ĐỘNG CỤ THỂ:")[1]
                    
                    # Extract actions
                    if "CẢNH BÁO RỦI RO:" in remaining:
                        actions_part = remaining.split("CẢNH BÁO RỦI RO:")[0].strip()
                        sections['risks'] = remaining.split("CẢNH BÁO RỦI RO:")[1].strip()
                    else:
                        actions_part = remaining.strip()
                    
                    # Parse actions list
                    for line in actions_part.split('\n'):
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                            sections['actions'].append(line[1:].strip())
                        elif line and len(line) > 15 and not line.startswith('CẢNH BÁO'):
                            sections['actions'].append(line)
            
            # Format comprehensive response
            expert_advice = f"""
📊 **PHÂN TÍCH CHUYÊN SÂU:**
{sections['analysis']}

🎯 **KẾT LUẬN & KHUYẾN NGHỊ:**
{sections['conclusion']}

⚠️ **CẢNH BÁO RỦI RO:**
{sections['risks'] if sections['risks'] else 'Luôn có rủi ro trong đầu tư. Chỉ đầu tư số tiền có thể chấp nhận mất.'}
""".strip()
            
            return {
                "expert_advice": expert_advice,
                "recommendations": sections['actions'][:5] if sections['actions'] else [
                    "Nghiên cứu kỹ báo cáo tài chính",
                    "Theo dõi tin tức ngành", 
                    "Đặt lệnh stop-loss",
                    "Đa dạng hóa danh mục",
                    "Chỉ đầu tư tiền nhàn rỗi"
                ]
            }
                
        except Exception as e:
            # Fallback parsing
            return {
                "expert_advice": f"📈 **PHÂN TÍCH:**\n{response_text}\n\n⚠️ **LƯU Ý:** Đây chỉ là tham khảo, không phải lời khuyên đầu tư tuyệt đối.",
                "recommendations": [
                    "Nghiên cứu thêm từ nhiều nguồn",
                    "Tham khảo chuyên gia tài chính",
                    "Đánh giá khả năng tài chính cá nhân",
                    "Chỉ đầu tư số tiền có thể chấp nhận mất"
                ]
            }
    
    def _format_data_for_ai(self, data: dict) -> str:
        """Format data for AI analysis"""
        if not data:
            return "Không có dữ liệu cụ thể"
        
        formatted = []
        
        # VN Stock Data
        if 'vn_stock_data' in data and data['vn_stock_data']:
            vn_data = data['vn_stock_data']
            formatted.append(f"📈 THÔNG TIN CỔ PHIẾU:")
            formatted.append(f"- Giá hiện tại: {vn_data.price:,} VND")
            formatted.append(f"- Thay đổi: {vn_data.change:+,} VND ({vn_data.change_percent:+.2f}%)")
            formatted.append(f"- Khối lượng: {vn_data.volume:,}")
            formatted.append(f"- Vốn hóa: {vn_data.market_cap:,} tỷ VND")
            formatted.append(f"- P/E: {vn_data.pe_ratio}, P/B: {vn_data.pb_ratio}")
            formatted.append(f"- Ngành: {vn_data.sector}, Sàn: {vn_data.exchange}")
        
        # Price Prediction
        if 'price_prediction' in data and data['price_prediction']:
            pred = data['price_prediction']
            formatted.append(f"\n🔮 DỰ ĐOÁN GIÁ:")
            formatted.append(f"- Xu hướng: {pred.get('trend', 'N/A')}")
            formatted.append(f"- Giá dự đoán: {pred.get('predicted_price', 'N/A')}")
            formatted.append(f"- Độ tin cậy: {pred.get('confidence', 'N/A')}")
        
        # Risk Assessment
        if 'risk_assessment' in data and data['risk_assessment']:
            risk = data['risk_assessment']
            formatted.append(f"\n⚠️ ĐÁNH GIÁ RỦI RO:")
            formatted.append(f"- Mức rủi ro: {risk.get('risk_level', 'N/A')}")
            formatted.append(f"- Độ biến động: {risk.get('volatility', 'N/A')}%")
            formatted.append(f"- Beta: {risk.get('beta', 'N/A')}")
            formatted.append(f"- Max Drawdown: {risk.get('max_drawdown', 'N/A')}%")
        
        # Investment Analysis
        if 'investment_analysis' in data and data['investment_analysis']:
            inv = data['investment_analysis']
            formatted.append(f"\n💼 PHÂN TÍCH ĐẦU TƯ:")
            formatted.append(f"- Khuyến nghị: {inv.get('recommendation', 'N/A')}")
            formatted.append(f"- Lý do: {inv.get('reason', 'N/A')}")
            formatted.append(f"- Cổ tức: {inv.get('dividend_yield', 'N/A')}%")
        
        return "\n".join(formatted) if formatted else "Dữ liệu không đầy đủ để phân tích"