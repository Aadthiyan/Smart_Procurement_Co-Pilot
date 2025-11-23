# Database Schema Documentation

## Overview
The application uses a document-based storage model (Cloudant/NoSQL).

## Collections / Document Types

### 1. Vendor
Stores information about registered suppliers.
```json
{
  "type": "vendor",
  "id": "ven_1",
  "name": "Acme Corp",
  "tax_id": "123-456-789",
  "address": "123 Business Rd",
  "status": "Active",
  "onboarding_date": "2025-11-22"
}
```

### 2. Requisition
Stores purchase requests.
```json
{
  "type": "requisition",
  "id": "req_1",
  "requester": "user@example.com",
  "item_name": "Laptop",
  "quantity": 5,
  "estimated_cost": 5000,
  "status": "Pending Approval",
  "created_at": "2025-11-22T10:00:00Z"
}
```

### 3. Approval Log
Tracks approval decisions.
```json
{
  "type": "approval",
  "requisition_id": "req_1",
  "approver": "manager@example.com",
  "decision": "Approved",
  "timestamp": "2025-11-22T12:00:00Z"
}
```
