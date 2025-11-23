# Implementation Integration Guide

## Overview

This guide provides step-by-step instructions to integrate all new gap-filling components into your existing codebase.

**Status:** All components created and ready for integration  
**Date:** November 23, 2025  
**Priority Level:** HIGH - Required for hackathon submission

---

## 📁 New Files Created

### Security Layer (`src/backend/security/`)

1. **`__init__.py`** - Security module exports
   - Exposes all security components
   - Single import point

2. **`secrets_manager.py`** - IBM Secrets Manager Integration
   - `IBMSecretsManagerClient` - Connect to Secrets Manager
   - `CredentialProvider` - Centralized credential access
   - Functions: `get_credential_provider()`
   - Features: Mock mode for development, fallback to env vars

3. **`audit_logger.py`** - Centralized Audit Logging
   - `AuditLogger` - Logs compliance events
   - `AuditEventType` - Event type enumeration (16 types)
   - `@audit_log` - Decorator for auto-logging functions
   - Function: `get_audit_logger()`
   - Logs to: `logs/audit.log`

4. **`rbac.py`** - Role-Based Access Control
   - `UserRole` - 7 roles (Admin, PM, PS, VM, FM, CO, Viewer)
   - `Permission` - 17 granular permissions
   - `AccessControl` - Permission validation
   - `@require_permission` - Decorator for enforcing permissions
   - `PermissionDeniedError` - Exception for denied access

### Integration Layer

5. **`watsonx_orchestrate_client.py`** - watsonx Orchestrate SDK
   - `WatsonxOrchestrationClient` - Main client
   - `ExecutionMode` - Sync/Async modes
   - `WorkflowStatus` - Status enumeration
   - Methods:
     - `execute_agent_workflow()` - Run workflows
     - `get_workflow_status()` - Check status
     - `invoke_skill()` - Call digital skills
     - `route_to_agent()` - Multi-agent handoff
     - `list_agents()` - List available agents
   - Function: `get_watsonx_client()`
   - Features: Mock mode for testing

6. **`agent_communication.py`** - Inter-Agent Communication
   - `AgentMessage` - Formal message contract
   - `AgentResponse` - Response contract
   - `MessageType` - Message types (6 types)
   - `MessagePriority` - Priority levels
   - `AgentCommunicationBus` - Communication hub
   - Methods:
     - `send_message()` - Send message
     - `send_sync_request()` - Synchronous call
     - `send_async_request()` - Asynchronous call with callback
     - `handle_response()` - Process response
     - `handoff_to_agent()` - Task handoff
     - `escalate_to_human()` - Escalate to human
   - Function: `get_communication_bus()`

7. **`session_manager.py`** - Session State Management
   - `SessionState` - User session state
   - `SessionManager` - Central session manager
   - Methods:
     - `create_session()` - Start new session
     - `get_session()` - Retrieve session
     - `end_session()` - End session
     - `cleanup_expired_sessions()` - Cleanup expired
     - `get_statistics()` - Session statistics
   - Function: `get_session_manager()`
   - Features: Auto-cleanup, archiving for audit

### Skill Framework

8. **`skill_base.py`** - Base Skill Class
   - `BaseSkill` - Abstract base class for all skills
   - `SkillInput` - Input contract
   - `SkillOutput` - Output contract
   - `SkillStatus` - Status enumeration
   - `SkillRegistry` - Skill registration and execution
   - Methods: `validate_input()`, `_execute_logic()`, `execute()`
   - Function: `get_skill_registry()`

### Updated Existing Files

9. **`orchestrate/skills/validate_vendor.py`** - Updated to use base class
   - `ValidateVendorSkill` - New class-based implementation
   - `validate_vendor()` - Legacy wrapper for compatibility
   - Formal input/output contracts
   - Audit logging integration

---

## 🔌 Integration Steps

### Step 1: Environment Configuration

Create/update `.env` file with required credentials:

```bash
# IBM Secrets Manager (for production)
IBM_API_KEY=your_ibm_api_key
SECRETS_MANAGER_URL=https://[instance-id].us-south.secrets-manager.appdomain.cloud
WATSONX_ACCOUNT_ID=your_account_id
USE_MOCK_SECRETS=true  # Set to false for production

# watsonx Integration
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_BASE_URL=https://api.watsonxdata.cloud.ibm.com/v2
USE_MOCK_WATSONX=true  # Set to false for production

# Database (fallback if Cloudant unavailable)
CLOUDANT_USERNAME=your_username
CLOUDANT_PASSWORD=your_password
CLOUDANT_URL=https://your-instance.cloudant.com
```

