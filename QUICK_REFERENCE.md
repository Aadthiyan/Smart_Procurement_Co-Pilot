# Quick Reference Card - All Components

## 🔐 Security Components

### Credential Management
```python
from security.secrets_manager import get_credential_provider

cred = get_credential_provider()
api_key = cred.get_watsonx_api_key()
db_creds = cred.get_cloudant_credentials()
```

### Audit Logging
```python
from security.audit_logger import get_audit_logger, AuditEventType

audit = get_audit_logger()
audit.log_event(AuditEventType.PO_CREATED, "user123", "po-001", "create")
```

### Role-Based Access Control
```python
from security.rbac import AccessControl, Permission, UserRole

# Check permission
if AccessControl.has_permission(UserRole.ADMIN, Permission.PO_APPROVE):
    # Allow action
    pass

# Use decorator
@require_permission(Permission.PO_CREATE)
def create_po():
    pass
```

---

## 🤖 Agent & Orchestration Components

### Agent Communication
```python
from agent_communication import get_communication_bus

bus = get_communication_bus()

# Sync request (wait for response)
response = bus.send_sync_request(
    from_agent="vendor_agent",
    to_agent="compliance_agent",
    subject="Check compliance",
    payload={"vendor_id": "v-123"},
    timeout_seconds=30
)

# Async request (callback when done)
bus.send_async_request(
    from_agent="vendor_agent",
    to_agent="compliance_agent",
    subject="Check compliance",
    payload={"vendor_id": "v-123"},
    callback_function=on_complete
)

# Escalate to human
escalation_id = bus.escalate_to_human(
    from_agent="approval_agent",
    escalation_type="approval_request",
    context={"po_id": "po-001"},
    reason="Exceeds budget"
)
```

### Session Management
```python
from session_manager import get_session_manager

mgr = get_session_manager()

# Create session
session = mgr.create_session("user123", metadata={"workflow": "po"})

# Add messages
session.add_message("agent1", "assistant", "What PO details?")
session.add_message("user", "user", "Need $50k for supplies")

# Store context
session.set_context("po_amount", 50000)
session.set_current_agent("requisition_agent")

# Get session
session = mgr.get_session(session_id)
history = session.get_conversation_history()
context = session.get_full_context()

# End session
mgr.end_session(session_id)

# Get stats
stats = mgr.get_statistics()
```

### watsonx Integration
```python
from watsonx_orchestrate_client import get_watsonx_client

wx = get_watsonx_client()

# Execute workflow
result = wx.execute_agent_workflow(
    agent_id="vendor_agent",
    workflow_id="supplier_onboarding",
    input_data={"vendor_name": "Acme", "tax_id": "123"}
)

# Get status
status = wx.get_workflow_status(
    agent_id="vendor_agent",
    execution_id=result["execution_id"]
)

# Invoke skill
skill_result = wx.invoke_skill(
    skill_name="validate_vendor",
    skill_input={"vendor_id": "v-123"}
)

# Agent handoff
handoff = wx.route_to_agent(
    target_agent="compliance_agent",
    context={"vendor_id": "v-123"}
)

# List agents
agents = wx.list_agents()
```

---

## 🛠️ Skill Components

### Base Skill Class
```python
from skill_base import BaseSkill, SkillOutput, SkillStatus

class MySkill(BaseSkill):
    def __init__(self):
        super().__init__("my_skill")
    
    def validate_input(self, input_data):
        return "required_field" in input_data
    
    def _execute_logic(self, input_data):
        return {"result": "success", "value": 42}

# Execute skill
skill = MySkill()
output = skill.execute({"required_field": "data"})

if output.status == "success":
    print(output.result)
else:
    print(f"Error: {output.error_message}")
```

### Skill Registry
```python
from skill_base import get_skill_registry

registry = get_skill_registry()

# Register skill
registry.register(MySkill())

# Execute by name
output = registry.execute_skill("my_skill", {"required_field": "data"})

# List skills
skills = registry.list_skills()
```

---

## 📊 File Structure

```
src/backend/
├── security/
│   ├── __init__.py
│   ├── secrets_manager.py      # Credential management
│   ├── audit_logger.py          # Audit logging
│   └── rbac.py                  # Access control
│
├── watsonx_orchestrate_client.py  # watsonx SDK
├── agent_communication.py         # Inter-agent messaging
├── session_manager.py             # Session state
├── skill_base.py                  # Skill base class
├── db_utils.py                    # (existing)
├── server.py                      # (update needed)
└── ...

orchestrate/skills/
├── validate_vendor.py            # (updated with BaseSkill)
├── check_budget.py               # (update needed)
├── search_catalog.py             # (update needed)
└── ...
```

---

## 🔄 Integration Checklist

- [ ] Copy all new files to project
- [ ] Update .env with credentials
- [ ] Update server.py to initialize components
- [ ] Add @audit_log to critical functions
- [ ] Add @require_permission to sensitive routes
- [ ] Update all skills to inherit from BaseSkill
- [ ] Update chat handler to use SessionManager
- [ ] Test each component
- [ ] Deploy

---

## 📚 Documentation Files

- `GAP_RESOLUTION_SUMMARY.md` - What was fixed
- `INTEGRATION_GUIDE.md` - How to integrate
- `docs/watsonx-integration-architecture.md` - Architecture details
- `docs/skills-inventory.md` - Skill specifications
- `docs/security-implementation.md` - Security details
- `docs/agent-communication-patterns.md` - Communication patterns

---

## 🚀 Key Points

1. **All credentials** go through `CredentialProvider` - never hardcode
2. **All actions** logged through `AuditLogger` - compliance ready
3. **All access** checked through `AccessControl` - permissions enforced
4. **All agents** communicate via `CommunicationBus` - formal protocol
5. **All sessions** managed by `SessionManager` - persistent state
6. **All skills** inherit from `BaseSkill` - formal contracts
7. **watsonx** accessed via `WatsonxOrchestrationClient` - single client
8. **Skills** registered in `SkillRegistry` - dynamic execution

---

## ⚡ Common Operations

### Create new skill
```python
# 1. Create class inheriting from BaseSkill
class MyNewSkill(BaseSkill):
    def validate_input(self, data):
        return True
    def _execute_logic(self, data):
        return {"result": "ok"}

# 2. Register it
registry = get_skill_registry()
registry.register(MyNewSkill())

# 3. Execute it
result = registry.execute_skill("my_new_skill", {})
```

### Log user action
```python
# Use decorator
@audit_log(AuditEventType.PO_CREATED)
def create_po(user_id, po_data):
    pass

# Or manual
audit.log_event(AuditEventType.PO_CREATED, "user123", "po-001", "create")
```

### Handle agent communication
```python
# Get bus
bus = get_communication_bus()

# Send message
response = bus.send_sync_request(
    from_agent="a1", to_agent="a2",
    subject="Test", payload={"test": True}
)

# Handle result
if response.status == "success":
    print(response.result)
```

### Create user session
```python
# Create session
mgr = get_session_manager()
session = mgr.create_session("user123")

# Use throughout conversation
session.add_message("agent", "assistant", "Hello")
session.set_context("po_id", "po-001")

# End when done
mgr.end_session(session.session_id)
```

---

**Ready to use! Start integrating.** 🚀
