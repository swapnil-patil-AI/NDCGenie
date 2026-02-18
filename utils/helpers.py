"""
Utility Functions for NDC Genie
Production-ready helper functions for data processing, validation, and formatting.
"""

import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
import pandas as pd

from utils.config import app_config


# ═══════════════════════════════════════════════════════════════════════════════
# DATA VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_transaction(txn: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a transaction record for completeness and correctness.
    
    Args:
        txn: Transaction dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    required_fields = ['transaction_id', 'customer', 'flight', 'pricing', 'lifecycle', 'status']
    
    for field in required_fields:
        if field not in txn:
            errors.append(f"Missing required field: {field}")
    
    # Validate customer
    if 'customer' in txn:
        customer_fields = ['customer_id', 'first_name', 'last_name', 'email']
        for field in customer_fields:
            if field not in txn['customer']:
                errors.append(f"Missing customer field: {field}")
        
        # Validate email format
        if 'email' in txn['customer']:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, txn['customer']['email']):
                errors.append(f"Invalid email format: {txn['customer']['email']}")
    
    # Validate flight
    if 'flight' in txn:
        flight_fields = ['flight_number', 'origin', 'destination', 'departure_date']
        for field in flight_fields:
            if field not in txn['flight']:
                errors.append(f"Missing flight field: {field}")
    
    # Validate pricing
    if 'pricing' in txn:
        if 'total' in txn['pricing']:
            if txn['pricing']['total'] < 0:
                errors.append("Pricing total cannot be negative")
    
    # Validate status
    if 'status' in txn:
        if txn['status'] not in app_config.TRANSACTION_STATUSES:
            errors.append(f"Invalid status: {txn['status']}")
    
    return (len(errors) == 0, errors)


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate Anthropic API key format.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if format is valid
    """
    if not api_key:
        return False
    
    # Anthropic keys typically start with 'sk-ant-'
    if api_key.startswith('sk-ant-') and len(api_key) > 20:
        return True
    
    # Also accept other formats for flexibility
    return len(api_key) > 30


# ═══════════════════════════════════════════════════════════════════════════════
# DATA FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    currency_symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
        "CAD": "C$", "AUD": "A$", "INR": "₹", "CNY": "¥"
    }
    symbol = currency_symbols.get(currency, currency + " ")
    return f"{symbol}{amount:,.2f}"


def format_datetime(dt_string: str, format_type: str = "full") -> str:
    """
    Format datetime string for display.
    
    Args:
        dt_string: ISO format datetime string
        format_type: 'full', 'date', 'time', 'relative'
        
    Returns:
        Formatted datetime string
    """
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return dt_string or "N/A"
    
    if format_type == "date":
        return dt.strftime("%Y-%m-%d")
    elif format_type == "time":
        return dt.strftime("%H:%M:%S")
    elif format_type == "relative":
        return get_relative_time(dt)
    else:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_relative_time(dt: datetime) -> str:
    """Get human-readable relative time (e.g., '2 hours ago')."""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if hours < 24:
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    days = hours // 24
    hours = hours % 24
    return f"{days}d {hours}h" if hours else f"{days}d"


def format_phone(phone: str) -> str:
    """Format phone number for display."""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11:
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone


# ═══════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_sla_status(txn: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate SLA status for a transaction.
    
    Returns dict with:
        - is_breached: bool
        - hours_remaining: float (negative if breached)
        - sla_type: str
        - deadline: datetime
    """
    try:
        created = datetime.fromisoformat(txn.get('created_at', '').replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return {"is_breached": False, "hours_remaining": None, "sla_type": "Unknown"}
    
    status = txn.get('status', '')
    priority = txn.get('priority', 'Low')
    
    # Determine SLA based on priority and status
    sla_hours = app_config.SLA_RESPONSE_TIME
    if priority == "Critical":
        sla_hours = 1
    elif priority == "High":
        sla_hours = 2
    elif "Refund" in status:
        sla_hours = app_config.SLA_REFUND_TIME
    
    deadline = created + timedelta(hours=sla_hours)
    now = datetime.now()
    hours_remaining = (deadline - now).total_seconds() / 3600
    
    return {
        "is_breached": hours_remaining < 0,
        "hours_remaining": round(hours_remaining, 1),
        "sla_type": "Response" if sla_hours <= 4 else "Resolution",
        "deadline": deadline.isoformat(),
        "sla_hours": sla_hours
    }


def get_failure_summary(transactions: List[Dict]) -> Dict[str, Any]:
    """
    Get detailed failure analysis from transactions.
    
    Returns comprehensive failure statistics.
    """
    failures = [t for t in transactions if t.get('status') == 'Failed']
    
    if not failures:
        return {
            "total_failures": 0,
            "by_stage": {},
            "by_reason": {},
            "by_airline": {},
            "by_route": {},
            "trends": []
        }
    
    by_stage = {}
    by_reason = {}
    by_airline = {}
    by_route = {}
    by_date = {}
    
    for t in failures:
        # By stage
        error_info = t.get('error_info', {})
        stage = error_info.get('error_stage', 'Unknown')
        by_stage[stage] = by_stage.get(stage, 0) + 1
        
        # By reason
        reason = error_info.get('error_message', 'Unknown')
        by_reason[reason] = by_reason.get(reason, 0) + 1
        
        # By airline
        airline = t.get('flight', {}).get('airline_name', 'Unknown')
        by_airline[airline] = by_airline.get(airline, 0) + 1
        
        # By route
        origin = t.get('flight', {}).get('origin', '???')
        dest = t.get('flight', {}).get('destination', '???')
        route = f"{origin}-{dest}"
        by_route[route] = by_route.get(route, 0) + 1
        
        # By date
        try:
            date = t.get('created_at', '')[:10]
            by_date[date] = by_date.get(date, 0) + 1
        except:
            pass
    
    # Sort trends by date
    trends = [{"date": k, "count": v} for k, v in sorted(by_date.items())]
    
    return {
        "total_failures": len(failures),
        "by_stage": dict(sorted(by_stage.items(), key=lambda x: -x[1])),
        "by_reason": dict(sorted(by_reason.items(), key=lambda x: -x[1])[:10]),
        "by_airline": dict(sorted(by_airline.items(), key=lambda x: -x[1])),
        "by_route": dict(sorted(by_route.items(), key=lambda x: -x[1])[:10]),
        "trends": trends[-14:]  # Last 14 days
    }


def get_refund_summary(transactions: List[Dict]) -> Dict[str, Any]:
    """
    Get detailed refund analysis from transactions.
    """
    refunds = [t for t in transactions if t.get('refund_info')]
    
    if not refunds:
        return {
            "total_refunds": 0,
            "completed": 0,
            "pending": 0,
            "rejected": 0,
            "total_value": 0,
            "pending_value": 0,
            "by_reason": {},
            "avg_processing_days": 0
        }
    
    completed = 0
    pending = 0
    rejected = 0
    total_value = 0
    pending_value = 0
    by_reason = {}
    processing_times = []
    
    for t in refunds:
        refund = t['refund_info']
        status = refund.get('status', 'Unknown')
        amount = refund.get('refund_amount', 0)
        reason = refund.get('refund_reason', 'Unknown')
        
        by_reason[reason] = by_reason.get(reason, 0) + 1
        
        if status == 'Completed':
            completed += 1
            total_value += amount
            # Calculate processing time
            try:
                initiated = datetime.fromisoformat(refund.get('initiated_at', '').replace('Z', ''))
                processed = datetime.fromisoformat(refund.get('processed_at', '').replace('Z', ''))
                processing_times.append((processed - initiated).days)
            except:
                pass
        elif status == 'Pending':
            pending += 1
            pending_value += amount
        elif status == 'Rejected':
            rejected += 1
    
    avg_processing = sum(processing_times) / len(processing_times) if processing_times else 0
    
    return {
        "total_refunds": len(refunds),
        "completed": completed,
        "pending": pending,
        "rejected": rejected,
        "total_value": round(total_value, 2),
        "pending_value": round(pending_value, 2),
        "by_reason": dict(sorted(by_reason.items(), key=lambda x: -x[1])),
        "avg_processing_days": round(avg_processing, 1)
    }


def get_customer_insights(transactions: List[Dict], customer_id: str = None, email: str = None) -> Dict[str, Any]:
    """
    Get insights for a specific customer or all customers.
    """
    if customer_id:
        customer_txns = [t for t in transactions if t.get('customer', {}).get('customer_id') == customer_id]
    elif email:
        customer_txns = [t for t in transactions if t.get('customer', {}).get('email', '').lower() == email.lower()]
    else:
        return {"error": "Customer ID or email required"}
    
    if not customer_txns:
        return {"error": "No transactions found for customer"}
    
    customer = customer_txns[0].get('customer', {})
    
    total_spent = sum(t.get('pricing', {}).get('total', 0) for t in customer_txns if t.get('status') == 'Completed')
    failed_count = len([t for t in customer_txns if t.get('status') == 'Failed'])
    refund_count = len([t for t in customer_txns if t.get('refund_info')])
    
    return {
        "customer": customer,
        "total_transactions": len(customer_txns),
        "completed": len([t for t in customer_txns if t.get('status') == 'Completed']),
        "failed": failed_count,
        "refunds": refund_count,
        "total_spent": round(total_spent, 2),
        "transactions": customer_txns
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH & FILTERING
# ═══════════════════════════════════════════════════════════════════════════════

def search_transactions(
    transactions: List[Dict],
    query: str,
    fields: List[str] = None
) -> List[Dict]:
    """
    Search transactions by multiple fields.
    
    Args:
        transactions: List of transaction dicts
        query: Search query string
        fields: Specific fields to search (None = search all)
        
    Returns:
        List of matching transactions
    """
    if not query:
        return transactions
    
    query = query.lower().strip()
    results = []
    
    default_fields = [
        ('transaction_id', lambda t: t.get('transaction_id', '')),
        ('customer_name', lambda t: f"{t.get('customer', {}).get('first_name', '')} {t.get('customer', {}).get('last_name', '')}"),
        ('email', lambda t: t.get('customer', {}).get('email', '')),
        ('phone', lambda t: t.get('customer', {}).get('phone', '')),
        ('flight_number', lambda t: t.get('flight', {}).get('flight_number', '')),
        ('booking_ref', lambda t: str(t.get('lifecycle', {}).get('booking', {}).get('metadata', {}).get('booking_ref', ''))),
        ('pnr', lambda t: str(t.get('lifecycle', {}).get('ticketing', {}).get('metadata', {}).get('pnr', ''))),
        ('e_ticket', lambda t: str(t.get('lifecycle', {}).get('ticketing', {}).get('metadata', {}).get('e_ticket_number', ''))),
    ]
    
    for txn in transactions:
        for field_name, extractor in default_fields:
            if fields and field_name not in fields:
                continue
            try:
                value = extractor(txn)
                if value and query in str(value).lower():
                    results.append(txn)
                    break
            except:
                continue
    
    return results


def advanced_filter(
    transactions: List[Dict],
    status: List[str] = None,
    priority: List[str] = None,
    airline: List[str] = None,
    date_from: str = None,
    date_to: str = None,
    amount_min: float = None,
    amount_max: float = None,
    has_error: bool = None,
    has_refund: bool = None,
    sla_breach: bool = None,
    loyalty_tier: List[str] = None
) -> List[Dict]:
    """
    Apply advanced filters to transactions.
    """
    results = transactions.copy()
    
    if status:
        results = [t for t in results if t.get('status') in status]
    
    if priority:
        results = [t for t in results if t.get('priority') in priority]
    
    if airline:
        results = [t for t in results if t.get('flight', {}).get('airline_name') in airline]
    
    if date_from:
        results = [t for t in results if t.get('created_at', '') >= date_from]
    
    if date_to:
        results = [t for t in results if t.get('created_at', '')[:10] <= date_to]
    
    if amount_min is not None:
        results = [t for t in results if t.get('pricing', {}).get('total', 0) >= amount_min]
    
    if amount_max is not None:
        results = [t for t in results if t.get('pricing', {}).get('total', 0) <= amount_max]
    
    if has_error is not None:
        if has_error:
            results = [t for t in results if t.get('error_info')]
        else:
            results = [t for t in results if not t.get('error_info')]
    
    if has_refund is not None:
        if has_refund:
            results = [t for t in results if t.get('refund_info')]
        else:
            results = [t for t in results if not t.get('refund_info')]
    
    if sla_breach is not None:
        results = [t for t in results if t.get('sla_breach') == sla_breach]
    
    if loyalty_tier:
        results = [t for t in results if t.get('customer', {}).get('loyalty_tier') in loyalty_tier]
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def export_to_csv(transactions: List[Dict]) -> bytes:
    """Export transactions to CSV format."""
    rows = []
    for t in transactions:
        customer = t.get('customer', {})
        flight = t.get('flight', {})
        pricing = t.get('pricing', {})
        lifecycle = t.get('lifecycle', {})
        error_info = t.get('error_info') or {}
        refund_info = t.get('refund_info') or {}
        
        row = {
            "Transaction ID": t.get('transaction_id'),
            "Status": t.get('status'),
            "Priority": t.get('priority'),
            "SLA Breach": "Yes" if t.get('sla_breach') else "No",
            "Customer ID": customer.get('customer_id'),
            "Customer Name": f"{customer.get('first_name', '')} {customer.get('last_name', '')}",
            "Email": customer.get('email'),
            "Phone": customer.get('phone'),
            "Loyalty Tier": customer.get('loyalty_tier'),
            "Flight Number": flight.get('flight_number'),
            "Airline": flight.get('airline_name'),
            "Origin": f"{flight.get('origin_city', '')} ({flight.get('origin', '')})",
            "Destination": f"{flight.get('destination_city', '')} ({flight.get('destination', '')})",
            "Departure Date": flight.get('departure_date'),
            "Departure Time": flight.get('departure_time'),
            "Cabin Class": flight.get('cabin_class'),
            "Passengers": flight.get('passengers'),
            "Base Fare": pricing.get('base_fare'),
            "Taxes": pricing.get('taxes'),
            "Total": pricing.get('total'),
            "Currency": pricing.get('currency'),
            "Booking Ref": lifecycle.get('booking', {}).get('metadata', {}).get('booking_ref') if isinstance(lifecycle.get('booking'), dict) else None,
            "PNR": lifecycle.get('ticketing', {}).get('metadata', {}).get('pnr') if isinstance(lifecycle.get('ticketing'), dict) else None,
            "E-Ticket": lifecycle.get('ticketing', {}).get('metadata', {}).get('e_ticket_number') if isinstance(lifecycle.get('ticketing'), dict) else None,
            "Error Stage": error_info.get('error_stage'),
            "Error Code": error_info.get('error_code'),
            "Error Message": error_info.get('error_message'),
            "Refund Status": refund_info.get('status'),
            "Refund Amount": refund_info.get('refund_amount'),
            "Refund Reason": refund_info.get('refund_reason'),
            "Created At": t.get('created_at'),
            "Last Updated": t.get('last_updated'),
            "Assigned Agent": t.get('assigned_agent'),
            "Tags": ", ".join(t.get('tags', []))
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode('utf-8')


def export_to_json(transactions: List[Dict]) -> bytes:
    """Export transactions to JSON format."""
    return json.dumps(transactions, indent=2, default=str).encode('utf-8')


def export_summary_report(transactions: List[Dict]) -> str:
    """Generate a text summary report of transactions."""
    stats = calculate_statistics(transactions)
    failure_summary = get_failure_summary(transactions)
    refund_summary = get_refund_summary(transactions)
    
    report = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      NDC_GENIE AI - TRANSACTION SUMMARY REPORT                ║
║                           Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝

1. OVERVIEW
   ─────────────────────────────────────────────────────────────────────────────
   Total Transactions: {stats['total']:,}
   Success Rate: {stats['success_rate']}%
   
   Status Breakdown:
   • Completed: {stats['status_breakdown'].get('Completed', 0):,}
   • Failed: {stats['status_breakdown'].get('Failed', 0):,}
   • Refunded: {stats['status_breakdown'].get('Refunded', 0):,}
   • Refund Pending: {stats['status_breakdown'].get('Refund Pending', 0):,}
   • Abandoned: {stats['status_breakdown'].get('Abandoned', 0):,}

2. FAILURE ANALYSIS
   ─────────────────────────────────────────────────────────────────────────────
   Total Failures: {failure_summary['total_failures']:,}
   
   By Stage:
"""
    for stage, count in failure_summary['by_stage'].items():
        report += f"   • {stage}: {count}\n"
    
    report += f"""
   Top Failure Reasons:
"""
    for reason, count in list(failure_summary['by_reason'].items())[:5]:
        report += f"   • {reason}: {count}\n"
    
    report += f"""
3. REFUND ANALYSIS
   ─────────────────────────────────────────────────────────────────────────────
   Total Refunds: {refund_summary['total_refunds']:,}
   Completed: {refund_summary['completed']:,}
   Pending: {refund_summary['pending']:,}
   Rejected: {refund_summary['rejected']:,}
   
   Total Value Refunded: ${refund_summary['total_value']:,.2f}
   Pending Refund Value: ${refund_summary['pending_value']:,.2f}
   Avg Processing Time: {refund_summary['avg_processing_days']} days

4. PRIORITY BREAKDOWN
   ─────────────────────────────────────────────────────────────────────────────
"""
    for priority, count in stats['priority_breakdown'].items():
        report += f"   • {priority}: {count:,}\n"
    
    report += f"""
   SLA Breaches: {stats.get('sla_breaches', 0):,}

═══════════════════════════════════════════════════════════════════════════════
                              END OF REPORT
═══════════════════════════════════════════════════════════════════════════════
"""
    return report


def calculate_statistics(transactions: List[Dict]) -> Dict[str, Any]:
    """Calculate comprehensive statistics from transactions."""
    total = len(transactions)
    if total == 0:
        return {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "success_rate": 0,
            "status_breakdown": {},
            "priority_breakdown": {},
            "sla_breaches": 0
        }
    
    status_breakdown = {}
    priority_breakdown = {}
    
    for t in transactions:
        status = t.get('status', 'Unknown')
        priority = t.get('priority', 'Low')
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
        priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
    
    completed = status_breakdown.get('Completed', 0)
    sla_breaches = sum(1 for t in transactions if t.get('sla_breach'))
    
    return {
        "total": total,
        "completed": completed,
        "failed": status_breakdown.get('Failed', 0),
        "success_rate": round(completed / total * 100, 1) if total > 0 else 0,
        "status_breakdown": status_breakdown,
        "priority_breakdown": priority_breakdown,
        "sla_breaches": sla_breaches
    }
