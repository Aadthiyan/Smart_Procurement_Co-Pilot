def validate_vendor(vendor_info):
    """
    Validates vendor information against basic rules.
    """
    errors = []
    
    if not vendor_info.get('name'):
        errors.append("Vendor Name is missing")
        
    tax_id = vendor_info.get('tax_id', '')
    if not tax_id or len(tax_id) < 9:
        errors.append("Invalid Tax ID")
        
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

if __name__ == "__main__":
    sample_vendor = {"name": "Acme Corp", "tax_id": "123"}
    print(validate_vendor(sample_vendor))
