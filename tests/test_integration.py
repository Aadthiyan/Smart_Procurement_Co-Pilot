import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from backend.db_utils import db_manager
from backend.ai_service import ai_service

def test_integration():
    print("\n=== Testing Database Integration ===")
    # Test Vendor Save
    vendor_id = db_manager.save_vendor({
        "name": "Integration Test Corp",
        "tax_id": "999-000-111",
        "address": "Cloud Way"
    })
    print(f"Saved Vendor ID: {vendor_id}")
    
    # Test Vendor Get
    vendor = db_manager.get_vendor(vendor_id)
    print(f"Retrieved Vendor: {vendor}")
    
    print("\n=== Testing AI Service Integration ===")
    # Test Sentiment Analysis
    text = "I am very happy with this vendor's performance."
    analysis = ai_service.analyze_text(text)
    print(f"Text: {text}")
    print(f"Analysis Result: {analysis}")

if __name__ == "__main__":
    test_integration()