### Step 2: Update Backend Server

Update `src/backend/server.py` to initialize all components:

```python
from security import CredentialProvider, AccessControl, get_audit_logger
from session_manager import get_session_manager
from agent_communication import get_communication_bus
from watsonx_orchestrate_client import get_watsonx_client
from skill_base import get_skill_registry

# Initialize on startup
cred_provider = CredentialProvider()
audit_logger = get_audit_logger()
session_mgr = get_session_manager()
comm_bus = get_communication_bus()
watsonx_client = get_watsonx_client()
skill_registry = get_skill_registry()

logger.info("All components initialized successfully")
```

### Step 3: Update Skills

Update all existing skills in `orchestrate/skills/` to use `BaseSkill`:

**For each skill file (validate_vendor.py, check_budget.py, etc.):**

```python
# Add imports
from backend.skill_base import BaseSkill, SkillOutput, SkillStatus
from backend.security.audit_logger import get_audit_logger

# Convert function to class
class MySkill(BaseSkill):
    def __init__(self):
        super().__init__("my_skill_name")
        self.audit_logger = get_audit_logger()
    
    def validate_input(self, input_data):
        # Validate input
        return True
    
    def _execute_logic(self, input_data):
        # Implement skill logic
        return {"result": "success"}

# Keep legacy wrapper for compatibility
def my_skill(input_data):
    skill = MySkill()
    output = skill.execute(input_data)
    return output.dict()
```

### Step 4: Add Security to Routes

Update Flask/Streamlit routes to enforce permissions:

```python
from security.rbac import require_permission, Permission, UserRole

# For Flask routes
@app.route('/api/po/create', methods=['POST'])
@require_permission(Permission.PO_CREATE)
def create_po():
    user_role = request.headers.get("X-User-Role", "viewer")
    # Create PO logic
    pass

# For Streamlit pages
if session_state.user_role in [UserRole.ADMIN, UserRole.PROCUREMENT_MANAGER]:
    st.button("Create PO", on_click=create_po)
else:
    st.warning("You don't have permission to create purchase orders")
```

### Step 5: Add Audit Logging to Critical Functions

Use the `@audit_log` decorator:

```python
from security.audit_logger import audit_log, AuditEventType

@audit_log(AuditEventType.PO_CREATED)
def create_purchase_order(user_id, po_data):
    # Implementation
    pass

@audit_log(AuditEventType.VENDOR_VALIDATED)
def validate_vendor(user_id, vendor_data):
    # Implementation
    pass
```

### Step 6: Initialize Session Management

In your chat/conversation handler:

```python
from session_manager import get_session_manager

session_mgr = get_session_manager()

# Create session for new user
session = session_mgr.create_session(
    user_id="user123",
    metadata={"workflow_type": "purchase_order"}
)

# Add messages to conversation
session.add_message(
    agent="requisition_agent",
    role="assistant",
    content="Please provide PO details"
)

# Store context
session.set_context("po_id", "po-2025-001")
session.set_current_agent("requisition_agent")

# Later: get session
session = session_mgr.get_session(session_id)
if session:
    history = session.get_conversation_history()
```

### Step 7: Agent-to-Agent Communication

Use the communication bus:

```python
from agent_communication import get_communication_bus

comm_bus = get_communication_bus()

# Synchronous request
response = comm_bus.send_sync_request(
    from_agent="vendor_agent",
    to_agent="compliance_agent",
    subject="Validate vendor compliance",
    payload={"vendor_id": "v-123"},
    timeout_seconds=30
)

# Asynchronous request with callback
def on_validation_complete(response):
    if response.status == "success":
        print(f"Validation passed: {response.result}")

comm_bus.send_async_request(
    from_agent="vendor_agent",
    to_agent="compliance_agent",
    subject="Validate vendor compliance",
    payload={"vendor_id": "v-123"},
    callback_function=on_validation_complete
)

# Escalate to human
escalation_id = comm_bus.escalate_to_human(
    from_agent="approval_agent",
    escalation_type="approval_request",
    context={"po_id": "po-2025-001"},
    reason="PO amount exceeds budget threshold"
)
```

