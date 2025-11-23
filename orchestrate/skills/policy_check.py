"""
Policy Check Skill - Validates requests against defined policies
"""
import sys
import os
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.skill_base import BaseSkill, SkillInput, SkillOutput, SkillStatus
from backend.security.audit_logger import get_audit_logger, AuditEventType


class PolicyCheckSkill(BaseSkill):
    """
    Validates requests against defined procurement policies.
    
    Input: request_data (dict with amount, vendor_status, etc.)
    Output: compliant (bool), violations (list)
    """
    
    def __init__(self):
        super().__init__("policy_check")
        self.audit_logger = get_audit_logger()
        
        # Define policy thresholds
        self.max_transaction_limit = 5000
        self.approved_vendors_only = True
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate required field: request_data"""
        if not input_data:
            raise ValueError("Input data is required")
        
        if "request_data" not in input_data:
            raise ValueError("Missing required field: request_data")
        
        if not isinstance(input_data["request_data"], dict):
            raise ValueError("request_data must be a dictionary")
        
        return True
    
    def _execute_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute policy validation logic"""
        request_data = input_data["request_data"]
        violations = []
        
        # Policy 1: Max transaction limit
        amount = request_data.get('amount', 0)
        if amount > self.max_transaction_limit:
            violations.append({
                "policy": "MAX_TRANSACTION_LIMIT",
                "message": f"Exceeds maximum single transaction limit of ${self.max_transaction_limit}",
                "threshold": self.max_transaction_limit,
                "actual": amount
            })
        
        # Policy 2: Vendor must be approved
        vendor_status = request_data.get('vendor_status', 'Unknown')
        if self.approved_vendors_only and vendor_status != 'Approved':
            violations.append({
                "policy": "VENDOR_APPROVAL",
                "message": "Vendor is not approved for procurement",
                "vendor_status": vendor_status
            })
        
        # Policy 3: Description required
        description = request_data.get('description', '').strip()
        if not description:
            violations.append({
                "policy": "DESCRIPTION_REQUIRED",
                "message": "Purchase request must include a description"
            })
        
        # Policy 4: Business justification for high-value items
        if amount > 1000 and not request_data.get('justification'):
            violations.append({
                "policy": "JUSTIFICATION_REQUIRED",
                "message": "High-value purchases (>$1000) require business justification",
                "amount": amount
            })
        
        compliant = len(violations) == 0
        
        # Log to audit
        try:
            self.audit_logger.log_event(
                event_type=AuditEventType.POLICY_CHECKED,
                user_id="system",
                resource_type="policy",
                resource_id="procurement_policy",
                action="validate",
                details={
                    "compliant": compliant,
                    "violations_count": len(violations),
                    "violations": violations,
                    "request_amount": amount
                }
            )
        except Exception as e:
            self.logger.warning(f"Failed to log policy check: {str(e)}")
        
        return {
            "compliant": compliant,
            "violations": violations,
            "violations_count": len(violations),
            "request_data_summary": {
                "amount": amount,
                "vendor_status": vendor_status
            }
        }


# Backward compatibility wrapper
def check_policy(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function-based interface for backward compatibility.
    
    Args:
        request_data: Dictionary with request details (amount, vendor_status, etc.)
        
    Returns:
        Dictionary with compliance status and violations list
    """
    skill = PolicyCheckSkill()
    try:
        output = skill.execute({"request_data": request_data})
        return output.dict() if hasattr(output, 'dict') else output
    except Exception as e:
        return {
            "compliant": False,
            "violations": [{"policy": "ERROR", "message": str(e)}],
            "violations_count": 1
        }


if __name__ == "__main__":
    # Test the skill
    skill = PolicyCheckSkill()
    sample_request = {"amount": 6000, "vendor_status": "Approved", "description": "Office supplies"}
    result = skill.execute({"request_data": sample_request})
    print(f"Policy check result: {result}")
    print(f"Status: {result.status if hasattr(result, 'status') else 'success'}")

