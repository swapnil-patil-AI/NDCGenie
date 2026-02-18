"""
Claude AI Integration for NDC Genie
Production-ready AI assistant with comprehensive error handling,
conversation memory, and optimized token usage.

Version: 2.1.0
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from anthropic import Anthropic

from utils.config import app_config


class ClaudeAssistant:
    """
    Production-ready Claude AI Assistant for transaction analysis.
    
    Features:
    - Conversation context memory across turns
    - Smart transaction filtering to stay within token limits
    - Comprehensive error handling
    - Fuzzy search for names and IDs
    - Action acknowledgment (escalate, process, etc.)
    - Hallucination prevention
    """
    
    # Configuration
    MAX_CONTEXT_TRANSACTIONS = 25
    MAX_CONVERSATION_HISTORY = 10
    
    def __init__(self, api_key: str):
        """Initialize the Claude assistant with API key"""
        self.client = Anthropic(api_key=api_key)
        self.model = app_config.ANTHROPIC_MODEL
        self.max_tokens = app_config.MAX_TOKENS
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TRANSACTION FORMATTING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _format_transaction_compact(self, t: Dict[str, Any]) -> str:
        """Create a compact string representation of a transaction"""
        
        customer = t.get('customer', {})
        flight = t.get('flight', {})
        lifecycle = t.get('lifecycle', {})
        
        # Extract booking ref and PNR
        booking_ref = ""
        pnr = ""
        if isinstance(lifecycle.get('booking'), dict):
            booking_ref = lifecycle['booking'].get('metadata', {}).get('booking_ref', '')
        if isinstance(lifecycle.get('ticketing'), dict):
            pnr = lifecycle['ticketing'].get('metadata', {}).get('pnr', '')
        
        # Build compact representation
        parts = [
            f"ID:{t.get('transaction_id', 'N/A')}",
            f"Status:{t.get('status', 'N/A')}",
            f"Priority:{t.get('priority', 'N/A')}",
            f"Customer:{customer.get('first_name', '')} {customer.get('last_name', '')}",
            f"Email:{customer.get('email', 'N/A')}",
            f"Phone:{customer.get('phone', 'N/A')}",
            f"Loyalty:{customer.get('loyalty_tier', 'N/A')}",
            f"Flight:{flight.get('flight_number', 'N/A')}",
            f"Airline:{flight.get('airline_name', 'N/A')}",
            f"Route:{flight.get('origin', '')}-{flight.get('destination', '')}",
            f"Date:{flight.get('departure_date', 'N/A')}",
            f"Class:{flight.get('cabin_class', 'N/A')}",
            f"Amount:${t.get('pricing', {}).get('total', 0):,.2f}",
        ]
        
        if booking_ref:
            parts.append(f"BookingRef:{booking_ref}")
        if pnr:
            parts.append(f"PNR:{pnr}")
        
        # Error details
        if t.get('error_info'):
            error = t['error_info']
            parts.append(f"Error:{error.get('error_message', 'N/A')}")
            if error.get('suggested_resolution'):
                parts.append(f"Fix:{error.get('suggested_resolution')[:80]}")
        
        # Refund details
        if t.get('refund_info'):
            refund = t['refund_info']
            parts.append(f"Refund:{refund.get('status', 'N/A')}-${refund.get('refund_amount', 0):,.2f}")
        
        # SLA status
        if t.get('sla_breach'):
            parts.append("SLA:BREACH")
        
        return " | ".join(parts)
    
    def _format_transaction_detailed(self, t: Dict[str, Any]) -> str:
        """Create a detailed multi-line representation for single transaction lookup"""
        
        customer = t.get('customer', {})
        flight = t.get('flight', {})
        pricing = t.get('pricing', {})
        lifecycle = t.get('lifecycle', {})
        
        # Extract booking ref and PNR
        booking_ref = ""
        pnr = ""
        e_ticket = ""
        if isinstance(lifecycle.get('booking'), dict):
            booking_ref = lifecycle['booking'].get('metadata', {}).get('booking_ref', '')
        if isinstance(lifecycle.get('ticketing'), dict):
            pnr = lifecycle['ticketing'].get('metadata', {}).get('pnr', '')
            e_ticket = lifecycle['ticketing'].get('metadata', {}).get('e_ticket_number', '')
        
        lines = [
            f"═══ TRANSACTION: {t.get('transaction_id')} ═══",
            f"Status: {t.get('status')} | Priority: {t.get('priority')} | SLA: {'⚠️ BREACH' if t.get('sla_breach') else 'OK'}",
            "",
            "CUSTOMER:",
            f"  Name: {customer.get('first_name')} {customer.get('last_name')}",
            f"  Email: {customer.get('email')}",
            f"  Phone: {customer.get('phone')}",
            f"  Loyalty: {customer.get('loyalty_tier')} ({customer.get('loyalty_points', 0):,} points)",
            f"  Customer ID: {customer.get('customer_id')}",
            "",
            "FLIGHT:",
            f"  Flight: {flight.get('flight_number')} ({flight.get('airline_name')})",
            f"  Route: {flight.get('origin_city')} ({flight.get('origin')}) → {flight.get('destination_city')} ({flight.get('destination')})",
            f"  Date: {flight.get('departure_date')} at {flight.get('departure_time')}",
            f"  Class: {flight.get('cabin_class')} | Passengers: {flight.get('passengers')}",
        ]
        
        if booking_ref or pnr:
            lines.extend([
                "",
                "BOOKING:",
                f"  Booking Ref: {booking_ref or 'N/A'}",
                f"  PNR: {pnr or 'N/A'}",
                f"  E-Ticket: {e_ticket or 'N/A'}",
            ])
        
        lines.extend([
            "",
            "PAYMENT:",
            f"  Base Fare: ${pricing.get('base_fare', 0):,.2f}",
            f"  Taxes: ${pricing.get('taxes', 0):,.2f}",
            f"  Total: ${pricing.get('total', 0):,.2f} {pricing.get('currency', 'USD')}",
        ])
        
        # Error details
        if t.get('error_info'):
            error = t['error_info']
            lines.extend([
                "",
                "ERROR DETAILS:",
                f"  Stage: {error.get('error_stage')}",
                f"  Code: {error.get('error_code')}",
                f"  Message: {error.get('error_message')}",
                f"  Resolution: {error.get('suggested_resolution', 'Contact support')}",
            ])
        
        # Refund details
        if t.get('refund_info'):
            refund = t['refund_info']
            lines.extend([
                "",
                "REFUND:",
                f"  Status: {refund.get('status')}",
                f"  Amount: ${refund.get('refund_amount', 0):,.2f}",
                f"  Reason: {refund.get('refund_reason')}",
                f"  Reference: {refund.get('refund_reference', 'N/A')}",
            ])
        
        return "\n".join(lines)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONVERSATION CONTEXT EXTRACTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _extract_conversation_context(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract all relevant context from conversation history."""
        context = {
            'transaction_ids': [],
            'emails': [],
            'booking_refs': [],
            'flight_numbers': [],
            'topics': set(),
            'pending_actions': [],
            'last_discussed_txn': None
        }
        
        for msg in messages:
            content = msg.get('content', '')
            content_lower = content.lower()
            role = msg.get('role', '')
            
            # Extract transaction IDs
            txn_matches = re.findall(r'TXN-\d{6}--[A-Z0-9]+', content, re.IGNORECASE)
            for match in txn_matches:
                txn_id = match.upper()
                if txn_id not in context['transaction_ids']:
                    context['transaction_ids'].append(txn_id)
                context['last_discussed_txn'] = txn_id
            
            # Extract emails
            email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
            for email in email_matches:
                if email.lower() not in [e.lower() for e in context['emails']]:
                    context['emails'].append(email)
            
            # Extract 6-character codes
            code_matches = re.findall(r'\b([A-Z0-9]{6})\b', content, re.IGNORECASE)
            for code in code_matches:
                code_upper = code.upper()
                if code_upper not in ['STATUS', 'FAILED', 'AMOUNT', 'FLIGHT', 'PLEASE', 'THANKS']:
                    if code_upper not in context['booking_refs']:
                        context['booking_refs'].append(code_upper)
            
            # Extract flight numbers
            flight_matches = re.findall(r'\b([A-Z]{2}\d{3,4})\b', content, re.IGNORECASE)
            for flight in flight_matches:
                if flight.upper() not in context['flight_numbers']:
                    context['flight_numbers'].append(flight.upper())
            
            # Detect topics
            if any(word in content_lower for word in ['failed', 'failure', 'error', 'problem', 'issue']):
                context['topics'].add('failures')
            if any(word in content_lower for word in ['refund', 'money back', 'cancel']):
                context['topics'].add('refunds')
            if any(word in content_lower for word in ['critical', 'urgent', 'priority', 'sla', 'breach']):
                context['topics'].add('priority')
            if any(word in content_lower for word in ['completed', 'success']):
                context['topics'].add('completed')
            
            # Track action requests
            if role == 'user':
                if any(word in content_lower for word in ['escalate', 'escalation']):
                    context['pending_actions'].append('escalate')
                if any(word in content_lower for word in ['process', 'proceed', 'continue', 'go ahead']):
                    context['pending_actions'].append('process')
                if any(word in content_lower for word in ['yes', 'ok', 'okay', 'sure', 'please do', 'confirm']):
                    context['pending_actions'].append('confirm')
        
        return context
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SMART TRANSACTION FILTERING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _fuzzy_match_id(self, search: str, txn_id: str) -> bool:
        """Fuzzy match for transaction IDs"""
        search = search.upper().replace(' ', '').replace('-', '')
        txn_id = txn_id.upper().replace(' ', '').replace('-', '')
        return search in txn_id or txn_id in search
    
    def _filter_transactions(
        self, 
        transactions: List[Dict], 
        context: Dict[str, Any],
        current_query: str
    ) -> Tuple[List[Dict], str]:
        """Filter transactions based on context and query."""
        
        query_lower = current_query.lower()
        max_results = self.MAX_CONTEXT_TRANSACTIONS
        
        # PRIORITY 1: Transaction IDs from conversation
        if context['transaction_ids']:
            matches = []
            for t in transactions:
                txn_id = t.get('transaction_id', '').upper()
                for mentioned_id in context['transaction_ids']:
                    if self._fuzzy_match_id(mentioned_id, txn_id):
                        if t not in matches:
                            matches.append(t)
            if matches:
                return matches[:max_results], f"Transactions: {', '.join(context['transaction_ids'][:3])}"
        
        # PRIORITY 2: Transaction ID in current query
        txn_match = re.search(r'TXN-\d{6}--[A-Z0-9]+', current_query, re.IGNORECASE)
        if txn_match:
            txn_id = txn_match.group(0).upper()
            matches = [t for t in transactions if self._fuzzy_match_id(txn_id, t.get('transaction_id', ''))]
            if matches:
                return matches[:max_results], f"Transaction: {txn_id}"
        
        # PRIORITY 3: Email lookup
        all_emails = context['emails'] + re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', current_query)
        if all_emails:
            matches = []
            for t in transactions:
                t_email = t.get('customer', {}).get('email', '').lower()
                for email in all_emails:
                    if email.lower() in t_email:
                        if t not in matches:
                            matches.append(t)
            if matches:
                return matches[:max_results], "Customer email search"
        
        # PRIORITY 4: Booking ref / PNR
        if context['booking_refs']:
            matches = []
            for t in transactions:
                lifecycle = t.get('lifecycle', {})
                booking_ref = ''
                pnr = ''
                if isinstance(lifecycle.get('booking'), dict):
                    booking_ref = str(lifecycle['booking'].get('metadata', {}).get('booking_ref', '')).upper()
                if isinstance(lifecycle.get('ticketing'), dict):
                    pnr = str(lifecycle['ticketing'].get('metadata', {}).get('pnr', '')).upper()
                
                for code in context['booking_refs']:
                    if code in booking_ref or code in pnr:
                        if t not in matches:
                            matches.append(t)
            if matches:
                return matches[:max_results], "Booking/PNR lookup"
        
        # PRIORITY 5: Topic-based filtering
        if 'failures' in context['topics'] or any(word in query_lower for word in ['failed', 'failure', 'error']):
            failed = [t for t in transactions if t.get('status') == 'Failed']
            return failed[:max_results], "Failed transactions"
        
        if 'refunds' in context['topics'] or any(word in query_lower for word in ['refund', 'pending refund']):
            refunds = [t for t in transactions if t.get('refund_info')]
            return refunds[:max_results], "Refund transactions"
        
        if 'priority' in context['topics'] or any(word in query_lower for word in ['critical', 'urgent', 'sla']):
            priority = [t for t in transactions if t.get('priority') in ['Critical', 'High'] or t.get('sla_breach')]
            return priority[:max_results], "Priority transactions"
        
        if 'completed' in context['topics'] or any(word in query_lower for word in ['completed', 'success']):
            completed = [t for t in transactions if t.get('status') == 'Completed']
            return completed[:max_results], "Completed transactions"
        
        # PRIORITY 6: Name search
        stop_words = ['about', 'show', 'tell', 'give', 'find', 'what', 'transaction', 'customer', 
                      'please', 'thank', 'thanks', 'help', 'escalate', 'resolve', 'process',
                      'information', 'details', 'status', 'check', 'need', 'want', 'this', 'that']
        
        search_words = [w for w in query_lower.split() if len(w) >= 3 and w.isalpha() and w not in stop_words]
        
        if search_words:
            matches = []
            for t in transactions:
                customer = t.get('customer', {})
                full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".lower()
                for word in search_words:
                    if word in full_name:
                        if t not in matches:
                            matches.append(t)
                        break
            if matches:
                return matches[:max_results], "Customer name search"
        
        # DEFAULT: Mix of important transactions
        critical = [t for t in transactions if t.get('priority') == 'Critical'][:6]
        high = [t for t in transactions if t.get('priority') == 'High'][:6]
        failed = [t for t in transactions if t.get('status') == 'Failed' and t not in critical + high][:6]
        refunds = [t for t in transactions if t.get('refund_info') and t not in critical + high + failed][:4]
        
        combined = critical + high + failed + refunds
        return combined[:max_results], "Overview (critical, failures, refunds)"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM PROMPT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _calculate_statistics(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics from transactions"""
        total = len(transactions)
        if total == 0:
            return {'total': 0}
        
        return {
            'total': total,
            'completed': len([t for t in transactions if t.get('status') == 'Completed']),
            'failed': len([t for t in transactions if t.get('status') == 'Failed']),
            'refunded': len([t for t in transactions if t.get('status') == 'Refunded']),
            'refund_pending': len([t for t in transactions if t.get('status') == 'Refund Pending']),
            'critical': len([t for t in transactions if t.get('priority') == 'Critical']),
            'high': len([t for t in transactions if t.get('priority') == 'High']),
            'sla_breaches': len([t for t in transactions if t.get('sla_breach')]),
            'payment_failures': len([t for t in transactions if t.get('outcome') == 'payment_failed']),
            'booking_failures': len([t for t in transactions if t.get('outcome') == 'booking_failed']),
            'success_rate': round(len([t for t in transactions if t.get('status') == 'Completed']) / total * 100, 1)
        }
    
    def _build_system_prompt(
        self, 
        transactions: List[Dict[str, Any]], 
        messages: List[Dict[str, str]],
        current_query: str
    ) -> str:
        """Build optimized system prompt"""
        
        if not transactions:
            return "You are NDC Genie. No transactions loaded."
        
        # Extract context
        context = self._extract_conversation_context(messages)
        stats = self._calculate_statistics(transactions)
        relevant, filter_reason = self._filter_transactions(transactions, context, current_query)
        
        # Single transaction = detailed view
        is_single = len(relevant) == 1 and context['transaction_ids']
        if is_single:
            txn_data = self._format_transaction_detailed(relevant[0])
        else:
            txn_data = "\n".join([self._format_transaction_compact(t) for t in relevant])
        
        # Context summary
        ctx_summary = ""
        if context['transaction_ids']:
            ctx_summary += f"\nDiscussed transactions: {', '.join(context['transaction_ids'][:5])}"
        if context['pending_actions']:
            ctx_summary += f"\nPending actions: {', '.join(set(context['pending_actions']))}"
        
        return f"""You are NDC Genie, an airline customer service assistant.

DATABASE ({stats['total']} transactions):
✅ Completed: {stats['completed']} ({stats['success_rate']}%) | ❌ Failed: {stats['failed']} | 💰 Refunded: {stats['refunded']} | ⏳ Pending: {stats['refund_pending']}
🔴 Critical: {stats['critical']} | 🟠 High: {stats['high']} | ⚠️ SLA Breaches: {stats['sla_breaches']}
Failures: Payment={stats['payment_failures']}, Booking={stats['booking_failures']}

CONVERSATION CONTEXT:{ctx_summary if ctx_summary else " New conversation"}

TRANSACTIONS ({len(relevant)} - {filter_reason}):
{txn_data}

RULES:
1. ONLY use transaction data above - NEVER invent transactions
2. If transaction not found, say "Transaction not found in current view"
3. For follow-ups (yes/proceed/escalate), use the last discussed transaction: {context['last_discussed_txn'] or 'None'}
4. For actions, acknowledge this is a DEMO and explain what would happen
5. Always include transaction IDs
6. Be helpful and concise

Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN RESPONSE METHOD
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_response(
        self, 
        messages: List[Dict[str, str]], 
        transactions: List[Dict[str, Any]]
    ) -> str:
        """Get AI response for the conversation."""
        
        if not messages:
            return "Please enter a question."
        
        # Get current query
        current_query = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                current_query = msg.get('content', '')
                break
        
        if not current_query.strip():
            return "How can I help you with airline transactions?"
        
        # Limit history
        limited_messages = messages[-self.MAX_CONVERSATION_HISTORY:]
        
        # Build prompt
        system_prompt = self._build_system_prompt(transactions, messages, current_query)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=limited_messages
            )
            return response.content[0].text
        
        except Exception as e:
            return self._handle_error(e)
    
    def _handle_error(self, error: Exception) -> str:
        """Handle API errors"""
        error_msg = str(error).lower()
        
        if "authentication" in error_msg or "401" in error_msg:
            return "⚠️ **Authentication Error**: Invalid API key. Check your Streamlit Secrets."
        elif "rate" in error_msg or "429" in error_msg:
            return "⚠️ **Rate Limit**: Too many requests. Wait 30 seconds and try again."
        elif "too long" in error_msg or "token" in error_msg:
            return "⚠️ **Query Too Complex**: Try asking about a specific transaction ID."
        elif "connection" in error_msg or "timeout" in error_msg:
            return "⚠️ **Connection Error**: Check your internet and try again."
        else:
            return "⚠️ **Error**: Something went wrong. Try rephrasing your question."
    
    # ═══════════════════════════════════════════════════════════════════════════
    # QUICK ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_quick_analysis(self, transactions: List[Dict[str, Any]], analysis_type: str) -> str:
        """Get quick pre-built analysis"""
        queries = {
            "critical_issues": "List Critical and High priority transactions needing attention.",
            "payment_failures": "Show top 5 payment failure reasons with transaction IDs.",
            "pending_refunds": "List pending refunds with amounts and customer names.",
            "daily_summary": "Brief summary: success rate, critical issues, pending refunds.",
        }
        
        query = queries.get(analysis_type, "Brief overview of transaction status.")
        messages = [{"role": "user", "content": query}]
        return self.get_response(messages, transactions)


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """Validate Anthropic API key"""
    if not api_key:
        return False, "API key is empty"
    
    if len(api_key) < 20:
        return False, "API key is too short"
    
    if not api_key.startswith('sk-ant-'):
        return False, "API key should start with 'sk-ant-'"
    
    try:
        client = Anthropic(api_key=api_key)
        client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True, "API key is valid"
    except Exception as e:
        error_msg = str(e).lower()
        if "authentication" in error_msg or "401" in error_msg:
            return False, "API key is invalid"
        elif "rate" in error_msg:
            return True, "API key valid (rate limited)"
        else:
            return False, f"Validation failed: {str(e)[:50]}"