### Step 8: watsonx Workflow Execution

Use the watsonx client:

```python
from watsonx_orchestrate_client import get_watsonx_client

watsonx = get_watsonx_client()

# Execute workflow
result = watsonx.execute_agent_workflow(
    agent_id="vendor_agent",
    workflow_id="supplier_onboarding_workflow",
    input_data={
        "vendor_name": "TechSupply Corp",
        "tax_id": "98-7654321"
    },
    execution_mode="sync"
)

if result["status"] == "success":
    print(f"Workflow result: {result['output']}")
else:
    print(f"Workflow failed: {result['error_message']}")

# Check workflow status
status = watsonx.get_workflow_status(
    agent_id="vendor_agent",
    execution_id=result["execution_id"]
)
```

---

## 📋 Integration Checklist

- [ ] Create `.env` file with all credentials
- [ ] Install any new dependencies (if needed: `pydantic`, `requests`)
- [ ] Copy all new files to correct directories
- [ ] Update `src/backend/server.py` with component initialization
- [ ] Update all skills to inherit from `BaseSkill`
- [ ] Add `@audit_log` decorator to critical functions
- [ ] Add `@require_permission` decorator to sensitive operations
- [ ] Update chat handler to use `SessionManager`
- [ ] Update agent orchestrator to use `AgentCommunicationBus`
- [ ] Update watsonx integration points to use `WatsonxOrchestrationClient`
- [ ] Test each component in isolation
- [ ] Run integrated system test
- [ ] Verify audit logs are being written
- [ ] Check permissions are enforced correctly

---

## 🧪 Testing Each Component

### Test Security

```python
# Test credentials
from security.secrets_manager import get_credential_provider
cred = get_credential_provider()
api_key = cred.get_watsonx_api_key()
assert api_key is not None

# Test RBAC
from security.rbac import AccessControl, Permission, UserRole
can_create = AccessControl.has_permission(
    UserRole.PROCUREMENT_MANAGER, 
    Permission.PO_CREATE
)
assert can_create == True

# Test audit logging
from security.audit_logger import get_audit_logger, AuditEventType
audit = get_audit_logger()
audit.log_event(
    AuditEventType.PO_CREATED,
    "user123",
    "po-001",
    "create"
)
```

### Test Session Management

```python
from session_manager import get_session_manager
session_mgr = get_session_manager()

# Create session
session = session_mgr.create_session("user123")
assert session is not None

# Add message
session.add_message("agent1", "assistant", "Hello")

# Retrieve session
retrieved = session_mgr.get_session(session.session_id)
assert len(retrieved.messages) == 1

# Cleanup
session_mgr.end_session(session.session_id)
```

### Test Agent Communication

```python
from agent_communication import get_communication_bus

comm_bus = get_communication_bus()

# Send sync request
response = comm_bus.send_sync_request(
    from_agent="test_agent1",
    to_agent="test_agent2",
    subject="Test message",
    payload={"test": True},
    timeout_seconds=5
)

# Simulate response
from agent_communication import AgentResponse
test_response = AgentResponse(
    in_reply_to=response.message_id,
    from_agent="test_agent2",
    to_agent="test_agent1",
    status="success",
    result={"success": True}
)
comm_bus.handle_response(test_response)
```

---

## 🔍 Verification

After integration, verify:

1. **Audit logs created:** `logs/audit.log` exists and has entries
2. **Security enforced:** Routes return 403 for unauthorized users
3. **Sessions active:** Can create/retrieve sessions without errors
4. **Agent communication:** Messages route between agents correctly
5. **watsonx integration:** Can execute workflows and skills
6. **Skill execution:** Skills execute with formal contracts

---

## 📞 Support

For integration questions or issues:

1. Check the specific component documentation in `/docs/`
2. Review code comments and docstrings
3. Check test files for usage examples
4. Refer to the 4 main architecture documents:
   - `watsonx-integration-architecture.md`
   - `skills-inventory.md`
   - `security-implementation.md`
   - `agent-communication-patterns.md`

---

**Status:** Ready for integration  
**Last Updated:** November 23, 2025
