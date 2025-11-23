class MockERP:
    def __init__(self):
        self.vendors = {
            "ven_1": {"name": "Acme Corp", "status": "Active"},
            "ven_2": {"name": "Globex", "status": "Pending"}
        }
        self.approvals = {}

    def get_vendor_status(self, vendor_id):
        return self.vendors.get(vendor_id, {}).get("status", "Unknown")

    def submit_approval(self, req_id, approver, decision):
        self.approvals[req_id] = {"approver": approver, "decision": decision}
        return {"status": "success", "req_id": req_id, "decision": decision}

mock_erp = MockERP()
