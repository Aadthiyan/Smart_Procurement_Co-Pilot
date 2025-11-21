# Digital Skills Documentation

## Overview
This document details the custom digital skills implemented for the Smart Procurement Co-Pilot agents.

## Skills by Agent

### Vendor Onboarding Agent
1.  **extract-contract-data**
    *   **Description**: Extracts Vendor Name, Tax ID, and Effective Date from unstructured contract text.
    *   **Input**: `contract_text` (string)
    *   **Output**: JSON object with extracted fields.
2.  **validate-vendor**
    *   **Description**: Validates vendor details (e.g., Tax ID format).
    *   **Input**: `vendor_info` (JSON)
    *   **Output**: `valid` (boolean), `errors` (list).

### Requisition Agent
1.  **check-budget**
    *   **Description**: Verifies if a department has sufficient funds.
    *   **Input**: `department_id`, `amount`
    *   **Output**: `approved` (boolean), `remaining_budget`.
2.  **search-catalog**
    *   **Description**: Searches the product catalog.
    *   **Input**: `query` (string)
    *   **Output**: List of matching products.

### Compliance Agent
1.  **policy-check**
    *   **Description**: Validates requests against business rules (e.g., spending limits).
    *   **Input**: `request_data` (JSON)
    *   **Output**: `compliant` (boolean), `violations` (list).

### Communication Agent
1.  **send-notification**
    *   **Description**: Sends email/slack alerts.
    *   **Input**: `recipient`, `message`
    *   **Output**: `status`.

## Usage Examples
Refer to `tests/test_skills.py` for executable examples of each skill.
