import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'orchestrate/skills'))

# Import skills dynamically or directly if paths allow, 
# but for simplicity in this script we will exec them or import if possible.
# Since they are in a subdirectory, we added it to path.

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_skills():
    print("--- Testing Digital Skills ---")

    # 1. Extract Contract Data
    extract_tool = load_module("extract_contract_data", "orchestrate/skills/extract-contract-data.py")
    contract_text = "Vendor Name: Tech Solutions\nTax ID: 99-888777\nEffective Date: 2024-01-01"
    print(f"Extract Data: {extract_tool.extract_contract_data(contract_text)}")

    # 2. Validate Vendor
    validate_tool = load_module("validate_vendor", "orchestrate/skills/validate-vendor.py")
    print(f"Validate Vendor (Valid): {validate_tool.validate_vendor({'name': 'Tech', 'tax_id': '123456789'})}")
    print(f"Validate Vendor (Invalid): {validate_tool.validate_vendor({'name': 'Tech', 'tax_id': '123'})}")

    # 3. Check Budget
    budget_tool = load_module("check_budget", "orchestrate/skills/check-budget.py")
    print(f"Check Budget (Pass): {budget_tool.check_budget('IT', 1000)}")
    print(f"Check Budget (Fail): {budget_tool.check_budget('IT', 60000)}")

    # 4. Search Catalog
    catalog_tool = load_module("search_catalog", "orchestrate/skills/search-catalog.py")
    print(f"Search Catalog: {catalog_tool.search_catalog('monitor')}")

    # 5. Policy Check
    policy_tool = load_module("policy_check", "orchestrate/skills/policy-check.py")
    print(f"Policy Check (Fail): {policy_tool.check_policy({'amount': 6000, 'vendor_status': 'Approved'})}")

    # 6. Send Notification
    notify_tool = load_module("send_notification", "orchestrate/skills/send-notification.py")
    print(f"Notification: {notify_tool.send_notification('admin@corp.com', 'Test Alert')}")

if __name__ == "__main__":
    test_skills()
