# watsonx Integration Architecture

## Overview

This document provides detailed technical specifications for integrating IBM watsonx services (watsonx.ai and watsonx.orchestrate) into the Smart Procurement Co-Pilot system.

---

## 1. Architecture Overview

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────┐
│           Smart Procurement CoPilot (User Facing)               │
│                  (Streamlit Frontend)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         API Gateway & Session Manager                           │
│    (Authentication, Rate Limiting, Request Routing)             │
└────────────────────────────┬────────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Chat Intent  │  │ API Router   │  │ Monitoring   │
    │ Detection    │  │              │  │ & Logging    │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │   watsonx.orchestrate              │
        │   ┌──────────────────────────────┐ │
        │   │  Orchestration Engine        │ │
        │   │  (Route, Schedule, Manage)   │ │
        │   └──────────────────────────────┘ │
        │   ┌──────────────────────────────┐ │
        │   │  Agent Lifecycle Manager     │ │
        │   └──────────────────────────────┘ │
        └────────┬─────────────────────┬─────┘
                 │                     │
        ┌────────▼──────────┐  ┌──────▼─────────┐
        │  Agent Layer      │  │ Skill Executor │
        │ (5 Agents)        │  │ & Router       │
        └────────┬──────────┘  └──────┬─────────┘
                 │                    │
        ┌────────▼──────────────────────────┐
        │     watsonx.ai (LLM Inference)    │
        │  ├─ Foundation Model (Granite)   │
        │  ├─ Prompt Management            │
        │  └─ Token Management             │
        └────────┬─────────────────────────┘
                 │
    ┌────────────┼────────────────┬──────────────┐
    │            │                │              │
    ▼            ▼                ▼              ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐
│ Skills │  │ External │  │ Business │  │ Secrets    │
│ Layer  │  │ APIs     │  │ Systems  │  │ Manager    │
└─┬──────┘  └──────────┘  └──────────┘  └────────────┘
  │
  ├─ validate_vendor_skill
  ├─ check_budget_skill
  ├─ search_catalog_skill
  ├─ policy_check_skill
  ├─ extract_contract_skill
  └─ send_notification_skill

┌──────────────────────────────────────────────────────┐
│    Data Layer                                        │
│  ├─ IBM Cloudant (Primary)                          │
│  ├─ Local JSON DB (Fallback)                        │
│  └─ Redis Cache (Session & Performance)             │
└──────────────────────────────────────────────────────┘
```

---

## 2. watsonx.orchestrate Integration

### 2.1 Agent Orchestration Framework

**Purpose:** Central orchestration of all agents, skills, and workflows

**Key Components:**

```yaml
Orchestration Layer:
  Agent Management:
    - Instantiation & Lifecycle
    - State Management
    - Context Preservation
  
  Workflow Engine:
    - DAG (Directed Acyclic Graph) Execution
    - Conditional Branching
    - Parallel Task Execution
    - Error Recovery & Fallbacks
  
  Skill Binding:
    - Dynamic Skill Registration
    - Execution Context
    - Result Mapping
  
  Integration Points:
    - IBM Cloud Services
    - External APIs
    - Message Queues (optional)
    - Event Stream (optional)
```

### 2.2 Agent Architecture

**Agent Structure:**

Each agent follows this pattern:

```json
{
  "agent_id": "vendor_agent",
  "name": "Vendor Onboarding Agent",
  "description": "Manages vendor registration and validation",
  "model": "granite-13b-chat-v2",
  "temperature": 0.7,
  "max_tokens": 2048,
  "system_prompt": "You are a procurement specialist focused on vendor evaluation...",
  
  "capabilities": [
    {
      "skill_id": "validate_vendor_skill",
      "input_schema": {...},
      "output_schema": {...}
    }
  ],
  
  "decision_rules": [
    {
      "condition": "vendor_score > 0.8",
      "action": "approve_vendor"
    }
  ],
  
  "error_handlers": [
    {
      "error_type": "validation_failure",
      "recovery_action": "request_additional_info"
    }
  ]
}
```

### 2.3 Orchestration Workflow Example

**Vendor Onboarding Flow:**

```yaml
Workflow: supplier_onboarding_workflow
Agents: [vendor_agent, compliance_agent, communication_agent]

