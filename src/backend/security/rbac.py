"""
Role-Based Access Control (RBAC)
Defines roles, permissions, and enforces access control
"""

from enum import Enum
from typing import Dict, Set, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """Defined roles in the procurement system"""
    ADMIN = "admin"  # Full system access
    PROCUREMENT_MANAGER = "procurement_manager"  # Can create/approve POs
    PROCUREMENT_SPECIALIST = "procurement_specialist"  # Can create requests
    VENDOR_MANAGER = "vendor_manager"  # Can onboard/manage vendors
    FINANCE_MANAGER = "finance_manager"  # Can approve budget
    COMPLIANCE_OFFICER = "compliance_officer"  # Can validate policies
    VIEWER = "viewer"  # Read-only access


class Permission(str, Enum):
    """Granular permissions in the system"""
    # Vendor Permissions
    VENDOR_CREATE = "vendor:create"
    VENDOR_READ = "vendor:read"
    VENDOR_UPDATE = "vendor:update"
    VENDOR_DELETE = "vendor:delete"
    VENDOR_VALIDATE = "vendor:validate"
    
    # PO Permissions
    PO_CREATE = "po:create"
    PO_READ = "po:read"
    PO_APPROVE = "po:approve"
    PO_REJECT = "po:reject"
    PO_DELETE = "po:delete"
    
    # Budget Permissions
    BUDGET_VIEW = "budget:view"
    BUDGET_MODIFY = "budget:modify"
    
    # Policy Permissions
    POLICY_VIEW = "policy:view"
    POLICY_ENFORCE = "policy:enforce"
    POLICY_OVERRIDE = "policy:override"
    
    # System Permissions
    AUDIT_VIEW = "audit:view"
    SETTINGS_MODIFY = "settings:modify"
    USER_MANAGE = "user:manage"


# Define role-to-permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        # All permissions for admin
        Permission.VENDOR_CREATE, Permission.VENDOR_READ,
        Permission.VENDOR_UPDATE, Permission.VENDOR_DELETE,
        Permission.VENDOR_VALIDATE, Permission.PO_CREATE,
        Permission.PO_READ, Permission.PO_APPROVE,
        Permission.PO_REJECT, Permission.PO_DELETE,
        Permission.BUDGET_VIEW, Permission.BUDGET_MODIFY,
        Permission.POLICY_VIEW, Permission.POLICY_ENFORCE,
        Permission.POLICY_OVERRIDE, Permission.AUDIT_VIEW,
        Permission.SETTINGS_MODIFY, Permission.USER_MANAGE
    },
    
    UserRole.PROCUREMENT_MANAGER: {
        # Can manage procurement operations
        Permission.VENDOR_READ, Permission.VENDOR_VALIDATE,
        Permission.PO_CREATE, Permission.PO_READ,
        Permission.PO_APPROVE, Permission.PO_REJECT,
        Permission.BUDGET_VIEW, Permission.POLICY_VIEW,
        Permission.AUDIT_VIEW
    },
    
    UserRole.PROCUREMENT_SPECIALIST: {
        # Can create and track requests
        Permission.VENDOR_READ, Permission.PO_CREATE,
        Permission.PO_READ, Permission.BUDGET_VIEW,
        Permission.POLICY_VIEW
    },
    
    UserRole.VENDOR_MANAGER: {
        # Can manage vendor onboarding
        Permission.VENDOR_CREATE, Permission.VENDOR_READ,
        Permission.VENDOR_UPDATE, Permission.VENDOR_VALIDATE,
        Permission.POLICY_VIEW
    },
    
    UserRole.FINANCE_MANAGER: {
        # Can manage budgets and approve large purchases
        Permission.BUDGET_VIEW, Permission.BUDGET_MODIFY,
        Permission.PO_READ, Permission.PO_APPROVE,
        Permission.AUDIT_VIEW
    },
    
    UserRole.COMPLIANCE_OFFICER: {
        # Can enforce policies and review compliance
        Permission.POLICY_VIEW, Permission.POLICY_ENFORCE,
        Permission.PO_READ, Permission.VENDOR_READ,
        Permission.VENDOR_VALIDATE, Permission.AUDIT_VIEW
    },
    
    UserRole.VIEWER: {
        # Read-only access across the board
        Permission.VENDOR_READ, Permission.PO_READ,
        Permission.BUDGET_VIEW, Permission.POLICY_VIEW
    }
}


