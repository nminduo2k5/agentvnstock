# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### 🎉 Initial Release

#### Added
- **6 AI Agents System**
  - 📈 PricePredictor: Dự đoán giá cổ phiếu
  - 📰 TickerNews: Tin tức cổ phiếu
  - 🌍 MarketNews: Tin tức thị trường
  - 💼 InvestmentExpert: Chuyên gia đầu tư
  - ⚠️ RiskExpert: Quản lý rủi ro
  - 🧠 GeminiAgent: AI Chatbot với Google Gemini

- **Real Data Integration**
  - VNStock 3.2.0+ integration for Vietnamese stocks
  - Yahoo Finance for international stocks
  - Real-time market data from VCI/TCBS

- **Modern UI/UX**
  - Streamlit web application with custom CSS
  - Responsive design with modern cards and gradients
  - Interactive charts and visualizations
  - Sidebar configuration panel

- **FastAPI Backend**
  - RESTful API with comprehensive endpoints
  - Async/await support for better performance
  - Auto-generated API documentation (Swagger/ReDoc)
  - CORS support for cross-origin requests

- **Error Handling & Logging**
  - Centralized error handling system
  - Comprehensive logging with different levels
  - Graceful fallbacks for API failures
  - User-friendly error messages

- **Configuration Management**
  - Environment-based configuration
  - Dynamic API key management
  - Centralized settings for all components
  - Support for multiple data sources

#### Features
- **Vietnamese Stock Analysis**
  - 30+ supported VN stocks (VCB, BID, VIC, etc.)
  - Real-time price data and technical indicators
  - Company information and financial ratios
  - News sentiment analysis

- **International Stock Support**
  - Yahoo Finance integration
  - Global market data access
  - Multi-currency support

- **AI-Powered Analysis**
  - Google Gemini integration for expert advice
  - Natural language query processing
  - Comprehensive investment recommendations
  - Risk assessment and management

- **Market Overview**
  - VN-Index real-time tracking
  - Top gainers/losers identification
  - Sector performance analysis
  - Foreign investment flows

#### Technical
- **Architecture**
  - Modular agent-based design
  - Async/await for concurrent processing
  - Clean separation of concerns
  - Extensible plugin system

- **Data Sources**
  - VNStock (VCI/TCBS) for Vietnamese data
  - Yahoo Finance for international data
  - Google Gemini for AI analysis
  - Real-time and historical data support

- **Installation & Setup**
  - Automated installation scripts (Windows/Linux/Mac)
  - Virtual environment setup
  - Dependency management
  - Configuration validation

#### Documentation
- Comprehensive README with setup instructions
- API documentation with examples
- Code comments and docstrings
- Troubleshooting guide

#### Testing
- Comprehensive system test suite
- Individual component tests
- API endpoint testing
- Error handling validation

### 🔧 Technical Details

#### Dependencies
- **Core**: Python 3.8+, Streamlit 1.28+, FastAPI 0.104+
- **AI/ML**: google-generativeai 0.3+, pandas 2.0+, numpy 1.24+
- **Data**: vnstock 3.2+, yfinance 0.2+, requests 2.31+
- **Visualization**: plotly 5.17+, matplotlib 3.7+

#### Supported Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, CentOS 8+)

#### API Endpoints
- `/health` - Health check
- `/analyze` - Comprehensive stock analysis
- `/query` - AI chatbot queries
- `/market` - Market overview
- `/predict/{symbol}` - Price prediction
- `/news/{symbol}` - Stock news
- `/risk/{symbol}` - Risk assessment
- `/vn-stock/{symbol}` - Vietnamese stock data
- `/vn-market` - Vietnamese market overview

### 🚀 Getting Started

1. **Quick Install**:
   ```bash
   git clone https://github.com/nminduo2k5/agentvnstock.git
   cd agentvnstock
   ./install.sh  # Linux/Mac
   install.bat   # Windows
   ```

2. **Configure API Key**:
   - Get Gemini API key from https://aistudio.google.com/apikey
   - Add to `.env` file or enter in app sidebar

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

### 🎯 Future Roadmap

#### Planned Features (v1.1.0)
- [ ] Portfolio management system
- [ ] Backtesting capabilities
- [ ] More technical indicators
- [ ] Email/SMS alerts
- [ ] Mobile app support

#### Planned Features (v1.2.0)
- [ ] Machine learning models
- [ ] Cryptocurrency support
- [ ] Social sentiment analysis
- [ ] Advanced charting tools
- [ ] Multi-language support

#### Planned Features (v2.0.0)
- [ ] Real-time trading integration
- [ ] Advanced AI models
- [ ] Cloud deployment options
- [ ] Enterprise features
- [ ] API rate limiting

### 🙏 Acknowledgments

- [vnstock](https://github.com/thinh-vu/vnstock) - Vietnamese stock data
- [Google Gemini](https://ai.google.dev) - AI chatbot capabilities
- [Streamlit](https://streamlit.io) - Web framework
- [FastAPI](https://fastapi.tiangolo.com) - API framework
- Vietnamese investment community for feedback and testing

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🇻🇳 Made with ❤️ for Vietnamese investors**