Steps:
  1.
    agent: vendor_agent
    skill: validate_vendor_skill
    inputs:
      - vendor_data (from user)
    outputs:
      - vendor_profile
      - validation_score
    on_failure: escalate_to_human
  
  2.
    agent: compliance_agent
    condition: vendor_profile.validation_score > 0.7
    skill: policy_check_skill
    inputs:
      - vendor_profile
      - company_policies
    outputs:
      - compliance_status
      - risk_level
  
  3.
    agent: communication_agent
    condition: compliance_status == "approved"
    skill: send_notification_skill
    inputs:
      - vendor_email
      - approval_message
    outputs:
      - notification_status

  4.
    action: store_vendor
    system: SAP_ERP
    inputs:
      - vendor_profile
      - compliance_approval
```

---

## 3. watsonx.ai Integration

### 3.1 LLM Foundation Model Configuration

**Model Details:**

```yaml
Foundation Model: IBM Granite 13B Chat
Region: us-south (or your region)
Configuration:
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9
  repetition_penalty: 1.05
  
Prompt Engineering Strategy:
  - Few-shot examples for complex tasks
  - Chain-of-thought for reasoning
  - Structured output formatting
```

### 3.2 Prompt Templates

**Example: Vendor Validation Prompt**

```
System Prompt:
You are an expert procurement specialist. Your role is to evaluate vendor 
information and assess compliance with company policies. You provide structured 
output with clear reasoning.

User Prompt Template:
---
Evaluate this vendor for onboarding:

Vendor Information:
- Name: {vendor_name}
- Tax ID: {tax_id}
- Industry: {industry}
- Annual Revenue: {revenue}
- Years in Business: {years}

Company Policies:
- Minimum revenue threshold: $1M
- Preferred industries: {preferred_industries}
- Risk tolerance: {risk_tolerance}

Provide evaluation in JSON format:
{
  "compliance_score": (0-1),
  "risk_assessment": "low|medium|high",
  "recommendation": "approve|review|reject",
  "reasoning": "explain your assessment"
}
---
```

### 3.3 Token Management

**Usage Optimization:**

```python
# Token calculation strategy
Max tokens per request: 2048
Average input tokens: 400-600
Average output tokens: 400-800
Reserved tokens: 200 (safety margin)

Cost estimation (per request):
- Input: 400 tokens × $0.0035/1K = $0.0014
- Output: 600 tokens × $0.007/1K = $0.0042
- Total: ~$0.0056 per request

Optimization tactics:
1. Use caching for repeated prompts
2. Batch processing where possible
3. Summarize long documents before processing
4. Implement token budget monitoring
```

---

## 4. IBM Cloud Integration

### 4.1 Service Integration Map

```
IBM Cloud Services:
┌─────────────────────────────────────────┐
│ Watson NLU (Intent, Entity Recognition) │
│ Used in: Chat Interface, Intent Detection│
└─────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────┐
│ Secrets Manager (Credential Management) │
│ Stores: API Keys, DB Credentials        │
└─────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────┐
│ Cloud Databases (Cloudant)              │
│ Primary Data Store                      │
└─────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────┐
│ Monitoring & Logging (Log Analysis)     │
│ Agent Activity, Performance Metrics     │
└─────────────────────────────────────────┘
```

### 4.2 API Integration Patterns

**Example: SAP ERP Integration**

```python
# Skill: vendor_registration_skill
# Integrates with SAP via OData API

