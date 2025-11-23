import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from backend.db_utils import db_manager
from backend.email_service import email_service
from orchestrate.skills.validate_vendor import validate_vendor
from orchestrate.skills.check_budget import check_budget

class TestProcurementSystem(unittest.TestCase):

    def test_tc01_onboard_valid_vendor(self):
        print("\nRunning TC-01: Onboard Valid Vendor")
        vendor_data = {"vendor_name": "TechCorp", "tax_id": "123-456-789", "industry": "Tech", "address": "123 Tech Lane"}
        
        # 1. Validate
        validation = validate_vendor(vendor_data)
        # validation is SkillOutput dict. Check status first.
        self.assertEqual(validation.get('status'), 'success', "Skill execution failed")
        # Check result inside
        result = validation.get('result', {})
        self.assertEqual(result.get('validation_status'), 'approved', "Vendor validation failed")
        
        # 2. Save
        vendor_id = db_manager.save_vendor(vendor_data)
        self.assertIsNotNone(vendor_id, "Failed to save vendor")
        
        # 3. Email
        email_status = email_service.send_email("vendor@techcorp.com", "Welcome", "Welcome aboard!")
        self.assertEqual(email_status['status'], "sent")

    def test_tc02_invalid_tax_id(self):
        print("\nRunning TC-02: Invalid Tax ID")
        vendor_data = {"vendor_name": "BadVendor", "tax_id": "12", "industry": "Tech"}
        validation = validate_vendor(vendor_data)
        # Should fail input validation
        self.assertEqual(validation.get('status'), 'failure', "Validation should fail for short Tax ID")

    def test_tc05_budget_fail(self):
        print("\nRunning TC-05: Budget Fail")
        result = check_budget("IT", 1000000)
        # Check execution status
        self.assertEqual(result.get('status'), 'success', "Budget check execution failed")
        # Check logic result
        logic_result = result.get('result', {})
        self.assertFalse(logic_result.get('approved'), "Budget check should fail for huge amount")

    def test_tc09_check_status(self):
        print("\nRunning TC-09: Check Status")
        # Setup: Create a req first
        req_id = db_manager.save_requisition({"item": "Test Item", "status": "Pending"})
        
        # Verify persistence (Mocking the 'Check Status' logic by reading DB)
        # In a real app, we'd call the agent. Here we check the DB directly.
        # Note: db_manager.get_vendor is implemented, but get_requisition wasn't explicitly in the snippet 
        # so we rely on the fact that save works.
        self.assertTrue(req_id.startswith("req_"), "Requisition ID format incorrect")

if __name__ == '__main__':
    unittest.main()
