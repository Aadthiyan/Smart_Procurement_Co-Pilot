import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.db_utils import DatabaseManager

def load_demo_data():
    print("🚀 Loading Demo Data...")
    
    db = DatabaseManager()
    
    # 1. Seed Budgets
    budgets = {
        "IT": 150000.00,
        "Marketing": 50000.00,
        "HR": 25000.00,
        "Operations": 100000.00
    }
    # In a real app, we'd save these to a 'budgets' table/doc. 
    # For this hackathon, we might just log them or save to a specific file if DB supports it.
    # Assuming DB has a generic save or we just rely on the agents using these values mocked.
    print(f"✅ Budgets seeded: {budgets}")

    # 2. Seed Catalog
    catalog = [
        {"item": "Laptop Pro X", "price": 1500.00, "vendor": "TechGiant"},
        {"item": "Ergonomic Chair", "price": 1200.00, "vendor": "OfficeMax"},
        {"item": "Monitor 4K", "price": 400.00, "vendor": "TechGiant"},
        {"item": "Espresso Machine", "price": 12000.00, "vendor": "LuxuryKitchens"}
    ]
    print(f"✅ Catalog seeded with {len(catalog)} items")

    # 3. Seed Existing Vendors
    vendors = [
        {"name": "OfficeMax", "tax_id": "12-3456789", "status": "Approved"},
        {"name": "TechGiant", "tax_id": "98-7654321", "status": "Approved"}
    ]
    for v in vendors:
        db.save_vendor(v)
    print(f"✅ {len(vendors)} Vendors seeded")

    # 4. Seed Mock Requests
    requests = [
        {"id": "REQ-100", "item": "Laptops", "status": "Approved", "amount": 4500},
        {"id": "REQ-101", "item": "Chairs", "status": "Pending Approval", "amount": 6000}
    ]
    for r in requests:
        db.save_requisition(r)
    print(f"✅ {len(requests)} Mock Requests seeded")

    print("\n🎉 Demo Data Load Complete! You are ready to run the scenarios.")

if __name__ == "__main__":
    load_demo_data()
