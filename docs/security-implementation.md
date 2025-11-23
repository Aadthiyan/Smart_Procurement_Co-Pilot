# Security Implementation Guide

## Overview

This document outlines comprehensive security practices for the Smart Procurement Co-Pilot system, including credential management, IBM Cloud integration, compliance, and operational security.

---

## 1. Credential Management

### 1.1 IBM Cloud Secrets Manager Integration

**Purpose:** Centralized, secure credential storage for all system integrations

**Setup Steps:**

```bash
# 1. Create Secrets Manager instance in IBM Cloud
ibmcloud resource service-instance-create \
  smart-procurement-secrets \
  secrets-manager \
  standard \
  us-south

# 2. Set up authentication
export IBM_CLOUD_APIKEY="your-api-key"
export SECRETS_MANAGER_INSTANCE_ID="instance-id"
export SECRETS_MANAGER_REGION="us-south"
```

### 1.2 Secret Types & Storage

**All credentials must be stored in Secrets Manager:**

```yaml
API Credentials:
  sap_vendor_api_key:
    type: api_key
    description: SAP Vendor Management API
    rotation_policy: 90_days
  
  dun_bradstreet_api_key:
    type: api_key
    description: Dun & Bradstreet Business Intelligence API
    rotation_policy: 90_days
  
  sendgrid_api_key:
    type: api_key
    description: SendGrid Email Service
    rotation_policy: 90_days
  
  twilio_auth_token:
    type: api_key
    description: Twilio SMS Service
    rotation_policy: 90_days

Database Credentials:
  cloudant_username:
    type: username_password
    description: IBM Cloudant database username
    rotation_policy: 180_days
  
  cloudant_password:
    type: username_password
    description: IBM Cloudant database password
    rotation_policy: 180_days

Service Credentials:
  watson_nlu_api_key:
    type: api_key
    description: IBM Watson NLU Service
    rotation_policy: 90_days
  
  watsonx_api_key:
    type: api_key
    description: IBM watsonx Services
    rotation_policy: 90_days

OAuth Tokens:
  oauth_refresh_token:
    type: oauth_token
    description: OAuth 2.0 refresh token
    rotation_policy: on_use
```

### 1.3 Credential Injection Pattern

**NEVER hardcode credentials. Always use Secrets Manager:**

```python
# ❌ WRONG - Never do this
API_KEY = "abc123xyz789"
DB_PASSWORD = "mypassword123"

# ✅ CORRECT - Use Secrets Manager
import ibm_secrets

class CredentialManager:
    def __init__(self):
        self.secrets_client = ibm_secrets.SecretsManagerClient(
            api_key=os.environ['IBM_CLOUD_APIKEY'],
            region=os.environ['SECRETS_MANAGER_REGION']
        )
    
    def get_credential(self, secret_name):
        """
        Retrieve credential from Secrets Manager
        
        Args:
            secret_name: Name of the secret (e.g., 'sap_vendor_api_key')
        
        Returns:
            Decrypted credential value
        
        Raises:
            SecretNotFoundError: If secret doesn't exist
        """
        try:
            secret = self.secrets_client.get_secret(
                secret_name=secret_name,
                secret_type='api_key'
            )
            return secret['resources'][0]['secret_data']['api_key']
        except Exception as e:
            logger.error(f"Failed to retrieve credential: {secret_name}")
            raise SecretRetrievalError(f"Cannot access {secret_name}") from e
    
    def get_db_credentials(self):
        """Get database connection credentials"""
        return {
            'username': self.get_credential('cloudant_username'),
            'password': self.get_credential('cloudant_password'),
            'host': os.environ['CLOUDANT_HOST']
        }

# Usage
cred_mgr = CredentialManager()
sap_api_key = cred_mgr.get_credential('sap_vendor_api_key')
```

### 1.4 Credential Rotation Policy

```yaml
Rotation Schedule:
  API Keys: Every 90 days
  Database Passwords: Every 180 days
  OAuth Tokens: On use (automatic refresh)
  Service Credentials: Every 90 days

Rotation Procedure:
  1. Create new credential in Secrets Manager
  2. Update dependent applications with new credential
  3. Test connectivity with new credential
  4. Monitor old credential usage for 24 hours
  5. Deactivate old credential
  6. Purge old credential after 30-day retention

Automation:
  - IBM Cloud Secrets Manager: Built-in rotation policies
  - Lambda/Cloud Functions: Trigger rotation events
  - Notifications: Alert ops team when rotation occurs
```

