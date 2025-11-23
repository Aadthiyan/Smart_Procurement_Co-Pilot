# System Architecture

## Overview

The Smart Procurement Co-Pilot is an **Agentic AI** system designed to automate complex procurement workflows. Unlike traditional rule-based automation, it uses **Autonomous Agents** powered by **IBM watsonx.ai** to reason, make decisions, and execute tasks.

The system is built on a microservices-inspired architecture, orchestrated by **IBM watsonx.orchestrate**, with a Python-based backend and a Streamlit frontend.

---

## 1. High-Level Architecture

```mermaid
graph TD
    User[User / Frontend] <--> Orch[Orchestrator / Main App]
    Orch <--> VA[Vendor Onboarding Agent]
    Orch <--> RA[Requisition Agent]
    Orch <--> CA[Compliance Agent]
    Orch <--> AA[Approval Agent]
    Orch <--> CMA[Communication Agent]

    VA -- "Updates Vendor DB" --> DB[(IBM Cloudant)]
    RA -- "Creates PR" --> DB
    CA -- "Reads Policies" --> DB
    AA -- "Updates Status" --> DB
    CMA -- "Sends Notifications" --> Ext[External Systems (Email/Slack)]
    
    subgraph "IBM watsonx Platform"
        WXO[watsonx.orchestrate]
        WXA[watsonx.ai (Granite 13B)]
    end
    
    Orch <--> WXO
    VA <--> WXA
    RA <--> WXA
    CA <--> WXA
```

---

## 2. Core Components

### 2.1 Orchestration Layer (The Brain)
*   **Role**: Manages the lifecycle of a user request.
*   **Technology**: Python `Orchestrator` class + **watsonx.orchestrate**.
*   **Responsibilities**:
    *   **Intent Detection**: Uses NLU/LLM to understand if the user wants to "buy something" or "onboard a vendor".
    *   **Routing**: Dispatches the request to the correct specialized agent.
    *   **State Management**: Maintains the session context (e.g., "currently talking about Vendor X").

### 2.2 Agent Layer (The Workers)
The system comprises 5 specialized agents, each with specific **Autonomy** and **Skills**.

| Agent | Role | Key Skills | Autonomy Level |
|-------|------|------------|----------------|
| **Vendor Agent** | Validates & onboards suppliers | `validate_vendor`, `extract_contract` | High (Auto-approves compliant vendors) |
| **Requisition Agent** | Manages purchase requests | `check_budget`, `search_catalog` | High (Auto-routes based on budget) |
| **Compliance Agent** | Enforces company policies | `policy_check` | High (Blocks violations) |
| **Approval Agent** | Manages sign-offs | `get_status`, `update_approval` | Medium (Routing logic) |
| **Communication Agent** | Sends alerts & updates | `send_notification` | Medium (Template selection) |

### 2.3 Skill Layer (The Tools)
Agents do not "hallucinate" actions; they execute **Formal Digital Skills**.
*   **Definition**: Python functions with strict Pydantic input/output models.
*   **Registry**: A central registry maps skill names to executable code.
*   **Example**: `validate_vendor` takes `tax_id` and returns `validation_score`.

### 2.4 Data & Security Layer
*   **Database**: **IBM Cloudant** (NoSQL) stores JSON documents for Vendors, Requisitions, and Logs.
*   **Security**:
    *   **RBAC**: Role-Based Access Control ensures only "Managers" can approve.
    *   **Secrets Manager**: IBM Secrets Manager protects API keys.
    *   **Audit Trail**: Every agent decision is logged to an immutable audit log.

---

## 3. Integration Architecture

### 3.1 watsonx.orchestrate Integration
The system uses **watsonx.orchestrate** to define and execute multi-step workflows.

```yaml
# Example Workflow Definition
Workflow: supplier_onboarding
Steps:
  1. Vendor Agent -> validate_vendor
  2. Compliance Agent -> policy_check (if score > 0.8)
  3. Approval Agent -> route_approval (if risk == medium)
  4. Communication Agent -> send_welcome_email
```

### 3.2 watsonx.ai Integration (LLM Reasoning)
Agents use **IBM Granite 13B Chat** for complex reasoning tasks that cannot be scripted.

*   **Prompt Engineering**: We use "Chain-of-Thought" prompting to ensure agents explain their decisions.
*   **Example Prompt**:
    > "Analyze this vendor's profile against our 'Sustainability Policy'. If they are a manufacturing company, ensure they have ISO 14001 certification. Provide a risk score (0-10) and reasoning."

---

## 4. Data Flow Patterns

### 4.1 Synchronous Request (Chat)
1.  **User** types: "I need to buy a laptop."
2.  **Orchestrator** detects intent: `PURCHASE_REQUEST`.
3.  **Requisition Agent** is activated.
4.  Agent calls `check_budget` skill (Synchronous).
5.  Agent returns response: "Budget available. Which model?"

### 4.2 Asynchronous Workflow (Approval)
1.  **Requisition Agent** submits PR #123.
2.  **Orchestrator** triggers `approval_workflow`.
3.  **Approval Agent** notifies Manager (Email).
4.  System waits for Manager action (Human-in-the-Loop).
5.  Manager clicks "Approve" in email/dashboard.
6.  Workflow resumes -> **Communication Agent** sends PO.

---

## 5. Security & Compliance

*   **Authentication**: Mocked for demo (User Roles), ready for OIDC/SAML.
*   **Authorization**: Decorator-based RBAC (`@require_permission`).
*   **Audit Logging**:
    *   **What**: User inputs, Agent decisions, Skill outputs.
    *   **Where**: `logs/audit.log` (Local) + Cloudant (Production).
    *   **Why**: Compliance with procurement regulations (SOX, GDPR).

---

## 6. Technology Stack

*   **Frontend**: Streamlit (Python)
*   **Backend**: Python 3.9+
*   **AI**: IBM watsonx.ai (Granite Model), IBM NLU
*   **Orchestration**: IBM watsonx.orchestrate
*   **Database**: IBM Cloudant
*   **Infrastructure**: IBM Cloud Code Engine (Target Deployment)
