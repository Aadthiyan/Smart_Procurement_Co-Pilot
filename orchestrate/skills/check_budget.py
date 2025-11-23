"""
Check Budget Skill - Verifies department budget availability
"""
import sys
import os
from typing import Dict, Any, Optional

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.skill_base import BaseSkill, SkillInput, SkillOutput, SkillStatus
from backend.security.audit_logger import get_audit_logger, AuditEventType
from pydantic import Field, ValidationError


class CheckBudgetSkill(BaseSkill):
    """
    Checks if a department has sufficient budget for a requested amount.
    
    Input: department_id (str), amount (float)
    Output: approved (bool), remaining_budget (float)
    """
    
    def __init__(self):
        super().__init__("check_budget")
        self.audit_logger = get_audit_logger()
        
        # Mock budget data
        self.budgets = {
            "IT": 50000,
            "HR": 10000,
            "Marketing": 20000,
            "Operations": 35000,
            "Finance": 25000
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate required fields: department_id, amount"""
        if not input_data:
            raise ValueError("Input data is required")
        
        required_fields = ["department_id", "amount"]
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate types
        if not isinstance(input_data["department_id"], str):
            raise ValueError("department_id must be a string")
        if not isinstance(input_data["amount"], (int, float)):
            raise ValueError("amount must be a number")
        
        return True
    
    def _execute_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute budget check logic"""
        department_id = input_data["department_id"]
        amount = input_data["amount"]
        
        # Get current budget
        current_budget = self.budgets.get(department_id, 0)
        
        if current_budget == 0:
            return {
                "approved": False,
                "remaining_budget": 0,
                "error": f"Department {department_id} not found or has no budget"
            }
        
        approved = current_budget >= amount
        remaining = current_budget - amount if approved else current_budget
        
        # Log to audit
        try:
            self.audit_logger.log_event(
                event_type=AuditEventType.BUDGET_CHECKED,
                user_id="system",
                resource_type="budget",
                resource_id=department_id,
                action="check",
                details={
                    "department": department_id,
                    "requested_amount": amount,
                    "approved": approved,
                    "remaining_budget": remaining
                }
            )
        except Exception as e:
            self.logger.warning(f"Failed to log budget check: {str(e)}")
        
        return {
            "approved": approved,
            "remaining_budget": remaining,
            "department_id": department_id,
            "requested_amount": amount
        }


# Backward compatibility wrapper
def check_budget(department_id: str, amount: float) -> Dict[str, Any]:
    """
    Legacy function-based interface for backward compatibility.
    
    Args:
        department_id: Department identifier
        amount: Amount to check budget for
        
    Returns:
        Dictionary with approved status and remaining budget
    """
    skill = CheckBudgetSkill()
    try:
        output = skill.execute({"department_id": department_id, "amount": amount})
        return output.dict() if hasattr(output, 'dict') else output
    except Exception as e:
        return {
            "approved": False,
            "remaining_budget": 0,
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the skill
    skill = CheckBudgetSkill()
    result = skill.execute({"department_id": "IT", "amount": 5000})
    print(f"Budget check result: {result}")
    print(f"Status: {result.status if hasattr(result, 'status') else 'success'}")

