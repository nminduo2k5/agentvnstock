import google.generativeai as genai
import openai
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
import asyncio
import json

load_dotenv()
logger = logging.getLogger(__name__)

class UnifiedAIAgent:
    def __init__(self, gemini_api_key: str = None, openai_api_key: str = None):
        """
        Initialize Unified AI Agent with multiple AI models
        """
        self.available_models = {}
        self.model_capabilities = {
            'gemini': {
                'strengths': ['analysis', 'vietnamese', 'reasoning', 'financial_advice'],
                'speed': 'fast',
                'cost': 'low'
            },
            'chatgpt': {
                'strengths': ['prediction', 'technical_analysis', 'news_analysis', 'risk_assessment'],
                'speed': 'medium',
                'cost': 'medium'
            }
        }
        
        # Initialize Gemini
        if not gemini_api_key:
            gemini_api_key = os.getenv('GOOGLE_API_KEY')
        
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
                self.available_models['gemini'] = genai.GenerativeModel(model_name)
                self.gemini_api_key = gemini_api_key
                logger.info("✅ Gemini AI initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
        
        # Initialize OpenAI
        if not openai_api_key:
            openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                self.available_models['chatgpt'] = self.openai_client
                self.openai_api_key = openai_api_key
                logger.info("✅ ChatGPT AI initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize ChatGPT: {str(e)}")
        
        if not self.available_models:
            raise ValueError("At least one AI model must be configured. Please provide API keys.")
    
    def test_connection(self):
        """Test API connections for all available models"""
        results = {}
        
        if 'gemini' in self.available_models:
            try:
                response = self.available_models['gemini'].generate_content("Hello")
                results['gemini'] = True
                logger.info("✅ Gemini connection test passed")
            except Exception as e:
                results['gemini'] = False
                logger.error(f"❌ Gemini connection test failed: {str(e)}")
        
        if 'chatgpt' in self.available_models:
            try:
                response = self.available_models['chatgpt'].chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                results['chatgpt'] = True
                logger.info("✅ ChatGPT connection test passed")
            except Exception as e:
                results['chatgpt'] = False
                logger.error(f"❌ ChatGPT connection test failed: {str(e)}")
        
        if not any(results.values()):
            raise ValueError("All API connection tests failed")
        
        return results
    
    def select_best_model(self, task_type: str) -> str:
        """
        Automatically select the best AI model for a specific task type
        """
        task_model_mapping = {
            'financial_advice': 'gemini',  # Gemini better for Vietnamese financial advice
            'price_prediction': 'chatgpt',  # ChatGPT better for technical analysis
            'risk_assessment': 'chatgpt',   # ChatGPT better for risk calculations
            'news_analysis': 'chatgpt',     # ChatGPT better for news sentiment
            'market_analysis': 'gemini',    # Gemini better for market reasoning
            'investment_analysis': 'chatgpt', # ChatGPT better for investment metrics
            'general_query': 'gemini'       # Gemini better for general Vietnamese queries
        }
        
        preferred_model = task_model_mapping.get(task_type, 'gemini')
        
        # Check if preferred model is available, otherwise use any available
        if preferred_model in self.available_models:
            return preferred_model
        elif self.available_models:
            return list(self.available_models.keys())[0]
        else:
            raise ValueError("No AI models available")
    
    def generate_with_model(self, prompt: str, model_name: str, max_tokens: int = 1000) -> str:
        """
        Generate response using specific AI model
        """
        try:
            if model_name == 'gemini' and 'gemini' in self.available_models:
                response = self.available_models['gemini'].generate_content(prompt)
                return response.text
            
            elif model_name == 'chatgpt' and 'chatgpt' in self.available_models:
                response = self.available_models['chatgpt'].chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            else:
                raise ValueError(f"Model {model_name} not available")
                
        except Exception as e:
            logger.error(f"Error generating with {model_name}: {str(e)}")
            raise
    
    def generate_with_fallback(self, prompt: str, task_type: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate response with automatic fallback to other models if primary fails
        """
        primary_model = self.select_best_model(task_type)
        
        try:
            response = self.generate_with_model(prompt, primary_model, max_tokens)
            return {
                'response': response,
                'model_used': primary_model,
                'success': True
            }
        except Exception as e:
            logger.warning(f"Primary model {primary_model} failed: {str(e)}")
            
            # Try other available models
            for model_name in self.available_models.keys():
                if model_name != primary_model:
                    try:
                        response = self.generate_with_model(prompt, model_name, max_tokens)
                        return {
                            'response': response,
                            'model_used': model_name,
                            'success': True,
                            'fallback': True
                        }
                    except Exception as fallback_error:
                        logger.warning(f"Fallback model {model_name} also failed: {str(fallback_error)}")
                        continue
            
            # If all models fail
            return {
                'response': f"Lỗi: Tất cả AI models đều không khả dụng. Task: {task_type}",
                'model_used': None,
                'success': False,
                'error': str(e)
            }
    
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
                return {
                    "expert_advice": f"❌ **LỖI AI SYSTEM:**\n{result.get('response', 'Không thể kết nối với AI models')}\n\n⚠️ **GỢI Ý:**\n- Kiểm tra API keys\n- Thử lại sau vài phút\n- Liên hệ hỗ trợ nếu vấn đề tiếp tục",
                    "recommendations": [
                        "Kiểm tra API keys (Gemini/OpenAI)",
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

# Backward compatibility alias
GeminiAgent = UnifiedAIAgent