---

## 2. API Security

### 2.1 API Key Management

**Policy:**
- All API keys stored in Secrets Manager
- No API keys in code, config files, or version control
- Separate keys for development, staging, production
- Keys rotated every 90 days

**Environment-Specific Configuration:**

```yaml
Development:
  secrets_manager_instance: dev-secrets
  api_rate_limit: 100 requests/min
  log_level: DEBUG
  tls_verify: true

Staging:
  secrets_manager_instance: staging-secrets
  api_rate_limit: 500 requests/min
  log_level: INFO
  tls_verify: true

Production:
  secrets_manager_instance: prod-secrets
  api_rate_limit: 1000 requests/min
  log_level: WARNING
  tls_verify: true (mandatory)
```

### 2.2 API Request/Response Security

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SecureAPIClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key  # From Secrets Manager
        self.base_url = base_url
        self.session = self._create_secure_session()
    
    def _create_secure_session(self):
        """Create session with security best practices"""
        session = requests.Session()
        
        # SSL/TLS Configuration
        session.verify = True  # Always verify SSL certificates
        session.headers.update({
            'User-Agent': 'SmartProcurement/1.0',
            'X-API-Client': 'SmartProcurement'
        })
        
        # Retry strategy for transient failures
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def request(self, method, endpoint, **kwargs):
        """
        Make secure API request
        
        Security features:
        - API key not exposed in logs
        - TLS verification
        - Request/response encryption
        - Timeout enforcement
        """
        url = f"{self.base_url}{endpoint}"
        
        # Add authentication header
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.api_key}"
        kwargs['headers'] = headers
        
        # Enforce timeout
        timeout = kwargs.get('timeout', 30)
        
        try:
            logger.debug(f"Making {method} request to {url}")  # No sensitive data
            response = self.session.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            # Don't expose API key in error messages
            raise APIError(f"Request to {endpoint} failed") from e
```

### 2.3 API Rate Limiting & Throttling

```python
from functools import wraps
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute=100):
        self.requests_per_minute = requests_per_minute
        self.request_times = defaultdict(list)
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_id = kwargs.get('client_id', 'default')
            now = time.time()
            
            # Clean old requests (older than 60 seconds)
            self.request_times[client_id] = [
                t for t in self.request_times[client_id]
                if now - t < 60
            ]
            
            # Check rate limit
            if len(self.request_times[client_id]) >= self.requests_per_minute:
                wait_time = 60 - (now - self.request_times[client_id][0])
                raise RateLimitExceeded(f"Wait {wait_time:.1f} seconds")
            
            # Record request and proceed
            self.request_times[client_id].append(now)
            return func(*args, **kwargs)
        
        return wrapper

# Usage
rate_limiter = RateLimiter(requests_per_minute=100)

@rate_limiter
def call_external_api(client_id, endpoint):
    # Implementation
    pass
```

---

## 3. Authentication & Authorization

### 3.1 User Authentication

**Implementation:**
- IBM Cloud Identity & Access Management (IAM)
- Multi-factor authentication (MFA) required
- Session timeout: 30 minutes of inactivity

```python
class AuthenticationManager:
    def __init__(self):
        self.iam_client = ibm_cloud.IAMClient()
        self.session_manager = SessionManager()
    
    def authenticate_user(self, email, password, mfa_token):
        """
        Authenticate user with MFA
        
        Args:
            email: User email
            password: User password
            mfa_token: MFA token from authenticator app
        
        Returns:
            Session token for authenticated user
        """
        try:
            # Step 1: Verify email/password
            user = self.iam_client.authenticate(email, password)
            
            # Step 2: Verify MFA
            if not self.iam_client.verify_mfa(user.id, mfa_token):
                logger.warning(f"MFA verification failed for {email}")
                raise AuthenticationError("Invalid MFA token")
            
            # Step 3: Create session
            session_token = self.session_manager.create_session(
                user_id=user.id,
                email=email,
                timeout_minutes=30
            )
            
            logger.info(f"User authenticated: {email}")
            return session_token
        
        except Exception as e:
            logger.error(f"Authentication failed for {email}")
            raise AuthenticationError("Invalid credentials or MFA") from e
