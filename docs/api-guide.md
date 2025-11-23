# API & Skill Reference Guide

This document details the interfaces for the Smart Procurement Co-Pilot, including the REST API for system management and the Internal Skill API used by agents.

---

## 1. REST API (System Management)

The backend server (`src/backend/server.py`) exposes endpoints for health checking and component monitoring.

### Base URL
`http://localhost:5000`

### Endpoints

#### `GET /api/health`
**Purpose**: Basic liveness check.
*   **Auth**: None
*   **Response**:
    ```json
    {
      "status": "healthy",
      "timestamp": "2025-11-23"
    }
    ```

#### `GET /api/init-status`
**Purpose**: Verifies that all sub-components (watsonx, Cloudant, Security) are initialized.
*   **Auth**: Required (RBAC: `VIEW_AUDIT_LOG`)
*   **Response**:
    ```json
    {
      "status": "initialized",
      "components": {
        "security": "ready",
        "audit_logging": "ready",
        "session_management": "ready",
        "agent_communication": "ready",
        "watsonx_orchestration": "ready",
        "skill_framework": "ready"
      }
    }
    ```

---

## 2. Internal Skill API (Agent Skills)

Agents execute these skills via the `SkillRegistry`. Each skill follows a strict input/output contract defined by Pydantic models.

### 2.1 Vendor Validation (`validate_vendor`)
**Description**: Validates vendor tax ID and compliance status.
*   **Input**:
    ```json
    {
      "vendor_name": "string",
      "tax_id": "string",
      "industry": "string"
    }
    ```
*   **Output**:
    ```json
    {
      "vendor_id": "string",
      "validation_status": "approved|rejected",
      "validation_score": float,
      "checks_performed": object
    }
    ```

### 2.2 Budget Check (`check_budget`)
**Description**: Verifies if a department has sufficient funds.
*   **Input**:
    ```json
    {
      "department": "string",
      "amount": float,
      "currency": "USD"
    }
    ```
*   **Output**:
    ```json
    {
      "approved": boolean,
      "remaining_budget": float,
      "reason": "string"
    }
    ```

### 2.3 Catalog Search (`search_catalog`)
**Description**: Searches approved vendors for items.
*   **Input**:
    ```json
    {
      "query": "string",
      "category": "string",
      "max_results": int
    }
    ```
*   **Output**:
    ```json
    {
      "results": [
        {
          "item_name": "string",
          "vendor": "string",
          "price": float
        }
      ]
    }
    ```

### 2.4 Policy Check (`policy_check`)
**Description**: Validates a request against corporate procurement policies.
*   **Input**:
    ```json
    {
      "request_type": "string",
      "amount": float,
      "attributes": object
    }
    ```
*   **Output**:
    ```json
    {
      "compliant": boolean,
      "violations": ["string"],
      "risk_level": "low|medium|high"
    }
    ```

---

## 3. Error Handling

All APIs follow standard HTTP status codes:
*   `200 OK`: Success
*   `401 Unauthorized`: Missing or invalid credentials
*   `403 Forbidden`: Insufficient permissions (RBAC)
*   `500 Internal Server Error`: System failure (check `logs/workflow_execution.log`)
