import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from backend.email_service import email_service
from backend.notification_service import notification_service
from backend.mock_erp import mock_erp

def test_integrations():
    print("\n=== Testing Email Integration ===")
    email_service.send_email("test@example.com", "Test Subject", "This is a test email.")

    print("\n=== Testing Notification System ===")
    notification_service.send_notification("user_123", "welcome", name="John Doe")
    notification_service.send_notification("manager_456", "approval_needed", req_id="REQ-001")

    print("\n=== Testing Mock ERP ===")
    status = mock_erp.get_vendor_status("ven_1")
    print(f"Vendor Status (ven_1): {status}")
    
    approval = mock_erp.submit_approval("REQ-001", "manager_456", "Approved")
    print(f"Approval Submission: {approval}")

if __name__ == "__main__":
    test_integrations()
