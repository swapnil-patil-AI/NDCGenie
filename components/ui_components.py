"""
UI Components and Styling for NDC Genie
Professional, production-ready UI components.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime
from utils.config import ui_config, app_config


# ═══════════════════════════════════════════════════════════════════════════════
# ICON DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

ICONS = {
    # Status icons
    "completed": "✓",
    "failed": "✗",
    "pending": "⏳",
    "refunded": "↩",
    "rejected": "⊘",
    "investigating": "🔍",
    "abandoned": "○",
    
    # Priority icons
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
    
    # Feature icons
    "search": "🔍",
    "filter": "🔧",
    "export": "📥",
    "refresh": "🔄",
    "chat": "💬",
    "analytics": "📈",
    "help": "❓",
    "settings": "⚙️",
    "user": "👤",
    "flight": "✈️",
    "payment": "💳",
    "refund": "💰",
    "calendar": "📅",
    "clock": "🕐",
    "warning": "⚠️",
    "error": "❌",
    "success": "✅",
    "info": "ℹ️",
    "note": "📝",
    "email": "📧",
    "phone": "📞",
    "loyalty": "⭐",
}


def inject_custom_css():
    """Inject comprehensive custom CSS for professional styling"""
    
    st.markdown(f"""
    <style>
        /* ═══════════════════════════════════════════════════════════════
           IMPORT FONTS
           ═══════════════════════════════════════════════════════════════ */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* ═══════════════════════════════════════════════════════════════
           ROOT VARIABLES
           ═══════════════════════════════════════════════════════════════ */
        :root {{
            --primary: {ui_config.PRIMARY_COLOR};
            --secondary: {ui_config.SECONDARY_COLOR};
            --accent: {ui_config.ACCENT_COLOR};
            --success: {ui_config.SUCCESS_COLOR};
            --warning: {ui_config.WARNING_COLOR};
            --danger: {ui_config.DANGER_COLOR};
            --info: {ui_config.INFO_COLOR};
            
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f1f5f9;
            
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            
            --border-color: #e2e8f0;
            --border-radius: 12px;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           GLOBAL STYLES
           ═══════════════════════════════════════════════════════════════ */
        .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* ═══════════════════════════════════════════════════════════════
           HEADER COMPONENT
           ═══════════════════════════════════════════════════════════════ */
        .app-header {{
            background: linear-gradient(135deg, {ui_config.PRIMARY_COLOR} 0%, {ui_config.SECONDARY_COLOR} 50%, {ui_config.ACCENT_COLOR} 100%);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }}
        
        .app-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            pointer-events: none;
        }}
        
        .app-header h1 {{
            color: white;
            font-size: 2.25rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .app-header .subtitle {{
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            font-weight: 400;
            margin-top: 0.5rem;
        }}
        
        .app-header .version {{
            position: absolute;
            top: 1rem;
            right: 1.5rem;
            background: rgba(255,255,255,0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            color: white;
            font-weight: 500;
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           METRIC CARDS
           ═══════════════════════════════════════════════════════════════ */
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--accent);
        }}
        
        .metric-card.success::before {{ background: var(--success); }}
        .metric-card.warning::before {{ background: var(--warning); }}
        .metric-card.danger::before {{ background: var(--danger); }}
        .metric-card.info::before {{ background: var(--info); }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1;
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .metric-change {{
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            display: inline-block;
            margin-top: 0.5rem;
            font-weight: 600;
        }}
        
        .metric-change.positive {{
            background: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }}
        
        .metric-change.negative {{
            background: rgba(229, 62, 62, 0.1);
            color: var(--danger);
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           STATUS BADGES
           ═══════════════════════════════════════════════════════════════ */
        .status-badge {{
            padding: 0.375rem 0.875rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            letter-spacing: 0.01em;
        }}
        
        .status-completed {{
            background: rgba(56, 161, 105, 0.15);
            color: #22543d;
            border: 1px solid rgba(56, 161, 105, 0.3);
        }}
        
        .status-failed {{
            background: rgba(229, 62, 62, 0.15);
            color: #9b2c2c;
            border: 1px solid rgba(229, 62, 62, 0.3);
        }}
        
        .status-refunded {{
            background: rgba(49, 130, 206, 0.15);
            color: #2a4365;
            border: 1px solid rgba(49, 130, 206, 0.3);
        }}
        
        .status-pending {{
            background: rgba(214, 158, 46, 0.15);
            color: #744210;
            border: 1px solid rgba(214, 158, 46, 0.3);
        }}
        
        .status-rejected {{
            background: rgba(155, 44, 44, 0.15);
            color: #742a2a;
            border: 1px solid rgba(155, 44, 44, 0.3);
        }}
        
        .status-investigation {{
            background: rgba(128, 90, 213, 0.15);
            color: #44337a;
            border: 1px solid rgba(128, 90, 213, 0.3);
        }}
        
        .status-abandoned {{
            background: rgba(113, 128, 150, 0.15);
            color: #4a5568;
            border: 1px solid rgba(113, 128, 150, 0.3);
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           PRIORITY BADGES
           ═══════════════════════════════════════════════════════════════ */
        .priority-badge {{
            padding: 0.25rem 0.625rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .priority-critical {{
            background: #fed7d7;
            color: #9b2c2c;
            animation: pulse-critical 2s infinite;
        }}
        
        @keyframes pulse-critical {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .priority-high {{
            background: #feebc8;
            color: #c05621;
        }}
        
        .priority-medium {{
            background: #faf089;
            color: #975a16;
        }}
        
        .priority-low {{
            background: #c6f6d5;
            color: #276749;
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           TRANSACTION CARDS
           ═══════════════════════════════════════════════════════════════ */
        .transaction-card {{
            background: white;
            border-radius: var(--border-radius);
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }}
        
        .transaction-card:hover {{
            border-color: var(--accent);
            box-shadow: var(--shadow-md);
        }}
        
        .transaction-card.failed {{
            border-left: 4px solid var(--danger);
        }}
        
        .transaction-card.completed {{
            border-left: 4px solid var(--success);
        }}
        
        .transaction-card.refund {{
            border-left: 4px solid var(--info);
        }}
        
        .transaction-card.pending {{
            border-left: 4px solid var(--warning);
        }}
        
        .transaction-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }}
        
        .transaction-id {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--primary);
        }}
        
        .transaction-meta {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           LIFECYCLE STAGES
           ═══════════════════════════════════════════════════════════════ */
        .lifecycle-container {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            padding: 1rem 0;
        }}
        
        .lifecycle-stage {{
            display: flex;
            align-items: center;
            gap: 0.375rem;
            padding: 0.375rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        
        .stage-completed {{
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
        }}
        
        .stage-failed {{
            background: linear-gradient(135deg, #fc8181, #e53e3e);
            color: white;
        }}
        
        .stage-pending {{
            background: linear-gradient(135deg, #f6e05e, #d69e2e);
            color: #744210;
        }}
        
        .stage-not-reached {{
            background: #e2e8f0;
            color: #718096;
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           CHAT INTERFACE
           ═══════════════════════════════════════════════════════════════ */
        .chat-container {{
            background: white;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
        }}
        
        .chat-message {{
            padding: 1rem 1.25rem;
            border-radius: 12px;
            margin: 0.75rem 0;
            line-height: 1.6;
        }}
        
        .chat-message.user {{
            background: linear-gradient(135deg, #ebf4ff, #c3dafe);
            border-left: 4px solid var(--accent);
            margin-left: 2rem;
        }}
        
        .chat-message.assistant {{
            background: linear-gradient(135deg, #f0fff4, #c6f6d5);
            border-left: 4px solid var(--success);
            margin-right: 2rem;
        }}
        
        .chat-message-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .chat-message-content {{
            font-size: 0.95rem;
            color: var(--text-primary);
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           SIDEBAR STYLES
           ═══════════════════════════════════════════════════════════════ */
        .sidebar-section {{
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border-color);
        }}
        
        .sidebar-section h4 {{
            margin: 0 0 0.75rem 0;
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .quick-stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .quick-stat:last-child {{
            border-bottom: none;
        }}
        
        .quick-stat-label {{
            font-size: 0.825rem;
            color: var(--text-secondary);
        }}
        
        .quick-stat-value {{
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--text-primary);
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           ALERT BOXES
           ═══════════════════════════════════════════════════════════════ */
        .alert-box {{
            padding: 1rem 1.25rem;
            border-radius: 8px;
            margin: 1rem 0;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }}
        
        .alert-box.error {{
            background: #fff5f5;
            border: 1px solid #feb2b2;
            color: #c53030;
        }}
        
        .alert-box.warning {{
            background: #fffff0;
            border: 1px solid #f6e05e;
            color: #975a16;
        }}
        
        .alert-box.success {{
            background: #f0fff4;
            border: 1px solid #9ae6b4;
            color: #276749;
        }}
        
        .alert-box.info {{
            background: #ebf8ff;
            border: 1px solid #90cdf4;
            color: #2b6cb0;
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           DATA TABLES
           ═══════════════════════════════════════════════════════════════ */
        .data-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.875rem;
        }}
        
        .data-table th {{
            background: var(--bg-tertiary);
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            color: var(--text-primary);
            border-bottom: 2px solid var(--border-color);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        
        .data-table td {{
            padding: 0.875rem 1rem;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
        }}
        
        .data-table tr:hover td {{
            background: var(--bg-tertiary);
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           BUTTONS
           ═══════════════════════════════════════════════════════════════ */
        .stButton > button {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 0.625rem 1.25rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-sm);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           TABS
           ═══════════════════════════════════════════════════════════════ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: white;
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            border: 1px solid var(--border-color);
            border-bottom: none;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           EXPANDER
           ═══════════════════════════════════════════════════════════════ */
        .streamlit-expanderHeader {{
            background: white;
            border-radius: 8px;
            font-weight: 600;
            border: 1px solid var(--border-color);
        }}
        
        .streamlit-expanderContent {{
            background: white;
            border: 1px solid var(--border-color);
            border-top: none;
            border-radius: 0 0 8px 8px;
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           ANIMATIONS
           ═══════════════════════════════════════════════════════════════ */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .animate-fade-in {{
            animation: fadeIn 0.3s ease-out forwards;
        }}
        
        /* ═══════════════════════════════════════════════════════════════
           SCROLLBAR
           ═══════════════════════════════════════════════════════════════ */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-tertiary);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--text-muted);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-secondary);
        }}
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the application header"""
    st.markdown(f"""
    <div class="app-header">
        <span class="version">v{app_config.APP_VERSION}</span>
        <h1>✈️ {app_config.APP_NAME}</h1>
        <div class="subtitle">{app_config.APP_DESCRIPTION}</div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(value: str, label: str, card_type: str = "", change: str = "", change_type: str = ""):
    """Render a metric card"""
    change_html = ""
    if change:
        change_html = f'<div class="metric-change {change_type}">{change}</div>'
    
    return f"""
    <div class="metric-card {card_type}">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {change_html}
    </div>
    """


def get_status_badge(status: str) -> str:
    """Get HTML for a status badge"""
    status_map = {
        "Completed": ("status-completed", "✓", "Completed"),
        "Failed": ("status-failed", "✗", "Failed"),
        "Refunded": ("status-refunded", "↩", "Refunded"),
        "Refund Pending": ("status-pending", "⏳", "Refund Pending"),
        "Refund Rejected": ("status-rejected", "⊘", "Rejected"),
        "Under Investigation": ("status-investigation", "🔍", "Investigating"),
        "Abandoned": ("status-abandoned", "○", "Abandoned"),
        "Partially Completed": ("status-pending", "◐", "Partial")
    }
    
    css_class, icon, label = status_map.get(status, ("status-pending", "?", status))
    return f'<span class="status-badge {css_class}">{icon} {label}</span>'


def get_priority_badge(priority: str) -> str:
    """Get HTML for a priority badge"""
    priority_map = {
        "Critical": ("priority-critical", "🔴 CRITICAL"),
        "High": ("priority-high", "🟠 HIGH"),
        "Medium": ("priority-medium", "🟡 MEDIUM"),
        "Low": ("priority-low", "🟢 LOW")
    }
    
    css_class, label = priority_map.get(priority, ("priority-low", priority))
    return f'<span class="priority-badge {css_class}">{label}</span>'


def render_lifecycle_visual(lifecycle: Dict[str, Any]) -> str:
    """Render lifecycle stages visual"""
    stages = ["search", "selection", "booking", "payment", "ticketing", "confirmation"]
    
    html = '<div class="lifecycle-container">'
    
    for stage in stages:
        stage_data = lifecycle.get(stage, {})
        status = stage_data.get("status", "not_reached") if isinstance(stage_data, dict) else "not_reached"
        
        icons = {
            "completed": "✓",
            "failed": "✗",
            "pending": "⏳",
            "not_reached": "○"
        }
        
        css_classes = {
            "completed": "stage-completed",
            "failed": "stage-failed", 
            "pending": "stage-pending",
            "not_reached": "stage-not-reached"
        }
        
        icon = icons.get(status, "○")
        css_class = css_classes.get(status, "stage-not-reached")
        
        html += f'<span class="lifecycle-stage {css_class}">{icon} {stage.upper()}</span>'
    
    # Check for refund stage
    refund_data = lifecycle.get("refund", {})
    refund_status = refund_data.get("status", "not_applicable") if isinstance(refund_data, dict) else "not_applicable"
    
    if refund_status != "not_applicable":
        if refund_status == "completed":
            html += '<span class="lifecycle-stage stage-completed">✓ REFUND</span>'
        elif refund_status == "rejected":
            html += '<span class="lifecycle-stage stage-failed">✗ REFUND</span>'
        else:
            html += '<span class="lifecycle-stage stage-pending">⏳ REFUND</span>'
    
    html += '</div>'
    return html


def render_chat_message(role: str, content: str) -> str:
    """Render a chat message"""
    if role == "user":
        return f"""
        <div class="chat-message user">
            <div class="chat-message-header">
                👤 Customer Service Agent
            </div>
            <div class="chat-message-content">{content}</div>
        </div>
        """
    else:
        return f"""
        <div class="chat-message assistant">
            <div class="chat-message-header">
                🤖 NDC Genie
            </div>
            <div class="chat-message-content">{content}</div>
        </div>
        """


def render_alert(message: str, alert_type: str = "info") -> str:
    """Render an alert box"""
    icons = {
        "error": "❌",
        "warning": "⚠️",
        "success": "✅",
        "info": "ℹ️"
    }
    
    icon = icons.get(alert_type, "ℹ️")
    return f"""
    <div class="alert-box {alert_type}">
        <span>{icon}</span>
        <span>{message}</span>
    </div>
    """


def render_transaction_card(txn: Dict[str, Any], compact: bool = False) -> str:
    """Render a transaction card"""
    status = txn.get("status", "Unknown")
    priority = txn.get("priority", "Low")
    
    card_class = "transaction-card"
    if status == "Failed":
        card_class += " failed"
    elif status == "Completed":
        card_class += " completed"
    elif "Refund" in status:
        card_class += " refund"
    elif status in ["Under Investigation", "Abandoned"]:
        card_class += " pending"
    
    customer = txn.get("customer", {})
    flight = txn.get("flight", {})
    
    html = f"""
    <div class="{card_class}">
        <div class="transaction-header">
            <div>
                <span class="transaction-id">{txn.get('transaction_id', 'N/A')}</span>
                <div style="margin-top: 0.25rem; color: var(--text-secondary); font-size: 0.875rem;">
                    {customer.get('first_name', '')} {customer.get('last_name', '')} • {customer.get('email', '')}
                </div>
            </div>
            <div class="transaction-meta">
                {get_status_badge(status)}
                {get_priority_badge(priority)}
            </div>
        </div>
    """
    
    if not compact:
        html += f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.5rem;">
            <div>
                <strong>Flight:</strong> {flight.get('flight_number', 'N/A')} ({flight.get('airline_name', '')})<br>
                <strong>Route:</strong> {flight.get('origin_city', '')} → {flight.get('destination_city', '')}<br>
                <strong>Date:</strong> {flight.get('departure_date', 'N/A')} {flight.get('departure_time', '')}
            </div>
            <div>
                <strong>Amount:</strong> ${txn.get('pricing', {}).get('total', 0):,.2f}<br>
                <strong>Booking Ref:</strong> {txn.get('lifecycle', {}).get('booking', {}).get('metadata', {}).get('booking_ref', 'N/A')}<br>
                <strong>Created:</strong> {txn.get('created_at', 'N/A')[:10] if txn.get('created_at') else 'N/A'}
            </div>
        </div>
        """
    
    html += "</div>"
    return html


def render_info_card(title: str, items: List[tuple], icon: str = "") -> str:
    """Render an information card with key-value pairs"""
    icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ''
    
    items_html = ""
    for label, value in items:
        items_html += f"""
        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
            <span style="color: var(--text-secondary);">{label}</span>
            <span style="font-weight: 600; color: var(--text-primary);">{value}</span>
        </div>
        """
    
    return f"""
    <div style="background: white; border-radius: var(--border-radius); padding: 1.25rem; border: 1px solid var(--border-color); box-shadow: var(--shadow-sm);">
        <h4 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 600; color: var(--text-primary);">
            {icon_html}{title}
        </h4>
        {items_html}
    </div>
    """


def render_timeline(events: List[Dict[str, Any]]) -> str:
    """Render a vertical timeline of events"""
    if not events:
        return '<div style="color: var(--text-muted); padding: 1rem;">No events to display</div>'
    
    html = '<div class="timeline-container" style="position: relative; padding-left: 2rem;">'
    
    for i, event in enumerate(events):
        is_last = i == len(events) - 1
        status = event.get('status', 'pending')
        
        # Determine colors based on status
        if status == 'completed':
            color = 'var(--success)'
            icon = '✓'
        elif status == 'failed':
            color = 'var(--danger)'
            icon = '✗'
        else:
            color = 'var(--warning)'
            icon = '○'
        
        # Line to next event
        line_html = '' if is_last else f'''
        <div style="position: absolute; left: 0.75rem; top: 1.5rem; bottom: -1rem; width: 2px; background: var(--border-color);"></div>
        '''
        
        html += f'''
        <div style="position: relative; padding-bottom: 1.5rem;">
            <div style="position: absolute; left: -1.75rem; top: 0; width: 1.5rem; height: 1.5rem; border-radius: 50%; background: {color}; color: white; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700;">{icon}</div>
            {line_html}
            <div style="font-weight: 600; color: var(--text-primary);">{event.get('title', 'Event')}</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">{event.get('description', '')}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">{event.get('timestamp', '')}</div>
        </div>
        '''
    
    html += '</div>'
    return html


def render_progress_bar(value: float, max_value: float = 100, label: str = "", color: str = None) -> str:
    """Render a progress bar"""
    percentage = min(100, max(0, (value / max_value) * 100)) if max_value > 0 else 0
    
    if color is None:
        if percentage >= 80:
            color = 'var(--success)'
        elif percentage >= 50:
            color = 'var(--warning)'
        else:
            color = 'var(--danger)'
    
    return f'''
    <div style="margin: 0.5rem 0;">
        {f'<div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.25rem;">{label}</div>' if label else ''}
        <div style="background: var(--bg-tertiary); border-radius: 4px; height: 8px; overflow: hidden;">
            <div style="background: {color}; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem; text-align: right;">{percentage:.1f}%</div>
    </div>
    '''


def render_stat_comparison(current: float, previous: float, label: str, format_fn=None) -> str:
    """Render a statistic with comparison to previous value"""
    if format_fn is None:
        format_fn = lambda x: f"{x:,.0f}"
    
    change = current - previous
    change_pct = (change / previous * 100) if previous != 0 else 0
    
    if change >= 0:
        change_color = 'var(--success)'
        change_icon = '↑'
    else:
        change_color = 'var(--danger)'
        change_icon = '↓'
    
    return f'''
    <div style="background: white; border-radius: var(--border-radius); padding: 1rem; border: 1px solid var(--border-color);">
        <div style="font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary); margin: 0.25rem 0;">{format_fn(current)}</div>
        <div style="font-size: 0.85rem; color: {change_color};">
            {change_icon} {abs(change_pct):.1f}% ({format_fn(abs(change))})
        </div>
    </div>
    '''


def render_empty_state(message: str, icon: str = "📭", action_text: str = None) -> str:
    """Render an empty state message"""
    action_html = f'<div style="margin-top: 1rem;"><button style="background: var(--accent); color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">{action_text}</button></div>' if action_text else ''
    
    return f'''
    <div style="text-align: center; padding: 3rem 2rem; color: var(--text-muted);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <div style="font-size: 1.1rem; color: var(--text-secondary);">{message}</div>
        {action_html}
    </div>
    '''


def render_loading_skeleton(rows: int = 3) -> str:
    """Render a loading skeleton placeholder"""
    skeleton_rows = ""
    for _ in range(rows):
        skeleton_rows += '''
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
            <div style="width: 60px; height: 60px; background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); border-radius: 8px; animation: shimmer 1.5s infinite;"></div>
            <div style="flex: 1;">
                <div style="height: 16px; background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); border-radius: 4px; margin-bottom: 0.5rem; animation: shimmer 1.5s infinite;"></div>
                <div style="height: 12px; width: 60%; background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); border-radius: 4px; animation: shimmer 1.5s infinite;"></div>
            </div>
        </div>
        '''
    
    return f'''
    <style>
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
    </style>
    <div style="background: white; border-radius: var(--border-radius); padding: 1.5rem; border: 1px solid var(--border-color);">
        {skeleton_rows}
    </div>
    '''


def render_keyboard_shortcut(key: str, description: str) -> str:
    """Render a keyboard shortcut hint"""
    return f'''
    <div style="display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.85rem;">
        <kbd style="background: var(--bg-tertiary); padding: 0.25rem 0.5rem; border-radius: 4px; border: 1px solid var(--border-color); font-family: monospace; font-size: 0.75rem;">{key}</kbd>
        <span style="color: var(--text-secondary);">{description}</span>
    </div>
    '''


def render_tooltip(content: str, tooltip_text: str) -> str:
    """Render content with a tooltip"""
    return f'''
    <span style="position: relative; cursor: help;" title="{tooltip_text}">
        {content}
        <sup style="color: var(--accent); font-size: 0.7em;">ⓘ</sup>
    </span>
    '''


def get_icon(name: str) -> str:
    """Get an icon by name"""
    return ICONS.get(name, "•")
