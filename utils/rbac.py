"""
Role-Based Access Control (RBAC) System for NDC Genie
Enterprise-grade authentication and authorization module.

Version: 1.0.0
"""

import hashlib
import secrets
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps
import streamlit as st


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS AND CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class Role(Enum):
    """User roles with hierarchical access levels"""
    SUPER_ADMIN = "super_admin"  # Full system access, can manage admins
    ADMIN = "admin"              # Full access, user management
    MANAGER = "manager"          # View all, approve refunds, escalations
    SENIOR_AGENT = "senior_agent"  # Handle escalations, view reports
    AGENT = "agent"              # Standard customer service operations
    VIEWER = "viewer"            # Read-only access
    
    @classmethod
    def get_hierarchy(cls) -> Dict[str, int]:
        """Returns role hierarchy levels (higher = more access)"""
        return {
            cls.SUPER_ADMIN.value: 100,
            cls.ADMIN.value: 90,
            cls.MANAGER.value: 70,
            cls.SENIOR_AGENT.value: 50,
            cls.AGENT.value: 30,
            cls.VIEWER.value: 10,
        }
    
    @classmethod
    def get_level(cls, role: str) -> int:
        """Get hierarchy level for a role"""
        return cls.get_hierarchy().get(role, 0)


class Permission(Enum):
    """Granular permissions for access control"""
    # Transaction permissions
    VIEW_TRANSACTIONS = "view_transactions"
    VIEW_ALL_TRANSACTIONS = "view_all_transactions"
    EDIT_TRANSACTIONS = "edit_transactions"
    DELETE_TRANSACTIONS = "delete_transactions"
    EXPORT_TRANSACTIONS = "export_transactions"
    
    # Refund permissions
    VIEW_REFUNDS = "view_refunds"
    REQUEST_REFUND = "request_refund"
    APPROVE_REFUND = "approve_refund"
    REJECT_REFUND = "reject_refund"
    
    # Escalation permissions
    VIEW_ESCALATIONS = "view_escalations"
    CREATE_ESCALATION = "create_escalation"
    RESOLVE_ESCALATION = "resolve_escalation"
    
    # AI Assistant permissions
    USE_AI_ASSISTANT = "use_ai_assistant"
    VIEW_AI_HISTORY = "view_ai_history"
    
    # Analytics permissions
    VIEW_BASIC_ANALYTICS = "view_basic_analytics"
    VIEW_ADVANCED_ANALYTICS = "view_advanced_analytics"
    EXPORT_REPORTS = "export_reports"
    
    # User management permissions
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    ASSIGN_ROLES = "assign_roles"
    
    # System permissions
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_SYSTEM_HEALTH = "view_system_health"


