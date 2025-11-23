"""
Security Module
Handles credential management, access control, and audit logging
"""

from .secrets_manager import CredentialProvider, IBMSecretsManagerClient
from .audit_logger import AuditLogger, AuditEventType, audit_log
from .rbac import AccessControl, require_permission, UserRole, Permission

__all__ = [
    'CredentialProvider',
    'IBMSecretsManagerClient',
    'AuditLogger',
    'AuditEventType',
    'audit_log',
    'AccessControl',
    'require_permission',
    'UserRole',
    'Permission'
]
