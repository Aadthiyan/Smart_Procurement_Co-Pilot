def check_policy(request_data):
    """
    Checks a request against defined policies.
    """
    violations = []
    
    # Policy 1: Max transaction limit
    if request_data.get('amount', 0) > 5000:
        violations.append("Exceeds maximum single transaction limit of $5000")
        
    # Policy 2: Vendor must be approved (mock)
    if request_data.get('vendor_status') != 'Approved':
        violations.append("Vendor is not approved")
        
    return {
        "compliant": len(violations) == 0,
        "violations": violations
    }

if __name__ == "__main__":
    sample_request = {"amount": 6000, "vendor_status": "Approved"}
    print(check_policy(sample_request))
