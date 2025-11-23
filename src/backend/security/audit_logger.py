"""
Centralized Audit Logging
Tracks all sensitive operations and compliance events
For compliance with SOC 2, GDPR, and audit requirements
"""

import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from functools import wraps
import os

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of auditable events"""
    # Vendor Operations
    VENDOR_CREATED = "vendor_created"
    VENDOR_VALIDATED = "vendor_validated"
    VENDOR_UPDATED = "vendor_updated"
    VENDOR_DELETED = "vendor_deleted"
    
    # PO Operations
    PO_CREATED = "po_created"
    PO_APPROVED = "po_approved"
    PO_REJECTED = "po_rejected"
    PO_DELETED = "po_deleted"
    
    # Budget Operations
    BUDGET_CHECKED = "budget_checked"
    BUDGET_EXCEEDED = "budget_exceeded"
    
    # Compliance Operations
    POLICY_VIOLATION = "policy_violation"
    POLICY_OVERRIDE = "policy_override"
    
    # Security Operations
    CREDENTIAL_ACCESSED = "credential_accessed"
    PERMISSION_CHANGED = "permission_changed"
    
    # User Operations
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    
    # Data Operations
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    
    # System Operations
    SYSTEM_ERROR = "system_error"
    CONFIGURATION_CHANGED = "configuration_changed"


class AuditLogger:
    """
    Centralized audit logging for compliance
    All critical operations are logged here for compliance audits
    """
    
    def __init__(self):
        """Initialize audit logger with separate file handler"""
        # Create audit logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Create file handler for audit logs
        handler = logging.FileHandler("logs/audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        resource_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        sensitive: bool = False
    ):
        """
        Log an audit event
        
        Args:
            event_type: Type of event (from AuditEventType enum)
            user_id: User performing action
            resource_id: Resource affected
            action: Action performed (e.g., 'create', 'approve', 'delete')
            details: Additional context data
            sensitive: Whether this involves sensitive/PII data
        """
        
        event_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type.value,
            "user_id": user_id,
            "resource_id": resource_id,
            "action": action,
            "ip_address": self._get_request_ip(),
            "sensitive_operation": sensitive,
        }
        
        # Handle sensitive data
        if sensitive and details:
            # Hash sensitive details for audit trail
            event_data["details_hash"] = self._hash_sensitive_data(details)
            event_data["details"] = "***REDACTED_FOR_PRIVACY***"
            logger.info(
                f"AUDIT: {event_type.value} by {user_id} on {resource_id} "
                f"(hash: {event_data['details_hash']})"
            )
        else:
            event_data["details"] = details or {}
            logger.info(json.dumps(event_data))
        
        # Write to audit log
        self.logger.info(json.dumps(event_data))
    
    def log_policy_violation(
        self,
        policy_name: str,
        violation_type: str,
        user_id: str,
        resource_id: str,
        details: Dict[str, Any]
    ):
        """
        Log security or compliance policy violations
        
        Args:
            policy_name: Name of the policy violated
            violation_type: Type of violation
            user_id: User who triggered violation
            resource_id: Resource involved
            details: Violation details
        """
        self.log_event(
            event_type=AuditEventType.POLICY_VIOLATION,
            user_id=user_id,
            resource_id=resource_id,
            action=f"{policy_name}:{violation_type}",
            details=details,
            sensitive=True
        )
    
    def log_credential_access(
        self,
        credential_type: str,
        user_id: str,
        action: str
    ):
        """
        Log whenever credentials are accessed
        Critical for security compliance
        
        Args:
            credential_type: Type of credential (api-key, password, etc.)
            user_id: User accessing the credential
            action: Action performed (retrieve, rotate, delete)
        """
        self.log_event(
            event_type=AuditEventType.CREDENTIAL_ACCESSED,
            user_id=user_id,
            resource_id=credential_type,
            action=action,
            sensitive=True
        )
    
    def log_data_export(
        self,
        user_id: str,
        data_type: str,
        record_count: int,
        export_format: str
    ):
        """Log when data is exported from the system"""
        self.log_event(
            event_type=AuditEventType.DATA_EXPORTED,
            user_id=user_id,
            resource_id=data_type,
            action="export",
            details={
                "record_count": record_count,
                "format": export_format,
                "timestamp": datetime.utcnow().isoformat()
            },
            sensitive=True
        )
    
    def log_permission_change(
        self,
        user_id: str,
        target_user: str,
        old_role: str,
        new_role: str
    ):
        """Log when user permissions are changed"""
        self.log_event(
            event_type=AuditEventType.PERMISSION_CHANGED,
            user_id=user_id,
            resource_id=target_user,
            action="permission_update",
            details={
                "old_role": old_role,
                "new_role": new_role
            }
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        user_id: str = "system",
        context: Optional[Dict[str, Any]] = None
    ):
        """Log system errors for debugging"""
        self.log_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            user_id=user_id,
            resource_id=error_type,
            action="error",
            details={
                "error_message": error_message,
                "context": context
            }
        )
    
    @staticmethod
    def _get_request_ip() -> str:
        """Get IP address from request context"""
        try:
            from flask import request
            return request.remote_addr if hasattr(request, 'remote_addr') else "unknown"
        except RuntimeError:
            # Outside request context
            return "background_task"
    
    @staticmethod
    def _hash_sensitive_data(data: Dict[str, Any]) -> str:
        """Hash sensitive data for audit trail"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()


def audit_log(event_type: AuditEventType, user_param: str = "user_id"):
    """
    Decorator to automatically audit function calls
    Automatically logs function execution with user and resource context
    
    Usage:
        @audit_log(AuditEventType.PO_CREATED)
        def create_purchase_order(user_id, po_data):
            # Function implementation
            return po
    
    Args:
        event_type: Type of audit event
        user_param: Name of parameter containing user_id (default: 'user_id')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            audit_logger = AuditLogger()
            
            # Extract user_id from kwargs or default to 'system'
            user_id = kwargs.get(user_param, "system")
            resource_id = kwargs.get("resource_id", "unknown")
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log successful execution
                audit_logger.log_event(
                    event_type=event_type,
                    user_id=str(user_id),
                    resource_id=str(resource_id),
                    action="success",
                    details={"function": func.__name__}
                )
                
                return result
                
            except Exception as e:
                # Log failed execution
                audit_logger.log_error(
                    error_type=func.__name__,
                    error_message=str(e),
                    user_id=str(user_id),
                    context={"resource_id": resource_id}
                )
                raise
        
        return wrapper
    return decorator


# Global audit logger instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance (singleton)"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
