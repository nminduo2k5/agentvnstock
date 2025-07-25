// Professional JavaScript for DUONG AI TRADING PRO
// Version 2.0 - Enhanced with modern ES6+ features

class TradingApp {
    constructor() {
        this.API_BASE = 'http://localhost:8000';
        this.selectedSymbol = '';
        this.symbols = [];
        this.sectors = {};
        this.apiKeyStatus = {
            gemini: false,
            crewai: false
        };
        this.investmentProfile = {
            timeHorizon: 'medium',
            riskTolerance: 50,
            investmentAmount: 100000000
        };
        
        this.init();
    }

    // Initialize the application
    async init() {
        this.showLoadingScreen();
        await this.setupEventListeners();
        await this.loadInitialData();
        this.hideLoadingScreen();
        this.updateUI();
    }

    // Show professional loading screen
    showLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.classList.remove('hidden');
        }
    }

    // Hide loading screen
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            setTimeout(() => {
                loadingScreen.classList.add('hidden');
            }, 2000);
        }
    }

    // Setup all event listeners
    async setupEventListeners() {
        // API Configuration
        this.setupElement('btn-setup-gemini', 'click', () => this.setupGeminiAPI());
        this.setupElement('btn-setup-crewai', 'click', () => this.setupCrewAI());

        // Investment Settings
        this.setupElement('timeHorizon', 'change', (e) => this.updateInvestmentProfile('timeHorizon', e.target.value));
        this.setupElement('riskTolerance', 'input', (e) => this.updateRiskTolerance(e.target.value));
        this.setupElement('investmentAmount', 'input', (e) => this.updateInvestmentProfile('investmentAmount', parseInt(e.target.value)));

        // Stock Selection
        this.setupElement('sectorSelect', 'change', (e) => this.onSectorChange(e.target.value));
        this.setupElement('stockSelect', 'change', (e) => this.onStockChange(e.target.value));

        // Tab Navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Analysis Controls
        this.setupElement('btn-full-analysis', 'click', () => this.performFullAnalysis());
        this.setupElement('btn-price-prediction', 'click', () => this.performPricePrediction());
        this.setupElement('btn-risk-assessment', 'click', () => this.performRiskAssessment());
        this.setupElement('btn-investment-analysis', 'click', () => this.performInvestmentAnalysis());

        // Chatbot
        this.setupElement('btn-send-message', 'click', () => this.sendChatMessage());
        this.setupElement('chatInput', 'keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });

        // Market Data
        this.setupElement('btn-refresh-market', 'click', () => this.refreshMarketData());
        this.setupElement('btn-refresh-news', 'click', () => this.refreshStockNews());
        this.setupElement('btn-company-analysis', 'click', () => this.performCompanyAnalysis());
        this.setupElement('btn-global-news', 'click', () => this.refreshGlobalNews());

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(e.target.closest('.nav-link'));
            });
        });
    }

    // Helper method to setup event listeners safely
    setupElement(id, event, handler) {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener(event, handler);
        }
    }

    // Load initial data
    async loadInitialData() {
        try {
            await this.loadSymbols();
            await this.checkAPIStatus();
            this.updateAgentsStatus();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showToast('Error loading initial data', 'error');
        }
    }

    // Load available symbols
    async loadSymbols() {
        try {
            const response = await fetch(`${this.API_BASE}/vn-symbols`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            this.symbols = await response.json();
            this.groupSymbolsBySector();
            this.populateSectorSelect();
            this.updateDataSourceIndicator();
        } catch (error) {
            console.error('Error loading symbols:', error);
            this.showToast('Failed to load stock symbols', 'error');
        }
    }

    // Group symbols by sector
    groupSymbolsBySector() {
        this.sectors = {};
        this.symbols.forEach(stock => {
            const sector = stock.sector || 'Other';
            if (!this.sectors[sector]) {
                this.sectors[sector] = [];
            }
            this.sectors[sector].push(stock);
        });
    }

    // Populate sector select dropdown
    populateSectorSelect() {
        const sectorSelect = document.getElementById('sectorSelect');
        if (!sectorSelect) return;

        sectorSelect.innerHTML = '<option value="">Select a sector...</option>';
        Object.keys(this.sectors).forEach(sector => {
            const option = document.createElement('option');
            option.value = sector;
            option.textContent = `${sector} (${this.sectors[sector].length} stocks)`;
            sectorSelect.appendChild(option);
        });
    }

    // Handle sector change
    onSectorChange(sector) {
        const stockSelect = document.getElementById('stockSelect');
        if (!stockSelect) return;

        if (!sector) {
            stockSelect.innerHTML = '<option value="">Select a sector first</option>';
            return;
        }

        stockSelect.innerHTML = '<option value="">Select a stock...</option>';
        this.sectors[sector].forEach(stock => {
            const option = document.createElement('option');
            option.value = stock.symbol;
            option.textContent = `${stock.symbol} - ${stock.name}`;
            stockSelect.appendChild(option);
        });
    }

    // Handle stock change
    onStockChange(symbol) {
        this.selectedSymbol = symbol;
        this.updateUI();
    }

    // Update data source indicator
    updateDataSourceIndicator() {
        const indicator = document.getElementById('dataSourceIndicator');
        if (!indicator) return;

        const dataSource = this.symbols.length > 0 ? this.symbols[0].data_source : 'Unknown';
        const isCrewAI = dataSource === 'CrewAI';
        
        indicator.className = `data-source-indicator ${isCrewAI ? 'crewai' : 'static'}`;
        indicator.innerHTML = `
            <i class="fas fa-${isCrewAI ? 'robot' : 'database'}"></i>
            ${isCrewAI ? `✅ ${this.symbols.length} symbols from CrewAI` : `📋 ${this.symbols.length} static symbols`}
        `;
    }

    // Setup Gemini API
    async setupGeminiAPI() {
        const apiKey = document.getElementById('geminiApiKey')?.value?.trim();
        if (!apiKey) {
            this.showToast('Please enter Gemini API key', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE}/set-gemini-key`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            });

            const result = await response.json();
            if (result.status === 'success') {
                this.apiKeyStatus.gemini = true;
                this.showToast('✅ Gemini API configured successfully!', 'success');
                this.updateAgentsStatus();
            } else {
                throw new Error(result.message || 'Failed to configure Gemini API');
            }
        } catch (error) {
            this.showToast(`❌ Error: ${error.message}`, 'error');
        }
    }

    // Setup CrewAI
    async setupCrewAI() {
        const geminiKey = document.getElementById('geminiApiKey')?.value?.trim();
        const serperKey = document.getElementById('serperApiKey')?.value?.trim();

        if (!geminiKey) {
            this.showToast('Gemini API key is required for CrewAI', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE}/set-crewai-keys`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    gemini_api_key: geminiKey,
                    serper_api_key: serperKey || null
                })
            });

            const result = await response.json();
            if (result.status === 'success') {
                this.apiKeyStatus.crewai = true;
                this.showToast('✅ CrewAI configured successfully!', 'success');
                await this.loadSymbols(); // Reload symbols with CrewAI data
                this.updateAgentsStatus();
            } else {
                this.showToast('⚠️ CrewAI not available, using fallback', 'warning');
            }
        } catch (error) {
            this.showToast(`❌ Error: ${error.message}`, 'error');
        }
    }

    // Check API status
    async checkAPIStatus() {
        try {
            const response = await fetch(`${this.API_BASE}/health`);
            const health = await response.json();
            
            this.apiKeyStatus.gemini = health.agents?.gemini_agent === 'ready';
            this.apiKeyStatus.crewai = health.agents?.crewai_integration === 'ready';
        } catch (error) {
            console.error('Error checking API status:', error);
        }
    }

    // Update agents status display
    updateAgentsStatus() {
        const agentsContainer = document.getElementById('agentsStatus');
        if (!agentsContainer) return;

        const agents = [
            { name: 'PricePredictor', icon: 'chart-line', status: 'active' },
            { name: 'TickerNews', icon: 'newspaper', status: 'active' },
            { name: 'MarketNews', icon: 'globe', status: 'active' },
            { name: 'InvestmentExpert', icon: 'briefcase', status: 'active' },
            { name: 'RiskExpert', icon: 'shield-alt', status: 'active' },
            { name: 'GeminiAgent', icon: 'robot', status: this.apiKeyStatus.gemini ? 'active' : 'inactive' },
            { name: 'CrewAI', icon: 'users', status: this.apiKeyStatus.crewai ? 'active' : 'inactive' }
        ];

        agentsContainer.innerHTML = agents.map(agent => `
            <div class="agent-status ${agent.status}">
                <span class="agent-name">
                    <i class="fas fa-${agent.icon}"></i>
                    ${agent.name}
                </span>
                <span class="status-indicator ${agent.status}"></span>
            </div>
        `).join('');
    }

    // Update investment profile
    updateInvestmentProfile(key, value) {
        this.investmentProfile[key] = value;
        this.updateInvestmentProfileDisplay();
    }

    // Update risk tolerance
    updateRiskTolerance(value) {
        document.getElementById('riskValue').textContent = value;
        this.updateInvestmentProfile('riskTolerance', parseInt(value));
    }

    // Update investment profile display
    updateInvestmentProfileDisplay() {
        const profileContainer = document.getElementById('investmentProfile');
        if (!profileContainer) return;

        const { timeHorizon, riskTolerance, investmentAmount } = this.investmentProfile;
        
        let riskLabel, riskColor;
        if (riskTolerance <= 30) {
            riskLabel = '🟢 Conservative';
            riskColor = 'var(--success-color)';
        } else if (riskTolerance <= 70) {
            riskLabel = '🟡 Balanced';
            riskColor = 'var(--warning-color)';
        } else {
            riskLabel = '🔴 Aggressive';
            riskColor = 'var(--danger-color)';
        }

        profileContainer.innerHTML = `
            <div class="profile-item">
                <span class="profile-label">Profile:</span>
                <span class="profile-value" style="color: ${riskColor}">${riskLabel}</span>
            </div>
            <div class="profile-item">
                <span class="profile-label">Horizon:</span>
                <span class="profile-value">${timeHorizon}</span>
            </div>
            <div class="profile-item">
                <span class="profile-label">Amount:</span>
                <span class="profile-value">${investmentAmount.toLocaleString()} VND</span>
            </div>
        `;
    }

    // Switch tabs
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName)?.classList.add('active');
    }

    // Handle navigation
    handleNavigation(link) {
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        const href = link.getAttribute('href');
        if (href && href.startsWith('#')) {
            const tabName = href.substring(1);
            this.switchTab(tabName);
        }
    }

    // Perform full analysis
    async performFullAnalysis() {
        if (!this.selectedSymbol) {
            this.showToast('Please select a stock first', 'warning');
            return;
        }

        const resultsContainer = document.getElementById('analysisResults');
        if (!resultsContainer) return;

        this.showAnalysisLoading(resultsContainer, 'Comprehensive Analysis in Progress');

        try {
            const response = await fetch(`${this.API_BASE}/analyze?symbol=${this.selectedSymbol}`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            this.displayAnalysisResults(resultsContainer, result);
            this.showToast('✅ Analysis completed successfully!', 'success');
        } catch (error) {
            this.showError(resultsContainer, error.message);
            this.showToast(`❌ Analysis failed: ${error.message}`, 'error');
        }
    }

    // Show analysis loading
    showAnalysisLoading(container, message) {
        container.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">${message}</div>
                <div class="loading-subtext">AI Agents are working...</div>
            </div>
        `;
    }

    // Display analysis results
    displayAnalysisResults(container, result) {
        let html = '';

        // Stock Information
        if (result.vn_stock_data) {
            html += this.createStockInfoCard(result.vn_stock_data);
        }

        // Create metrics grid
        html += '<div class="metrics-grid">';
        
        if (result.vn_stock_data) {
            const stock = result.vn_stock_data;
            html += this.createMetricCard('Market Cap', `${stock.market_cap.toLocaleString()}B VND`);
            html += this.createMetricCard('P/E Ratio', stock.pe_ratio || 'N/A');
            html += this.createMetricCard('P/B Ratio', stock.pb_ratio || 'N/A');
            html += this.createMetricCard('Volume', stock.volume.toLocaleString());
        }
        
        html += '</div>';

        // Analysis Cards
        const analysisCards = document.createElement('div');
        analysisCards.style.display = 'grid';
        analysisCards.style.gridTemplateColumns = 'repeat(auto-fit, minmax(400px, 1fr))';
        analysisCards.style.gap = 'var(--spacing-lg)';
        analysisCards.style.marginTop = 'var(--spacing-xl)';

        // Price Prediction
        if (result.price_prediction && !result.price_prediction.error) {
            html += this.createPredictionCard(result.price_prediction);
        }

        // Investment Analysis
        if (result.investment_analysis && !result.investment_analysis.error) {
            html += this.createInvestmentCard(result.investment_analysis);
        }

        // Risk Assessment
        if (result.risk_assessment && !result.risk_assessment.error) {
            html += this.createRiskCard(result.risk_assessment);
        }

        container.innerHTML = html;
    }

    // Create stock info card
    createStockInfoCard(stock) {
        const changeClass = stock.change_percent > 0 ? 'positive' : stock.change_percent < 0 ? 'negative' : 'neutral';
        const changeIcon = stock.change_percent > 0 ? '↗️' : stock.change_percent < 0 ? '↘️' : '➡️';

        return `
            <div class="card" style="margin-bottom: var(--spacing-xl);">
                <div class="card-header">
                    <h2 class="card-title">${stock.symbol} - ${stock.sector}</h2>
                </div>
                <div class="card-body">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-lg);">
                        <div>
                            <div style="font-size: var(--font-size-4xl); font-weight: 700; color: var(--primary-color);">
                                ${stock.price.toLocaleString()} VND
                            </div>
                            <div class="metric-change ${changeClass}" style="font-size: var(--font-size-xl); font-weight: 600;">
                                ${changeIcon} ${stock.change_percent > 0 ? '+' : ''}${stock.change_percent.toFixed(2)}% (${stock.change > 0 ? '+' : ''}${stock.change.toLocaleString()})
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: var(--font-size-sm); color: var(--gray-600);">Exchange</div>
                            <div style="font-size: var(--font-size-lg); font-weight: 600;">${stock.exchange}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Create metric card
    createMetricCard(title, value, change = null) {
        const changeHtml = change ? `<div class="metric-change">${change}</div>` : '';
        return `
            <div class="metric-card">
                <div class="metric-title">${title}</div>
                <div class="metric-value">${value}</div>
                ${changeHtml}
            </div>
        `;
    }

    // Create prediction card
    createPredictionCard(prediction) {
        const trendClass = prediction.trend === 'bullish' ? 'success' : prediction.trend === 'bearish' ? 'danger' : 'warning';
        const trendIcon = prediction.trend === 'bullish' ? '📈' : prediction.trend === 'bearish' ? '📉' : '📊';

        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-chart-line"></i>
                        Price Prediction
                    </h3>
                </div>
                <div class="card-body">
                    <div class="recommendation-card ${trendClass === 'success' ? 'buy' : trendClass === 'danger' ? 'sell' : 'hold'}">
                        <div class="rec-icon">${trendIcon}</div>
                        <div class="rec-title">${prediction.trend.toUpperCase()}</div>
                        <div class="rec-reason">
                            Predicted Price: ${prediction.predicted_price?.toLocaleString() || 'N/A'} VND<br>
                            Change: ${prediction.change_percent > 0 ? '+' : ''}${prediction.change_percent?.toFixed(2) || 0}%
                        </div>
                        <div class="rec-confidence">Confidence: ${prediction.confidence || 'N/A'}</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Create investment card
    createInvestmentCard(investment) {
        const recClass = investment.recommendation === 'BUY' ? 'buy' : investment.recommendation === 'SELL' ? 'sell' : 'hold';
        const recIcon = investment.recommendation === 'BUY' ? '🚀' : investment.recommendation === 'SELL' ? '📉' : '⏸️';

        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-briefcase"></i>
                        Investment Analysis
                    </h3>
                </div>
                <div class="card-body">
                    <div class="recommendation-card ${recClass}">
                        <div class="rec-icon">${recIcon}</div>
                        <div class="rec-title">${investment.recommendation || 'HOLD'}</div>
                        <div class="rec-reason">${investment.reason || 'Analysis based on current market conditions'}</div>
                        <div class="rec-confidence">Confidence: 75%</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Create risk card
    createRiskCard(risk) {
        const riskLevel = risk.risk_level || 'MEDIUM';
        const riskColor = riskLevel === 'LOW' ? 'success' : riskLevel === 'HIGH' ? 'danger' : 'warning';
        const riskIcon = riskLevel === 'LOW' ? '✅' : riskLevel === 'HIGH' ? '⚠️' : '⚡';

        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-shield-alt"></i>
                        Risk Assessment
                    </h3>
                </div>
                <div class="card-body">
                    <div class="recommendation-card ${riskColor === 'success' ? 'buy' : riskColor === 'danger' ? 'sell' : 'hold'}">
                        <div class="rec-icon">${riskIcon}</div>
                        <div class="rec-title">${riskLevel} RISK</div>
                        <div class="rec-reason">
                            Volatility: ${risk.volatility?.toFixed(2) || 'N/A'}%<br>
                            Max Drawdown: ${risk.max_drawdown?.toFixed(2) || 'N/A'}%
                        </div>
                        <div class="rec-confidence">Risk Score: ${risk.risk_score || 'N/A'}/10</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Perform individual analyses
    async performPricePrediction() {
        await this.performIndividualAnalysis('predict', 'Price Prediction');
    }

    async performRiskAssessment() {
        await this.performIndividualAnalysis('risk', 'Risk Assessment');
    }

    async performInvestmentAnalysis() {
        // This would need to be implemented in the backend
        this.showToast('Investment analysis coming soon!', 'info');
    }

    // Generic method for individual analysis
    async performIndividualAnalysis(endpoint, title) {
        if (!this.selectedSymbol) {
            this.showToast('Please select a stock first', 'warning');
            return;
        }

        const resultsContainer = document.getElementById('analysisResults');
        if (!resultsContainer) return;

        this.showAnalysisLoading(resultsContainer, `${title} in Progress`);

        try {
            const response = await fetch(`${this.API_BASE}/${endpoint}/${this.selectedSymbol}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            resultsContainer.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">${title} Results</h3>
                    </div>
                    <div class="card-body">
                        <pre style="background: var(--gray-100); padding: var(--spacing-lg); border-radius: var(--border-radius); overflow-x: auto;">
${JSON.stringify(result, null, 2)}
                        </pre>
                    </div>
                </div>
            `;
            
            this.showToast(`✅ ${title} completed!`, 'success');
        } catch (error) {
            this.showError(resultsContainer, error.message);
            this.showToast(`❌ ${title} failed: ${error.message}`, 'error');
        }
    }

    // Send chat message
    async sendChatMessage() {
        const chatInput = document.getElementById('chatInput');
        const chatMessages = document.getElementById('chatMessages');
        
        if (!chatInput || !chatMessages) return;
        
        const message = chatInput.value.trim();
        if (!message) return;

        if (!this.apiKeyStatus.gemini) {
            this.showToast('Please configure Gemini API key first', 'warning');
            return;
        }

        // Add user message
        this.addChatMessage(chatMessages, message, 'user');
        chatInput.value = '';

        // Add loading message
        const loadingId = this.addChatMessage(chatMessages, 'AI is thinking...', 'bot', true);

        try {
            const response = await fetch(`${this.API_BASE}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: message,
                    symbol: this.selectedSymbol || ''
                })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const result = await response.json();
            
            // Remove loading message
            document.getElementById(loadingId)?.remove();
            
            if (result.expert_advice) {
                this.addChatMessage(chatMessages, result.expert_advice, 'bot');
                
                if (result.recommendations && result.recommendations.length > 0) {
                    const recommendations = result.recommendations.map((rec, i) => `${i + 1}. ${rec}`).join('\n');
                    this.addChatMessage(chatMessages, `**Recommendations:**\n${recommendations}`, 'bot');
                }
            } else {
                this.addChatMessage(chatMessages, 'Sorry, I couldn\'t process your request.', 'bot');
            }
        } catch (error) {
            document.getElementById(loadingId)?.remove();
            this.addChatMessage(chatMessages, `Error: ${error.message}`, 'bot');
            this.showToast(`❌ Chat error: ${error.message}`, 'error');
        }
    }

    // Add chat message
    addChatMessage(container, message, type, isLoading = false) {
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const messageHtml = `
            <div id="${messageId}" class="chat-message ${type}">
                <div class="message-avatar">
                    <i class="fas fa-${type === 'user' ? 'user' : 'robot'}"></i>
                </div>
                <div class="message-content">
                    <p>${isLoading ? '<i class="fas fa-spinner fa-spin"></i> ' + message : this.formatChatMessage(message)}</p>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', messageHtml);
        container.scrollTop = container.scrollHeight;
        
        return messageId;
    }

    // Format chat message
    formatChatMessage(message) {
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    // Refresh market data
    async refreshMarketData() {
        const marketContainer = document.getElementById('marketData');
        if (!marketContainer) return;

        marketContainer.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading Market Data</div>
            </div>
        `;

        try {
            const response = await fetch(`${this.API_BASE}/vn-market`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            this.displayMarketData(marketContainer, data);
            this.showToast('✅ Market data refreshed!', 'success');
        } catch (error) {
            this.showError(marketContainer, error.message);
            this.showToast(`❌ Failed to refresh market data: ${error.message}`, 'error');
        }
    }

    // Display market data
    displayMarketData(container, data) {
        let html = '<div class="metrics-grid">';
        
        if (data.vn_index) {
            const vn = data.vn_index;
            const changeClass = vn.change_percent > 0 ? 'positive' : vn.change_percent < 0 ? 'negative' : 'neutral';
            html += this.createMetricCard(
                'VN-Index',
                vn.value.toLocaleString(),
                `<span class="${changeClass}">${vn.change_percent > 0 ? '+' : ''}${vn.change_percent.toFixed(2)}%</span>`
            );
        }

        if (data.vn30_index) {
            const vn30 = data.vn30_index;
            const changeClass = vn30.change_percent > 0 ? 'positive' : vn30.change_percent < 0 ? 'negative' : 'neutral';
            html += this.createMetricCard(
                'VN30-Index',
                vn30.value.toLocaleString(),
                `<span class="${changeClass}">${vn30.change_percent > 0 ? '+' : ''}${vn30.change_percent.toFixed(2)}%</span>`
            );
        }

        if (data.hn_index) {
            const hn = data.hn_index;
            const changeClass = hn.change_percent > 0 ? 'positive' : hn.change_percent < 0 ? 'negative' : 'neutral';
            html += this.createMetricCard(
                'HN-Index',
                hn.value.toLocaleString(),
                `<span class="${changeClass}">${hn.change_percent > 0 ? '+' : ''}${hn.change_percent.toFixed(2)}%</span>`
            );
        }

        html += '</div>';

        // Top movers
        if (data.top_gainers || data.top_losers) {
            html += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-lg); margin-top: var(--spacing-xl);">';
            
            if (data.top_gainers) {
                html += '<div class="card"><div class="card-header"><h3 class="card-title">🚀 Top Gainers</h3></div><div class="card-body">';
                data.top_gainers.slice(0, 5).forEach(stock => {
                    html += `<div style="padding: var(--spacing-sm); background: #d4edda; margin: var(--spacing-xs) 0; border-radius: var(--border-radius-sm); border-left: 4px solid var(--success-color);">
                        <strong>${stock.symbol}</strong>: +${stock.change_percent.toFixed(2)}%
                    </div>`;
                });
                html += '</div></div>';
            }

            if (data.top_losers) {
                html += '<div class="card"><div class="card-header"><h3 class="card-title">📉 Top Losers</h3></div><div class="card-body">';
                data.top_losers.slice(0, 5).forEach(stock => {
                    html += `<div style="padding: var(--spacing-sm); background: #f8d7da; margin: var(--spacing-xs) 0; border-radius: var(--border-radius-sm); border-left: 4px solid var(--danger-color);">
                        <strong>${stock.symbol}</strong>: ${stock.change_percent.toFixed(2)}%
                    </div>`;
                });
                html += '</div></div>';
            }

            html += '</div>';
        }

        container.innerHTML = html;
    }

    // Refresh stock news
    async refreshStockNews() {
        if (!this.selectedSymbol) {
            this.showToast('Please select a stock first', 'warning');
            return;
        }

        const newsContainer = document.getElementById('newsContent');
        if (!newsContainer) return;

        newsContainer.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading Stock News</div>
            </div>
        `;

        try {
            const response = await fetch(`${this.API_BASE}/news/${this.selectedSymbol}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            this.displayNews(newsContainer, data);
            this.showToast('✅ News refreshed!', 'success');
        } catch (error) {
            this.showError(newsContainer, error.message);
            this.showToast(`❌ Failed to refresh news: ${error.message}`, 'error');
        }
    }

    // Display news
    displayNews(container, data) {
        if (data.error) {
            this.showError(container, data.error);
            return;
        }

        if (!data.news || data.news.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <div class="card-body" style="text-align: center; padding: var(--spacing-2xl);">
                        <i class="fas fa-newspaper" style="font-size: 3rem; color: var(--gray-400); margin-bottom: var(--spacing-lg);"></i>
                        <h3>No news available</h3>
                        <p>No recent news found for ${this.selectedSymbol}</p>
                    </div>
                </div>
            `;
            return;
        }

        let html = `<div style="margin-bottom: var(--spacing-lg);">
            <h3>📰 Latest News for ${this.selectedSymbol}</h3>
            <p>Found ${data.news_count || data.news.length} news articles</p>
        </div>`;

        data.news.forEach((news, index) => {
            html += `
                <div class="news-card">
                    <div class="news-title">${news.title || 'No title'}</div>
                    <div class="news-meta">${news.publisher || 'Unknown'} • ${news.published || 'Unknown date'}</div>
                    <div class="news-summary">${news.summary || 'No summary available'}</div>
                    ${news.link ? `<a href="${news.link}" target="_blank" class="news-link">
                        <i class="fas fa-external-link-alt"></i>
                        Read more
                    </a>` : ''}
                </div>
            `;
        });

        container.innerHTML = html;
    }

    // Perform company analysis
    async performCompanyAnalysis() {
        if (!this.selectedSymbol) {
            this.showToast('Please select a stock first', 'warning');
            return;
        }

        if (!this.apiKeyStatus.crewai) {
            this.showToast('CrewAI is required for company analysis', 'warning');
            return;
        }

        const companyContainer = document.getElementById('companyContent');
        if (!companyContainer) return;

        companyContainer.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Analyzing Company Data</div>
                <div class="loading-subtext">CrewAI is gathering information...</div>
            </div>
        `;

        // This would need to be implemented in the backend
        setTimeout(() => {
            companyContainer.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🏢 Company Analysis for ${this.selectedSymbol}</h3>
                    </div>
                    <div class="card-body">
                        <p>Company analysis feature is coming soon! This will include:</p>
                        <ul>
                            <li>Detailed company information</li>
                            <li>Financial metrics</li>
                            <li>Management team</li>
                            <li>Business segments</li>
                            <li>Competitive analysis</li>
                        </ul>
                    </div>
                </div>
            `;
            this.showToast('Company analysis feature coming soon!', 'info');
        }, 2000);
    }

    // Refresh global news
    async refreshGlobalNews() {
        const globalContainer = document.getElementById('globalNewsContent');
        if (!globalContainer) return;

        globalContainer.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading Global News</div>
            </div>
        `;

        // This would need to be implemented in the backend
        setTimeout(() => {
            globalContainer.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🌍 Global Market News</h3>
                    </div>
                    <div class="card-body">
                        <p>Global news feature is coming soon! This will include:</p>
                        <ul>
                            <li>International market updates</li>
                            <li>Economic indicators</li>
                            <li>Central bank decisions</li>
                            <li>Geopolitical events</li>
                            <li>Currency movements</li>
                        </ul>
                    </div>
                </div>
            `;
            this.showToast('Global news feature coming soon!', 'info');
        }, 2000);
    }

    // Show error
    showError(container, message) {
        container.innerHTML = `
            <div class="card">
                <div class="card-body" style="text-align: center; padding: var(--spacing-2xl);">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--danger-color); margin-bottom: var(--spacing-lg);"></i>
                    <h3 style="color: var(--danger-color);">Error</h3>
                    <p>${message}</p>
                </div>
            </div>
        `;
    }

    // Show toast notification
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        if (!toast) return;

        toast.textContent = message;
        toast.className = `toast ${type} show`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }

    // Update UI
    updateUI() {
        this.updateInvestmentProfileDisplay();
        this.updateAgentsStatus();
        
        // Update header with selected stock
        if (this.selectedSymbol) {
            const headerTitle = document.querySelector('.content-header h1');
            if (headerTitle) {
                headerTitle.textContent = `Stock Analysis Dashboard - ${this.selectedSymbol}`;
            }
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.tradingApp = new TradingApp();
});

// Export for global access
window.TradingApp = TradingApp;