```

### 3.2 Role-Based Access Control (RBAC)

**Roles:**

```yaml
Roles:
  admin:
    permissions:
      - manage_users
      - approve_purchases
      - configure_policies
      - view_audit_logs
  
  procurement_manager:
    permissions:
      - create_purchase_orders
      - approve_requisitions (up to $50k)
      - manage_vendors
      - view_reports
  
  procurement_specialist:
    permissions:
      - create_purchase_orders
      - submit_requisitions
      - search_catalog
      - view_own_requests
  
  vendor:
    permissions:
      - update_own_profile
      - view_own_contracts
      - submit_invoices
  
  compliance_officer:
    permissions:
      - approve_vendors
      - approve_requisitions (policy review)
      - view_audit_logs
```

**Implementation:**

```python
class AuthorizationManager:
    def __init__(self):
        self.role_store = load_roles_from_db()
        self.policy_engine = PolicyEngine()
    
    def has_permission(self, user_id, action, resource_id=None):
        """
        Check if user has permission for action
        
        Args:
            user_id: User identifier
            action: Action to perform (e.g., 'approve_requisition')
            resource_id: Optional resource ID for granular control
        
        Returns:
            Boolean indicating if user has permission
        """
        user_roles = self.get_user_roles(user_id)
        
        for role in user_roles:
            if self.policy_engine.evaluate(role, action, resource_id):
                logger.debug(f"Permission granted: {user_id} -> {action}")
                return True
        
        logger.warning(f"Permission denied: {user_id} -> {action}")
        return False

# Usage
auth_mgr = AuthorizationManager()

if not auth_mgr.has_permission(user_id, 'approve_requisition'):
    raise PermissionDenied("User cannot approve requisitions")
```

---

## 4. Data Protection

### 4.1 Data Encryption

**In Transit:**
- TLS 1.2+ for all network communication
- Certificate pinning for critical APIs

```python
import ssl

# TLS Configuration
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.minimum_version = ssl.TLSVersion.TLSv1_2
SSL_CONTEXT.check_hostname = True
SSL_CONTEXT.verify_mode = ssl.CERT_REQUIRED

# Certificate pinning for critical APIs
PINNED_CERTIFICATES = {
    'sap.example.com': 'sha256/abcd1234...',
    'api.vendor.com': 'sha256/efgh5678...'
}
```

**At Rest:**
- IBM Cloudant: Encryption by default
- Local JSON database: AES-256 encryption

```python
from cryptography.fernet import Fernet
import json

