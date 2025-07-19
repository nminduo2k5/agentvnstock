import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class ReportGenerator:
    def __init__(self):
        self.name = "Report Generator Agent"
        self.reports_dir = "reports"
        self._ensure_reports_dir()
    
    def _ensure_reports_dir(self):
        """Ensure reports directory exists"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_comprehensive_report(self, analysis_data: dict, symbol: str, time_horizon: str = "Trung hạn", risk_tolerance: int = 50):
        """Tạo báo cáo đầu tư toàn diện từ tất cả agents"""
        try:
            # Extract data from all agents
            stock_data = analysis_data.get('vn_stock_data') or analysis_data.get('stock_data')
            price_pred = analysis_data.get('price_prediction', {})
            risk_data = analysis_data.get('risk_assessment', {})
            invest_data = analysis_data.get('investment_analysis', {})
            news_data = analysis_data.get('ticker_news', {})
            
            # Calculate correlation scores
            correlation_score = self._calculate_correlation(price_pred, risk_data, invest_data)
            
            # Generate executive summary
            exec_summary = self._generate_executive_summary(stock_data, price_pred, risk_data, invest_data, correlation_score)
            
            # Technical analysis summary
            tech_analysis = self._generate_technical_summary(price_pred, stock_data)
            
            # Fundamental analysis
            fundamental = self._generate_fundamental_summary(invest_data, stock_data)
            
            # Risk assessment
            risk_summary = self._generate_risk_summary(risk_data, risk_tolerance)
            
            # Final recommendation with confidence
            final_rec, confidence = self._generate_final_recommendation(
                price_pred, risk_data, invest_data, correlation_score, time_horizon, risk_tolerance
            )
            
            # Key factors
            key_factors = self._extract_key_factors(price_pred, risk_data, invest_data, news_data)
            
            # Warnings
            warnings = self._generate_warnings(risk_data, price_pred, invest_data)
            
            return {
                'symbol': symbol,
                'timestamp': self._get_timestamp(),
                'investment_profile': {
                    'time_horizon': time_horizon,
                    'risk_tolerance': risk_tolerance,
                    'risk_label': self._get_risk_label(risk_tolerance)
                },
                'executive_summary': exec_summary,
                'technical_analysis': tech_analysis,
                'fundamental_analysis': fundamental,
                'risk_assessment': risk_summary,
                'final_recommendation': final_rec,
                'confidence_score': confidence,
                'correlation_score': correlation_score,
                'key_factors': key_factors,
                'warnings': warnings,
                'data_quality': self._assess_data_quality(analysis_data)
            }
            
        except Exception as e:
            return {
                'error': f'Lỗi tạo báo cáo: {str(e)}',
                'symbol': symbol,
                'timestamp': self._get_timestamp()
            }
    
    def generate_report_file(self, analysis_data: dict, symbol: str, time_horizon: str = "Trung hạn", risk_tolerance: int = 50) -> Dict[str, str]:
        """Generate comprehensive report and save to file"""
        try:
            # Generate comprehensive report
            report_data = self.generate_comprehensive_report(analysis_data, symbol, time_horizon, risk_tolerance)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"investment_report_{symbol}_{timestamp}"
            
            # Generate different formats
            files_created = {}
            
            # 1. JSON Report
            json_file = os.path.join(self.reports_dir, f"{filename}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
            files_created['json'] = json_file
            
            # 2. HTML Report
            html_file = os.path.join(self.reports_dir, f"{filename}.html")
            html_content = self._generate_html_report(report_data, symbol)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            files_created['html'] = html_file
            
            # 3. Text Report
            txt_file = os.path.join(self.reports_dir, f"{filename}.txt")
            txt_content = self._generate_text_report(report_data, symbol)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(txt_content)
            files_created['txt'] = txt_file
            
            return {
                'success': True,
                'files': files_created,
                'report_data': report_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files': {}
            }
    
    def _generate_html_report(self, report_data: dict, symbol: str) -> str:
        """Generate HTML report"""
        # Format lists safely
        key_factors_html = self._format_list_items(report_data.get('key_factors', []))
        warnings_html = self._format_warning_items(report_data.get('warnings', []))
        
        html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo đầu tư {symbol} - DUONG AI TRADING</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 8px; }}
        .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #667eea; background: #f8f9fa; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #e3f2fd; border-radius: 5px; min-width: 150px; }}
        .recommendation {{ padding: 15px; margin: 10px 0; border-radius: 8px; font-weight: bold; }}
        .buy {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .sell {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .hold {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .warning {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .footer {{ text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 BÁO CÁO ĐẦU TƯ TOÀN DIỆN</h1>
            <h2>{symbol}</h2>
            <p>Thời gian: {report_data.get('timestamp', 'N/A')}</p>
        </div>
        
        <div class="section">
            <h3>🎯 HỒ SƠ ĐẦU TƯ</h3>
            <div class="metric">Thời gian: {report_data.get('investment_profile', {}).get('time_horizon', 'N/A')}</div>
            <div class="metric">Rủi ro: {report_data.get('investment_profile', {}).get('risk_tolerance', 'N/A')}%</div>
            <div class="metric">Nhãn rủi ro: {report_data.get('investment_profile', {}).get('risk_label', 'N/A')}</div>
        </div>
        
        <div class="section">
            <h3>📈 TÓM TẮT ĐIỀU HÀNH</h3>
            <p>{report_data.get('executive_summary', 'Không có dữ liệu').replace(chr(10), '<br>')}</p>
        </div>
        
        <div class="section">
            <h3>🎯 KHUYẾN NGHỊ CUỐI CÙNG</h3>
            <div class="recommendation {report_data.get('final_recommendation', 'HOLD').lower()}">
                {report_data.get('final_recommendation', 'HOLD')}
            </div>
            <p><strong>Độ tin cậy:</strong> {report_data.get('confidence_score', 0):.1%}</p>
            <p><strong>Điểm tương quan:</strong> {report_data.get('correlation_score', 0):.1%}</p>
        </div>
        
        <div class="section">
            <h3>📊 PHÂN TÍCH KỸ THUẬT</h3>
            <p>{report_data.get('technical_analysis', 'Không có dữ liệu').replace(chr(10), '<br>')}</p>
        </div>
        
        <div class="section">
            <h3>💰 PHÂN TÍCH CƠ BẢN</h3>
            <p>{report_data.get('fundamental_analysis', 'Không có dữ liệu').replace(chr(10), '<br>')}</p>
        </div>
        
        <div class="section">
            <h3>⚠️ ĐÁNH GIÁ RỦI RO</h3>
            <p>{report_data.get('risk_assessment', 'Không có dữ liệu').replace(chr(10), '<br>')}</p>
        </div>
        
        <div class="section">
            <h3>🔑 YẾU TỐ QUAN TRỌNG</h3>
            <ul>
            {key_factors_html}
            </ul>
        </div>
        
        <div class="section">
            <h3>⚠️ CẢNH BÁO</h3>
            {warnings_html}
        </div>
        
        <div class="footer">
            <p><strong>🤖 DUONG AI TRADING SIUUUU</strong></p>
            <p>Báo cáo được tạo bởi 6 AI Agents + Gemini AI</p>
            <p><em>Đây chỉ là phân tích tham khảo, không phải lời khuyên đầu tư tuyệt đối</em></p>
        </div>
    </div>
</body>
</html>"""
        return html_template
    
    def _generate_text_report(self, report_data: dict, symbol: str) -> str:
        """Generate text report"""
        # Format lists safely
        key_factors_text = self._format_text_list(report_data.get('key_factors', []))
        warnings_text = self._format_text_list(report_data.get('warnings', []))
        
        text_report = f"""================================================================================
                    BÁO CÁO ĐẦU TƯ TOÀN DIỆN - {symbol}
                        DUONG AI TRADING SIUUUU
================================================================================

Thời gian tạo báo cáo: {report_data.get('timestamp', 'N/A')}

🎯 HỒ SƠ ĐẦU TƯ:
- Thời gian đầu tư: {report_data.get('investment_profile', {}).get('time_horizon', 'N/A')}
- Mức độ rủi ro: {report_data.get('investment_profile', {}).get('risk_tolerance', 'N/A')}%
- Nhãn rủi ro: {report_data.get('investment_profile', {}).get('risk_label', 'N/A')}

📈 TÓM TẮT ĐIỀU HÀNH:
{report_data.get('executive_summary', 'Không có dữ liệu')}

🎯 KHUYẾN NGHỊ CUỐI CÙNG: {report_data.get('final_recommendation', 'HOLD')}
- Độ tin cậy: {report_data.get('confidence_score', 0):.1%}
- Điểm tương quan: {report_data.get('correlation_score', 0):.1%}

📊 PHÂN TÍCH KỸ THUẬT:
{report_data.get('technical_analysis', 'Không có dữ liệu')}

💰 PHÂN TÍCH CƠ BẢN:
{report_data.get('fundamental_analysis', 'Không có dữ liệu')}

⚠️ ĐÁNH GIÁ RỦI RO:
{report_data.get('risk_assessment', 'Không có dữ liệu')}

🔑 YẾU TỐ QUAN TRỌNG:
{key_factors_text}

⚠️ CẢNH BÁO:
{warnings_text}

================================================================================
                        DISCLAIMER - TUYÊN BỐ MIỄN TRỪ
================================================================================

Đây chỉ là phân tích tham khảo được tạo bởi AI, KHÔNG PHẢI lời khuyên đầu tư 
tuyệt đối. Nhà đầu tư cần:

- Thực hiện nghiên cứu độc lập
- Tham khảo chuyên gia tài chính
- Chỉ đầu tư số tiền có thể chấp nhận mất
- Hiểu rõ rủi ro trước khi đầu tư

Tác giả không chịu trách nhiệm về bất kỳ tổn thất tài chính nào.

================================================================================"""
        return text_report
    
    def _format_list_items(self, items: list) -> str:
        """Format list items for HTML"""
        return ''.join([f'<li>{item}</li>' for item in items])
    
    def _format_warning_items(self, warnings: list) -> str:
        """Format warning items for HTML"""
        return ''.join([f'<div class="warning">{warning}</div>' for warning in warnings])
    
    def _format_text_list(self, items: list) -> str:
        """Format list items for text"""
        result = ""
        for item in items:
            result += f"- {item}\n"
        return result
    
    def _calculate_correlation(self, price_pred: dict, risk_data: dict, invest_data: dict) -> float:
        """Tính correlation giữa các kết quả agents"""
        try:
            correlations = []
            
            # Price vs Investment correlation
            price_trend = price_pred.get('trend', 'neutral')
            invest_rec = invest_data.get('recommendation', 'HOLD')
            
            if (price_trend == 'bullish' and invest_rec == 'BUY') or (price_trend == 'bearish' and invest_rec == 'SELL'):
                correlations.append(1.0)
            elif price_trend == 'neutral' or invest_rec == 'HOLD':
                correlations.append(0.5)
            else:
                correlations.append(0.0)
            
            # Risk vs Investment correlation
            risk_level = risk_data.get('risk_level', 'MEDIUM')
            if risk_level == 'HIGH' and invest_rec == 'SELL':
                correlations.append(1.0)
            elif risk_level == 'LOW' and invest_rec == 'BUY':
                correlations.append(1.0)
            else:
                correlations.append(0.5)
            
            return sum(correlations) / len(correlations) if correlations else 0.5
            
        except:
            return 0.5
    
    def _generate_executive_summary(self, stock_data, price_pred: dict, risk_data: dict, invest_data: dict, correlation: float) -> str:
        """Tạo tóm tắt điều hành"""
        try:
            symbol = stock_data.symbol if stock_data else 'N/A'
            current_price = f"{stock_data.price:,.0f} VND" if stock_data else 'N/A'
            trend = price_pred.get('trend', 'neutral')
            risk_level = risk_data.get('risk_level', 'MEDIUM')
            recommendation = invest_data.get('recommendation', 'HOLD')
            
            correlation_text = 'phù hợp cao' if correlation > 0.7 else 'phù hợp trung bình' if correlation > 0.4 else 'chưa phù hợp'
            
            summary = f"""📊 **Tổng quan {symbol}:**
- Giá hiện tại: {current_price}
- Xu hướng: {trend.upper()}
- Mức rủi ro: {risk_level}
- Khuyến nghị: {recommendation}
- Độ tương quan: {correlation:.1%}

🎯 **Kết luận nhanh:** Các agents {correlation_text} trong đánh giá."""
            return summary.strip()
        except:
            return "Không thể tạo tóm tắt điều hành"
    
    def _generate_technical_summary(self, price_pred: dict, stock_data) -> str:
        """Tạo tóm tắt phân tích kỹ thuật"""
        try:
            trend = price_pred.get('trend', 'neutral')
            confidence = price_pred.get('confidence', 'medium')
            predicted_price = price_pred.get('predicted_price', 0)
            current_price = price_pred.get('current_price', 0)
            
            change_pct = ((predicted_price - current_price) / current_price * 100) if current_price > 0 else 0
            
            indicators = price_pred.get('indicators', {})
            rsi = indicators.get('rsi', 'N/A')
            
            return f"""📈 **Phân tích kỹ thuật:**
- Xu hướng: {trend.upper()} (độ tin cậy: {confidence})
- Dự đoán giá: {predicted_price:,.0f} VND ({change_pct:+.1f}%)
- RSI: {rsi}
- Signals: {len(price_pred.get('signals', []))} chỉ báo""".strip()
        except:
            return "Không thể tạo phân tích kỹ thuật"
    
    def _generate_fundamental_summary(self, invest_data: dict, stock_data) -> str:
        """Tạo tóm tắt phân tích cơ bản"""
        try:
            pe_ratio = invest_data.get('pe_ratio', stock_data.pe_ratio if stock_data else 'N/A')
            pb_ratio = invest_data.get('pb_ratio', stock_data.pb_ratio if stock_data else 'N/A')
            recommendation = invest_data.get('recommendation', 'HOLD')
            reason = invest_data.get('reason', 'Không có lý do')
            
            return f"""💰 **Phân tích cơ bản:**
- P/E: {pe_ratio}
- P/B: {pb_ratio}
- Khuyến nghị: {recommendation}
- Lý do: {reason}""".strip()
        except:
            return "Không thể tạo phân tích cơ bản"
    
    def _generate_risk_summary(self, risk_data: dict, risk_tolerance: int) -> str:
        """Tạo tóm tắt đánh giá rủi ro"""
        try:
            risk_level = risk_data.get('risk_level', 'MEDIUM')
            volatility = risk_data.get('volatility', 0)
            max_drawdown = risk_data.get('max_drawdown', 0)
            beta = risk_data.get('beta', 1.0)
            
            risk_match = self._assess_risk_match(risk_level, risk_tolerance)
            
            return f"""⚠️ **Đánh giá rủi ro:**
- Mức rủi ro: {risk_level}
- Độ biến động: {volatility:.1f}%
- Max Drawdown: {max_drawdown:.1f}%
- Beta: {beta:.2f}
- Phù hợp hồ sơ: {risk_match}""".strip()
        except:
            return "Không thể tạo đánh giá rủi ro"
    
    def _generate_final_recommendation(self, price_pred: dict, risk_data: dict, invest_data: dict, 
                                     correlation: float, time_horizon: str, risk_tolerance: int) -> tuple:
        """Tạo khuyến nghị cuối cùng và độ tin cậy"""
        try:
            # Collect recommendations
            price_trend = price_pred.get('trend', 'neutral')
            invest_rec = invest_data.get('recommendation', 'HOLD')
            risk_level = risk_data.get('risk_level', 'MEDIUM')
            
            # Scoring system
            score = 0
            
            # Price prediction influence
            if price_trend == 'bullish':
                score += 1
            elif price_trend == 'bearish':
                score -= 1
            
            # Investment analysis influence
            if invest_rec == 'BUY':
                score += 1
            elif invest_rec == 'SELL':
                score -= 1
            
            # Risk adjustment
            if risk_level == 'HIGH' and risk_tolerance < 50:
                score -= 0.5
            elif risk_level == 'LOW' and risk_tolerance > 70:
                score += 0.5
            
            # Time horizon adjustment
            if time_horizon == 'Dài hạn' and score > 0:
                score += 0.3
            
            # Final recommendation
            if score >= 1:
                final_rec = 'MUA'
                confidence = min(0.9, 0.6 + correlation * 0.3)
            elif score <= -1:
                final_rec = 'BÁN'
                confidence = min(0.9, 0.6 + correlation * 0.3)
            else:
                final_rec = 'GIỮ'
                confidence = 0.5 + correlation * 0.2
            
            return final_rec, confidence
            
        except:
            return 'GIỮ', 0.5
    
    def _extract_key_factors(self, price_pred: dict, risk_data: dict, invest_data: dict, news_data: dict) -> list:
        """Trích xuất các yếu tố quan trọng"""
        factors = []
        
        try:
            # Price factors
            if price_pred.get('confidence') == 'high':
                factors.append(f"Dự đoán giá độ tin cậy cao: {price_pred.get('trend', 'N/A')}")
            
            # Risk factors
            volatility = risk_data.get('volatility', 0)
            if volatility > 30:
                factors.append(f"Độ biến động cao: {volatility:.1f}%")
            elif volatility < 15:
                factors.append(f"Độ biến động thấp: {volatility:.1f}%")
            
            # Investment factors
            pe_ratio = invest_data.get('pe_ratio', 0)
            if pe_ratio and pe_ratio < 15:
                factors.append(f"P/E thấp hấp dẫn: {pe_ratio}")
            elif pe_ratio and pe_ratio > 25:
                factors.append(f"P/E cao cần thận trọng: {pe_ratio}")
            
            # News factors
            sentiment = news_data.get('sentiment', 'Neutral')
            if sentiment != 'Neutral':
                factors.append(f"Sentiment tin tức: {sentiment}")
            
            return factors[:5]  # Top 5 factors
            
        except:
            return ['Không thể xác định yếu tố chính']
    
    def _generate_warnings(self, risk_data: dict, price_pred: dict, invest_data: dict) -> list:
        """Tạo cảnh báo"""
        warnings = []
        
        try:
            # High risk warning
            if risk_data.get('risk_level') == 'HIGH':
                warnings.append('⚠️ Rủi ro cao - chỉ phù hợp nhà đầu tư có kinh nghiệm')
            
            # Low confidence warning
            if price_pred.get('confidence') == 'low':
                warnings.append('⚠️ Dự đoán giá độ tin cậy thấp')
            
            # Data quality warning
            if price_pred.get('data_source') == 'Fallback':
                warnings.append('⚠️ Sử dụng dữ liệu dự phòng - cần thận trọng')
            
            # High volatility warning
            volatility = risk_data.get('volatility', 0)
            if volatility > 40:
                warnings.append(f'⚠️ Độ biến động rất cao ({volatility:.1f}%) - rủi ro lớn')
            
            # General disclaimer
            warnings.append('📝 Đây chỉ là phân tích tham khảo, không phải lời khuyên đầu tư tuyệt đối')
            
            return warnings
            
        except:
            return ['⚠️ Vui lòng thận trọng khi đầu tư']
    
    def _assess_data_quality(self, analysis_data: dict) -> dict:
        """Đánh giá chất lượng dữ liệu"""
        try:
            quality_score = 0
            total_checks = 0
            
            # Check each data source
            for key, data in analysis_data.items():
                total_checks += 1
                if data and not isinstance(data, dict) or (isinstance(data, dict) and not data.get('error')):
                    quality_score += 1
            
            quality_pct = (quality_score / total_checks * 100) if total_checks > 0 else 0
            
            return {
                'score': quality_pct,
                'level': 'Cao' if quality_pct > 80 else 'Trung bình' if quality_pct > 50 else 'Thấp',
                'sources_available': quality_score,
                'total_sources': total_checks
            }
        except:
            return {'score': 50, 'level': 'Không xác định', 'sources_available': 0, 'total_sources': 0}
    
    def _get_risk_label(self, risk_tolerance: int) -> str:
        """Lấy nhãn mức độ rủi ro"""
        if risk_tolerance <= 30:
            return '🟢 Thận trọng'
        elif risk_tolerance <= 70:
            return '🟡 Cân bằng'
        else:
            return '🔴 Tích cực'
    
    def _assess_risk_match(self, risk_level: str, risk_tolerance: int) -> str:
        """Đánh giá sự phù hợp giữa rủi ro cổ phiếu và tolerance"""
        risk_scores = {'LOW': 25, 'MEDIUM': 50, 'HIGH': 75}
        stock_risk = risk_scores.get(risk_level, 50)
        
        diff = abs(stock_risk - risk_tolerance)
        if diff <= 20:
            return '✅ Phù hợp'
        elif diff <= 40:
            return '⚠️ Chấp nhận được'
        else:
            return '❌ Không phù hợp'
    
    def _get_timestamp(self) -> str:
        """Lấy timestamp hiện tại"""
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')