import google.generativeai as genai
import os
import logging
from typing import Dict, Any, Optional, List
import asyncio
import json
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class UnifiedAIAgent:
    def __init__(self, gemini_api_key: str = None):
        """
        Initialize AI Agent with Gemini AI
        """
        self.available_models = {}
        self.current_model_name = None
        self.model_capabilities = {
            'gemini': {
                'strengths': ['analysis', 'vietnamese', 'reasoning', 'financial_advice', 'prediction', 'technical_analysis', 'news_analysis', 'risk_assessment'],
                'speed': 'fast',
                'cost': 'free'
            }
        }
        
        # Initialize Gemini with user-provided API key only
        # No hardcoded or environment variables used
        
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                
                # Try different model names (Google đã update)
                model_names = [
                    'gemini-1.5-flash',     # Model mới nhất
                    'gemini-1.5-pro',       # Pro version
                    'gemini-1.0-pro',       # Fallback
                    'models/gemini-1.5-flash',  # With prefix
                    'models/gemini-1.0-pro'     # With prefix fallback
                ]
                
                model_initialized = False
                for model_name in model_names:
                    try:
                        model = genai.GenerativeModel(model_name)
                        # Test the model with a simple request
                        test_response = model.generate_content("Hello")
                        if test_response and test_response.text:
                            self.available_models['gemini'] = model
                            self.gemini_api_key = gemini_api_key
                            self.current_model_name = model_name
                            logger.info(f"✅ Gemini AI initialized with model: {model_name}")
                            model_initialized = True
                            break
                    except Exception as e:
                        logger.warning(f"⚠️ Model {model_name} not available: {e}")
                        continue
                
                if not model_initialized:
                    # If no model works, raise error
                    raise Exception("No available Gemini models found")
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
                # Don't set available_models if initialization failed
                self.available_models = {}
        
        if not self.available_models:
            raise ValueError("Gemini AI must be configured.")
    
    def test_connection(self):
        """Test AI API connections"""
        results = {}
        
        if 'gemini' in self.available_models:
            try:
                response = self.available_models['gemini'].generate_content("Test")
                if response and response.text:
                    results['gemini'] = True
                    logger.info("✅ Gemini connection test passed")
                else:
                    results['gemini'] = False
                    logger.error("❌ Gemini returned empty response")
            except Exception as e:
                results['gemini'] = False
                logger.error(f"❌ Gemini connection test failed: {str(e)}")
        
        if not any(results.values()):
            raise ValueError("Gemini API connection test failed")
        
        return results
    
    def select_best_model(self, task_type: str) -> str:
        """
        Select the best available model for a specific task type
        """
        if 'gemini' in self.available_models:
            return 'gemini'
        
        raise ValueError("Gemini AI model not available")
    
    def generate_with_model(self, prompt: str, model_name: str, max_tokens: int = 1000) -> str:
        """
        Generate response using specified AI model
        """
        try:
            if model_name == 'gemini' and 'gemini' in self.available_models:
                response = self.available_models['gemini'].generate_content(prompt)
                return response.text

            else:
                raise ValueError(f"Model {model_name} not available.")
                
        except Exception as e:
            logger.error(f"Error generating with {model_name}: {str(e)}")
            raise
    
    def generate_with_fallback(self, prompt: str, task_type: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate response with automatic fallback to offline mode if primary fails
        """
        try:
            response = self.generate_with_model(prompt, 'gemini', max_tokens)
            return {
                'response': response,
                'model_used': 'gemini',
                'success': True
            }
        except Exception as e:
            logger.error(f"Gemini model failed: {str(e)}")
            # Check if it's a quota/rate limit error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['quota', 'rate limit', 'exceeded', 'limit']):
                # Use offline fallback for quota issues
                return self._generate_offline_fallback(prompt, task_type)
            else:
                return {
                    'response': f'Gemini AI failed: {str(e)}',
                    'model_used': None,
                    'success': False,
                    'error': str(e)
                }
    
    def _generate_offline_fallback(self, prompt: str, task_type: str) -> Dict[str, Any]:
        """
        Generate offline fallback response when API quota is exhausted
        """
        try:
            # Extract key information from prompt
            if 'CÂU HỎI:' in prompt:
                question = prompt.split('CÂU HỎI:')[1].split('MÃ CỔ PHIẾU:')[0].strip()
            else:
                question = prompt[:200] + '...' if len(prompt) > 200 else prompt
            
            # Generate contextual offline response based on task type
            if task_type == 'financial_advice':
                response = self._generate_financial_advice_fallback(question)
            elif task_type == 'general_query':
                response = self._generate_general_fallback(question)
            else:
                response = self._generate_default_fallback(question)
            
            return {
                'response': response,
                'model_used': 'offline_fallback',
                'success': True,
                'quota_exceeded': True
            }
        except Exception as e:
            return {
                'response': f'Offline fallback failed: {str(e)}',
                'model_used': 'offline_fallback',
                'success': False,
                'error': str(e)
            }
    
    def _generate_financial_advice_fallback(self, question: str) -> str:
        """
        Generate financial advice fallback when API quota exceeded
        """
        return f"""
PHÂN TÍCH CHUYÊN SÂU:
Do Gemini API đã hết quota, hệ thống chuyển sang chế độ offline. Đây là phân tích cơ bản dựa trên nguyên tắc đầu tư:

📊 **Nguyên tắc phân tích kỹ thuật:**
- Xem xét xu hướng giá trong 20-50 phiên gần nhất
- Kiểm tra khối lượng giao dịch và momentum
- Xác định vùng hỗ trợ và kháng cự

💰 **Nguyên tắc phân tích cơ bản:**
- P/E < 15 thường được coi là hấp dẫn
- P/B < 2 cho thấy định giá hợp lý
- Tăng trưởng doanh thu ổn định qua các quý

KẾT LUẬN & KHUYẾN NGHỊ:
Không thể đưa ra khuyến nghị cụ thể do thiếu dữ liệu real-time. Khuyến nghị:
- Nghiên cứu kỹ báo cáo tài chính gần nhất
- Tham khảo ý kiến nhiều chuyên gia
- Chỉ đầu tư số tiền có thể chấp nhận mất

HÀNH ĐỘNG CỤ THỂ:
- Đợi API quota reset để có phân tích chi tiết
- Tham khảo các nguồn tin tức tài chính uy tín
- Xem xét tình hình thị trường tổng thể
- Đa dạng hóa danh mục đầu tư

CẢNH BÁO RỦI RO:
⚠️ **QUAN TRỌNG:** Đây là phân tích offline cơ bản do hết quota API. 
Không nên dựa vào đây để đưa ra quyết định đầu tư quan trọng.
Hãy đợi API reset hoặc tham khảo chuyên gia tài chính.
"""
    
    def _generate_general_fallback(self, question: str) -> str:
        """
        Generate general query fallback when API quota exceeded
        """
        return f"""
📈 **PHÂN TÍCH OFFLINE:**

Do Gemini API đã hết quota, tôi không thể phân tích chi tiết câu hỏi của bạn lúc này.

**Câu hỏi của bạn:** {question}

💡 **Gợi ý chung về đầu tư:**
- Luôn nghiên cứu kỹ trước khi đầu tư
- Đa dạng hóa danh mục để giảm rủi ro
- Chỉ đầu tư số tiền có thể chấp nhận mất
- Theo dõi tin tức và báo cáo tài chính
- Tham khảo ý kiến chuyên gia

⚠️ **LƯU Ý:** Để nhận được phân tích chi tiết và cá nhân hóa, 
vui lòng thử lại sau khi API quota được reset (thường là 24h).
"""
    
    def _generate_default_fallback(self, question: str) -> str:
        """
        Generate default fallback response
        """
        return f"""
🤖 **HỆ THỐNG OFFLINE:**

Xin lỗi, Gemini API đã hết quota nên tôi không thể phân tích chi tiết lúc này.

**Câu hỏi:** {question}

**Khuyến nghị:**
- Thử lại sau vài giờ khi quota reset
- Tham khảo các nguồn thông tin tài chính uy tín
- Liên hệ chuyên gia tài chính nếu cần tư vấn gấp

⏰ **Quota thường reset sau 24 giờ**
"""
    
    def generate_expert_advice(self, query: str, symbol: str = None, data: dict = None):
        """Generate expert financial advice using best available AI model with fallback"""
        
        # Detect query type for better handling
        query_type = self.detect_query_type(query)
        
        # Handle general questions without stock context
        if not symbol and query_type == "general":
            return self.generate_general_response(query)
        
        # Build comprehensive context for stock analysis
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
        
        # Use the new unified AI system with fallback
        try:
            result = self.generate_with_fallback(context, 'financial_advice', max_tokens=2048)
            
            if result['success']:
                parsed_response = self._parse_response(result['response'])
                
                # Add model info to response
                if result.get('fallback'):
                    parsed_response['expert_advice'] += f"\n\n🤖 **AI Model:** {result['model_used']} (fallback)"
                else:
                    parsed_response['expert_advice'] += f"\n\n🤖 **AI Model:** {result['model_used']}"
                
                return parsed_response
            else:
                # Check if quota exceeded
                if result.get('quota_exceeded'):
                    parsed_response = self._parse_response(result['response'])
                    parsed_response['expert_advice'] += "\n\n🤖 **AI Model:** Offline Fallback (Quota Exceeded)"
                    return parsed_response
                else:
                    return {
                        "expert_advice": f"❌ **LỖI AI SYSTEM:**\n{result.get('response', 'Không thể kết nối với AI models')}\n\n⚠️ **GỢI Ý:**\n- Kiểm tra API keys\n- Thử lại sau vài phút\n- Liên hệ hỗ trợ nếu vấn đề tiếp tục",
                        "recommendations": [
                            "Kiểm tra Gemini API key",
                            "Thử lại sau vài phút", 
                            "Liên hệ hỗ trợ kỹ thuật",
                            "Sử dụng chế độ offline"
                        ]
                    }
                
        except Exception as e:
            logger.error(f"Critical error in generate_expert_advice: {str(e)}")
            return {
                "expert_advice": f"❌ **LỖI NGHIÊM TRỌNG:**\n{str(e)}\n\n⚠️ Hệ thống AI tạm thời không khả dụng.",
                "recommendations": [
                    "Thử lại sau 5-10 phút",
                    "Kiểm tra kết nối internet",
                    "Liên hệ hỗ trợ kỹ thuật"
                ]
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
            formatted.append(f"- Giá mục tiêu: {inv.get('target_price', 'N/A')}")
        
        return "\n".join(formatted) if formatted else "Dữ liệu không đầy đủ để phân tích"
    
    def generate_general_response(self, query: str) -> dict:
        """Generate response for general questions using best available AI model"""
        try:
            # Enhanced context for general financial questions
            context = f"""
Bạn là một chuyên gia tài chính và đầu tư hàng đầu tại Việt Nam với 20+ năm kinh nghiệm.
Bạn có thể trả lời mọi câu hỏi về:
- Thị trường chứng khoán Việt Nam và quốc tế
- Phân tích kỹ thuật và cơ bản
- Chiến lược đầu tư và quản lý rủi ro
- Kinh tế vĩ mô và vi mô
- Các sản phẩm tài chính (cổ phiếu, trái phiếu, quỹ, forex)
- Lập kế hoạch tài chính cá nhân
- Thuế và pháp lý đầu tư
- Tâm lý học đầu tư
- Fintech và công nghệ tài chính

CÂU HỎI: {query}

HÃY TRẢ LỜI:
1. 📚 KIẾN THỨC CƠ BẢN: Giải thích khái niệm/vấn đề
2. 🎯 PHÂN TÍCH THỰC TẾ: Áp dụng vào thị trường VN
3. 💡 KHUYẾN NGHỊ: Lời khuyên cụ thể và thực tế
4. ⚠️ LƯU Ý: Rủi ro và điều cần chú ý

Trả lời bằng tiếng Việt, chuyên nghiệp nhưng dễ hiểu.
"""
            
            # Use unified AI system with fallback
            result = self.generate_with_fallback(context, 'general_query', max_tokens=2048)
            
            if result['success']:
                if result.get('quota_exceeded'):
                    # Quota exceeded, return offline response
                    return {
                        "expert_advice": f"📈 **PHÂN TÍCH OFFLINE:**\n{result['response']}\n\n🤖 **AI Model:** Offline Fallback (Quota Exceeded)\n\n⚠️ **LƯU Ý:** Đây là phản hồi offline do hết quota API.",
                        "recommendations": [
                            "Đợi quota reset (24h) để có phân tích chi tiết",
                            "Tham khảo các nguồn tin tức tài chính", 
                            "Liên hệ chuyên gia nếu cần tư vấn gấp",
                            "Chỉ đầu tư số tiền có thể chấp nhận mất"
                        ]
                    }
                else:
                    # Normal AI response
                    return {
                        "expert_advice": f"📈 **PHÂN TÍCH CHUYÊN GIA:**\n{result['response']}\n\n🤖 **AI Model:** {result['model_used']}\n\n⚠️ **LƯU Ý:** Đây là thông tin tham khảo, không phải lời khuyên đầu tư tuyệt đối.",
                        "recommendations": [
                            "Nghiên cứu thêm từ nhiều nguồn",
                            "Tham khảo chuyên gia tài chính", 
                            "Đánh giá khả năng tài chính cá nhân",
                            "Chỉ đầu tư số tiền có thể chấp nhận mất"
                        ]
                    }
            else:
                return self._get_fallback_response(query)
                
        except Exception as e:
            logger.error(f"Error in generate_general_response: {str(e)}")
            return self._get_fallback_response(query)
    
    def _get_fallback_response(self, query: str) -> dict:
        """Fallback response when Gemini fails"""
        return {
            "expert_advice": f"📈 **VỀ CÂU HỎI: {query}**\n\nXin lỗi, tôi không thể xử lý câu hỏi này lúc này. Vui lòng thử lại sau hoặc đặt câu hỏi khác.\n\n⚠️ **GỢI Ý:**\n- Kiểm tra kết nối internet\n- Thử đặt câu hỏi ngắn gọn hơn\n- Liên hệ hỗ trợ nếu vấn đề tiếp tục",
            "recommendations": [
                "Thử đặt câu hỏi khác",
                "Kiểm tra kết nối mạng",
                "Liên hệ hỗ trợ kỹ thuật"
            ]
        }
    
    def detect_query_type(self, query: str) -> str:
        """Detect if query is stock-specific or general"""
        query_lower = query.lower()
        
        # Stock symbols patterns
        stock_patterns = ['vcb', 'bid', 'ctg', 'vic', 'vhm', 'hpg', 'fpt', 'msn', 'mwg', 'gas', 'plx']
        
        # Check for stock symbols
        for pattern in stock_patterns:
            if pattern in query_lower:
                return "stock_specific"
        
        # Check for stock-related keywords
        stock_keywords = ['cổ phiếu', 'mã', 'ticker', 'stock', 'share']
        if any(keyword in query_lower for keyword in stock_keywords):
            return "stock_specific"
        
        return "general"
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get comprehensive API status information"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'available_models': list(self.available_models.keys()),
            'model_count': len(self.available_models),
            'capabilities': self.model_capabilities,
            'api_keys_configured': {}
        }
        
        # Check API key configuration
        status['api_keys_configured']['gemini'] = hasattr(self, 'gemini_api_key') and bool(self.gemini_api_key)
        
        # Test connections
        try:
            connection_results = self.test_connection()
            status['connection_status'] = connection_results
            status['healthy_models'] = [model for model, healthy in connection_results.items() if healthy]
        except Exception as e:
            status['connection_status'] = {'error': str(e)}
            status['healthy_models'] = []
        
        return status
    
    def update_api_key(self, provider: str, api_key: str) -> Dict[str, Any]:
        """Dynamically update Gemini API key"""
        try:
            if provider.lower() == 'gemini':
                genai.configure(api_key=api_key)
                
                # Try different model names (Google đã update)
                model_names = [
                    'gemini-1.5-flash',     # Model mới nhất
                    'gemini-1.5-pro',       # Pro version
                    'gemini-1.0-pro',       # Fallback
                    'models/gemini-1.5-flash',  # With prefix
                    'models/gemini-1.0-pro'     # With prefix fallback
                ]
                
                for model_name in model_names:
                    try:
                        model = genai.GenerativeModel(model_name)
                        # Test the model with a simple request
                        test_response = model.generate_content("Test")
                        self.available_models['gemini'] = model
                        self.gemini_api_key = api_key
                        logger.info(f"✅ Gemini API key updated with model: {model_name}")
                        return {'success': True, 'message': f'Gemini API key updated with model: {model_name}'}
                    except Exception as e:
                        logger.warning(f"⚠️ Model {model_name} not available: {e}")
                        continue
                else:
                    # If no model works, return error
                    return {'success': False, 'message': 'No available Gemini models found'}
            else:
                return {'success': False, 'message': f'Only Gemini provider is supported. Got: {provider}'}
                
        except Exception as e:
            logger.error(f"❌ Failed to update {provider} API key: {str(e)}")
            return {'success': False, 'message': f'Failed to update {provider} API key: {str(e)}'}
    
    def get_model_recommendations(self, task_type: str) -> Dict[str, Any]:
        """Get model recommendations for specific task types"""
        recommendations = {
            'task_type': task_type,
            'primary_model': self.select_best_model(task_type),
            'available_alternatives': [],
            'reasoning': ''
        }
        
        # Get all available models except primary
        primary = recommendations['primary_model']
        alternatives = [model for model in self.available_models.keys() if model != primary]
        recommendations['available_alternatives'] = alternatives
        
        # Add reasoning based on task type
        task_reasoning = {
            'financial_advice': 'Gemini excels at Vietnamese financial analysis and reasoning',
            'price_prediction': 'Gemini provides comprehensive technical analysis and prediction models',
            'risk_assessment': 'Gemini offers superior risk calculation and assessment',
            'news_analysis': 'Gemini has excellent sentiment analysis capabilities',
            'market_analysis': 'Gemini provides excellent market reasoning and context understanding',
            'investment_analysis': 'Gemini excels at investment metrics and calculations',
            'general_query': 'Gemini handles Vietnamese queries and general reasoning perfectly'
        }
        
        recommendations['reasoning'] = task_reasoning.get(task_type, 'Default model selection based on availability')
        
        return recommendations
    
    async def generate_async(self, prompt: str, task_type: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Asynchronous generation with fallback support"""
        try:
            # Run the synchronous method in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.generate_with_fallback, 
                prompt, 
                task_type, 
                max_tokens
            )
            return result
        except Exception as e:
            logger.error(f"Async generation failed: {str(e)}")
            return {
                'response': f'Async generation error: {str(e)}',
                'model_used': None,
                'success': False,
                'error': str(e)
            }
    
    def batch_generate(self, prompts: List[Dict[str, Any]], max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Generate responses for multiple prompts with concurrency control"""
        async def process_batch():
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_single(prompt_data):
                async with semaphore:
                    prompt = prompt_data.get('prompt', '')
                    task_type = prompt_data.get('task_type', 'general_query')
                    max_tokens = prompt_data.get('max_tokens', 1000)
                    
                    result = await self.generate_async(prompt, task_type, max_tokens)
                    result['original_data'] = prompt_data
                    return result
            
            tasks = [process_single(prompt_data) for prompt_data in prompts]
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new event loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, process_batch())
                    return future.result()
            else:
                return asyncio.run(process_batch())
        except Exception as e:
            logger.error(f"Batch generation failed: {str(e)}")
            return [{'success': False, 'error': str(e)} for _ in prompts]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        return {
            'available_models': list(self.available_models.keys()),
            'current_model': self.current_model_name,
            'model_count': len(self.available_models),
            'is_active': len(self.available_models) > 0
        }

# Backward compatibility alias
GeminiAgent = UnifiedAIAgent