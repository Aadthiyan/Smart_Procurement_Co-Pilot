import re

def extract_contract_data(contract_text):
    """
    Extracts key data points from a contract text.
    """
    data = {}
    
    # Extract Vendor Name
    name_match = re.search(r"Vendor Name:\s*(.*)", contract_text)
    if name_match:
        data['vendor_name'] = name_match.group(1).strip()
        
    # Extract Tax ID
    tax_match = re.search(r"Tax ID:\s*([\d-]+)", contract_text)
    if tax_match:
        data['tax_id'] = tax_match.group(1).strip()
        
    # Extract Effective Date
    date_match = re.search(r"Effective Date:\s*(\d{4}-\d{2}-\d{2})", contract_text)
    if date_match:
        data['effective_date'] = date_match.group(1).strip()
        
    return data

if __name__ == "__main__":
    sample_text = """
    Contract Agreement
    Vendor Name: Acme Corp
    Tax ID: 12-3456789
    Effective Date: 2023-01-01
    """
    print(extract_contract_data(sample_text))
