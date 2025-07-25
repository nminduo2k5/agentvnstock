import streamlit as st
from typing import Dict, List, Optional, Any

class BootstrapComponents:
    """Bootstrap-enhanced UI components for professional trading interface"""
    
    @staticmethod
    def alert(message: str, alert_type: str = "info", dismissible: bool = False, icon: str = None) -> str:
        """Create Bootstrap alert with icons"""
        icons = {
            "success": "bi-check-circle-fill",
            "danger": "bi-x-circle-fill", 
            "warning": "bi-exclamation-triangle-fill",
            "info": "bi-info-circle-fill"
        }
        
        icon_html = f'<i class="bi {icon or icons.get(alert_type, "bi-info-circle-fill")} me-2"></i>'
        dismiss_html = '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' if dismissible else ''
        
        return f"""
        <div class="alert alert-{alert_type} border-0 shadow-sm {'alert-dismissible' if dismissible else ''}" role="alert">
            <div class="d-flex align-items-center">
                {icon_html}
                <div class="flex-grow-1">{message}</div>
                {dismiss_html}
            </div>
        </div>
        """
    
    @staticmethod
    def card(title: str, content: str, header_class: str = "bg-primary text-white", 
             footer: str = None, card_class: str = "border-0 shadow-sm") -> str:
        """Create Bootstrap card with professional styling"""
        footer_html = f'<div class="card-footer bg-light">{footer}</div>' if footer else ''
        
        return f"""
        <div class="card {card_class} mb-4">
            <div class="card-header {header_class}">
                <h5 class="card-title mb-0">{title}</h5>
            </div>
            <div class="card-body">
                {content}
            </div>
            {footer_html}
        </div>
        """
    
    @staticmethod
    def metric_card(title: str, value: str, change: str = None, 
                   change_type: str = "neutral", icon: str = None) -> str:
        """Create professional metric card with Bootstrap styling"""
        change_colors = {
            "positive": "text-success",
            "negative": "text-danger", 
            "neutral": "text-muted"
        }
        
        icon_html = f'<i class="bi {icon} text-primary fs-2 mb-2"></i>' if icon else ''
        change_html = f'<div class="mt-2 {change_colors.get(change_type, "text-muted")}">{change}</div>' if change else ''
        
        return f"""
        <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
                {icon_html}
                <h6 class="card-subtitle mb-2 text-muted text-uppercase fw-bold">{title}</h6>
                <h3 class="card-title text-primary fw-bold mb-0">{value}</h3>
                {change_html}
            </div>
        </div>
        """
    
    @staticmethod
    def progress_bar(value: int, label: str = None, color: str = "primary", 
                    striped: bool = False, animated: bool = False) -> str:
        """Create Bootstrap progress bar"""
        classes = f"progress-bar bg-{color}"
        if striped:
            classes += " progress-bar-striped"
        if animated:
            classes += " progress-bar-animated"
            
        label_html = f'<div class="d-flex justify-content-between mb-1"><span>{label}</span><span>{value}%</span></div>' if label else ''
        
        return f"""
        {label_html}
        <div class="progress mb-3" style="height: 10px;">
            <div class="{classes}" role="progressbar" style="width: {value}%"></div>
        </div>
        """
    
    @staticmethod
    def badge(text: str, color: str = "primary", pill: bool = True) -> str:
        """Create Bootstrap badge"""
        pill_class = "rounded-pill" if pill else ""
        return f'<span class="badge bg-{color} {pill_class}">{text}</span>'
    
    @staticmethod
    def button_group(buttons: List[Dict[str, str]], size: str = "md") -> str:
        """Create Bootstrap button group"""
        size_class = f"btn-group-{size}" if size != "md" else "btn-group"
        
        buttons_html = ""
        for btn in buttons:
            buttons_html += f'<button type="button" class="btn btn-{btn.get("color", "primary")}" onclick="{btn.get("onclick", "")}">{btn.get("text", "")}</button>'
        
        return f'<div class="{size_class}" role="group">{buttons_html}</div>'
    
    @staticmethod
    def list_group(items: List[Dict[str, Any]], flush: bool = True) -> str:
        """Create Bootstrap list group"""
        flush_class = "list-group-flush" if flush else ""
        
        items_html = ""
        for item in items:
            active_class = "active" if item.get("active", False) else ""
            badge_html = f' <span class="badge bg-{item.get("badge_color", "primary")} rounded-pill">{item["badge"]}</span>' if item.get("badge") else ""
            icon_html = f'<i class="bi {item["icon"]} me-2"></i>' if item.get("icon") else ""
            
            items_html += f"""
            <li class="list-group-item d-flex justify-content-between align-items-center {active_class}">
                <div>{icon_html}{item["text"]}</div>
                {badge_html}
            </li>
            """
        
        return f'<ul class="list-group {flush_class}">{items_html}</ul>'
    
    @staticmethod
    def accordion(items: List[Dict[str, str]], accordion_id: str = "accordion") -> str:
        """Create Bootstrap accordion"""
        items_html = ""
        
        for i, item in enumerate(items):
            item_id = f"{accordion_id}-{i}"
            show_class = "show" if i == 0 else ""
            collapsed_class = "" if i == 0 else "collapsed"
            
            items_html += f"""
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button {collapsed_class}" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#{item_id}">
                        {item["title"]}
                    </button>
                </h2>
                <div id="{item_id}" class="accordion-collapse collapse {show_class}" 
                     data-bs-parent="#{accordion_id}">
                    <div class="accordion-body">
                        {item["content"]}
                    </div>
                </div>
            </div>
            """
        
        return f'<div class="accordion" id="{accordion_id}">{items_html}</div>'
    
    @staticmethod
    def modal(modal_id: str, title: str, body: str, footer: str = None, 
              size: str = "md", centered: bool = True) -> str:
        """Create Bootstrap modal"""
        size_class = f"modal-{size}" if size != "md" else ""
        centered_class = "modal-dialog-centered" if centered else ""
        footer_html = f'<div class="modal-footer">{footer}</div>' if footer else ''
        
        return f"""
        <div class="modal fade" id="{modal_id}" tabindex="-1">
            <div class="modal-dialog {size_class} {centered_class}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">{title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        {body}
                    </div>
                    {footer_html}
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def toast(toast_id: str, title: str, message: str, color: str = "primary", 
              auto_hide: bool = True, delay: int = 5000) -> str:
        """Create Bootstrap toast notification"""
        auto_hide_attr = f'data-bs-autohide="true" data-bs-delay="{delay}"' if auto_hide else 'data-bs-autohide="false"'
        
        return f"""
        <div class="toast align-items-center text-bg-{color} border-0" id="{toast_id}" 
             role="alert" {auto_hide_attr}>
            <div class="d-flex">
                <div class="toast-body">
                    <strong>{title}</strong><br>
                    {message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        </div>
        """

class TradingComponents:
    """Specialized components for trading interface"""
    
    @staticmethod
    def stock_header(symbol: str, name: str, price: float, change: float, 
                    change_percent: float, volume: int, sector: str = None) -> str:
        """Create professional stock header"""
        change_class = "text-success" if change > 0 else "text-danger" if change < 0 else "text-muted"
        change_icon = "bi-arrow-up" if change > 0 else "bi-arrow-down" if change < 0 else "bi-arrow-right"
        sector_html = f'<span class="badge bg-secondary rounded-pill">{sector}</span>' if sector else ''
        
        return f"""
        <div class="card border-0 shadow-lg mb-4">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <div class="d-flex align-items-center mb-2">
                            <h1 class="display-6 fw-bold text-primary me-3">{symbol}</h1>
                            {sector_html}
                        </div>
                        <h5 class="text-muted mb-3">{name}</h5>
                        <div class="d-flex align-items-center">
                            <span class="display-4 fw-bold text-primary me-3">{price:,.0f} VND</span>
                            <div class="{change_class}">
                                <i class="bi {change_icon} me-1"></i>
                                <span class="fs-5 fw-bold">{change:+,.0f} ({change_percent:+.2f}%)</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="text-muted mb-1">Volume</div>
                        <div class="fs-4 fw-bold">{volume:,}</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def recommendation_card(recommendation: str, reason: str, confidence: int, 
                          price_target: float = None) -> str:
        """Create professional recommendation card"""
        rec_colors = {
            "BUY": {"bg": "success", "icon": "bi-arrow-up-circle-fill"},
            "SELL": {"bg": "danger", "icon": "bi-arrow-down-circle-fill"},
            "HOLD": {"bg": "warning", "icon": "bi-pause-circle-fill"}
        }
        
        rec_config = rec_colors.get(recommendation.upper(), {"bg": "secondary", "icon": "bi-dash-circle-fill"})
        price_target_html = f'<div class="mt-2"><strong>Price Target:</strong> {price_target:,.0f} VND</div>' if price_target else ''
        
        return f"""
        <div class="card border-0 shadow-lg text-white bg-{rec_config['bg']} mb-4">
            <div class="card-body text-center">
                <i class="bi {rec_config['icon']} display-1 mb-3"></i>
                <h2 class="card-title fw-bold mb-3">{recommendation}</h2>
                <p class="card-text fs-5 mb-3">{reason}</p>
                <div class="progress bg-light bg-opacity-25 mb-2" style="height: 8px;">
                    <div class="progress-bar bg-white" style="width: {confidence}%"></div>
                </div>
                <small>Confidence: {confidence}%</small>
                {price_target_html}
            </div>
        </div>
        """
    
    @staticmethod
    def risk_indicator(risk_level: str, volatility: float = None, 
                      max_drawdown: float = None) -> str:
        """Create risk assessment indicator"""
        risk_configs = {
            "LOW": {"color": "success", "icon": "bi-shield-check", "text": "Low Risk"},
            "MEDIUM": {"color": "warning", "icon": "bi-shield-exclamation", "text": "Medium Risk"},
            "HIGH": {"color": "danger", "icon": "bi-shield-x", "text": "High Risk"}
        }
        
        config = risk_configs.get(risk_level.upper(), risk_configs["MEDIUM"])
        
        metrics_html = ""
        if volatility is not None:
            metrics_html += f'<div class="col-6"><strong>Volatility:</strong><br>{volatility:.2f}%</div>'
        if max_drawdown is not None:
            metrics_html += f'<div class="col-6"><strong>Max Drawdown:</strong><br>{max_drawdown:.2f}%</div>'
        
        if metrics_html:
            metrics_html = f'<div class="row mt-3 text-center">{metrics_html}</div>'
        
        return f"""
        <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
                <div class="text-{config['color']} mb-3">
                    <i class="bi {config['icon']} display-4"></i>
                </div>
                <h4 class="text-{config['color']} fw-bold">{config['text']}</h4>
                {metrics_html}
            </div>
        </div>
        """
    
    @staticmethod
    def news_card(title: str, summary: str, source: str, published: str, 
                 link: str = None, sentiment: str = None) -> str:
        """Create professional news card"""
        sentiment_html = ""
        if sentiment:
            sentiment_colors = {
                "positive": "success",
                "negative": "danger", 
                "neutral": "secondary"
            }
            color = sentiment_colors.get(sentiment.lower(), "secondary")
            sentiment_html = f'<span class="badge bg-{color} ms-2">{sentiment.title()}</span>'
        
        link_html = f'<a href="{link}" target="_blank" class="btn btn-outline-primary btn-sm"><i class="bi bi-box-arrow-up-right me-1"></i>Read More</a>' if link else ''
        
        return f"""
        <div class="card border-0 shadow-sm mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="card-title text-primary fw-bold mb-0">{title}</h6>
                    {sentiment_html}
                </div>
                <p class="card-text text-muted small mb-2">{source} • {published}</p>
                <p class="card-text">{summary}</p>
                <div class="d-flex justify-content-end">
                    {link_html}
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def agent_status_list(agents: List[Dict[str, Any]]) -> str:
        """Create agent status list with Bootstrap styling"""
        items_html = ""
        
        for agent in agents:
            status_color = "success" if agent["status"] == "active" else "danger"
            status_icon = "bi-check-circle-fill" if agent["status"] == "active" else "bi-x-circle-fill"
            
            items_html += f"""
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center">
                    <i class="bi {agent.get('icon', 'bi-robot')} text-primary me-2"></i>
                    <span class="fw-medium">{agent['name']}</span>
                </div>
                <i class="bi {status_icon} text-{status_color}"></i>
            </li>
            """
        
        return f'<ul class="list-group list-group-flush">{items_html}</ul>'

def render_bootstrap_components():
    """Render Bootstrap components for Streamlit"""
    st.markdown("""
    <script>
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    })
    </script>
    """, unsafe_allow_html=True)