class EncryptedLocalDB:
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
    
    def save_encrypted(self, data, filename):
        """Save data with encryption"""
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        
        with open(filename, 'wb') as f:
            f.write(encrypted)
    
    def load_encrypted(self, filename):
        """Load and decrypt data"""
        with open(filename, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
```

### 4.2 Sensitive Data Handling

**PII (Personally Identifiable Information):**
- Employee names, emails
- Vendor contact information
- Bank account details (last 4 digits only in logs)

**Policy:**
- Never log sensitive data
- Mask PII in error messages
- Use data classification labels

```python
import logging

class SecureLogger:
    def __init__(self, logger):
        self.logger = logger
        self.sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{16}\b',              # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
    
    def sanitize(self, message):
        """Mask sensitive data in log messages"""
        sanitized = message
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, '***REDACTED***', sanitized)
        return sanitized
    
    def info(self, message, *args, **kwargs):
        self.logger.info(self.sanitize(message), *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        self.logger.error(self.sanitize(message), *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        self.logger.debug(self.sanitize(message), *args, **kwargs)
```

---

## 5. Audit Logging & Compliance

### 5.1 Audit Trail Requirements

**All critical operations must be logged:**

```yaml
Audit Events:
  User Actions:
    - User login/logout
    - Permission changes
    - Data access
  
  Procurement Operations:
    - Purchase order creation/modification
    - Requisition approval
    - Vendor registration
    - Contract signature
    - Payment processing
  
  System Operations:
    - API key rotation
    - Configuration changes
    - Error conditions
    - Security events
  
  Data Operations:
    - Data export/download
    - Data deletion
    - Database backups
    - Encryption key rotation
```

### 5.2 Audit Log Implementation

```python
import json
from datetime import datetime
from uuid import uuid4

class AuditLogger:
    def __init__(self, cloudant_client):
        self.db = cloudant_client['audit_logs']
    
    def log_event(self, event_type, user_id, resource_type, 
                  resource_id, action, details, status):
        """
        Log an audit event
        
        Args:
            event_type: Type of event (user_action, data_access, etc.)
            user_id: User who performed action
            resource_type: Type of resource (requisition, vendor, etc.)
            resource_id: ID of resource
            action: Action performed (create, update, delete, approve)
            details: Additional details
            status: success, failure, error
        """
        
        audit_entry = {
            '_id': str(uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'details': details,
            'status': status,
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent()
        }
        
        try:
            self.db.create_document(audit_entry)
            logger.debug(f"Audit logged: {event_type} by {user_id}")
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Don't fail main operation if audit logging fails
            raise AuditLoggingError("Cannot log audit event") from e

# Usage
audit_logger = AuditLogger(cloudant_client)

audit_logger.log_event(
    event_type='procurement_operation',
    user_id='user123',
    resource_type='purchase_order',
    resource_id='po-2025-001',
    action='create',
    details={'amount': 50000, 'vendor': 'vendor123'},
    status='success'
)
```

### 5.3 Audit Log Retention

```yaml
Retention Policy:
  Active logs: 90 days (hot storage)
  Archive logs: 7 years (cold storage)
  Deletion: After retention period, securely delete
  
  Compliance:
    - SOC 2: Maintain for audit trail
    - GDPR: Respect right to be forgotten
    - HIPAA: If applicable, 6 years
    - FINRA: 6 years minimum
```

---

## 6. Vulnerability & Threat Management

### 6.1 Dependency Management

**Keep all dependencies updated:**

```bash
# Check for vulnerabilities
npm audit  # for Node.js
pip-audit  # for Python
snyk scan  # for multi-language

# Update dependencies safely
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# Lock versions
pip freeze > requirements.txt
```

### 6.2 Security Scanning

**Automated scanning in CI/CD:**

```yaml
# GitHub Actions example
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload results to GitHub Security
        uses: github/codeql-action/upload-sarif@v1
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run Bandit (Python)
        run: bandit -r . -f json -o bandit-report.json
      
      - name: Run SonarQube
        uses: SonarSource/sonarqube-scan-action@master
```

### 6.3 Incident Response Plan

```yaml
Incident Response Procedure:
  
  1. Detection & Alerting
     - Monitor for suspicious activity
     - Automated alerts for security events
     - Manual review of audit logs
  
  2. Response
     - Isolate affected systems
     - Preserve evidence
     - Notify relevant stakeholders
     - Assess impact
  
  3. Remediation
     - Apply patches/fixes
     - Rotate compromised credentials
     - Update security controls
     - Communicate with users
  
  4. Review
     - Post-incident review
     - Root cause analysis
     - Process improvements
     - Update security policies

Contact Information:
  Security Team: security@example.com
  Incident Commander: incident@example.com
  Executive Sponsor: ciso@example.com
```

---

## 7. Compliance Checklist

- [ ] All credentials in Secrets Manager
- [ ] No API keys in code or config files
- [ ] TLS 1.2+ for all communications
- [ ] MFA enabled for all users
- [ ] RBAC implemented
- [ ] Audit logging enabled
- [ ] Data encryption at rest
- [ ] Data encryption in transit
- [ ] Audit logs retained 7+ years
- [ ] Regular security scans (weekly)
- [ ] Dependency updates (monthly)
- [ ] Incident response plan documented
- [ ] Security training for team
- [ ] Annual security audit
- [ ] Compliance certifications (SOC 2, etc.)

---

## 8. Security Standards & References

**Industry Standards:**
- OWASP Top 10
- NIST Cybersecurity Framework
- ISO 27001
- SOC 2 Type II

**IBM Cloud Security:**
- IBM Cloud Security Best Practices
- IBM Secrets Manager Documentation
- IBM Cloudant Security

**Procurement-Specific:**
- CISA Supply Chain Risk Management Practices
- NIST SP 800-53 (Security Controls)

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Ready for Implementation  
**Security Classification:** Internal Only