Class VendorRegistrationSkill:
    def __init__(self, orchestrator_context):
        self.sap_endpoint = get_secret("SAP_VENDOR_API")
        self.api_key = get_secret("SAP_API_KEY")
    
    def execute(self, vendor_profile):
        """
        Input Schema:
        {
            "vendor_name": string,
            "tax_id": string,
            "contact_info": object
        }
        
        Output Schema:
        {
            "vendor_id": string,
            "registration_status": "success|error",
            "sap_record_id": string,
            "timestamp": ISO8601
        }
        """
        try:
            # Call SAP OData API
            response = requests.post(
                f"{self.sap_endpoint}/Vendors",
                json=vendor_profile,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 201:
                return {
                    "vendor_id": response.json()["ID"],
                    "registration_status": "success",
                    "sap_record_id": response.json()["SAP_ID"]
                }
        except Exception as e:
            # Fallback: Queue for manual processing
            self.queue_for_manual_review(vendor_profile)
            return {
                "registration_status": "error",
                "fallback_action": "queued_for_review"
            }
```

---

## 5. Data Flow Diagrams

### 5.1 User Request to Agent Response Flow

```
User Input (Chat)
      │
      ▼
┌─────────────────────────────────────┐
│ Intent Detection (NLU)              │
│ Extract: intent, entities, context  │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌─────────────────┐
        │ Route to Agent  │
        │ (Orchestrate)   │
        └────────┬────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ Agent Initialization │
        │ Load context/history │
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ LLM Inference        │
        │ (watsonx.ai)         │
        │ Generate response    │
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ Skill Execution      │
        │ Call required skills │
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ Result Aggregation   │
        │ Format response      │
        └────────┬─────────────┘
                 │
                 ▼
        Response to User (Chat)
```

### 5.2 Workflow Execution Flow

```
Workflow Trigger (User/System)
      │
      ▼
Orchestrate: Parse Workflow DAG
      │
      ├─► Parallel Execution (if applicable)
      │
      ▼
Agent 1: Execute Step
    │
    ├─► LLM: Generate action
    │
    ├─► Skill A: Execute
    │
    └─► Store Result
        │
        ▼
Agent 2: Execute Step (conditional)
    │
    ├─► LLM: Evaluate previous result
    │
    ├─► Skill B: Execute
    │
    └─► Store Result
        │
        ▼
Error Handler (if needed)
    │
    ├─► Retry Strategy
    │
    ├─► Fallback Action
    │
    └─► Notify Admin
        │
        ▼
Workflow Complete
```

---

## 6. Integration Checklist

- [ ] **watsonx.orchestrate Setup**
  - [ ] Create orchestrator instance in IBM Cloud
  - [ ] Configure authentication (API keys)
  - [ ] Set up agent registry
  - [ ] Configure workflow engine

- [ ] **watsonx.ai Setup**
  - [ ] Select foundation model (Granite)
  - [ ] Configure model parameters
  - [ ] Set up prompt templates
  - [ ] Configure token management

- [ ] **IBM Cloud Services**
  - [ ] Set up Secrets Manager
  - [ ] Configure Cloudant instance
  - [ ] Enable logging & monitoring
  - [ ] Set up NLU service

- [ ] **External Integrations**
  - [ ] Document all external API endpoints
  - [ ] Set up credential injection
  - [ ] Configure retry strategies
  - [ ] Set up fallback mechanisms

- [ ] **Monitoring & Observability**
  - [ ] Configure logging
  - [ ] Set up performance metrics
  - [ ] Enable audit trails
  - [ ] Create alerting rules

---

## 7. Best Practices

1. **Agent Design**
   - Keep agents focused on specific domains
   - Use clear, descriptive system prompts
   - Implement decision rules for consistency

2. **Skill Management**
   - Define strict input/output contracts
   - Implement comprehensive error handling
   - Use timeouts to prevent hanging

3. **LLM Usage**
   - Use few-shot prompts for complex tasks
   - Implement output validation
   - Monitor token usage
   - Cache repeated prompts

4. **Integration**
   - Use Secrets Manager for all credentials
   - Implement exponential backoff for retries
   - Log all API interactions
   - Monitor third-party API availability

5. **Security**
   - Never expose API keys in code
   - Implement API rate limiting
   - Use VPC for sensitive operations
   - Audit all data access

---

## 8. Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent timeout | Complex LLM inference | Reduce max_tokens or use faster model |
| Skill execution failure | External API down | Implement fallback, queue for retry |
| Token limit exceeded | Prompt too verbose | Summarize input or split request |
| Authentication error | Invalid credentials | Verify in Secrets Manager |
| Workflow deadlock | Missing conditional | Review workflow DAG |

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Ready for Implementation
