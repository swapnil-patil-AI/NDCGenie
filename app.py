"""
app.py - NDC Genie Main Streamlit Application

NDC Short-Sell flow tracked per transaction:
  Shopping → OfferPrice → SeatAvailability → ServiceAvailability → OrderCreate

Each transaction carries the full ID chain from all stages it passed through.
"""

import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from data.demo_data import get_demo_data
from components.ui_components import (
    get_status_badge,
    get_priority_badge,
    render_lifecycle_visual,
    render_metric_card,
    render_ndc_id_chain,
    render_transaction_summary_row,
)
from utils.config import AppConfig
from utils.ai_assistant import ClaudeAssistant

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="NDC Genie",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2b6cb0;
        color: white;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .block-container { padding-top: 1rem; }
    code { font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "transactions" not in st.session_state:
    st.session_state.transactions = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("ANTHROPIC_API_KEY", "")


@st.cache_data
def load_transactions(count: int = AppConfig.DEMO_TRANSACTION_COUNT) -> list[dict]:
    return get_demo_data(count=count, seed=42)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ✈️ NDC Genie")
    st.markdown("*Enterprise Airline Transaction Tracker*")
    st.divider()

    # API Key
    api_key_input = st.text_input(
        "Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        help="Enter your Anthropic API key to enable AI chat",
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    st.divider()

    # Filters (used in Transaction tab)
    st.markdown("### 🔍 Filters")

    status_filter = st.multiselect(
        "Status",
        options=["Completed", "Failed", "In Progress", "Refunded"],
        default=[],
    )

    priority_filter = st.multiselect(
        "Priority",
        options=["Critical", "High", "Medium", "Low"],
        default=[],
    )

    stage_filter = st.multiselect(
        "NDC Flow Stage",
        options=["Shopping", "OfferPrice", "SeatAvail", "ServiceAvail", "OrderCreate"],
        default=[],
        help="Filter by the deepest NDC stage reached",
    )

    date_filter = st.selectbox(
        "Date Range",
        options=["All Time", "Today", "Last 7 Days", "Last 30 Days"],
    )

    sla_breach_only = st.checkbox("SLA Breach Only", value=False)

    st.divider()

    # Export
    st.markdown("### 📥 Export")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CSV", use_container_width=True):
            st.session_state.export_csv = True
    with col2:
        if st.button("JSON", use_container_width=True):
            st.session_state.export_json = True

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

if not st.session_state.transactions:
    st.session_state.transactions = load_transactions()

transactions = st.session_state.transactions

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------

def apply_filters(txns: list[dict]) -> list[dict]:
    filtered = txns

    if status_filter:
        filtered = [t for t in filtered if t["status"] in status_filter]

    if priority_filter:
        filtered = [t for t in filtered if t["priority"] in priority_filter]

    if stage_filter:
        # Map display labels to internal stage names
        stage_map = {
            "Shopping": "Shopping",
            "OfferPrice": "OfferPrice",
            "SeatAvail": "SeatAvail",
            "ServiceAvail": "ServiceAvail",
            "OrderCreate": "OrderCreate",
        }
        allowed = {stage_map[s] for s in stage_filter if s in stage_map}
        filtered = [t for t in filtered if t.get("ndc_flow", {}).get("deepest_stage") in allowed]

    if sla_breach_only:
        filtered = [t for t in filtered if t.get("sla_breach", False)]

    if date_filter != "All Time":
        now = datetime.now()
        cutoffs = {
            "Today": now - timedelta(days=1),
            "Last 7 Days": now - timedelta(days=7),
            "Last 30 Days": now - timedelta(days=30),
        }
        cutoff = cutoffs.get(date_filter, datetime.min)
        filtered = [
            t for t in filtered
            if datetime.fromisoformat(t["created_at"]) >= cutoff
        ]

    return filtered


filtered_transactions = apply_filters(transactions)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    "<h1 style='margin-bottom:4px;'>✈️ NDC Genie</h1>"
    "<p style='color:#6b7280;margin-top:0;'>Enterprise Airline Transaction Lifecycle Tracker</p>",
    unsafe_allow_html=True,
)

# Top KPI strip
total = len(transactions)
completed = sum(1 for t in transactions if t["status"] == "Completed")
failed = sum(1 for t in transactions if t["status"] == "Failed")
sla_breaches = sum(1 for t in transactions if t.get("sla_breach"))
success_rate = (completed / total * 100) if total else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(render_metric_card("Total Transactions", str(total), color="#2563eb"), unsafe_allow_html=True)
with c2:
    st.markdown(render_metric_card("Completed", str(completed), color="#059669"), unsafe_allow_html=True)
with c3:
    st.markdown(render_metric_card("Failed", str(failed), color="#dc2626"), unsafe_allow_html=True)
with c4:
    st.markdown(render_metric_card("SLA Breaches", str(sla_breaches), color="#d97706"), unsafe_allow_html=True)
with c5:
    st.markdown(render_metric_card("Success Rate", f"{success_rate:.1f}%", color="#7c3aed"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_chat, tab_txn, tab_analytics, tab_help = st.tabs([
    "💬 AI Chat",
    "📋 Transactions",
    "📈 Analytics",
    "❓ Help",
])


# ===========================================================================
# TAB: Transactions
# ===========================================================================

with tab_txn:
    st.markdown(
        f"### Transaction Browser "
        f"<span style='font-size:14px;color:#6b7280;font-weight:400;'>"
        f"({len(filtered_transactions)} of {total})</span>",
        unsafe_allow_html=True,
    )

    # Search box
    search_query = st.text_input(
        "🔍 Search by Transaction ID, Customer, Email, Order ID, Offer ID...",
        placeholder="e.g. TXN-202501, john.smith, OFP-, ORD-",
    )

    if search_query:
        q = search_query.lower()
        def _txn_matches(t: dict) -> bool:
            # Search in standard fields
            if q in t["transaction_id"].lower():
                return True
            c = t.get("customer", {})
            if q in c.get("email", "").lower():
                return True
            if q in (c.get("first_name", "") + " " + c.get("last_name", "")).lower():
                return True
            # Search in NDC IDs
            ndc = t.get("ndc_flow", {})
            if q in ndc.get("order_id", "").lower():
                return True
            if q in ndc.get("priced_offer_id", "").lower():
                return True
            if any(q in oid.lower() for oid in ndc.get("shopping_offer_ids", [])):
                return True
            if any(q in oid.lower() for oid in ndc.get("seat_offer_ids", [])):
                return True
            if any(q in oid.lower() for oid in ndc.get("service_offer_ids", [])):
                return True
            return False

        filtered_transactions = [t for t in filtered_transactions if _txn_matches(t)]
        st.caption(f"Search matched {len(filtered_transactions)} transactions")

    # Pagination
    PAGE_SIZE = 15
    total_pages = max(1, (len(filtered_transactions) + PAGE_SIZE - 1) // PAGE_SIZE)
    if "txn_page" not in st.session_state:
        st.session_state.txn_page = 1
    st.session_state.txn_page = min(st.session_state.txn_page, total_pages)

    col_prev, col_info, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("← Prev", disabled=st.session_state.txn_page <= 1):
            st.session_state.txn_page -= 1
    with col_info:
        st.caption(f"Page {st.session_state.txn_page} of {total_pages}")
    with col_next:
        if st.button("Next →", disabled=st.session_state.txn_page >= total_pages):
            st.session_state.txn_page += 1

    start = (st.session_state.txn_page - 1) * PAGE_SIZE
    page_txns = filtered_transactions[start: start + PAGE_SIZE]

    # ---------------------------------------------------------------------------
    # Transaction list
    # ---------------------------------------------------------------------------
    for txn in page_txns:
        customer = txn.get("customer", {})
        flight = txn.get("flight", {})
        pricing = txn.get("pricing", {})
        ndc = txn.get("ndc_flow", {})
        lifecycle = txn.get("lifecycle", {})

        cust_name = f"{customer.get('first_name','')} {customer.get('last_name','')}".strip()
        route = f"{flight.get('origin','?')} → {flight.get('destination','?')}"
        deepest = ndc.get("deepest_stage", "Shopping")
        order_id = ndc.get("order_id", "")

        # Expander header line
        header_col1, header_col2, header_col3 = (
            txn["transaction_id"],
            f"{cust_name} · {route}",
            f"${pricing.get('total',0):,.2f}",
        )

        sla_icon = " 🚨" if txn.get("sla_breach") else ""
        expander_label = (
            f"{txn['transaction_id']}{sla_icon}  |  "
            f"{cust_name}  |  "
            f"{route}  |  "
            f"Stage: {deepest}  |  "
            f"${pricing.get('total',0):,.2f}"
        )

        with st.expander(expander_label, expanded=False):
            # ---- Row 1: badges + summary ----
            col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 2])
            with col_a:
                st.markdown(
                    f"**Status:** {get_status_badge(txn['status'])}<br>"
                    f"**Priority:** {get_priority_badge(txn['priority'])}",
                    unsafe_allow_html=True,
                )
            with col_b:
                st.markdown(
                    f"**Customer:** {cust_name}<br>"
                    f"**Email:** {customer.get('email','—')}<br>"
                    f"**Loyalty:** {customer.get('loyalty_tier','—')}",
                    unsafe_allow_html=True,
                )
            with col_c:
                st.markdown(
                    f"**Flight:** {flight.get('flight_number','—')}<br>"
                    f"**Route:** {route}<br>"
                    f"**Cabin:** {flight.get('cabin_class','—')} · {flight.get('passengers',1)} pax",
                    unsafe_allow_html=True,
                )
            with col_d:
                st.markdown(
                    f"**Total:** ${pricing.get('total',0):,.2f}<br>"
                    f"**Base:** ${pricing.get('base_fare',0):,.2f}<br>"
                    f"**Payment:** {pricing.get('payment_method','—')}",
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # ---- Row 2: NDC Flow pipeline visual ----
            st.markdown("**NDC Flow Pipeline**")
            st.markdown(render_lifecycle_visual(lifecycle), unsafe_allow_html=True)

            # ---- Row 3: NDC ID Chain (the new section) ----
            st.markdown(render_ndc_id_chain(ndc, lifecycle), unsafe_allow_html=True)

            # ---- Row 4: Error / Refund info ----
            err = txn.get("error_info")
            ref = txn.get("refund_info")
            if err or ref:
                col_e, col_f = st.columns(2)
                if err:
                    with col_e:
                        st.error(
                            f"**{err['error_code']}** @ {err['error_stage']}\n\n"
                            f"{err['error_message']}\n\n"
                            f"💡 {err['suggested_resolution']}"
                        )
                if ref:
                    with col_f:
                        st.info(
                            f"**Refund:** {ref.get('refund_id','—')}\n\n"
                            f"Amount: **${ref.get('refund_amount',0):,.2f}**\n\n"
                            f"Status: {ref.get('refund_status','—')}  |  Reason: {ref.get('refund_reason','—')}"
                        )

            # ---- Raw JSON toggle ----
            with st.expander("🔧 Raw Transaction JSON"):
                st.json(txn)

    # Export
    if getattr(st.session_state, "export_csv", False):
        rows = []
        for t in filtered_transactions:
            ndc = t.get("ndc_flow", {})
            c = t.get("customer", {})
            f = t.get("flight", {})
            p = t.get("pricing", {})
            rows.append({
                "transaction_id": t["transaction_id"],
                "status": t["status"],
                "priority": t["priority"],
                "sla_breach": t.get("sla_breach"),
                "ndc_deepest_stage": ndc.get("deepest_stage"),
                "shopping_offer_count": ndc.get("shopping_offer_count"),
                "selected_shopping_offer_id": ndc.get("selected_shopping_offer_id", ""),
                "priced_offer_id": ndc.get("priced_offer_id", ""),
                "seat_offer_ids": "|".join(ndc.get("seat_offer_ids", [])),
                "service_offer_ids": "|".join(ndc.get("service_offer_ids", [])),
                "order_id": ndc.get("order_id", ""),
                "customer_name": f"{c.get('first_name','')} {c.get('last_name','')}",
                "customer_email": c.get("email"),
                "route": f"{f.get('origin')} → {f.get('destination')}",
                "total": p.get("total"),
                "created_at": t["created_at"],
            })
        df = pd.DataFrame(rows)
        st.download_button(
            "⬇️ Download CSV",
            data=df.to_csv(index=False),
            file_name="ndc_transactions.csv",
            mime="text/csv",
        )
        st.session_state.export_csv = False

    if getattr(st.session_state, "export_json", False):
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(filtered_transactions, indent=2),
            file_name="ndc_transactions.json",
            mime="application/json",
        )
        st.session_state.export_json = False


# ===========================================================================
# TAB: AI Chat
# ===========================================================================

with tab_chat:
    st.markdown("### 💬 AI Transaction Assistant")

    if not st.session_state.api_key:
        st.warning("⚠️ Enter your Anthropic API key in the sidebar to enable AI chat.")
    else:
        # Chat history display
        for msg in st.session_state.chat_history:
            role = msg["role"]
            with st.chat_message(role):
                st.markdown(msg["content"])

        # Input
        user_input = st.chat_input("Ask about transactions, failures, offer IDs, orders...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        assistant = ClaudeAssistant(api_key=st.session_state.api_key)
                        response = assistant.get_response(
                            messages=st.session_state.chat_history,
                            transactions=transactions[:50],  # send sample for context
                        )
                        st.markdown(response)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": response}
                        )
                    except Exception as e:
                        err_msg = f"Error: {str(e)}"
                        st.error(err_msg)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": err_msg}
                        )

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()


# ===========================================================================
# TAB: Analytics
# ===========================================================================

with tab_analytics:
    st.markdown("### 📈 Analytics Dashboard")

    df_all = pd.DataFrame([
        {
            "status": t["status"],
            "priority": t["priority"],
            "deepest_stage": t.get("ndc_flow", {}).get("deepest_stage", "Shopping"),
            "sla_breach": t.get("sla_breach", False),
            "total": t.get("pricing", {}).get("total", 0),
            "has_order": bool(t.get("ndc_flow", {}).get("order_id")),
        }
        for t in transactions
    ])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Status Distribution**")
        status_counts = df_all["status"].value_counts()
        st.bar_chart(status_counts)

    with col2:
        st.markdown("**NDC Stage Distribution**")
        stage_counts = df_all["deepest_stage"].value_counts()
        st.bar_chart(stage_counts)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Priority Distribution**")
        priority_counts = df_all["priority"].value_counts()
        st.bar_chart(priority_counts)

    with col4:
        st.markdown("**Key Stats**")
        order_rate = df_all["has_order"].mean() * 100
        avg_value = df_all["total"].mean()
        sla_rate = df_all["sla_breach"].mean() * 100
        st.markdown(f"""
        - Order Conversion Rate: **{order_rate:.1f}%**
        - Average Transaction Value: **${avg_value:,.2f}**
        - SLA Breach Rate: **{sla_rate:.1f}%**
        - Total Transactions: **{len(df_all)}**
        """)


# ===========================================================================
# TAB: Help
# ===========================================================================

with tab_help:
    st.markdown("### ❓ Help & Documentation")

    st.markdown("""
    #### NDC Short-Sell Flow

    NDC Genie tracks the full NDC short-sell message chain:

    | Stage | Message | IDs Returned | IDs Required |
    |---|---|---|---|
    | 1 | **Shopping** | 1–200 `shopping_offer_ids` | — |
    | 2 | **OfferPrice** | 1 `priced_offer_id` | `shopping_offer_id` |
    | 3 | **SeatAvailability** | N `seat_offer_ids` | `transaction_id` |
    | 4 | **ServiceAvailability** | N `service_offer_ids` | `transaction_id` |
    | 5 | **OrderCreate** | `order_id`, `pnr`, `e_ticket` | `priced_offer_id` + `seat_offer_ids` + `service_offer_ids` |

    Each transaction in the **Transactions tab** shows:
    - The deepest stage reached
    - All offer IDs returned/used at each stage
    - Which IDs were passed from one stage to the next

    #### Searching by ID
    Use the search box to find transactions by:
    - `TXN-` prefix → transaction ID
    - `OFP-` prefix → priced offer ID
    - `ORD-` prefix → order ID
    - `SHP-` prefix → shopping offer ID
    - `SAV-` prefix → seat offer ID
    - `SVC-` prefix → service offer ID
    """)