class AccessControl:
    """Access control enforcement and validation"""
    
    @staticmethod
    def has_permission(user_role: UserRole, required_permission: Permission) -> bool:
        """
        Check if user role has required permission
        
        Args:
            user_role: Role of the user
            required_permission: Permission being checked
        
        Returns:
            True if user has permission, False otherwise
        """
        user_permissions = ROLE_PERMISSIONS.get(user_role, set())
        return required_permission in user_permissions
    
    @staticmethod
    def check_access(
        user_role: UserRole, 
        resource_type: str, 
        action: str
    ) -> bool:
        """
        Check if user can access a resource with given action
        
        Args:
            user_role: User's role
            resource_type: Type of resource (vendor, po, budget, etc.)
            action: Action to perform (create, read, update, delete, approve)
        
        Returns:
            True if access granted, False otherwise
        
        Example:
            can_create_po = AccessControl.check_access(
                UserRole.PROCUREMENT_MANAGER, 'po', 'create'
            )
        """
        permission_string = f"{resource_type}:{action}"
        try:
            permission = Permission(permission_string)
            return AccessControl.has_permission(user_role, permission)
        except ValueError:
            logger.warning(f"Unknown permission: {permission_string}")
            return False
    
    @staticmethod
    def get_user_permissions(user_role: UserRole) -> Set[Permission]:
        """Get all permissions for a role"""
        return ROLE_PERMISSIONS.get(user_role, set())
    
    @staticmethod
    def list_all_roles() -> Dict[str, Set[str]]:
        """List all roles and their permissions"""
        return {
            role.value: {perm.value for perm in perms}
            for role, perms in ROLE_PERMISSIONS.items()
        }


def require_permission(required_permission: Permission):
    """
    Decorator to enforce permission checks on functions
    
    Usage:
        @require_permission(Permission.PO_CREATE)
        def create_purchase_order(user_id, po_data):
            # Implementation
            pass
    
    Args:
        required_permission: Permission required to execute function
    
    Raises:
        PermissionDeniedError: If user doesn't have required permission
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get user role from kwargs (should be passed by caller)
            user_role_str = kwargs.get("user_role", None)
            
            if not user_role_str:
                logger.error("user_role not provided in function call")
                raise PermissionDeniedError("Missing user role in request")
            
            try:
                user_role = UserRole(user_role_str)
            except ValueError:
                logger.error(f"Invalid user role: {user_role_str}")
                raise PermissionDeniedError(f"Invalid user role: {user_role_str}")
            
            # Check permission
            if not AccessControl.has_permission(user_role, required_permission):
                logger.warning(
                    f"Access denied: {user_role} attempted {required_permission}"
                )
                raise PermissionDeniedError(
                    f"User role '{user_role}' is not authorized for "
                    f"permission '{required_permission.value}'"
                )
            
            # Permission granted, execute function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class PermissionDeniedError(Exception):
    """Raised when user lacks required permission"""
    pass


def get_role_from_request(request_headers: Dict[str, str]) -> Optional[UserRole]:
    """
    Extract user role from request headers
    
    Args:
        request_headers: HTTP request headers
    
    Returns:
        UserRole if found, None otherwise
    """
    role_str = request_headers.get("X-User-Role", None)
    if role_str:
        try:
            return UserRole(role_str)
        except ValueError:
            logger.warning(f"Invalid role in header: {role_str}")
    return None
