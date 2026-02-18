"""
NDC Genie - Enterprise Airline Transaction Lifecycle Tracker
Main Application Entry Point

A production-ready Streamlit application powered by Claude AI for 
tracking airline transactions, investigating failures, and managing refunds.

Author: Enterprise Solutions Team
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys
import os
import hashlib
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import app_config, ui_config
from utils.ai_assistant import ClaudeAssistant, validate_api_key
from utils.validators import (
    TransactionValidator, 
    DataSanitizer, 
    validate_api_key_format,
    format_currency,
    format_duration,
    format_datetime
)
from data.demo_data import get_demo_data
from components.ui_components import (
    inject_custom_css,
    render_header,
    render_metric_card,
    get_status_badge,
    get_priority_badge,
    render_lifecycle_visual,
    render_chat_message,
    render_alert,
    render_info_card,
    render_timeline,
    render_progress_bar,
    render_empty_state,
    ICONS
)

# RBAC Authentication System
from utils.rbac import get_auth_manager, Permission, Role
from components.rbac_ui import (
    require_authentication,
    render_user_management,
    check_page_access
)

# Operations Dashboard (Flight Status, EU261, Fraud, Corporate)
from components.operations_ui import render_operations_tab


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=f"{app_config.APP_NAME} - {app_config.APP_DESCRIPTION}",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': f"""
        ## {app_config.APP_NAME} v{app_config.APP_VERSION}
        
        Enterprise Airline Transaction Lifecycle Tracker powered by Claude AI.
        
        **Features:**
        - AI-powered transaction analysis
        - Real-time failure tracking
        - Refund management
        - SLA monitoring
        - Pattern analysis
        """
    }
)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def init_session_state():
    """Initialize all session state variables"""
    
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.messages = []
        st.session_state.transactions = get_demo_data(count=app_config.DEMO_TRANSACTION_COUNT)
        st.session_state.api_key_valid = False
        st.session_state.selected_transaction = None
        st.session_state.filters = {
            "status": [],
            "priority": [],
            "date_range": "all",
            "search_query": "",
            "airline": [],
            "loyalty_tier": []
        }
        st.session_state.current_tab = "chat"
        st.session_state.view_mode = "cards"  # cards or table
        st.session_state.sort_by = "created_at"
        st.session_state.sort_order = "desc"
        st.session_state.page = 0
        st.session_state.per_page = 20
        st.session_state.error_log = []
        st.session_state.last_refresh = datetime.now().isoformat()
        st.session_state.theme = "light"
        
        # Initialize analytics cache
        st.session_state.analytics_cache = None
        st.session_state.analytics_cache_time = None


def log_error(error_type: str, message: str, details: Dict = None):
    """Log an error for debugging"""
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": error_type,
        "message": message,
        "details": details or {}
    }
    
    if "error_log" not in st.session_state:
        st.session_state.error_log = []
    
    st.session_state.error_log.append(error_entry)
    
    # Keep only last 100 errors
    if len(st.session_state.error_log) > 100:
        st.session_state.error_log = st.session_state.error_log[-100:]


def get_cached_analytics():
    """Get cached analytics or recalculate if stale"""
    cache_duration = 60  # seconds
    
    if st.session_state.analytics_cache_time:
        cache_age = (datetime.now() - datetime.fromisoformat(st.session_state.analytics_cache_time)).seconds
        if cache_age < cache_duration and st.session_state.analytics_cache:
            return st.session_state.analytics_cache
    
    # Recalculate
    stats = calculate_statistics(st.session_state.transactions)
    st.session_state.analytics_cache = stats
    st.session_state.analytics_cache_time = datetime.now().isoformat()
    
    return stats


init_session_state()


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def filter_transactions(
    transactions: List[Dict],
    status_filter: List[str] = None,
    priority_filter: List[str] = None,
    search_query: str = "",
    date_range: str = "all",
    airline_filter: List[str] = None,
    loyalty_filter: List[str] = None,
    sla_breach_only: bool = False,
    has_error_only: bool = False,
    has_refund_only: bool = False
) -> List[Dict]:
    """Apply filters to transactions with comprehensive options"""
    
    filtered = transactions.copy()
    
    # Status filter
    if status_filter:
        filtered = [t for t in filtered if t.get('status') in status_filter]
    
    # Priority filter
    if priority_filter:
        filtered = [t for t in filtered if t.get('priority') in priority_filter]
    
    # Airline filter
    if airline_filter:
        filtered = [
            t for t in filtered 
            if t.get('flight', {}).get('airline_name') in airline_filter
        ]
    
    # Loyalty tier filter
    if loyalty_filter:
        filtered = [
            t for t in filtered
            if t.get('customer', {}).get('loyalty_tier') in loyalty_filter
        ]
    
    # SLA breach filter
    if sla_breach_only:
        filtered = [t for t in filtered if t.get('sla_breach')]
    
    # Has error filter
    if has_error_only:
        filtered = [t for t in filtered if t.get('error_info')]
    
    # Has refund filter
    if has_refund_only:
        filtered = [t for t in filtered if t.get('refund_info')]
    
    # Search query - comprehensive search across multiple fields
    if search_query:
        query = search_query.lower().strip()
        
        def matches_query(t: Dict) -> bool:
            # Transaction ID
            if query in t.get('transaction_id', '').lower():
                return True
            
            # Customer fields
            customer = t.get('customer', {})
            if query in customer.get('first_name', '').lower():
                return True
            if query in customer.get('last_name', '').lower():
                return True
            if query in customer.get('email', '').lower():
                return True
            if query in f"{customer.get('first_name', '')} {customer.get('last_name', '')}".lower():
                return True
            if query in customer.get('customer_id', '').lower():
                return True
            
            # Flight fields
            flight = t.get('flight', {})
            if query in flight.get('flight_number', '').lower():
                return True
            if query in flight.get('origin', '').lower():
                return True
            if query in flight.get('destination', '').lower():
                return True
            if query in flight.get('origin_city', '').lower():
                return True
            if query in flight.get('destination_city', '').lower():
                return True
            
            # Booking reference and PNR
            lifecycle = t.get('lifecycle', {})
            booking = lifecycle.get('booking', {})
            if isinstance(booking, dict):
                booking_ref = booking.get('metadata', {}).get('booking_ref', '')
                if query in str(booking_ref).lower():
                    return True
            
            ticketing = lifecycle.get('ticketing', {})
            if isinstance(ticketing, dict):
                pnr = ticketing.get('metadata', {}).get('pnr', '')
                if query in str(pnr).lower():
                    return True
                e_ticket = ticketing.get('metadata', {}).get('e_ticket_number', '')
                if query in str(e_ticket).lower():
                    return True
            
            return False
        
        filtered = [t for t in filtered if matches_query(t)]
    
    # Date range filter
    if date_range != "all":
        now = datetime.now()
        start_date = None
        
        if date_range == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "yesterday":
            start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "week":
            start_date = now - timedelta(days=7)
        elif date_range == "month":
            start_date = now - timedelta(days=30)
        elif date_range == "quarter":
            start_date = now - timedelta(days=90)
        
        if start_date:
            filtered = [
                t for t in filtered
                if datetime.fromisoformat(t.get('created_at', '2000-01-01').replace('Z', '')) >= start_date
            ]
    
    return filtered


def sort_transactions(
    transactions: List[Dict],
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[Dict]:
    """Sort transactions by specified field"""
    
    reverse = sort_order == "desc"
    
    if sort_by == "created_at":
        return sorted(transactions, key=lambda x: x.get('created_at', ''), reverse=reverse)
    elif sort_by == "status":
        return sorted(transactions, key=lambda x: x.get('status', ''), reverse=reverse)
    elif sort_by == "priority":
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        return sorted(transactions, key=lambda x: priority_order.get(x.get('priority', 'Low'), 3), reverse=reverse)
    elif sort_by == "customer":
        return sorted(transactions, key=lambda x: x.get('customer', {}).get('last_name', ''), reverse=reverse)
    elif sort_by == "amount":
        return sorted(transactions, key=lambda x: x.get('pricing', {}).get('total', 0), reverse=reverse)
    elif sort_by == "airline":
        return sorted(transactions, key=lambda x: x.get('flight', {}).get('airline_name', ''), reverse=reverse)
    
    return transactions


def paginate_transactions(
    transactions: List[Dict],
    page: int = 0,
    per_page: int = 20
) -> tuple:
    """Paginate transactions and return page info"""
    total = len(transactions)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    
    start = page * per_page
    end = min(start + per_page, total)
    
    return (
        transactions[start:end],
        {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "start": start + 1,
            "end": end
        }
    )


def calculate_statistics(transactions: List[Dict]) -> Dict[str, Any]:
    """Calculate comprehensive statistics from transactions"""
    
    total = len(transactions)
    if total == 0:
        return {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "success_rate": 0,
            "status_breakdown": {},
            "priority_breakdown": {},
            "failure_breakdown": {},
            "airline_breakdown": {},
            "loyalty_breakdown": {},
            "refund_stats": {"total": 0, "pending": 0, "completed": 0, "value": 0, "pending_value": 0},
            "sla_breaches": 0,
            "avg_transaction_value": 0,
            "total_revenue": 0,
            "top_routes": [],
            "hourly_distribution": {},
            "daily_trend": []
        }
    
    # Status breakdown
    status_breakdown = {}
    for t in transactions:
        status = t.get('status', 'Unknown')
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    # Priority breakdown
    priority_breakdown = {}
    for t in transactions:
        priority = t.get('priority', 'Low')
        priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
    
    # Failure breakdown by stage
    failure_breakdown = {}
    failure_reasons = {}
    for t in transactions:
        if t.get('error_info'):
            stage = t['error_info'].get('error_stage', 'Unknown')
            failure_breakdown[stage] = failure_breakdown.get(stage, 0) + 1
            
            reason = t['error_info'].get('error_message', 'Unknown')
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
    
    # Airline breakdown
    airline_breakdown = {}
    for t in transactions:
        airline = t.get('flight', {}).get('airline_name', 'Unknown')
        airline_breakdown[airline] = airline_breakdown.get(airline, 0) + 1
    
    # Loyalty tier breakdown
    loyalty_breakdown = {}
    for t in transactions:
        tier = t.get('customer', {}).get('loyalty_tier', 'None')
        loyalty_breakdown[tier] = loyalty_breakdown.get(tier, 0) + 1
    
    # Refund statistics
    refund_completed = sum(
        1 for t in transactions 
        if t.get('refund_info') and t['refund_info'].get('status') == 'Completed'
    )
    refund_pending = sum(
        1 for t in transactions
        if t.get('refund_info') and t['refund_info'].get('status') == 'Pending'
    )
    refund_value = sum(
        t['refund_info']['refund_amount']
        for t in transactions
        if t.get('refund_info') and t['refund_info'].get('status') == 'Completed' and t['refund_info'].get('refund_amount')
    )
    pending_refund_value = sum(
        t['refund_info']['refund_amount']
        for t in transactions
        if t.get('refund_info') and t['refund_info'].get('status') == 'Pending' and t['refund_info'].get('refund_amount')
    )
    
    # SLA breaches
    sla_breaches = sum(1 for t in transactions if t.get('sla_breach'))
    
    # Financial metrics
    total_revenue = sum(t.get('pricing', {}).get('total', 0) for t in transactions if t.get('status') == 'Completed')
    avg_transaction_value = total_revenue / status_breakdown.get('Completed', 1) if status_breakdown.get('Completed', 0) > 0 else 0
    
    # Top routes
    route_counts = {}
    for t in transactions:
        flight = t.get('flight', {})
        route = f"{flight.get('origin', '?')} → {flight.get('destination', '?')}"
        route_counts[route] = route_counts.get(route, 0) + 1
    top_routes = sorted(route_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Hourly distribution
    hourly_dist = {str(h): 0 for h in range(24)}
    for t in transactions:
        try:
            created = datetime.fromisoformat(t.get('created_at', '').replace('Z', ''))
            hour = str(created.hour)
            hourly_dist[hour] = hourly_dist.get(hour, 0) + 1
        except:
            pass
    
    # Daily trend (last 7 days)
    daily_trend = []
    today = datetime.now().date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        count = sum(
            1 for t in transactions
            if t.get('created_at', '').startswith(day_str)
        )
        daily_trend.append({"date": day_str, "count": count})
    
    completed = status_breakdown.get('Completed', 0)
    
    return {
        "total": total,
        "completed": completed,
        "failed": status_breakdown.get('Failed', 0),
        "success_rate": round(completed / total * 100, 1) if total > 0 else 0,
        "status_breakdown": status_breakdown,
        "priority_breakdown": priority_breakdown,
        "failure_breakdown": failure_breakdown,
        "failure_reasons": dict(sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:10]),
        "airline_breakdown": airline_breakdown,
        "loyalty_breakdown": loyalty_breakdown,
        "sla_breaches": sla_breaches,
        "refund_stats": {
            "total": refund_completed + refund_pending,
            "completed": refund_completed,
            "pending": refund_pending,
            "value": round(refund_value, 2),
            "pending_value": round(pending_refund_value, 2)
        },
        "avg_transaction_value": round(avg_transaction_value, 2),
        "total_revenue": round(total_revenue, 2),
        "top_routes": top_routes,
        "hourly_distribution": hourly_dist,
        "daily_trend": daily_trend
    }


def export_transactions(transactions: List[Dict], format: str = "csv") -> bytes:
    """Export transactions to CSV or JSON"""
    
    if format == "json":
        return json.dumps(transactions, indent=2, default=str).encode('utf-8')
    
    # Flatten for CSV
    rows = []
    for t in transactions:
        row = {
            "Transaction ID": t.get('transaction_id'),
            "Status": t.get('status'),
            "Priority": t.get('priority'),
            "Customer Name": f"{t.get('customer', {}).get('first_name', '')} {t.get('customer', {}).get('last_name', '')}",
            "Customer Email": t.get('customer', {}).get('email'),
            "Customer Phone": t.get('customer', {}).get('phone'),
            "Loyalty Tier": t.get('customer', {}).get('loyalty_tier'),
            "Flight Number": t.get('flight', {}).get('flight_number'),
            "Airline": t.get('flight', {}).get('airline_name'),
            "Origin": f"{t.get('flight', {}).get('origin_city')} ({t.get('flight', {}).get('origin')})",
            "Destination": f"{t.get('flight', {}).get('destination_city')} ({t.get('flight', {}).get('destination')})",
            "Departure Date": t.get('flight', {}).get('departure_date'),
            "Departure Time": t.get('flight', {}).get('departure_time'),
            "Cabin Class": t.get('flight', {}).get('cabin_class'),
            "Passengers": t.get('flight', {}).get('passengers'),
            "Total Amount": t.get('pricing', {}).get('total'),
            "Currency": t.get('pricing', {}).get('currency'),
            "Booking Ref": t.get('lifecycle', {}).get('booking', {}).get('metadata', {}).get('booking_ref'),
            "PNR": t.get('lifecycle', {}).get('ticketing', {}).get('metadata', {}).get('pnr'),
            "E-Ticket": t.get('lifecycle', {}).get('ticketing', {}).get('metadata', {}).get('e_ticket_number'),
            "Error Stage": t.get('error_info', {}).get('error_stage') if t.get('error_info') else None,
            "Error Message": t.get('error_info', {}).get('error_message') if t.get('error_info') else None,
            "Refund Status": t.get('refund_info', {}).get('status') if t.get('refund_info') else None,
            "Refund Amount": t.get('refund_info', {}).get('refund_amount') if t.get('refund_info') else None,
            "Created At": t.get('created_at'),
            "SLA Breach": t.get('sla_breach')
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode('utf-8')


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    """Render the sidebar with configuration and quick stats"""
    
    with st.sidebar:
        # Logo/Brand
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2.5rem;">✈️</div>
            <div style="font-weight: 700; font-size: 1.25rem; color: #1a365d;">NDC Genie</div>
            <div style="font-size: 0.75rem; color: #718096;">Enterprise Edition v2.0</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # API Configuration - Read from Streamlit Secrets
        st.markdown("### 🔑 API Status")
        
        # Check for API key in Streamlit secrets first
        api_key_from_secrets = None
        try:
            api_key_from_secrets = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            pass
        
        if api_key_from_secrets:
            # API key found in secrets
            is_valid, msg = validate_api_key_format(api_key_from_secrets)
            if is_valid:
                st.session_state.api_key = api_key_from_secrets
                st.session_state.api_key_valid = True
                st.markdown("""
                <div style="background: linear-gradient(135deg, #c6f6d5, #9ae6b4); padding: 0.75rem; border-radius: 8px; border-left: 4px solid #38a169;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.25rem;">✅</span>
                        <div>
                            <div style="font-weight: 600; color: #22543d;">API Connected</div>
                            <div style="font-size: 0.75rem; color: #276749;">Loaded from Streamlit Secrets</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.session_state.api_key_valid = False
                st.error(f"✗ Invalid API key in secrets: {msg}")
        else:
            # No API key in secrets - show manual input option
            st.markdown("""
            <div style="background: linear-gradient(135deg, #feebc8, #fbd38d); padding: 0.75rem; border-radius: 8px; border-left: 4px solid #d69e2e;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.25rem;">⚠️</span>
                    <div>
                        <div style="font-weight: 600; color: #744210;">API Key Not Found</div>
                        <div style="font-size: 0.75rem; color: #975a16;">Add ANTHROPIC_API_KEY to Streamlit Secrets</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Fallback: Manual input for local development
            with st.expander("🔧 Manual Entry (Development Only)"):
                api_key = st.text_input(
                    "API Key",
                    type="password",
                    help="For local development only. In production, use Streamlit Secrets.",
                    placeholder="sk-ant-...",
                    label_visibility="collapsed"
                )
                
                if api_key:
                    is_valid, msg = validate_api_key_format(api_key)
                    if is_valid:
                        st.session_state.api_key = api_key
                        st.session_state.api_key_valid = True
                        st.success("✓ API key configured")
                    else:
                        st.error(f"✗ {msg}")
                        st.session_state.api_key_valid = False
        
        st.markdown("---")
        
        # Quick Statistics
        st.markdown("### 📊 Quick Statistics")
        stats = get_cached_analytics()
        
        # Row 1
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", f"{stats['total']:,}")
            st.metric("Failed", stats['failed'], delta_color="inverse")
        with col2:
            st.metric("Success", f"{stats['success_rate']}%")
            st.metric("SLA Breach", stats['sla_breaches'], delta_color="inverse")
        
        # Financial summary
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ebf8ff, #bee3f8); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
            <div style="font-size: 0.75rem; color: #2c5282; text-transform: uppercase;">Total Revenue</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #1a365d;">{format_currency(stats['total_revenue'])}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Priority Queue
        st.markdown("### 🚨 Priority Queue")
        priority = stats['priority_breakdown']
        
        if priority.get('Critical', 0) > 0:
            st.markdown(f"""
            <div style="background: #fed7d7; padding: 0.5rem 0.75rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #9b2c2c; font-weight: 600;">🔴 Critical</span>
                <span style="background: #9b2c2c; color: white; padding: 0.125rem 0.5rem; border-radius: 10px; font-size: 0.75rem; font-weight: 700;">{priority.get('Critical', 0)}</span>
            </div>
            """, unsafe_allow_html=True)
        
        if priority.get('High', 0) > 0:
            st.markdown(f"""
            <div style="background: #feebc8; padding: 0.5rem 0.75rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #c05621; font-weight: 600;">🟠 High</span>
                <span style="background: #c05621; color: white; padding: 0.125rem 0.5rem; border-radius: 10px; font-size: 0.75rem; font-weight: 700;">{priority.get('High', 0)}</span>
            </div>
            """, unsafe_allow_html=True)
        
        if priority.get('Medium', 0) > 0:
            st.markdown(f"""
            <div style="background: #faf089; padding: 0.5rem 0.75rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #975a16; font-weight: 600;">🟡 Medium</span>
                <span style="background: #975a16; color: white; padding: 0.125rem 0.5rem; border-radius: 10px; font-size: 0.75rem; font-weight: 700;">{priority.get('Medium', 0)}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Filters Section
        st.markdown("### 🔍 Filters")
        
        # Status filter
        status_filter = st.multiselect(
            "Status",
            options=app_config.TRANSACTION_STATUSES,
            default=st.session_state.filters.get('status', []),
            key="status_filter",
            help="Filter by transaction status"
        )
        st.session_state.filters['status'] = status_filter
        
        # Priority filter
        priority_filter = st.multiselect(
            "Priority",
            options=["Critical", "High", "Medium", "Low"],
            default=st.session_state.filters.get('priority', []),
            key="priority_filter",
            help="Filter by priority level"
        )
        st.session_state.filters['priority'] = priority_filter
        
        # Date range
        date_range = st.selectbox(
            "Date Range",
            options=["all", "today", "yesterday", "week", "month", "quarter"],
            format_func=lambda x: {
                "all": "All Time", 
                "today": "Today", 
                "yesterday": "Yesterday",
                "week": "Last 7 Days", 
                "month": "Last 30 Days",
                "quarter": "Last 90 Days"
            }[x],
            key="date_range",
            help="Filter by creation date"
        )
        st.session_state.filters['date_range'] = date_range
        
        # Advanced filters in expander
        with st.expander("🔧 Advanced Filters"):
            # Get unique airlines
            airlines = list(set(
                t.get('flight', {}).get('airline_name', '') 
                for t in st.session_state.transactions 
                if t.get('flight', {}).get('airline_name')
            ))
            airline_filter = st.multiselect(
                "Airline",
                options=sorted(airlines),
                key="airline_filter"
            )
            st.session_state.filters['airline'] = airline_filter
            
            # Loyalty tiers
            loyalty_filter = st.multiselect(
                "Loyalty Tier",
                options=["None", "Bronze", "Silver", "Gold", "Platinum", "Diamond"],
                key="loyalty_filter"
            )
            st.session_state.filters['loyalty_tier'] = loyalty_filter
            
            # Boolean filters
            st.checkbox("SLA Breaches Only", key="sla_breach_filter")
            st.checkbox("Errors Only", key="error_filter")
            st.checkbox("Refunds Only", key="refund_filter")
        
        # Clear filters button
        if st.button("🔄 Clear All Filters", use_container_width=True):
            st.session_state.filters = {
                "status": [], "priority": [], "date_range": "all",
                "search_query": "", "airline": [], "loyalty_tier": []
            }
            st.rerun()
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 CSV", use_container_width=True, help="Export to CSV"):
                csv_data = export_transactions(st.session_state.transactions, "csv")
                st.download_button(
                    "⬇️ Download",
                    data=csv_data,
                    file_name=f"ndc-genie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📥 JSON", use_container_width=True, help="Export to JSON"):
                json_data = export_transactions(st.session_state.transactions, "json")
                st.download_button(
                    "⬇️ Download",
                    data=json_data,
                    file_name=f"ndc-genie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        if st.button("🔄 Refresh Data", use_container_width=True, help="Regenerate demo data"):
            with st.spinner("Refreshing..."):
                st.session_state.transactions = get_demo_data(count=app_config.DEMO_TRANSACTION_COUNT)
                st.session_state.analytics_cache = None
                st.session_state.last_refresh = datetime.now().isoformat()
            st.success("✓ Data refreshed!")
            time.sleep(0.5)
            st.rerun()
        
        st.markdown("---")
        
        # Sample Queries
        st.markdown("### 💡 AI Query Templates")
        
        sample_queries = [
            ("🚨 Critical Cases", "Show all critical and high priority transactions requiring immediate attention, including SLA breaches"),
            ("💳 Payment Issues", "Analyze all payment failures. Show breakdown by failure reason and identify any patterns"),
            ("💰 Refund Status", "List all pending refunds with amounts, expected dates, and any that might be overdue"),
            ("📊 Daily Report", "Generate a comprehensive daily summary including total transactions, success rate, failures, and key issues"),
            ("🔍 Pattern Analysis", "Identify patterns in transaction failures. Are there specific airlines, routes, or time periods with higher failure rates?")
        ]
        
        for label, query in sample_queries:
            if st.button(label, key=f"sample_{label}", use_container_width=True, help=query[:50] + "..."):
                st.session_state.pending_query = query
                st.session_state.current_tab = "chat"
                st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; font-size: 0.7rem; color: #a0aec0;">
            Last refreshed: {format_datetime(st.session_state.get('last_refresh', ''), 'relative')}<br>
            Transactions: {len(st.session_state.transactions):,}
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT TABS
# ═══════════════════════════════════════════════════════════════════════════════

def render_chat_tab():
    """Render the AI Chat interface"""
    
    st.markdown("### 💬 AI-Powered Transaction Assistant")
    st.markdown("Ask questions about transactions, investigate failures, track refunds, or analyze patterns.")
    
    # Check for pending query
    if "pending_query" in st.session_state:
        query = st.session_state.pending_query
        del st.session_state.pending_query
        st.session_state.messages.append({"role": "user", "content": query})
        
        if st.session_state.api_key_valid:
            assistant = ClaudeAssistant(st.session_state.api_key)
            with st.spinner("🔍 Analyzing transactions..."):
                response = assistant.get_response(
                    st.session_state.messages,
                    st.session_state.transactions
                )
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            # Welcome message
            st.markdown("""
            <div class="chat-message assistant">
                <div class="chat-message-header">🤖 NDC Genie</div>
                <div class="chat-message-content">
                    <p>👋 Welcome! I'm your AI-powered transaction assistant. I can help you with:</p>
                    <ul>
                        <li><strong>Transaction Lookup</strong> - Find by ID, customer name, email, PNR, or booking reference</li>
                        <li><strong>Failure Investigation</strong> - Understand what went wrong and suggested resolutions</li>
                        <li><strong>Refund Tracking</strong> - Check status, amounts, and expected dates</li>
                        <li><strong>Pattern Analysis</strong> - Identify trends and systemic issues</li>
                        <li><strong>Priority Management</strong> - View critical cases and SLA breaches</li>
                    </ul>
                    <p>💡 <strong>New!</strong> Check out the <strong>Operations</strong> tab for:</p>
                    <ul>
                        <li>🛫 <strong>Flight Status</strong> - Real-time flight tracking and disruption management</li>
                        <li>🎫 <strong>PNR Lookup</strong> - Generate and view booking details with E-tickets</li>
                        <li>💶 <strong>EU261 Calculator</strong> - Calculate passenger compensation eligibility</li>
                        <li>🛡️ <strong>Fraud Detection</strong> - Risk assessment and fraud scoring</li>
                        <li>🏢 <strong>Corporate Travel</strong> - Policy compliance and travel analytics</li>
                    </ul>
                    <p>Try asking: <em>"Show all failed payment transactions from this week"</em></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display messages
        for msg in st.session_state.messages:
            st.markdown(render_chat_message(msg["role"], msg["content"]), unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.chat_input(
            "Ask about transactions, failures, refunds, or patterns...",
            key="chat_input"
        )
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear chat history"):
            st.session_state.messages = []
            st.rerun()
    
    if user_input:
        if not st.session_state.api_key_valid:
            st.error("⚠️ Please enter a valid Anthropic API key in the sidebar to use the AI assistant.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            assistant = ClaudeAssistant(st.session_state.api_key)
            with st.spinner("🔍 Analyzing transactions..."):
                response = assistant.get_response(
                    st.session_state.messages,
                    st.session_state.transactions
                )
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()


def render_transactions_tab():
    """Render the Transaction Browser with enhanced features"""
    
    st.markdown("### 📋 Transaction Browser")
    
    # Search and controls row
    col1, col2, col3, col4 = st.columns([4, 1.5, 1.5, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Search by ID, Name, Email, PNR, Booking Ref, Flight Number...",
            key="transaction_search",
            label_visibility="collapsed"
        )
        st.session_state.filters['search_query'] = search_query
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            options=["created_at", "status", "priority", "customer", "amount", "airline"],
            format_func=lambda x: {
                "created_at": "📅 Date", 
                "status": "🔖 Status", 
                "priority": "🚨 Priority", 
                "customer": "👤 Customer",
                "amount": "💰 Amount",
                "airline": "✈️ Airline"
            }[x],
            label_visibility="collapsed",
            key="sort_by_select"
        )
        st.session_state.sort_by = sort_by
    
    with col3:
        sort_order = st.selectbox(
            "Order",
            options=["desc", "asc"],
            format_func=lambda x: "↓ Newest" if x == "desc" else "↑ Oldest",
            label_visibility="collapsed",
            key="sort_order_select"
        )
        st.session_state.sort_order = sort_order
    
    with col4:
        view_mode = st.selectbox(
            "View",
            options=["cards", "table"],
            format_func=lambda x: "🃏" if x == "cards" else "📊",
            label_visibility="collapsed",
            key="view_mode_select"
        )
        st.session_state.view_mode = view_mode
    
    # Apply all filters
    filtered_transactions = filter_transactions(
        st.session_state.transactions,
        status_filter=st.session_state.filters.get('status'),
        priority_filter=st.session_state.filters.get('priority'),
        search_query=st.session_state.filters.get('search_query', ''),
        date_range=st.session_state.filters.get('date_range', 'all'),
        airline_filter=st.session_state.filters.get('airline'),
        loyalty_filter=st.session_state.filters.get('loyalty_tier'),
        sla_breach_only=st.session_state.get('sla_breach_filter', False),
        has_error_only=st.session_state.get('error_filter', False),
        has_refund_only=st.session_state.get('refund_filter', False)
    )
    
    # Sort
    sorted_transactions = sort_transactions(filtered_transactions, sort_by, sort_order)
    
    # Paginate
    paginated_transactions, page_info = paginate_transactions(
        sorted_transactions,
        page=st.session_state.get('page', 0),
        per_page=st.session_state.get('per_page', 20)
    )
    
    # Results summary
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem;">
        <div style="color: #4a5568;">
            Showing <strong>{page_info['start']}-{page_info['end']}</strong> of <strong>{page_info['total']:,}</strong> transactions
        </div>
        <div style="display: flex; gap: 0.5rem; align-items: center;">
            <span style="font-size: 0.8rem; color: #718096;">Per page:</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Per page selector
    per_page_col, pagination_col = st.columns([1, 3])
    with per_page_col:
        per_page = st.selectbox(
            "Per page",
            options=[10, 20, 50, 100],
            index=[10, 20, 50, 100].index(st.session_state.get('per_page', 20)),
            label_visibility="collapsed",
            key="per_page_select"
        )
        if per_page != st.session_state.get('per_page', 20):
            st.session_state.per_page = per_page
            st.session_state.page = 0
            st.rerun()
    
    # No results
    if not paginated_transactions:
        st.markdown(render_empty_state(
            "No transactions found matching your filters",
            "🔍",
            "Clear Filters"
        ), unsafe_allow_html=True)
        return
    
    # Render based on view mode
    if view_mode == "table":
        render_transactions_table(paginated_transactions)
    else:
        render_transactions_cards(paginated_transactions)
    
    # Pagination controls
    st.markdown("<br>", unsafe_allow_html=True)
    
    if page_info['total_pages'] > 1:
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ First", disabled=page_info['page'] == 0, use_container_width=True):
                st.session_state.page = 0
                st.rerun()
        
        with col2:
            if st.button("◀️ Prev", disabled=page_info['page'] == 0, use_container_width=True):
                st.session_state.page = max(0, page_info['page'] - 1)
                st.rerun()
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; color: #4a5568;">
                Page <strong>{page_info['page'] + 1}</strong> of <strong>{page_info['total_pages']}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if st.button("Next ▶️", disabled=page_info['page'] >= page_info['total_pages'] - 1, use_container_width=True):
                st.session_state.page = min(page_info['total_pages'] - 1, page_info['page'] + 1)
                st.rerun()
        
        with col5:
            if st.button("Last ⏭️", disabled=page_info['page'] >= page_info['total_pages'] - 1, use_container_width=True):
                st.session_state.page = page_info['total_pages'] - 1
                st.rerun()


def render_transactions_table(transactions: List[Dict]):
    """Render transactions in table format"""
    
    # Prepare data for table
    table_data = []
    for txn in transactions:
        customer = txn.get('customer', {})
        flight = txn.get('flight', {})
        pricing = txn.get('pricing', {})
        
        table_data.append({
            "ID": txn.get('transaction_id', 'N/A')[-12:],  # Last 12 chars for readability
            "Customer": f"{customer.get('first_name', '')} {customer.get('last_name', '')}",
            "Status": txn.get('status', 'Unknown'),
            "Priority": txn.get('priority', 'Low'),
            "Flight": flight.get('flight_number', 'N/A'),
            "Route": f"{flight.get('origin', '')} → {flight.get('destination', '')}",
            "Amount": f"${pricing.get('total', 0):,.2f}",
            "Date": txn.get('created_at', '')[:10] if txn.get('created_at') else 'N/A'
        })
    
    df = pd.DataFrame(table_data)
    
    # Display with streamlit
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn(width="medium"),
            "Priority": st.column_config.TextColumn(width="small"),
            "Amount": st.column_config.TextColumn(width="small"),
        }
    )


def render_transactions_cards(transactions: List[Dict]):
    """Render transactions as expandable cards"""
    
    for txn in transactions:
        status = txn.get('status', 'Unknown')
        priority = txn.get('priority', 'Low')
        customer = txn.get('customer', {})
        flight = txn.get('flight', {})
        
        # Status indicator
        status_emoji = {
            "Completed": "✅",
            "Failed": "❌",
            "Refunded": "💰",
            "Refund Pending": "⏳",
            "Refund Rejected": "🚫",
            "Under Investigation": "🔍",
            "Abandoned": "🚶"
        }.get(status, "•")
        
        # Priority indicator
        priority_emoji = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢"
        }.get(priority, "")
        
        expander_label = f"{status_emoji} {txn.get('transaction_id', 'N/A')} | {customer.get('first_name', '')} {customer.get('last_name', '')} | {flight.get('flight_number', '')} | ${txn.get('pricing', {}).get('total', 0):,.2f} {priority_emoji}"
        
        with st.expander(expander_label, expanded=False):
            render_transaction_detail(txn)


def render_transaction_detail(txn: Dict[str, Any]):
    """Render detailed transaction view"""
    
    customer = txn.get('customer', {})
    flight = txn.get('flight', {})
    pricing = txn.get('pricing', {})
    lifecycle = txn.get('lifecycle', {})
    error_info = txn.get('error_info')
    refund_info = txn.get('refund_info')
    
    # Header with status and priority
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Transaction ID:** `{txn.get('transaction_id')}`")
        st.markdown(f"**Created:** {txn.get('created_at', 'N/A')[:19] if txn.get('created_at') else 'N/A'}")
    
    with col2:
        st.markdown(get_status_badge(txn.get('status', 'Unknown')), unsafe_allow_html=True)
    
    with col3:
        st.markdown(get_priority_badge(txn.get('priority', 'Low')), unsafe_allow_html=True)
    
    if txn.get('sla_breach'):
        st.markdown(render_alert("⚠️ SLA BREACH - This transaction requires immediate attention!", "warning"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main content in tabs
    detail_tabs = st.tabs(["👤 Customer", "✈️ Flight", "💳 Payment", "📊 Lifecycle", "🔧 Error Details", "💰 Refund", "📝 Notes"])
    
    with detail_tabs[0]:  # Customer
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Personal Information**")
            st.write(f"- **Name:** {customer.get('first_name', '')} {customer.get('last_name', '')}")
            st.write(f"- **Email:** {customer.get('email', 'N/A')}")
            st.write(f"- **Phone:** {customer.get('phone', 'N/A')}")
            st.write(f"- **Nationality:** {customer.get('nationality', 'N/A')}")
        
        with col2:
            st.markdown("**Loyalty Information**")
            st.write(f"- **Tier:** {customer.get('loyalty_tier', 'None')}")
            st.write(f"- **Points:** {customer.get('loyalty_points', 0):,}")
            st.write(f"- **Member Since:** {customer.get('member_since', 'N/A')}")
            st.write(f"- **Lifetime Value:** ${customer.get('lifetime_value', 0):,.2f}")
    
    with detail_tabs[1]:  # Flight
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Flight Details**")
            st.write(f"- **Flight:** {flight.get('flight_number', 'N/A')}")
            st.write(f"- **Airline:** {flight.get('airline_name', 'N/A')}")
            st.write(f"- **Aircraft:** {flight.get('aircraft_type', 'N/A')}")
            st.write(f"- **Class:** {flight.get('cabin_class', 'N/A')} ({flight.get('fare_class', '')})")
        
        with col2:
            st.markdown("**Route & Schedule**")
            st.write(f"- **From:** {flight.get('origin_city', '')} ({flight.get('origin', '')})")
            st.write(f"- **To:** {flight.get('destination_city', '')} ({flight.get('destination', '')})")
            st.write(f"- **Date:** {flight.get('departure_date', 'N/A')}")
            st.write(f"- **Time:** {flight.get('departure_time', '')} - {flight.get('arrival_time', '')}")
            st.write(f"- **Duration:** {flight.get('duration_minutes', 0)} minutes")
        
        st.markdown("**Passenger Details**")
        st.write(f"- **Passengers:** {flight.get('passengers', 0)}")
        st.write(f"- **Seats:** {', '.join(flight.get('seat_numbers', []))}")
        st.write(f"- **Meal:** {flight.get('meal_preference', 'N/A')}")
        if flight.get('special_requests'):
            st.write(f"- **Special Requests:** {', '.join(flight.get('special_requests', []))}")
    
    with detail_tabs[2]:  # Payment
        st.markdown("**Pricing Breakdown**")
        
        pricing_data = [
            ("Base Fare", pricing.get('base_fare', 0)),
            ("Taxes", pricing.get('taxes', 0)),
            ("Fuel Surcharge", pricing.get('fuel_surcharge', 0)),
            ("Booking Fee", pricing.get('booking_fee', 0)),
            ("Insurance", pricing.get('insurance', 0)),
            ("Baggage Fee", pricing.get('baggage_fee', 0)),
            ("Seat Selection", pricing.get('seat_selection_fee', 0)),
            ("Meal Upgrade", pricing.get('meal_upgrade', 0)),
        ]
        
        for label, value in pricing_data:
            if value > 0:
                st.write(f"- **{label}:** ${value:,.2f}")
        
        if pricing.get('discount_amount', 0) > 0:
            st.write(f"- **Discount ({pricing.get('discount_code', '')}):** -${pricing.get('discount_amount', 0):,.2f}")
        
        st.markdown(f"### Total: ${pricing.get('total', 0):,.2f} {pricing.get('currency', 'USD')}")
        
        # Payment method info
        payment_data = lifecycle.get('payment', {})
        if isinstance(payment_data, dict) and payment_data.get('metadata'):
            st.markdown("**Payment Information**")
            st.write(f"- **Method:** {payment_data.get('metadata', {}).get('payment_method', 'N/A')}")
            if payment_data.get('metadata', {}).get('authorization_code'):
                st.write(f"- **Auth Code:** {payment_data['metadata']['authorization_code']}")
    
    with detail_tabs[3]:  # Lifecycle
        st.markdown("**Transaction Lifecycle**")
        st.markdown(render_lifecycle_visual(lifecycle), unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**Stage Details**")
        
        for stage_name in ["search", "selection", "booking", "payment", "ticketing", "confirmation"]:
            stage = lifecycle.get(stage_name, {})
            if isinstance(stage, dict) and stage.get('status') not in [None, 'not_reached']:
                status_icon = "✓" if stage.get('status') == 'completed' else "✗" if stage.get('status') == 'failed' else "⏳"
                st.write(f"**{status_icon} {stage_name.upper()}**")
                st.write(f"- Status: {stage.get('status', 'N/A')}")
                st.write(f"- Details: {stage.get('details', 'N/A')}")
                if stage.get('timestamp'):
                    st.write(f"- Timestamp: {stage.get('timestamp')[:19]}")
                if stage.get('duration_seconds'):
                    st.write(f"- Duration: {stage.get('duration_seconds')} seconds")
    
    with detail_tabs[4]:  # Error Details
        if error_info:
            st.markdown(render_alert(f"Transaction failed at {error_info.get('error_stage', 'Unknown')} stage", "error"), unsafe_allow_html=True)
            
            st.markdown("**Error Information**")
            st.write(f"- **Error Code:** `{error_info.get('error_code', 'N/A')}`")
            st.write(f"- **Category:** {error_info.get('error_category', 'N/A')}")
            st.write(f"- **Message:** {error_info.get('error_message', 'N/A')}")
            st.write(f"- **Technical Details:** {error_info.get('technical_details', 'N/A')}")
            
            st.markdown("**Resolution**")
            st.write(f"- **Requires Action:** {'Yes' if error_info.get('requires_action') else 'No'}")
            st.write(f"- **Escalation Level:** {error_info.get('escalation_level', 'N/A')}")
            st.write(f"- **Suggested Resolution:** {error_info.get('suggested_resolution', 'N/A')}")
            st.write(f"- **Auto-Retry Eligible:** {'Yes' if error_info.get('auto_retry_eligible') else 'No'}")
            st.write(f"- **Retry Count:** {error_info.get('retry_count', 0)}")
        else:
            st.info("No errors recorded for this transaction.")
    
    with detail_tabs[5]:  # Refund
        if refund_info:
            status_color = "success" if refund_info.get('status') == 'Completed' else "warning" if refund_info.get('status') == 'Pending' else "error"
            st.markdown(render_alert(f"Refund Status: {refund_info.get('status', 'Unknown')}", status_color), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Refund Details**")
                st.write(f"- **Reference:** `{refund_info.get('refund_reference', 'N/A')}`")
                st.write(f"- **Amount:** ${refund_info.get('refund_amount', 0):,.2f}")
                st.write(f"- **Percentage:** {refund_info.get('refund_percentage', 0)}%")
                st.write(f"- **Reason:** {refund_info.get('refund_reason', 'N/A')}")
            
            with col2:
                st.markdown("**Processing Information**")
                st.write(f"- **Type:** {refund_info.get('refund_type', 'N/A')}")
                st.write(f"- **Cancellation Fee:** ${refund_info.get('cancellation_fee', 0):,.2f}")
                st.write(f"- **Initiated:** {refund_info.get('initiated_at', 'N/A')[:10] if refund_info.get('initiated_at') else 'N/A'}")
                st.write(f"- **Expected Date:** {refund_info.get('expected_date', 'N/A')}")
                st.write(f"- **Notes:** {refund_info.get('processing_notes', 'N/A')}")
        else:
            st.info("No refund information for this transaction.")
    
    with detail_tabs[6]:  # Notes
        notes = txn.get('agent_notes', [])
        comms = txn.get('communication_log', [])
        
        if notes:
            st.markdown("**Agent Notes**")
            for note in notes:
                st.markdown(f"""
                <div style="background: #f7fafc; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem; border-left: 3px solid #4299e1;">
                    <strong>{note.get('agent_name', 'Unknown')} ({note.get('agent_id', '')})</strong>
                    <span style="color: #718096; font-size: 0.8rem;"> - {note.get('timestamp', '')[:16]}</span><br>
                    <span style="color: #2d3748;">{note.get('content', '')}</span>
                </div>
                """, unsafe_allow_html=True)
        
        if comms:
            st.markdown("**Communication Log**")
            for comm in comms:
                direction_icon = "📤" if comm.get('direction') == 'Outbound' else "📥"
                st.markdown(f"""
                <div style="background: #f7fafc; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                    <strong>{direction_icon} {comm.get('channel', '')} - {comm.get('subject', '')}</strong>
                    <span style="color: #718096; font-size: 0.8rem;"> - {comm.get('timestamp', '')[:16]}</span><br>
                    <span style="color: #2d3748;">{comm.get('summary', '')}</span><br>
                    <span style="font-size: 0.75rem; color: #a0aec0;">Sentiment: {comm.get('sentiment', 'Unknown')} | Resolved: {'Yes' if comm.get('resolved') else 'No'}</span>
                </div>
                """, unsafe_allow_html=True)
        
        if not notes and not comms:
            st.info("No notes or communications recorded for this transaction.")


def render_analytics_tab():
    """Render the Analytics Dashboard"""
    
    st.markdown("### 📈 Analytics Dashboard")
    
    transactions = st.session_state.transactions
    stats = calculate_statistics(transactions)
    
    # Key Metrics Row
    st.markdown("#### Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(render_metric_card(
            str(stats['total']),
            "Total Transactions",
            ""
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_metric_card(
            f"{stats['success_rate']}%",
            "Success Rate",
            "success" if stats['success_rate'] > 80 else "warning" if stats['success_rate'] > 60 else "danger"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_metric_card(
            str(stats['failed']),
            "Failed Transactions",
            "danger" if stats['failed'] > 20 else "warning"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(render_metric_card(
            str(stats['refund_stats']['pending']),
            "Pending Refunds",
            "warning" if stats['refund_stats']['pending'] > 10 else ""
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(render_metric_card(
            f"${stats['refund_stats']['value']:,.0f}",
            "Total Refunds Value",
            "info"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Transaction Status Distribution")
        status_df = pd.DataFrame([
            {"Status": k, "Count": v}
            for k, v in stats['status_breakdown'].items()
        ])
        if not status_df.empty:
            st.bar_chart(status_df.set_index("Status"))
    
    with col2:
        st.markdown("#### Failure Breakdown by Stage")
        failure_df = pd.DataFrame([
            {"Stage": k, "Count": v}
            for k, v in stats['failure_breakdown'].items()
        ])
        if not failure_df.empty:
            st.bar_chart(failure_df.set_index("Stage"))
        else:
            st.info("No failures recorded")
    
    st.markdown("---")
    
    # Detailed Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Priority Distribution")
        for priority, count in sorted(stats['priority_breakdown'].items(), key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x[0], 4)):
            pct = round(count / stats['total'] * 100, 1) if stats['total'] > 0 else 0
            st.markdown(f"{get_priority_badge(priority)} **{count}** ({pct}%)", unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Refund Statistics")
        st.write(f"- **Completed Refunds:** {stats['refund_stats']['completed']}")
        st.write(f"- **Pending Refunds:** {stats['refund_stats']['pending']}")
        st.write(f"- **Total Refund Value:** ${stats['refund_stats']['value']:,.2f}")
        st.write(f"- **SLA Breaches:** {stats['sla_breaches']}")
    
    st.markdown("---")
    
    # Failure Analysis
    st.markdown("#### 🔍 Detailed Failure Analysis")
    
    # Payment Failures
    payment_failures = [t for t in transactions if t.get('outcome') == 'payment_failed']
    if payment_failures:
        st.markdown("**Payment Failure Reasons:**")
        payment_reasons = {}
        for t in payment_failures:
            if t.get('error_info'):
                reason = t['error_info'].get('error_message', 'Unknown')
                payment_reasons[reason] = payment_reasons.get(reason, 0) + 1
        
        for reason, count in sorted(payment_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.write(f"- {reason}: **{count}** occurrences")
    
    # Booking Failures
    booking_failures = [t for t in transactions if t.get('outcome') == 'booking_failed']
    if booking_failures:
        st.markdown("**Booking Failure Reasons:**")
        booking_reasons = {}
        for t in booking_failures:
            if t.get('error_info'):
                reason = t['error_info'].get('error_message', 'Unknown')
                booking_reasons[reason] = booking_reasons.get(reason, 0) + 1
        
        for reason, count in sorted(booking_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.write(f"- {reason}: **{count}** occurrences")


def render_help_tab():
    """Render the Help & Documentation tab"""
    
    st.markdown("### 📚 Help & Documentation")
    
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        **Welcome to NDC Genie!**
        
        1. **API Key Setup**: 
           - For Streamlit Cloud: Add `ANTHROPIC_API_KEY` to your app's Secrets
           - For local development: Use the manual entry in the sidebar
        2. **Use the AI Chat**: Ask natural language questions about transactions
        3. **Browse Transactions**: View and filter all transactions in the browser
        4. **Analyze Patterns**: Use the Analytics dashboard for insights
        
        **Sample Questions to Ask:**
        - "Show all failed payment transactions"
        - "Find transaction for customer John Smith"
        - "What are the common failure reasons?"
        - "List all pending refunds with amounts"
        """)
    
    with st.expander("🔍 Search Tips"):
        st.markdown("""
        **You can search transactions by:**
        - Transaction ID (e.g., `TXN-202501-ABCD1234`)
        - Customer name (e.g., `John Smith`)
        - Customer email
        - Booking reference (6 characters)
        - PNR (6 characters)
        - Flight number
        
        **Pro Tips:**
        - Use filters in the sidebar for bulk filtering
        - Combine search with filters for precise results
        - Export filtered results using the Export buttons
        """)
    
    with st.expander("📊 Understanding Transaction Lifecycle"):
        st.markdown("""
        **Transaction Stages:**
        
        1. **Search** ➜ Customer searches for flights
        2. **Selection** ➜ Customer selects a flight
        3. **Booking** ➜ Passenger details are entered
        4. **Payment** ➜ Payment is processed
        5. **Ticketing** ➜ E-ticket is generated
        6. **Confirmation** ➜ Confirmation sent to customer
        7. **Refund** ➜ (If applicable) Refund is processed
        
        **Status Indicators:**
        - ✓ Green = Completed successfully
        - ✗ Red = Failed at this stage
        - ⏳ Yellow = Pending/In progress
        - ○ Gray = Not reached
        """)
    
    with st.expander("⚠️ Priority Levels"):
        st.markdown("""
        **Priority Classification:**
        
        - 🔴 **Critical**: Payment or ticketing failures requiring immediate attention
        - 🟠 **High**: Booking failures or escalated cases
        - 🟡 **Medium**: Refund requests and standard issues
        - 🟢 **Low**: Routine inquiries and completed transactions
        
        **SLA Guidelines:**
        - Response Time: 4 hours
        - Resolution Time: 24 hours
        - Refund Processing: 72 hours
        """)
    
    with st.expander("💡 AI Query Examples"):
        st.markdown("""
        **Transaction Lookup:**
        - "Find transaction TXN-202501-ABC12345"
        - "Show all bookings for customer@email.com"
        - "What is the status of PNR ABC123?"
        
        **Failure Investigation:**
        - "Why did transaction TXN-XXX fail?"
        - "Show all payment failures from today"
        - "What are the most common booking errors?"
        
        **Refund Management:**
        - "List all pending refunds over $500"
        - "Show refunds that are overdue"
        - "What is the refund status for booking ABCDEF?"
        
        **Analytics:**
        - "What is our success rate this week?"
        - "Show failure trends by airline"
        - "Identify patterns in payment declines"
        """)
    
    with st.expander("🔑 API Configuration"):
        st.markdown("""
        **Setting up the Anthropic API Key**
        
        **For Streamlit Cloud Deployment (Recommended):**
        1. Go to your app on [share.streamlit.io](https://share.streamlit.io)
        2. Click the **⋮** menu → **Settings**
        3. Navigate to **Secrets** section
        4. Add your API key:
        ```toml
        ANTHROPIC_API_KEY = "sk-ant-your-key-here"
        ```
        5. Click **Save** - the app will automatically reload
        
        **For Local Development:**
        1. Create a file `.streamlit/secrets.toml` in your project folder
        2. Add your API key:
        ```toml
        ANTHROPIC_API_KEY = "sk-ant-your-key-here"
        ```
        3. Alternatively, use the manual entry option in the sidebar
        
        **Getting an API Key:**
        1. Visit [console.anthropic.com](https://console.anthropic.com)
        2. Sign up or log in
        3. Navigate to **API Keys**
        4. Click **Create Key**
        5. Copy and save your key securely
        
        **Security Best Practices:**
        - Never commit API keys to version control
        - Use Streamlit Secrets for production deployments
        - Rotate keys periodically
        - Monitor usage in the Anthropic Console
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point"""
    
    # Inject custom CSS
    inject_custom_css()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AUTHENTICATION CHECK - Shows login page if not authenticated
    # ═══════════════════════════════════════════════════════════════════════════
    
    user = require_authentication()
    
    if not user:
        return  # Stop here - login page is shown by require_authentication()
    
    # Get auth manager for permission checks
    auth = get_auth_manager()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AUTHENTICATED USER - Render main application
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Build tabs based on user permissions
    tab_names = []
    tab_permissions = []
    
    # AI Assistant - requires USE_AI_ASSISTANT permission
    if auth.has_permission(Permission.USE_AI_ASSISTANT.value):
        tab_names.append("💬 AI Assistant")
        tab_permissions.append("ai")
    
    # Transactions - requires VIEW_TRANSACTIONS permission
    if auth.has_permission(Permission.VIEW_TRANSACTIONS.value):
        tab_names.append("📋 Transactions")
        tab_permissions.append("transactions")
    
    # Analytics - requires VIEW_BASIC_ANALYTICS permission
    if auth.has_permission(Permission.VIEW_BASIC_ANALYTICS.value):
        tab_names.append("📈 Analytics")
        tab_permissions.append("analytics")
    
    # Operations - requires VIEW_BASIC_ANALYTICS permission (same as analytics)
    if auth.has_permission(Permission.VIEW_BASIC_ANALYTICS.value):
        tab_names.append("✈️ Operations")
        tab_permissions.append("operations")
    
    # User Management - requires VIEW_USERS permission
    if auth.has_permission(Permission.VIEW_USERS.value):
        tab_names.append("👥 Users")
        tab_permissions.append("users")
    
    # Help - available to all authenticated users
    tab_names.append("❓ Help")
    tab_permissions.append("help")
    
    # Render tabs
    if len(tab_names) > 0:
        tabs = st.tabs(tab_names)
        
        for i, tab_type in enumerate(tab_permissions):
            with tabs[i]:
                if tab_type == "ai":
                    render_chat_tab()
                elif tab_type == "transactions":
                    render_transactions_tab()
                elif tab_type == "analytics":
                    render_analytics_tab()
                elif tab_type == "operations":
                    render_operations_tab()
                elif tab_type == "users":
                    render_user_management()
                elif tab_type == "help":
                    render_help_tab()


if __name__ == "__main__":
    main()
