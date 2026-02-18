"""
RBAC Integration Example for NDC Genie
Shows how to integrate the RBAC system with the main application.

This file demonstrates the authentication and authorization flow.
"""

import streamlit as st

# Import RBAC components
from utils.rbac import (
    get_auth_manager, 
    Permission, 
    Role,
    require_auth,
    require_permission,
    require_role
)
from components.rbac_ui import (
    require_authentication,
    render_user_management,
    check_page_access,
    render_access_denied,
    render_role_badge
)


def main():
    """
    Main application with RBAC integration example.
    """
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: REQUIRE AUTHENTICATION
    # ═══════════════════════════════════════════════════════════════════════
    
    # This shows the login page if user is not authenticated
    # Returns the current user object if authenticated
    user = require_authentication()
    
    if not user:
        return  # Stop here if not authenticated
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2: GET AUTH MANAGER FOR PERMISSION CHECKS
    # ═══════════════════════════════════════════════════════════════════════
    
    auth = get_auth_manager()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3: BUILD NAVIGATION BASED ON PERMISSIONS
    # ═══════════════════════════════════════════════════════════════════════
    
    st.title(f"✈️ NDC Genie")
    st.markdown(f"Welcome, **{user.get_display_name()}**! {render_role_badge(user.role)}", unsafe_allow_html=True)
    
    # Build menu based on permissions
    menu_items = []
    
    # Everyone can see dashboard
    menu_items.append("🏠 Dashboard")
    
    # AI Assistant - requires USE_AI_ASSISTANT permission
    if auth.has_permission(Permission.USE_AI_ASSISTANT.value):
        menu_items.append("🤖 AI Assistant")
    
    # Transactions - requires VIEW_TRANSACTIONS permission
    if auth.has_permission(Permission.VIEW_TRANSACTIONS.value):
        menu_items.append("📋 Transactions")
    
    # Analytics - check for basic or advanced
    if auth.has_permission(Permission.VIEW_ADVANCED_ANALYTICS.value):
        menu_items.append("📊 Advanced Analytics")
    elif auth.has_permission(Permission.VIEW_BASIC_ANALYTICS.value):
        menu_items.append("📊 Basic Analytics")
    
    # Refunds - requires VIEW_REFUNDS permission
    if auth.has_permission(Permission.VIEW_REFUNDS.value):
        menu_items.append("💰 Refunds")
    
    # User Management - requires VIEW_USERS permission
    if auth.has_permission(Permission.VIEW_USERS.value):
        menu_items.append("👥 User Management")
    
    # Settings - requires MANAGE_SETTINGS permission
    if auth.has_permission(Permission.MANAGE_SETTINGS.value):
        menu_items.append("⚙️ Settings")
    
    # Navigation
    selected = st.sidebar.selectbox("Navigation", menu_items)
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 4: RENDER PAGES WITH PERMISSION CHECKS
    # ═══════════════════════════════════════════════════════════════════════
    
    if selected == "🏠 Dashboard":
        render_dashboard(auth, user)
    
    elif selected == "🤖 AI Assistant":
        if check_page_access(Permission.USE_AI_ASSISTANT.value):
            render_ai_assistant_demo()
    
    elif selected == "📋 Transactions":
        if check_page_access(Permission.VIEW_TRANSACTIONS.value):
            render_transactions_demo(auth)
    
    elif selected in ["📊 Advanced Analytics", "📊 Basic Analytics"]:
        render_analytics_demo(auth)
    
    elif selected == "💰 Refunds":
        if check_page_access(Permission.VIEW_REFUNDS.value):
            render_refunds_demo(auth)
    
    elif selected == "👥 User Management":
        render_user_management()
    
    elif selected == "⚙️ Settings":
        if check_page_access(Permission.MANAGE_SETTINGS.value):
            render_settings_demo()


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════════════════════

def render_dashboard(auth, user):
    """Render dashboard with role-specific content"""
    st.header("🏠 Dashboard")
    
    # Show different content based on role
    if auth.has_role_or_higher(Role.MANAGER.value):
        st.info("📊 **Manager View**: You can see team performance metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Transactions", "1,234", "+12%")
        col2.metric("Success Rate", "94.5%", "+2.1%")
        col3.metric("Pending Refunds", "23", "-5")
        col4.metric("SLA Breaches", "3", "-2")
    
    elif auth.has_role(Role.AGENT.value):
        st.info("📋 **Agent View**: Your assigned transactions")
        st.write("You have **5** transactions assigned to you today")
    
    else:
        st.info("👁️ **Viewer Mode**: Read-only access")
    
    # Quick actions based on permissions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if auth.has_permission(Permission.CREATE_ESCALATION.value):
            if st.button("🚨 Create Escalation", use_container_width=True):
                st.success("Escalation created!")
        else:
            st.button("🚨 Create Escalation", use_container_width=True, disabled=True)
            st.caption("Permission required")
    
    with col2:
        if auth.has_permission(Permission.EXPORT_TRANSACTIONS.value):
            if st.button("📤 Export Data", use_container_width=True):
                st.success("Export started!")
        else:
            st.button("📤 Export Data", use_container_width=True, disabled=True)
            st.caption("Permission required")
    
    with col3:
        if auth.has_permission(Permission.APPROVE_REFUND.value):
            if st.button("✅ Approve Refunds", use_container_width=True):
                st.success("Refund approved!")
        else:
            st.button("✅ Approve Refunds", use_container_width=True, disabled=True)
            st.caption("Permission required")


