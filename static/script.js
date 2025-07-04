const API_BASE = 'http://localhost:8000';
let selectedVNStock = '';
let vnStocks = [];
let agentStatus = {
    'PricePredictor': 'idle',
    'TickerNews': 'idle', 
    'MarketNews': 'idle',
    'InvestmentExpert': 'idle',
    'RiskExpert': 'idle',
    'GeminiAgent': 'idle'
};
let realTimeInterval = null;

function initVNStocks() {
    const container = document.getElementById('vnStocks');
    if (!container) return;
    container.innerHTML = vnStocks.map(stock => `
        <div class="stock-card" data-symbol="${stock.symbol}">
            <div class="stock-symbol">${stock.symbol}</div>
            <div class="stock-name">${stock.name}</div>
            <div style="font-size: 0.8rem; color: #999; margin-top: 5px;">${stock.sector}</div>
        </div>
    `).join('');
}

async function loadVNStocks() {
    try {
        const response = await fetch(`${API_BASE}/vn-symbols`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        vnStocks = data; // Cập nhật danh sách từ API
        initVNStocks(); // Render lại danh sách
    } catch (error) {
        console.error("Could not load VN stocks:", error);
        const container = document.getElementById('vnStocks');
        if (container) {
            container.innerHTML = '<p class="error-message">Không thể tải danh sách cổ phiếu VN. Vui lòng thử lại.</p>';
        }
    }
}

function selectVNStock(event) {
    const card = event.target.closest('.stock-card');
    if (!card) return;
    const symbol = card.dataset.symbol;
    selectedVNStock = symbol;
    document.querySelectorAll('.stock-card').forEach(card => {
        card.classList.remove('selected');
    });
    card.classList.add('selected');
    document.getElementById('symbol').value = symbol;
}

function switchTab(event) {
    const tabName = event.target.dataset.tab;
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

function showResult(data, isError = false, title = 'Kết quả phân tích') {
    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'block';
    resultDiv.className = isError ? 'result error' : 'result';
    
    const icon = isError ? 'fas fa-exclamation-circle' : 'fas fa-check-circle';
    
    if (isError) {
        resultDiv.innerHTML = `
            <div class="result-header">
                <i class="${icon}"></i>
                <h3>${title}</h3>
            </div>
            <div class="json-viewer">${JSON.stringify(data, null, 2)}</div>
        `;
    } else {
        resultDiv.innerHTML = `
            <div class="result-header">
                <i class="${icon}"></i>
                <h3>${title}</h3>
            </div>
            ${formatSingleData(data)}
        `;
    }
    
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

function showLoading(message = 'Đang xử lý...') {
    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'block';
    resultDiv.className = 'result loading';
    resultDiv.innerHTML = `
        <div class="result-header">
            <i class="fas fa-spinner fa-spin"></i>
            <h3>${message}</h3>
        </div>
        <div class="agent-status-container">
            ${Object.keys(agentStatus).map(agent => `
                <div class="agent-status" id="status-${agent}">
                    <span class="agent-name">${agent}</span>
                    <span class="status-indicator idle">⏳</span>
                </div>
            `).join('')}
        </div>
    `;
}

function updateAgentStatus(agent, status) {
    agentStatus[agent] = status;
    const statusEl = document.getElementById(`status-${agent}`);
    if (statusEl) {
        const indicator = statusEl.querySelector('.status-indicator');
        indicator.className = `status-indicator ${status}`;
        indicator.textContent = status === 'working' ? '🔄' : status === 'done' ? '✅' : '⏳';
    }
}

function startRealTimeUpdates() {
    if (realTimeInterval) clearInterval(realTimeInterval);
    
    realTimeInterval = setInterval(async () => {
        const symbol = document.getElementById('symbol').value.trim();
        if (symbol && selectedVNStock) {
            try {
                const response = await fetch(`${API_BASE}/vn-stock/${symbol}`);
                if (response.ok) {
                    const data = await response.json();
                    updateMiniDisplay(data);
                }
            } catch (error) {
                console.log('Real-time update failed:', error);
            }
        }
    }, 30000); // Update every 30 seconds
}

function updateMiniDisplay(data) {
    const miniDisplay = document.getElementById('mini-display');
    if (miniDisplay && data.price) {
        const changeClass = data.change_percent > 0 ? 'positive' : data.change_percent < 0 ? 'negative' : 'neutral';
        miniDisplay.innerHTML = `
            <div class="mini-stock-info">
                <span class="mini-symbol">${data.symbol}</span>
                <span class="mini-price ${changeClass}">${data.price.toLocaleString()} VND</span>
                <span class="mini-change ${changeClass}">(${data.change_percent > 0 ? '+' : ''}${data.change_percent}%)</span>
            </div>
        `;
    }
}

function formatSingleData(data) {
    if (!data || typeof data !== 'object') {
        return `<div class="json-viewer">${JSON.stringify(data, null, 2)}</div>`;
    }
    
    // Check if it's a conversational response
    if (data.response_type === 'conversational') {
        return formatConversationalResponse(data);
    }
    
    // Check if it's a single prediction result
    if (data.symbol && data.predicted_price && !data.vn_stock_data) {
        return formatPredictionCard(data);
    }
    
    // Check if it's a single news result
    if ((data.news || data.sentiment || data.headlines) && !data.vn_stock_data) {
        return formatNewsCard(data);
    }
    
    // Check if it's a single risk result
    if (data.risk_level && data.volatility && !data.vn_stock_data) {
        return formatRiskCard(data);
    }
    
    // Check if it's VN stock data only
    if (data.price && data.sector && data.exchange && !data.vn_stock_data) {
        return formatVNStockCard(data);
    }
    
    // Otherwise use the comprehensive formatter
    return formatAnalysisData(data);
}

function formatAnalysisData(data) {
    if (!data || typeof data !== 'object') {
        return `<div class="json-viewer">${JSON.stringify(data, null, 2)}</div>`;
    }
    
    let html = '';
    
    // VN Stock Data
    if (data.vn_stock_data) {
        html += formatVNStockCard(data.vn_stock_data);
    }
    
    // Price Prediction
    if (data.price_prediction) {
        html += formatPredictionCard(data.price_prediction);
    }
    
    // Investment Analysis
    if (data.investment_analysis) {
        html += formatInvestmentCard(data.investment_analysis);
    }
    
    // Risk Assessment
    if (data.risk_assessment) {
        html += formatRiskCard(data.risk_assessment);
    }
    
    // News
    if (data.ticker_news) {
        html += formatNewsCard(data.ticker_news);
    }
    
    // Fallback to JSON if no specific formatting
    if (!html) {
        html = `<div class="json-viewer">${JSON.stringify(data, null, 2)}</div>`;
    }
    
    return html;
}

function formatVNStockCard(data) {
    const changeClass = data.change_percent > 0 ? 'positive' : data.change_percent < 0 ? 'negative' : 'neutral';
    const changeIcon = data.change_percent > 0 ? '↗️' : data.change_percent < 0 ? '↘️' : '➡️';
    
    return `
        <div class="analysis-card">
            <div class="analysis-header">
                <i class="fas fa-chart-line"></i>
                <span class="analysis-title">Thông tin cổ phiếu ${data.symbol}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Giá hiện tại:</span>
                <span class="metric-value">${data.price.toLocaleString()} VND</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Thay đổi:</span>
                <span class="metric-value ${changeClass}">${changeIcon} ${data.change.toLocaleString()} VND (${data.change_percent}%)</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Khối lượng:</span>
                <span class="metric-value">${data.volume.toLocaleString()}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Vốn hóa:</span>
                <span class="metric-value">${data.market_cap.toLocaleString()} tỷ VND</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">P/E:</span>
                <span class="metric-value">${data.pe_ratio}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Ngành:</span>
                <span class="metric-value">${data.sector} - ${data.exchange}</span>
            </div>
        </div>
    `;
}

function formatPredictionCard(data) {
    const trendIcon = data.trend === 'bullish' ? '📈' : data.trend === 'bearish' ? '📉' : '📊';
    const trendClass = data.trend === 'bullish' ? 'positive' : data.trend === 'bearish' ? 'negative' : 'neutral';
    
    return `
        <div class="analysis-card">
            <div class="analysis-header">
                <i class="fas fa-crystal-ball"></i>
                <span class="analysis-title">Dự đoán giá ${data.symbol}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Giá hiện tại:</span>
                <span class="metric-value">${typeof data.current_price === 'number' ? data.current_price.toLocaleString() : data.current_price}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Giá dự đoán:</span>
                <span class="metric-value">${typeof data.predicted_price === 'number' ? data.predicted_price.toLocaleString() : data.predicted_price}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Xu hướng:</span>
                <span class="metric-value ${trendClass}">${trendIcon} ${data.trend}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Độ tin cậy:</span>
                <span class="metric-value">${data.confidence}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Thời gian:</span>
                <span class="metric-value">${data.timeframe}</span>
            </div>
        </div>
    `;
}

function formatInvestmentCard(data) {
    const recClass = data.recommendation === 'BUY' ? 'buy' : data.recommendation === 'SELL' ? 'sell' : 'hold';
    
    return `
        <div class="analysis-card">
            <div class="analysis-header">
                <i class="fas fa-chart-bar"></i>
                <span class="analysis-title">Phân tích đầu tư ${data.symbol}</span>
            </div>
            <div class="recommendation ${recClass}">
                🎯 ${data.recommendation}: ${data.reason}
            </div>
            <div class="metric-row">
                <span class="metric-label">P/E Ratio:</span>
                <span class="metric-value">${data.pe_ratio}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Vốn hóa:</span>
                <span class="metric-value">${data.market_cap}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Cổ tức:</span>
                <span class="metric-value">${data.dividend_yield}%</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Cao nhất 52W:</span>
                <span class="metric-value">${typeof data.year_high === 'number' ? data.year_high.toLocaleString() : data.year_high}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Thấp nhất 52W:</span>
                <span class="metric-value">${typeof data.year_low === 'number' ? data.year_low.toLocaleString() : data.year_low}</span>
            </div>
        </div>
    `;
}

function formatRiskCard(data) {
    const riskColor = data.risk_level === 'HIGH' ? 'negative' : data.risk_level === 'LOW' ? 'positive' : 'neutral';
    const riskIcon = data.risk_level === 'HIGH' ? '⚠️' : data.risk_level === 'LOW' ? '✅' : '⚡';
    
    return `
        <div class="analysis-card">
            <div class="analysis-header">
                <i class="fas fa-shield-alt"></i>
                <span class="analysis-title">Đánh giá rủi ro ${data.symbol}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Mức độ rủi ro:</span>
                <span class="metric-value ${riskColor}">${riskIcon} ${data.risk_level}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Độ biến động:</span>
                <span class="metric-value">${data.volatility}%</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Max Drawdown:</span>
                <span class="metric-value negative">${data.max_drawdown}%</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Beta:</span>
                <span class="metric-value">${data.beta}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Risk Score:</span>
                <span class="metric-value">${data.risk_score}/10</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Benchmark:</span>
                <span class="metric-value">${data.benchmark || 'N/A'}</span>
            </div>
        </div>
    `;
}

function formatConversationalResponse(data) {
    // Backend trả về dữ liệu JSON thô, frontend chịu trách nhiệm render HTML.
    // data.expert_advice là văn bản thô từ AI.
    // data.recommendations là một mảng các hành động.
    let html = `
        <div class="analysis-card">
            <div class="analysis-header">
                <i class="fas fa-user-graduate"></i>
                <span class="analysis-title">🎓 Phân tích chuyên sâu từ chuyên gia</span>
            </div>
            
            <div class="expert-advice-box">
                <div class="expert-advice-title">
                    <i class="fas fa-chart-line"></i>
                    Phân tích & Kết luận
                </div>
                <div class="expert-advice-content">${formatAdviceContent(data.expert_advice)}</div>
            </div>
    `;
    
    // Render danh sách hành động cụ thể nếu có
    if (data.recommendations && data.recommendations.length > 0) {
        html += `
            <div class="expert-recommendations-title">
                <i class="fas fa-lightbulb"></i>
                Hành động cụ thể
            </div>
            <ul class="expert-recommendations-list">
                ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>`;
    }
    
    html += '</div>';
    
    // Add data visualization if available
    if (data.data) {
        html += formatAnalysisData(data.data);
    }
    
    return html;
}

function formatAdviceContent(advice) {
    if (!advice) return '';
    
    // Convert markdown-style formatting to HTML
    return advice
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
        .replace(/📊/g, '<span style="color: #2a5298; font-weight: 600;">📊</span>')
        .replace(/🎯/g, '<span style="color: #28a745; font-weight: 600;">🎯</span>')
        .replace(/⚠️/g, '<span style="color: #dc3545; font-weight: 600;">⚠️</span>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
}

function formatNewsCard(data) {
    let html = `
        <div class="analysis-card">
            <div class="analysis-header">
                <i class="fas fa-newspaper"></i>
                <span class="analysis-title">Tin tức & Sentiment</span>
            </div>
    `;
    
    if (data.sentiment) {
        const sentimentIcon = data.sentiment === 'Positive' ? '😊' : data.sentiment === 'Negative' ? '😟' : '😐';
        const sentimentClass = data.sentiment === 'Positive' ? 'positive' : data.sentiment === 'Negative' ? 'negative' : 'neutral';
        
        html += `
            <div class="metric-row">
                <span class="metric-label">Sentiment:</span>
                <span class="metric-value ${sentimentClass}">${sentimentIcon} ${data.sentiment}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Điểm sentiment:</span>
                <span class="metric-value">${data.sentiment_score}/1.0</span>
            </div>
        `;
        
        if (data.headlines && data.headlines.length > 0) {
            html += '<div style="margin-top: 15px;"><strong>📰 Tin tức nổi bật:</strong></div>';
            data.headlines.forEach(headline => {
                html += `<div class="news-item"><div class="news-title">${headline}</div></div>`;
            });
        }
    } else if (data.news && data.news.length > 0) {
        data.news.forEach(item => {
            html += `
                <div class="news-item">
                    <div class="news-title">${item.title}</div>
                    <div class="news-meta">${item.publisher} - ${item.published}</div>
                </div>
            `;
        });
    }
    
    html += '</div>';
    return html;
}

// API Functions
async function analyzeStock() {
    const symbol = document.getElementById('symbol').value.trim();
    if (!symbol) {
        alert('Vui lòng nhập mã cổ phiếu');
        return;
    }
    
    showLoading(`6 AI Agents đang phân tích ${symbol}...`);
    
    // Simulate agent working sequence
    const agents = ['PricePredictor', 'RiskExpert', 'InvestmentExpert', 'TickerNews', 'MarketNews', 'GeminiAgent'];
    
    try {
        // Start analysis
        for (let i = 0; i < agents.length; i++) {
            updateAgentStatus(agents[i], 'working');
            await new Promise(resolve => setTimeout(resolve, 500)); // Visual delay
        }
        
        const response = await fetch(`${API_BASE}/analyze?symbol=${symbol}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Mark all agents as done
        agents.forEach(agent => updateAgentStatus(agent, 'done'));
        
        showResult(data, false, `✅ Phân tích hoàn tất: ${symbol}`);
        startRealTimeUpdates();
        
    } catch (error) {
        // Reset agent status on error
        Object.keys(agentStatus).forEach(agent => updateAgentStatus(agent, 'idle'));
        showResult({error: error.message}, true, 'Lỗi');
    }
}

async function predictPrice() {
    const symbol = document.getElementById('symbol').value.trim();
    if (!symbol) {
        alert('Vui lòng nhập mã cổ phiếu');
        return;
    }
    
    showLoading(`Đang dự đoán giá ${symbol}...`);
    try {
        const response = await fetch(`${API_BASE}/predict/${symbol}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        showResult(data, false, `Dự đoán giá ${symbol}`);
    } catch (error) {
        showResult({error: error.message}, true, 'Lỗi');
    }
}

async function getNews() {
    const symbol = document.getElementById('symbol').value.trim();
    if (!symbol) {
        alert('Vui lòng nhập mã cổ phiếu');
        return;
    }
    
    showLoading(`Đang lấy tin tức ${symbol}...`);
    try {
        const response = await fetch(`${API_BASE}/news/${symbol}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        showResult(data, false, `Tin tức ${symbol}`);
    } catch (error) {
        showResult({error: error.message}, true, 'Lỗi');
    }
}

async function assessRisk() {
    const symbol = document.getElementById('symbol').value.trim();
    if (!symbol) {
        alert('Vui lòng nhập mã cổ phiếu');
        return;
    }
    
    showLoading(`Đang đánh giá rủi ro ${symbol}...`);
    try {
        const response = await fetch(`${API_BASE}/risk/${symbol}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        showResult(data, false, `Đánh giá rủi ro ${symbol}`);
    } catch (error) {
        showResult({error: error.message}, true, 'Lỗi');
    }
}

async function processQuery() {
    const query = document.getElementById('query').value.trim();
    const symbol = document.getElementById('symbol').value.trim();
    
    if (!query) {
        alert('Vui lòng nhập câu hỏi');
        return;
    }
    
    showLoading('🧠 Gemini AI đang suy nghĩ...');
    updateAgentStatus('GeminiAgent', 'working');
    
    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                symbol: symbol || ""
            })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        updateAgentStatus('GeminiAgent', 'done');
        showResult(data, false, '🎓 Lời khuyên từ chuyên gia AI');
        
        // Clear query input
        document.getElementById('query').value = '';
        
    } catch (error) {
        updateAgentStatus('GeminiAgent', 'idle');
        showResult({error: error.message}, true, 'Lỗi');
    }
}

async function getMarket() {
    showLoading('Đang lấy tin tức thị trường...');
    try {
        const response = await fetch(`${API_BASE}/market`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        showResult(data, false, 'Tin tức thị trường');
    } catch (error) {
        showResult({error: error.message}, true, 'Lỗi');
    }
}

// VN Stock functions
async function getVNStock() {
    const symbol = selectedVNStock || document.getElementById('symbol').value.trim();
    if (!symbol) {
        alert('Vui lòng chọn hoặc nhập mã cổ phiếu VN');
        return;
    }
    
    showLoading(`Đang phân tích ${symbol}...`);
    try {
        const response = await fetch(`${API_BASE}/vn-stock/${symbol}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        showResult(data, false, `Phân tích cổ phiếu ${symbol}`);
    } catch (error) {
        showResult({error: error.message}, true, 'Lỗi');
    }
}

async function getVNMarket() {
    showLoading('Đang lấy tổng quan thị trường VN...');
    try {
        const response = await fetch(`${API_BASE}/vn-market`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        showResult(data, false, 'Tổng quan thị trường Việt Nam');
    } catch (error) {
        showResult({error: error.message}, true, 'Lỗi');
    }
}

async function getVNSymbols() {
    showLoading('Đang lấy danh sách mã cổ phiếu VN...');
    try {
        const response = await fetch(`${API_BASE}/vn-symbols`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        showResult(data, false, 'Danh sách mã cổ phiếu VN');
    } catch (error) {
        showResult({error: error.message}, true, 'Lỗi');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Tải danh sách cổ phiếu VN động từ API
    loadVNStocks();
    document.getElementById('vnStocks').addEventListener('click', selectVNStock);

    // Tab switching
    document.querySelector('.tabs').addEventListener('click', (event) => {
        if (event.target.classList.contains('tab')) {
            switchTab(event);
        }
    });

    // Button listeners
    document.getElementById('btn-analyze').addEventListener('click', analyzeStock);
    document.getElementById('btn-predict').addEventListener('click', predictPrice);
    document.getElementById('btn-news').addEventListener('click', getNews);
    document.getElementById('btn-risk').addEventListener('click', assessRisk);
    document.getElementById('btn-query').addEventListener('click', processQuery);
    document.getElementById('btn-market').addEventListener('click', getMarket);
    document.getElementById('btn-vn-stock').addEventListener('click', getVNStock);
    document.getElementById('btn-vn-market').addEventListener('click', getVNMarket);
    document.getElementById('btn-vn-symbols').addEventListener('click', getVNSymbols);
    
    // Add mini display for real-time updates
    const inputSection = document.querySelector('.input-section');
    if (inputSection) {
        const miniDisplay = document.createElement('div');
        miniDisplay.id = 'mini-display';
        miniDisplay.className = 'mini-display';
        inputSection.appendChild(miniDisplay);
    }
    
    // Auto-focus on symbol input
    const symbolInput = document.getElementById('symbol');
    if (symbolInput) {
        symbolInput.focus();
        
        // Enter key support
        symbolInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeStock();
            }
        });
    }
    
    // Enter key support for query
    const queryInput = document.getElementById('query');
    if (queryInput) {
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processQuery();
            }
        });
    }
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (realTimeInterval) {
            clearInterval(realTimeInterval);
        }
    });
});