# Role-Permission mapping
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    Role.SUPER_ADMIN.value: {p.value for p in Permission},  # All permissions
    
    Role.ADMIN.value: {
        Permission.VIEW_TRANSACTIONS.value,
        Permission.VIEW_ALL_TRANSACTIONS.value,
        Permission.EDIT_TRANSACTIONS.value,
        Permission.DELETE_TRANSACTIONS.value,
        Permission.EXPORT_TRANSACTIONS.value,
        Permission.VIEW_REFUNDS.value,
        Permission.REQUEST_REFUND.value,
        Permission.APPROVE_REFUND.value,
        Permission.REJECT_REFUND.value,
        Permission.VIEW_ESCALATIONS.value,
        Permission.CREATE_ESCALATION.value,
        Permission.RESOLVE_ESCALATION.value,
        Permission.USE_AI_ASSISTANT.value,
        Permission.VIEW_AI_HISTORY.value,
        Permission.VIEW_BASIC_ANALYTICS.value,
        Permission.VIEW_ADVANCED_ANALYTICS.value,
        Permission.EXPORT_REPORTS.value,
        Permission.VIEW_USERS.value,
        Permission.CREATE_USERS.value,
        Permission.EDIT_USERS.value,
        Permission.DELETE_USERS.value,
        Permission.ASSIGN_ROLES.value,
        Permission.VIEW_AUDIT_LOG.value,
        Permission.MANAGE_SETTINGS.value,
        Permission.VIEW_SYSTEM_HEALTH.value,
    },
    
    Role.MANAGER.value: {
        Permission.VIEW_TRANSACTIONS.value,
        Permission.VIEW_ALL_TRANSACTIONS.value,
        Permission.EDIT_TRANSACTIONS.value,
        Permission.EXPORT_TRANSACTIONS.value,
        Permission.VIEW_REFUNDS.value,
        Permission.REQUEST_REFUND.value,
        Permission.APPROVE_REFUND.value,
        Permission.REJECT_REFUND.value,
        Permission.VIEW_ESCALATIONS.value,
        Permission.CREATE_ESCALATION.value,
        Permission.RESOLVE_ESCALATION.value,
        Permission.USE_AI_ASSISTANT.value,
        Permission.VIEW_AI_HISTORY.value,
        Permission.VIEW_BASIC_ANALYTICS.value,
        Permission.VIEW_ADVANCED_ANALYTICS.value,
        Permission.EXPORT_REPORTS.value,
        Permission.VIEW_USERS.value,
        Permission.VIEW_AUDIT_LOG.value,
    },
    
    Role.SENIOR_AGENT.value: {
        Permission.VIEW_TRANSACTIONS.value,
        Permission.VIEW_ALL_TRANSACTIONS.value,
        Permission.EDIT_TRANSACTIONS.value,
        Permission.EXPORT_TRANSACTIONS.value,
        Permission.VIEW_REFUNDS.value,
        Permission.REQUEST_REFUND.value,
        Permission.VIEW_ESCALATIONS.value,
        Permission.CREATE_ESCALATION.value,
        Permission.RESOLVE_ESCALATION.value,
        Permission.USE_AI_ASSISTANT.value,
        Permission.VIEW_AI_HISTORY.value,
        Permission.VIEW_BASIC_ANALYTICS.value,
        Permission.VIEW_ADVANCED_ANALYTICS.value,
    },
    
    Role.AGENT.value: {
        Permission.VIEW_TRANSACTIONS.value,
        Permission.EDIT_TRANSACTIONS.value,
        Permission.VIEW_REFUNDS.value,
        Permission.REQUEST_REFUND.value,
        Permission.VIEW_ESCALATIONS.value,
        Permission.CREATE_ESCALATION.value,
        Permission.USE_AI_ASSISTANT.value,
        Permission.VIEW_BASIC_ANALYTICS.value,
    },
    
    Role.VIEWER.value: {
        Permission.VIEW_TRANSACTIONS.value,
        Permission.VIEW_REFUNDS.value,
        Permission.VIEW_ESCALATIONS.value,
        Permission.VIEW_BASIC_ANALYTICS.value,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class User:
    """User account model"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: str
    first_name: str
    last_name: str
    department: str = ""
    is_active: bool = True
    is_locked: bool = False
    failed_login_attempts: int = 0
    last_login: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "system"
    password_changed_at: Optional[str] = None
    must_change_password: bool = False
    custom_permissions: List[str] = field(default_factory=list)  # Additional permissions
    denied_permissions: List[str] = field(default_factory=list)  # Explicitly denied
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes password_hash)"""
        data = asdict(self)
        del data['password_hash']
        return data
    
    def get_display_name(self) -> str:
        """Get user's display name"""
        return f"{self.first_name} {self.last_name}"


@dataclass
class Session:
    """User session model"""
    session_id: str
    user_id: str
    username: str
    role: str
    created_at: str
    expires_at: str
    ip_address: str = ""
    user_agent: str = ""
    is_active: bool = True
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AuditLogEntry:
    """Audit log entry for tracking user actions"""
    log_id: str
    timestamp: str
    user_id: str
    username: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: str = ""
    status: str = "success"  # success, failure, denied


# ═══════════════════════════════════════════════════════════════════════════════
# PASSWORD UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

class PasswordManager:
    """Secure password handling"""
    
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @classmethod
    def hash_password(cls, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash a password with a salt.
        Returns (hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2-like approach with SHA-256
        salted = f"{salt}{password}{salt}".encode('utf-8')
        
        # Multiple rounds for security
        hash_result = salted
        for _ in range(10000):
            hash_result = hashlib.sha256(hash_result).digest()
        
        final_hash = hashlib.sha256(hash_result).hexdigest()
        return f"{salt}${final_hash}", salt
    
    @classmethod
    def verify_password(cls, password: str, stored_hash: str) -> bool:
        """Verify a password against a stored hash"""
        try:
            salt, _ = stored_hash.split('$')
            computed_hash, _ = cls.hash_password(password, salt)
            return secrets.compare_digest(computed_hash, stored_hash)
        except (ValueError, AttributeError):
            return False
    
    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength.
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters")
        
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            errors.append(f"Password must contain at least one special character ({cls.SPECIAL_CHARS})")
        
        return len(errors) == 0, errors
    
    @classmethod
    def generate_temporary_password(cls) -> str:
        """Generate a secure temporary password"""
        # Ensure all requirements are met
        password = [
            secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            secrets.choice('abcdefghijklmnopqrstuvwxyz'),
            secrets.choice('0123456789'),
            secrets.choice(cls.SPECIAL_CHARS),
        ]
        # Add random characters to reach minimum length
        all_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789' + cls.SPECIAL_CHARS
        password.extend(secrets.choice(all_chars) for _ in range(cls.MIN_LENGTH))
        
        # Shuffle
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class AuthenticationManager:
    """
    Manages user authentication, sessions, and access control.
    
    In production, this would integrate with a database.
    For demo purposes, uses session state storage.
    """
    
    SESSION_DURATION_HOURS = 8
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    def __init__(self):
        """Initialize the authentication manager"""
        self._initialize_storage()
        self._create_default_users()
    
    def _initialize_storage(self):
        """Initialize session state storage"""
        if 'rbac_users' not in st.session_state:
            st.session_state.rbac_users = {}
        if 'rbac_sessions' not in st.session_state:
            st.session_state.rbac_sessions = {}
        if 'rbac_audit_log' not in st.session_state:
            st.session_state.rbac_audit_log = []
        if 'current_session' not in st.session_state:
            st.session_state.current_session = None
    
    def _create_default_users(self):
        """Create default demo users if none exist"""
        if not st.session_state.rbac_users:
            default_users = [
                {
                    "username": "admin",
                    "email": "admin@ndc-genie.ai",
                    "password": "Admin@123",
                    "role": Role.ADMIN.value,
                    "first_name": "System",
                    "last_name": "Administrator",
                    "department": "IT"
                },
                {
                    "username": "manager",
                    "email": "manager@ndc-genie.ai",
                    "password": "Manager@123",
                    "role": Role.MANAGER.value,
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "department": "Customer Service"
                },
                {
                    "username": "senior_agent",
                    "email": "senior@ndc-genie.ai",
                    "password": "Senior@123",
                    "role": Role.SENIOR_AGENT.value,
                    "first_name": "Michael",
                    "last_name": "Chen",
                    "department": "Customer Service"
                },
                {
                    "username": "agent",
                    "email": "agent@ndc-genie.ai",
                    "password": "Agent@123",
                    "role": Role.AGENT.value,
                    "first_name": "Emily",
                    "last_name": "Davis",
                    "department": "Customer Service"
                },
                {
                    "username": "viewer",
                    "email": "viewer@ndc-genie.ai",
                    "password": "Viewer@123",
                    "role": Role.VIEWER.value,
                    "first_name": "James",
                    "last_name": "Wilson",
                    "department": "Quality Assurance"
                },
            ]
            
            for user_data in default_users:
                self.create_user(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],
                    role=user_data["role"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    department=user_data["department"],
                    created_by="system"
                )
    
    # ─────────────────────────────────────────────────────────────────────────
    # USER MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str,
        first_name: str,
        last_name: str,
        department: str = "",
        created_by: str = "system",
        must_change_password: bool = False
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Create a new user.
        Returns (success, message, user)
        """
        # Validate username
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
            return False, "Username must be 3-30 alphanumeric characters or underscores", None
        
        # Check if username exists
        if username.lower() in [u.username.lower() for u in st.session_state.rbac_users.values()]:
            return False, "Username already exists", None
        
        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid email format", None
        
        # Check if email exists
        if email.lower() in [u.email.lower() for u in st.session_state.rbac_users.values()]:
            return False, "Email already registered", None
        
        # Validate password
        is_valid, errors = PasswordManager.validate_password_strength(password)
        if not is_valid:
            return False, "; ".join(errors), None
        
        # Validate role
        valid_roles = [r.value for r in Role]
        if role not in valid_roles:
            return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}", None
        
        # Create user
        user_id = f"USR-{secrets.token_hex(8).upper()}"
        password_hash, _ = PasswordManager.hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            first_name=first_name,
            last_name=last_name,
            department=department,
            created_by=created_by,
            must_change_password=must_change_password,
            password_changed_at=datetime.now().isoformat() if not must_change_password else None
        )
        
        st.session_state.rbac_users[user_id] = user
        
        # Audit log
        self._log_action(
            user_id=created_by if created_by != "system" else "SYSTEM",
            username=created_by,
            action="CREATE_USER",
            resource_type="user",
            resource_id=user_id,
            details={"username": username, "role": role}
        )
        
        return True, "User created successfully", user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return st.session_state.rbac_users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in st.session_state.rbac_users.values():
            if user.username.lower() == username.lower():
                return user
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return list(st.session_state.rbac_users.values())
    
    def update_user(
        self,
        user_id: str,
        updated_by: str,
        **kwargs
    ) -> Tuple[bool, str]:
        """Update user properties"""
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        allowed_fields = ['email', 'first_name', 'last_name', 'department', 
                         'is_active', 'role', 'custom_permissions', 'denied_permissions']
        
        changes = {}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)
                changes[field] = value
        
        user.updated_at = datetime.now().isoformat()
        
        # Audit log
        self._log_action(
            user_id=updated_by,
            username=self.get_user(updated_by).username if self.get_user(updated_by) else updated_by,
            action="UPDATE_USER",
            resource_type="user",
            resource_id=user_id,
            details=changes
        )
        
        return True, "User updated successfully"
    
    def delete_user(self, user_id: str, deleted_by: str) -> Tuple[bool, str]:
        """Delete (deactivate) a user"""
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        # Don't allow deleting yourself
        current = self.get_current_user()
        if current and current.user_id == user_id:
            return False, "Cannot delete your own account"
        
        user.is_active = False
        user.updated_at = datetime.now().isoformat()
        
        # Invalidate sessions
        for session in st.session_state.rbac_sessions.values():
            if session.user_id == user_id:
                session.is_active = False
        
        # Audit log
        self._log_action(
            user_id=deleted_by,
            username=self.get_user(deleted_by).username if self.get_user(deleted_by) else deleted_by,
            action="DELETE_USER",
            resource_type="user",
            resource_id=user_id,
            details={"username": user.username}
        )
        
        return True, "User deactivated successfully"
    
    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """Change user password"""
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        # Verify current password
        if not PasswordManager.verify_password(current_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Validate new password
        is_valid, errors = PasswordManager.validate_password_strength(new_password)
        if not is_valid:
            return False, "; ".join(errors)
        
        # Update password
        user.password_hash, _ = PasswordManager.hash_password(new_password)
        user.password_changed_at = datetime.now().isoformat()
        user.must_change_password = False
        user.updated_at = datetime.now().isoformat()
        
        # Audit log
        self._log_action(
            user_id=user_id,
            username=user.username,
            action="CHANGE_PASSWORD",
            resource_type="user",
            resource_id=user_id,
            details={}
        )
        
        return True, "Password changed successfully"
    
    def reset_password(self, user_id: str, reset_by: str) -> Tuple[bool, str, str]:
        """
        Reset user password to a temporary one.
        Returns (success, message, new_password)
        """
        user = self.get_user(user_id)
        if not user:
            return False, "User not found", ""
        
        # Generate temporary password
        temp_password = PasswordManager.generate_temporary_password()
        user.password_hash, _ = PasswordManager.hash_password(temp_password)
        user.must_change_password = True
        user.failed_login_attempts = 0
        user.is_locked = False
        user.updated_at = datetime.now().isoformat()
        
        # Audit log
        self._log_action(
            user_id=reset_by,
            username=self.get_user(reset_by).username if self.get_user(reset_by) else reset_by,
            action="RESET_PASSWORD",
            resource_type="user",
            resource_id=user_id,
            details={"username": user.username}
        )
        
        return True, "Password reset successfully", temp_password
    
    def unlock_user(self, user_id: str, unlocked_by: str) -> Tuple[bool, str]:
        """Unlock a locked user account"""
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        user.is_locked = False
        user.failed_login_attempts = 0
        user.updated_at = datetime.now().isoformat()
        
        # Audit log
        self._log_action(
            user_id=unlocked_by,
            username=self.get_user(unlocked_by).username if self.get_user(unlocked_by) else unlocked_by,
            action="UNLOCK_USER",
            resource_type="user",
            resource_id=user_id,
            details={"username": user.username}
        )
        
        return True, "User account unlocked"
    
    # ─────────────────────────────────────────────────────────────────────────
    # AUTHENTICATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def login(self, username: str, password: str, ip_address: str = "", user_agent: str = "") -> Tuple[bool, str]:
        """
        Authenticate user and create session.
        Returns (success, message)
        """
        user = self.get_user_by_username(username)
        
        if not user:
            self._log_action(
                user_id="UNKNOWN",
                username=username,
                action="LOGIN_ATTEMPT",
                resource_type="session",
                resource_id="",
                details={"reason": "user_not_found"},
                status="failure"
            )
            return False, "Invalid username or password"
        
        # Check if account is active
        if not user.is_active:
            return False, "Account is deactivated. Contact administrator."
        
        # Check if account is locked
        if user.is_locked:
            return False, "Account is locked due to too many failed attempts. Contact administrator."
        
        # Verify password
        if not PasswordManager.verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            
            # Lock account after max attempts
            if user.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
                user.is_locked = True
                self._log_action(
                    user_id=user.user_id,
                    username=user.username,
                    action="ACCOUNT_LOCKED",
                    resource_type="user",
                    resource_id=user.user_id,
                    details={"attempts": user.failed_login_attempts},
                    status="failure"
                )
                return False, "Account locked due to too many failed attempts"
            
            self._log_action(
                user_id=user.user_id,
                username=user.username,
                action="LOGIN_ATTEMPT",
                resource_type="session",
                resource_id="",
                details={"reason": "invalid_password", "attempts": user.failed_login_attempts},
                status="failure"
            )
            return False, "Invalid username or password"
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.now().isoformat()
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        now = datetime.now()
        expires_at = now + timedelta(hours=self.SESSION_DURATION_HOURS)
        
        session = Session(
            session_id=session_id,
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        st.session_state.rbac_sessions[session_id] = session
        st.session_state.current_session = session_id
        
        # Audit log
        self._log_action(
            user_id=user.user_id,
            username=user.username,
            action="LOGIN",
            resource_type="session",
            resource_id=session_id,
            details={"ip": ip_address}
        )
        
        # Check if password change required
        if user.must_change_password:
            return True, "LOGIN_SUCCESS_CHANGE_PASSWORD"
        
        return True, "Login successful"
    
    def logout(self) -> bool:
        """Logout current user"""
        session_id = st.session_state.get('current_session')
        
        if session_id and session_id in st.session_state.rbac_sessions:
            session = st.session_state.rbac_sessions[session_id]
            session.is_active = False
            
            # Audit log
            self._log_action(
                user_id=session.user_id,
                username=session.username,
                action="LOGOUT",
                resource_type="session",
                resource_id=session_id,
                details={}
            )
        
        st.session_state.current_session = None
        return True
    
    def get_current_session(self) -> Optional[Session]:
        """Get current active session"""
        session_id = st.session_state.get('current_session')
        
        if not session_id:
            return None
        
        session = st.session_state.rbac_sessions.get(session_id)
        
        if not session or not session.is_active:
            return None
        
        # Check expiration
        if datetime.fromisoformat(session.expires_at) < datetime.now():
            session.is_active = False
            st.session_state.current_session = None
            return None
        
        # Update last activity
        session.last_activity = datetime.now().isoformat()
        
        return session
    
    def get_current_user(self) -> Optional[User]:
        """Get current logged-in user"""
        session = self.get_current_session()
        if not session:
            return None
        return self.get_user(session.user_id)
    
    def is_authenticated(self) -> bool:
        """Check if current request is authenticated"""
        return self.get_current_session() is not None
    
    # ─────────────────────────────────────────────────────────────────────────
    # AUTHORIZATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """Get all permissions for a user"""
        # Start with role permissions
        role_perms = ROLE_PERMISSIONS.get(user.role, set()).copy()
        
        # Add custom permissions
        role_perms.update(user.custom_permissions)
        
        # Remove denied permissions
        role_perms -= set(user.denied_permissions)
        
        return role_perms
    
    def has_permission(self, permission: str, user: Optional[User] = None) -> bool:
        """Check if user has a specific permission"""
        if user is None:
            user = self.get_current_user()
        
        if not user:
            return False
        
        if not user.is_active:
            return False
        
        user_permissions = self.get_user_permissions(user)
        return permission in user_permissions
    
    def has_any_permission(self, permissions: List[str], user: Optional[User] = None) -> bool:
        """Check if user has any of the specified permissions"""
        if user is None:
            user = self.get_current_user()
        
        if not user:
            return False
        
        user_permissions = self.get_user_permissions(user)
        return bool(user_permissions.intersection(permissions))
    
    def has_all_permissions(self, permissions: List[str], user: Optional[User] = None) -> bool:
        """Check if user has all specified permissions"""
        if user is None:
            user = self.get_current_user()
        
        if not user:
            return False
        
        user_permissions = self.get_user_permissions(user)
        return all(p in user_permissions for p in permissions)
    
    def has_role(self, role: str, user: Optional[User] = None) -> bool:
        """Check if user has specific role"""
        if user is None:
            user = self.get_current_user()
        
        if not user:
            return False
        
        return user.role == role
    
    def has_role_or_higher(self, role: str, user: Optional[User] = None) -> bool:
        """Check if user has specified role or higher in hierarchy"""
        if user is None:
            user = self.get_current_user()
        
        if not user:
            return False
        
        required_level = Role.get_level(role)
        user_level = Role.get_level(user.role)
        
        return user_level >= required_level
    
    def can_manage_user(self, target_user: User, user: Optional[User] = None) -> bool:
        """Check if user can manage another user"""
        if user is None:
            user = self.get_current_user()
        
        if not user:
            return False
        
        # Can't manage yourself (for role changes)
        if user.user_id == target_user.user_id:
            return False
        
        # Must have higher role level
        user_level = Role.get_level(user.role)
        target_level = Role.get_level(target_user.role)
        
        return user_level > target_level
    
    # ─────────────────────────────────────────────────────────────────────────
    # AUDIT LOG
    # ─────────────────────────────────────────────────────────────────────────
    
    def _log_action(
        self,
        user_id: str,
        username: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any],
        ip_address: str = "",
        status: str = "success"
    ):
        """Log an action to the audit log"""
        entry = AuditLogEntry(
            log_id=f"LOG-{secrets.token_hex(8).upper()}",
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            status=status
        )
        st.session_state.rbac_audit_log.append(entry)
        
        # Keep only last 1000 entries
        if len(st.session_state.rbac_audit_log) > 1000:
            st.session_state.rbac_audit_log = st.session_state.rbac_audit_log[-1000:]
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """Get audit log entries with optional filters"""
        entries = st.session_state.rbac_audit_log.copy()
        
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        
        if action:
            entries = [e for e in entries if e.action == action]
        
        if resource_type:
            entries = [e for e in entries if e.resource_type == resource_type]
        
        # Sort by timestamp descending
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return entries[:limit]


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATORS AND UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = AuthenticationManager()
        if not auth.is_authenticated():
            st.error("🔒 Authentication required. Please log in.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def require_permission(permission: str) -> Callable:
    """Decorator to require specific permission"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth = AuthenticationManager()
            if not auth.is_authenticated():
                st.error("🔒 Authentication required. Please log in.")
                st.stop()
            if not auth.has_permission(permission):
                st.error(f"🚫 Access denied. Required permission: {permission}")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: str) -> Callable:
    """Decorator to require specific role or higher"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth = AuthenticationManager()
            if not auth.is_authenticated():
                st.error("🔒 Authentication required. Please log in.")
                st.stop()
            if not auth.has_role_or_higher(role):
                st.error(f"🚫 Access denied. Required role: {role} or higher")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

def get_auth_manager() -> AuthenticationManager:
    """Get the authentication manager instance"""
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthenticationManager()
    return st.session_state.auth_manager
