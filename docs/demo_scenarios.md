# Demo Scenarios

This document outlines the key scenarios to demonstrate the capabilities of the Smart Procurement Co-Pilot.

---

## Scenario 1: Supplier Onboarding (Autonomous)

**Objective**: Demonstrate the Vendor Agent's ability to autonomously validate and onboard a supplier using watsonx.ai reasoning.

**Persona**: Vendor Manager
**Input**: "I want to onboard a new vendor."

**Steps**:
1.  **User**: Initiates chat with "Add a new vendor".
2.  **Agent**: Asks for details (Name, Tax ID, Industry).
3.  **User**: Enters:
    *   Name: "Quantum Systems Inc"
    *   Tax ID: "99-8877665"
    *   Industry: "Technology Hardware"
4.  **System Action**:
    *   **Vendor Agent** validates Tax ID format.
    *   **watsonx.ai** analyzes industry risk (Hardware = Medium Risk).
    *   **Agent** checks policies (Hardware is allowed).
    *   **Agent** auto-approves based on high confidence score.
5.  **Output**: "✅ Vendor 'Quantum Systems Inc' has been successfully onboarded. Vendor ID: V-998877."

---

## Scenario 2: Purchase Request (Budget Check & Optimization)

**Objective**: Show the Requisition Agent's ability to check real-time budget and find items.

**Persona**: Employee (IT Dept)
**Input**: "I need to buy 5 ergonomic chairs."

**Steps**:
1.  **User**: Types "I need to buy 5 ergonomic chairs for IT."
2.  **System Action**:
    *   **Requisition Agent** identifies item "ergonomic chair" and quantity "5".
    *   **Agent** calls `check_budget` for IT Department.
    *   **Agent** calls `search_catalog` for "ergonomic chair".
3.  **Agent Response**: "I found 'Herman Miller Aeron' at $1,200 each. Total: $6,000. Your IT budget has $150,000 remaining. Shall I create the request?"
4.  **User**: "Yes, proceed."
5.  **System Action**:
    *   Total ($6,000) > Auto-approval limit ($5,000).
    *   **Agent** routes to **Approval Agent**.
6.  **Output**: "Request REQ-101 created. Status: Pending Approval (Manager)."

---

## Scenario 3: Policy Compliance (Violation Detection)

**Objective**: Demonstrate the Compliance Agent blocking a non-compliant request.

**Persona**: Employee
**Input**: "Buy a $12,000 espresso machine."

**Steps**:
1.  **User**: Types "Order a $12,000 espresso machine for the break room."
2.  **System Action**:
    *   **Compliance Agent** analyzes request.
    *   **watsonx.ai** detects violation: "Luxury item > $1,000 requires VP approval and business justification."
3.  **Output**: "⚠️ **Policy Violation Detected**. Purchasing 'espresso machine' ($12,000) exceeds the discretionary limit for break room supplies. Please provide a business justification or reduce amount."

---

## Scenario 4: Status Tracking (Observability)

**Objective**: Show visibility into the process.

**Persona**: Employee
**Input**: "Check status of REQ-101."

**Steps**:
1.  **User**: Types "What is the status of REQ-101?"
2.  **System Action**:
    *   **Approval Agent** looks up ID `REQ-101`.
3.  **Output**: "Request REQ-101 (5x Ergonomic Chairs) is currently **Pending Approval** by the Finance Director. Last update: 10 minutes ago."

---

## Demo Data Setup

To run these scenarios, ensure the system is seeded with:
*   **Budgets**: IT ($150k), Marketing ($50k).
*   **Policies**: Luxury items restricted.
*   **Catalog**: Office supplies, Electronics.
