# Integration Documentation

## 1. Email Service
**Module**: `src/backend/email_service.py`
**Description**: Handles sending transactional emails. Defaults to "Mock Mode" which prints to console, avoiding the need for real SMTP credentials during development.
**Usage**:
```python
email_service.send_email("user@example.com", "Welcome", "Hello World")
```

## 2. Notification Service
**Module**: `src/backend/notification_service.py`
**Description**: Manages in-app notifications using predefined templates.
**Templates**:
- `welcome`: For new vendors.
- `approval_needed`: For managers.
- `status_update`: For requesters.

## 3. Mock ERP
**Module**: `src/backend/mock_erp.py`
**Description**: Simulates an external Enterprise Resource Planning system.
**Data**:
- Pre-populated with mock vendors (Acme Corp, Globex).
- Stores approval decisions in memory.
