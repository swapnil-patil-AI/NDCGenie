"""
RBAC UI Components for NDC Genie
Login screens, user management interface, and access control UI elements.

Version: 1.0.0
"""

import streamlit as st
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any

from utils.rbac import (
    AuthenticationManager, get_auth_manager,
    Role, Permission, ROLE_PERMISSIONS,
    User, Session, AuditLogEntry,
    PasswordManager
)


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_login_page() -> bool:
    """
    Render the login page.
    Returns True if user is authenticated.
    """
    auth = get_auth_manager()
    
    # Check if already authenticated
    if auth.is_authenticated():
        return True
    
    # Custom CSS for login page
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .login-header {
        text-align: center;
        margin-bottom: 10px;
        padding-top: 20px;
    }
    
    .login-title {
        font-size: 26px;
        font-weight: 700;
        color: #1a365d;
        margin: 15px 0 5px 0;
    }
    
    .login-subtitle {
        font-size: 13px;
        color: #718096;
        margin: 0;
    }
    
    .demo-box {
        background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
        border: 1px solid #9ae6b4;
        border-radius: 10px;
        padding: 14px 18px;
        margin-top: 15px;
    }
    
    .demo-box-title {
        color: #276749;
        font-weight: 600;
        font-size: 12px;
        margin-bottom: 8px;
    }
    
    .demo-table {
        width: 100%;
        font-size: 11px;
    }
    
    .demo-table td {
        padding: 4px 0;
        color: #4a5568;
    }
    
    .demo-table td:first-child {
        font-weight: 600;
        color: #2d3748;
        width: 65px;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1.5px solid #e2e8f0 !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4299e1 !important;
        box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.15) !important;
    }
    
    .stTextInput > label {
        font-size: 13px !important;
        color: #4a5568 !important;
    }
    
    .stButton > button {
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%) !important;
        border: none !important;
    }
    
    [data-testid="stForm"] {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Professional Corporate Logo
    logo_svg = '''<svg width="65" height="65" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#1a365d"/><stop offset="50%" style="stop-color:#2b6cb0"/><stop offset="100%" style="stop-color:#4299e1"/></linearGradient><linearGradient id="lg2" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#ed8936"/><stop offset="100%" style="stop-color:#f6ad55"/></linearGradient></defs><circle cx="50" cy="50" r="48" fill="url(#lg1)"/><circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/><g transform="translate(50, 50) rotate(-30)"><ellipse cx="0" cy="0" rx="28" ry="6" fill="white"/><ellipse cx="22" cy="0" rx="8" ry="5" fill="rgba(255,255,255,0.9)"/><path d="M -5 0 L -15 -18 L 5 -18 L 10 0 Z" fill="url(#lg2)"/><path d="M -5 0 L -15 18 L 5 18 L 10 0 Z" fill="url(#lg2)"/><path d="M -25 0 L -32 -10 L -22 -10 L -20 0 Z" fill="url(#lg2)"/><circle cx="10" cy="0" r="2" fill="#1a365d"/><circle cx="3" cy="0" r="1.5" fill="#1a365d"/><circle cx="-3" cy="0" r="1.5" fill="#1a365d"/></g><ellipse cx="50" cy="50" rx="44" ry="15" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" transform="rotate(-20, 50, 50)"/><circle cx="25" cy="38" r="3" fill="#48bb78"/><circle cx="75" cy="62" r="3" fill="#ed8936"/></svg>'''
    logo_b64 = base64.b64encode(logo_svg.encode()).decode()
    
    st.markdown(f"""
    <div class="login-header">
        <img src="data:image/svg+xml;base64,{logo_b64}" width="65" height="65" alt="NDC Genie">
        <h1 class="login-title">NDC Genie</h1>
        <p class="login-subtitle">Enterprise Transaction Tracker</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the form using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            btn1, btn2 = st.columns(2)
            with btn1:
                submit = st.form_submit_button("🔐 Sign In", use_container_width=True, type="primary")
            with btn2:
                st.form_submit_button("Forgot?", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                success, message = auth.login(username, password)
                
                if success:
                    if message == "LOGIN_SUCCESS_CHANGE_PASSWORD":
                        st.warning("⚠️ You must change your password")
                        st.session_state.show_password_change = True
                    else:
                        st.success("✅ " + message)
                    st.rerun()
                else:
                    st.error("❌ " + message)
        
        # Demo credentials
        st.markdown("""
        <div class="demo-box">
            <div class="demo-box-title">🔑 Demo Credentials</div>
            <table class="demo-table">
                <tr><td>Admin:</td><td>admin / Admin@123</td></tr>
                <tr><td>Manager:</td><td>manager / Manager@123</td></tr>
                <tr><td>Agent:</td><td>agent / Agent@123</td></tr>
                <tr><td>Viewer:</td><td>viewer / Viewer@123</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    return False


def render_password_change_dialog():
    """Render forced password change dialog"""
    auth = get_auth_manager()
    user = auth.get_current_user()
    
    if not user or not user.must_change_password:
        return
    
    st.warning("⚠️ You must change your password before continuing")
    
    with st.form("password_change_form"):
        st.subheader("🔐 Change Password")
        
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Change Password", type="primary"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = auth.change_password(
                    user.user_id, current_password, new_password
                )
                if success:
                    st.success("✅ " + message)
                    st.session_state.show_password_change = False
                    st.rerun()
                else:
                    st.error("❌ " + message)


def render_user_menu():
    """Render user menu in sidebar"""
    auth = get_auth_manager()
    user = auth.get_current_user()
    
    if not user:
        return
    
    with st.sidebar:
        st.markdown("---")
        
        # User info
        role_colors = {
            "super_admin": "#e53e3e",
            "admin": "#805ad5",
            "manager": "#3182ce",
            "senior_agent": "#38a169",
            "agent": "#718096",
            "viewer": "#a0aec0"
        }
        
        role_color = role_colors.get(user.role, "#718096")
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                ">👤</div>
                <div>
                    <div style="color: white; font-weight: 600; font-size: 14px;">
                        {user.get_display_name()}
                    </div>
                    <div style="
                        color: {role_color};
                        background: white;
                        padding: 2px 8px;
                        border-radius: 10px;
                        font-size: 10px;
                        font-weight: 600;
                        display: inline-block;
                        margin-top: 3px;
                    ">{user.role.upper().replace('_', ' ')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        session = auth.get_current_session()
        if session:
            st.caption(f"🕐 Session expires: {session.expires_at[:16]}")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            auth.logout()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# USER MANAGEMENT COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_user_management():
    """Render user management interface"""
    auth = get_auth_manager()
    current_user = auth.get_current_user()
    
    # Check permissions
    if not auth.has_permission(Permission.VIEW_USERS.value):
        st.error("🚫 You don't have permission to view users")
        return
    
    st.title("👥 User Management")
    
    # Tabs
    tabs = st.tabs(["📋 All Users", "➕ Create User", "📊 Audit Log", "🔐 My Profile"])
    
    # ─────────────────────────────────────────────────────────────────────────
    # ALL USERS TAB
    # ─────────────────────────────────────────────────────────────────────────
    
    with tabs[0]:
        users = auth.get_all_users()
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            role_filter = st.selectbox(
                "Filter by Role",
                ["All"] + [r.value for r in Role],
                key="user_role_filter"
            )
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Active", "Inactive", "Locked"],
                key="user_status_filter"
            )
        with col3:
            search = st.text_input("🔍 Search", placeholder="Username or email")
        
        # Apply filters
        filtered_users = users
        
        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u.role == role_filter]
        
        if status_filter == "Active":
            filtered_users = [u for u in filtered_users if u.is_active and not u.is_locked]
        elif status_filter == "Inactive":
            filtered_users = [u for u in filtered_users if not u.is_active]
        elif status_filter == "Locked":
            filtered_users = [u for u in filtered_users if u.is_locked]
        
        if search:
            search_lower = search.lower()
            filtered_users = [
                u for u in filtered_users
                if search_lower in u.username.lower() or search_lower in u.email.lower()
            ]
        
        # Display users
        st.markdown(f"**{len(filtered_users)}** users found")
        
        for user in filtered_users:
            with st.expander(f"👤 {user.username} - {user.get_display_name()}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Email:** {user.email}")
                    st.write(f"**Department:** {user.department or 'N/A'}")
                    st.write(f"**Role:** {user.role}")
                    st.write(f"**Created:** {user.created_at[:10]}")
                    st.write(f"**Last Login:** {user.last_login[:16] if user.last_login else 'Never'}")
                
                with col2:
                    # Status badges
                    if user.is_locked:
                        st.error("🔒 Locked")
                    elif not user.is_active:
                        st.warning("⚠️ Inactive")
                    else:
                        st.success("✅ Active")
                    
                    # Actions (if user has permissions)
                    if auth.has_permission(Permission.EDIT_USERS.value) and auth.can_manage_user(user):
                        st.markdown("---")
                        
                        if user.is_locked:
                            if st.button("🔓 Unlock", key=f"unlock_{user.user_id}"):
                                success, msg = auth.unlock_user(user.user_id, current_user.user_id)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        
                        if st.button("🔑 Reset Password", key=f"reset_{user.user_id}"):
                            success, msg, temp_pwd = auth.reset_password(user.user_id, current_user.user_id)
                            if success:
                                st.success(f"{msg}\nTemporary password: `{temp_pwd}`")
                            else:
                                st.error(msg)
                        
                        if user.is_active:
                            if st.button("🗑️ Deactivate", key=f"deactivate_{user.user_id}"):
                                success, msg = auth.delete_user(user.user_id, current_user.user_id)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
    
    # ─────────────────────────────────────────────────────────────────────────
    # CREATE USER TAB
    # ─────────────────────────────────────────────────────────────────────────
    
    with tabs[1]:
        if not auth.has_permission(Permission.CREATE_USERS.value):
            st.warning("🚫 You don't have permission to create users")
        else:
            st.subheader("Create New User")
            
            with st.form("create_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("Username*", placeholder="johndoe")
                    new_email = st.text_input("Email*", placeholder="john@company.com")
                    new_password = st.text_input("Password*", type="password")
                    
                with col2:
                    new_first_name = st.text_input("First Name*", placeholder="John")
                    new_last_name = st.text_input("Last Name*", placeholder="Doe")
                    new_department = st.text_input("Department", placeholder="Customer Service")
                
                # Role selection (can only assign roles lower than own)
                current_level = Role.get_level(current_user.role)
                available_roles = [
                    r.value for r in Role
                    if Role.get_level(r.value) < current_level
                ]
                
                new_role = st.selectbox("Role*", available_roles)
                
                must_change = st.checkbox("Require password change on first login", value=True)
                
                if st.form_submit_button("➕ Create User", type="primary"):
                    if not all([new_username, new_email, new_password, new_first_name, new_last_name]):
                        st.error("Please fill in all required fields")
                    else:
                        success, message, user = auth.create_user(
                            username=new_username,
                            email=new_email,
                            password=new_password,
                            role=new_role,
                            first_name=new_first_name,
                            last_name=new_last_name,
                            department=new_department,
                            created_by=current_user.user_id,
                            must_change_password=must_change
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
            
            # Password requirements
            st.info("""
            **Password Requirements:**
            - Minimum 8 characters
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one digit
            - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
            """)
    
    # ─────────────────────────────────────────────────────────────────────────
    # AUDIT LOG TAB
    # ─────────────────────────────────────────────────────────────────────────
    
    with tabs[2]:
        if not auth.has_permission(Permission.VIEW_AUDIT_LOG.value):
            st.warning("🚫 You don't have permission to view audit logs")
        else:
            st.subheader("📊 Audit Log")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                action_filter = st.selectbox(
                    "Action",
                    ["All", "LOGIN", "LOGOUT", "CREATE_USER", "UPDATE_USER", 
                     "DELETE_USER", "CHANGE_PASSWORD", "RESET_PASSWORD", "ACCOUNT_LOCKED"]
                )
            with col2:
                user_filter = st.selectbox(
                    "User",
                    ["All"] + [u.username for u in users]
                )
            with col3:
                limit = st.number_input("Limit", min_value=10, max_value=500, value=100)
            
            # Get logs
            logs = auth.get_audit_log(
                user_id=next((u.user_id for u in users if u.username == user_filter), None) if user_filter != "All" else None,
                action=action_filter if action_filter != "All" else None,
                limit=limit
            )
            
            # Display logs
            for log in logs:
                status_icon = "✅" if log.status == "success" else "❌" if log.status == "failure" else "🚫"
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 2, 2, 3])
                    col1.write(status_icon)
                    col2.write(f"**{log.action}**")
                    col3.write(f"👤 {log.username}")
                    col4.write(f"🕐 {log.timestamp[:19]}")
                    
                    if log.details:
                        with st.expander("Details"):
                            st.json(log.details)
    
    # ─────────────────────────────────────────────────────────────────────────
    # MY PROFILE TAB
    # ─────────────────────────────────────────────────────────────────────────
    
    with tabs[3]:
        st.subheader("👤 My Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Username:** {current_user.username}  
            **Email:** {current_user.email}  
            **Name:** {current_user.get_display_name()}  
            **Department:** {current_user.department or 'N/A'}  
            **Role:** {current_user.role}  
            **Created:** {current_user.created_at[:10]}  
            **Last Login:** {current_user.last_login[:16] if current_user.last_login else 'N/A'}
            """)
        
        with col2:
            # Permissions list
            st.markdown("**Your Permissions:**")
            permissions = auth.get_user_permissions(current_user)
            for perm in sorted(permissions):
                st.write(f"✅ {perm}")
        
        # Change password
        st.markdown("---")
        st.subheader("🔐 Change Password")
        
        with st.form("change_password_form"):
            current_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔄 Update Password"):
                if new_pwd != confirm_pwd:
                    st.error("Passwords do not match")
                else:
                    success, message = auth.change_password(
                        current_user.user_id, current_pwd, new_pwd
                    )
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")


# ═══════════════════════════════════════════════════════════════════════════════
# ACCESS CONTROL UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def check_page_access(required_permission: str) -> bool:
    """
    Check if current user can access a page.
    Shows error message if not.
    Returns True if access granted.
    """
    auth = get_auth_manager()
    
    if not auth.is_authenticated():
        st.error("🔒 Please log in to access this page")
        return False
    
    if not auth.has_permission(required_permission):
        st.error(f"🚫 Access denied. You need '{required_permission}' permission.")
        return False
    
    return True


def render_access_denied():
    """Render access denied page"""
    st.markdown("""
    <div style="
        text-align: center;
        padding: 60px 20px;
    ">
        <div style="font-size: 80px; margin-bottom: 20px;">🚫</div>
        <h1 style="color: #c53030; margin-bottom: 10px;">Access Denied</h1>
        <p style="color: #718096; font-size: 18px;">
            You don't have permission to access this resource.
        </p>
        <p style="color: #a0aec0; font-size: 14px;">
            Please contact your administrator if you believe this is an error.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_permission_badge(permission: str, has_it: bool) -> str:
    """Render a permission badge"""
    if has_it:
        return f'<span style="background:#c6f6d5;color:#276749;padding:2px 8px;border-radius:10px;font-size:12px;">✅ {permission}</span>'
    else:
        return f'<span style="background:#fed7d7;color:#c53030;padding:2px 8px;border-radius:10px;font-size:12px;">❌ {permission}</span>'


def render_role_badge(role: str) -> str:
    """Render a role badge with appropriate styling"""
    colors = {
        "super_admin": ("#fff5f5", "#c53030"),
        "admin": ("#faf5ff", "#6b46c1"),
        "manager": ("#ebf8ff", "#2b6cb0"),
        "senior_agent": ("#f0fff4", "#276749"),
        "agent": ("#f7fafc", "#4a5568"),
        "viewer": ("#f7fafc", "#a0aec0"),
    }
    
    bg, text = colors.get(role, ("#f7fafc", "#718096"))
    display = role.upper().replace('_', ' ')
    
    return f'<span style="background:{bg};color:{text};padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600;">{display}</span>'


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AUTHENTICATION WRAPPER
# ═══════════════════════════════════════════════════════════════════════════════

def require_authentication() -> Optional[User]:
    """
    Main authentication check.
    Call at the start of your app.
    Returns the current user if authenticated, shows login page otherwise.
    """
    auth = get_auth_manager()
    
    # Check if user needs to change password
    if st.session_state.get('show_password_change'):
        render_password_change_dialog()
        return None
    
    # Show login page if not authenticated
    if not render_login_page():
        return None
    
    # Render user menu
    render_user_menu()
    
    return auth.get_current_user()