def render_ai_assistant_demo():
    """Demo AI Assistant page"""
    st.header("🤖 AI Assistant")
    st.write("Ask questions about transactions in natural language.")
    
    query = st.text_input("Ask a question", placeholder="Show me failed transactions from today")
    
    if query:
        st.info(f"You asked: {query}")
        st.write("*This is a demo - connect to the real AI assistant in production*")


def render_transactions_demo(auth):
    """Demo Transactions page with permission-based actions"""
    st.header("📋 Transactions")
    
    # Sample data
    transactions = [
        {"id": "TXN-001", "status": "Completed", "amount": "$500", "customer": "John Doe"},
        {"id": "TXN-002", "status": "Failed", "amount": "$750", "customer": "Jane Smith"},
        {"id": "TXN-003", "status": "Pending", "amount": "$300", "customer": "Bob Wilson"},
    ]
    
    for txn in transactions:
        with st.expander(f"{txn['id']} - {txn['customer']}"):
            col1, col2 = st.columns(2)
            col1.write(f"**Status:** {txn['status']}")
            col1.write(f"**Amount:** {txn['amount']}")
            
            with col2:
                # Edit button - requires permission
                if auth.has_permission(Permission.EDIT_TRANSACTIONS.value):
                    if st.button("✏️ Edit", key=f"edit_{txn['id']}"):
                        st.info("Edit mode")
                
                # Delete button - requires permission
                if auth.has_permission(Permission.DELETE_TRANSACTIONS.value):
                    if st.button("🗑️ Delete", key=f"delete_{txn['id']}"):
                        st.warning("Delete confirmation needed")
    
    # Export section
    if auth.has_permission(Permission.EXPORT_TRANSACTIONS.value):
        st.markdown("---")
        col1, col2 = st.columns(2)
        col1.download_button("📥 Download CSV", "sample,data", "transactions.csv")
        col2.download_button("📥 Download JSON", "{}", "transactions.json")


def render_analytics_demo(auth):
    """Demo Analytics page"""
    st.header("📊 Analytics")
    
    # Basic analytics - available to all who can see this page
    st.subheader("Basic Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", "1,000")
    col2.metric("Completed", "940")
    col3.metric("Failed", "60")
    
    # Advanced analytics - requires advanced permission
    if auth.has_permission(Permission.VIEW_ADVANCED_ANALYTICS.value):
        st.markdown("---")
        st.subheader("📈 Advanced Analytics")
        st.write("Detailed breakdown, trends, and predictive analysis")
        st.info("*Charts and advanced metrics would appear here*")
    else:
        st.markdown("---")
        st.warning("🔒 Advanced analytics require additional permissions")


def render_refunds_demo(auth):
    """Demo Refunds page"""
    st.header("💰 Refunds")
    
    refunds = [
        {"id": "REF-001", "amount": "$200", "status": "Pending", "customer": "Alice Brown"},
        {"id": "REF-002", "amount": "$150", "status": "Approved", "customer": "Charlie Davis"},
    ]
    
    for ref in refunds:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            col1.write(f"**{ref['id']}** - {ref['customer']}")
            col2.write(ref['amount'])
            col3.write(ref['status'])
            
            with col4:
                if ref['status'] == "Pending":
                    if auth.has_permission(Permission.APPROVE_REFUND.value):
                        if st.button("✅ Approve", key=f"approve_{ref['id']}"):
                            st.success("Approved!")
                    
                    if auth.has_permission(Permission.REJECT_REFUND.value):
                        if st.button("❌ Reject", key=f"reject_{ref['id']}"):
                            st.error("Rejected!")


def render_settings_demo():
    """Demo Settings page"""
    st.header("⚙️ Settings")
    st.write("System configuration options")
    
    st.text_input("API Endpoint", value="https://api.ndc-genie.ai")
    st.number_input("Session Timeout (hours)", value=8)
    st.checkbox("Enable Debug Mode", value=False)
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved!")


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATOR EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

@require_auth
def protected_function():
    """This function requires authentication"""
    return "You are authenticated!"


@require_permission(Permission.APPROVE_REFUND.value)
def approve_refund_function(refund_id: str):
    """This function requires APPROVE_REFUND permission"""
    return f"Refund {refund_id} approved!"


@require_role(Role.MANAGER.value)
def manager_only_function():
    """This function requires Manager role or higher"""
    return "Manager content"


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    st.set_page_config(
        page_title="NDC Genie - RBAC Demo",
        page_icon="✈️",
        layout="wide"
    )
    main()
