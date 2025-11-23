# Test Scenarios

## 1. Supplier Onboarding
| ID | Scenario | Input Data | Expected Result |
| :--- | :--- | :--- | :--- |
| **TC-01** | **Happy Path**: Onboard valid vendor | Name: "TechCorp", TaxID: "123-456-789" | Vendor saved, Welcome email sent. |
| **TC-02** | **Validation Fail**: Invalid Tax ID | Name: "BadVendor", TaxID: "123" | Error message: "Invalid Tax ID". |
| **TC-03** | **Compliance Fail**: Sanctioned Vendor | Name: "Banned Corp" | Compliance check fails, Rejection email sent. |

## 2. Purchase Request
| ID | Scenario | Input Data | Expected Result |
| :--- | :--- | :--- | :--- |
| **TC-04** | **Happy Path**: Small Purchase | Item: "Mouse", Qty: 5, Cost: $100 | Auto-approved (if logic exists) or routed to Manager. |
| **TC-05** | **Budget Fail**: Exceeds Budget | Item: "Server Farm", Cost: $1,000,000 | "Budget exceeded" alert. |
| **TC-06** | **Policy Fail**: Restricted Item | Item: "Gambling Chips" | Compliance Agent rejects request. |

## 3. Approval Routing
| ID | Scenario | Input Data | Expected Result |
| :--- | :--- | :--- | :--- |
| **TC-07** | **Manager Approval** | REQ-001 (Pending) | Status changes to "Approved", Notification sent to requester. |
| **TC-08** | **Manager Rejection** | REQ-002 (Pending) | Status changes to "Rejected", Notification sent. |

## 4. Status Tracking
| ID | Scenario | Input Data | Expected Result |
| :--- | :--- | :--- | :--- |
| **TC-09** | **Check Valid ID** | "Status of REQ-001" | Returns current status. |
| **TC-10** | **Check Invalid ID** | "Status of REQ-999" | "Request not found". |
