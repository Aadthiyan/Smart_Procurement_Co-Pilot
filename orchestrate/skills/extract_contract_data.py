"""
Extract Contract Data Skill - Extracts key data from contract text
"""
import re
import sys
import os
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.skill_base import BaseSkill, SkillInput, SkillOutput, SkillStatus
from backend.security.audit_logger import get_audit_logger, AuditEventType


class ExtractContractDataSkill(BaseSkill):
    """
    Extracts key data points from contract text using pattern matching.
    
    Input: contract_text (str)
    Output: extracted_data (dict with vendor_name, tax_id, effective_date, etc.)
    """
    
    def __init__(self):
        super().__init__("extract_contract_data")
        self.audit_logger = get_audit_logger()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate required field: contract_text"""
        if not input_data:
            raise ValueError("Input data is required")
        
        if "contract_text" not in input_data:
            raise ValueError("Missing required field: contract_text")
        
        if not isinstance(input_data["contract_text"], str):
            raise ValueError("contract_text must be a string")
        
        if len(input_data["contract_text"].strip()) == 0:
            raise ValueError("contract_text cannot be empty")
        
        return True
    
    def _execute_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute contract data extraction logic"""
        contract_text = input_data["contract_text"]
        extracted_data = {}
        extraction_confidence = {}
        
        # Extract Vendor Name
        name_match = re.search(r"Vendor Name:\s*([^\n]+)", contract_text, re.IGNORECASE)
        if name_match:
            extracted_data['vendor_name'] = name_match.group(1).strip()
            extraction_confidence['vendor_name'] = 0.95
        
        # Extract Tax ID
        tax_match = re.search(r"Tax ID:\s*([\d\-]+)", contract_text, re.IGNORECASE)
        if tax_match:
            extracted_data['tax_id'] = tax_match.group(1).strip()
            extraction_confidence['tax_id'] = 0.90
        
        # Extract Effective Date
        date_match = re.search(r"Effective Date:\s*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})", 
                               contract_text, re.IGNORECASE)
        if date_match:
            extracted_data['effective_date'] = date_match.group(1).strip()
            extraction_confidence['effective_date'] = 0.92
        
        # Extract Contract Value
        value_match = re.search(r"Contract Value:\s*\$?([\d,]+\.?\d*)", contract_text, re.IGNORECASE)
        if value_match:
            amount_str = value_match.group(1).replace(',', '')
            try:
                extracted_data['contract_value'] = float(amount_str)
                extraction_confidence['contract_value'] = 0.88
            except ValueError:
                pass
        
        # Extract Contact Email
        email_match = re.search(r"Contact Email:\s*([\w\.\-]+@[\w\.\-]+)", contract_text, re.IGNORECASE)
        if email_match:
            extracted_data['contact_email'] = email_match.group(1).strip()
            extraction_confidence['contact_email'] = 0.85
        
        # Extract Terms and Conditions
        terms_match = re.search(r"Terms:\s*([^\n]+)", contract_text, re.IGNORECASE)
        if terms_match:
            extracted_data['terms'] = terms_match.group(1).strip()
            extraction_confidence['terms'] = 0.80
        
        # Calculate overall extraction quality
        if extraction_confidence:
            overall_confidence = sum(extraction_confidence.values()) / len(extraction_confidence)
        else:
            overall_confidence = 0
        
        # Log to audit
        try:
            self.audit_logger.log_event(
                event_type=AuditEventType.CONTRACT_DATA_EXTRACTED,
                user_id="system",
                resource_type="contract",
                resource_id="contract_data",
                action="extract",
                details={
                    "fields_extracted": len(extracted_data),
                    "overall_confidence": overall_confidence,
                    "extracted_fields": list(extracted_data.keys())
                }
            )
        except Exception as e:
            self.logger.warning(f"Failed to log contract extraction: {str(e)}")
        
        return {
            "extracted_data": extracted_data,
            "extraction_confidence": extraction_confidence,
            "overall_confidence": overall_confidence,
            "fields_count": len(extracted_data),
            "success": len(extracted_data) > 0
        }


# Backward compatibility wrapper
def extract_contract_data(contract_text: str) -> Dict[str, Any]:
    """
    Legacy function-based interface for backward compatibility.
    
    Args:
        contract_text: Raw contract text to extract data from
        
    Returns:
        Dictionary with extracted data fields
    """
    skill = ExtractContractDataSkill()
    try:
        output = skill.execute({"contract_text": contract_text})
        result_dict = output.dict() if hasattr(output, 'dict') else output
        return result_dict.get("extracted_data", {})
    except Exception as e:
        return {}


if __name__ == "__main__":
    # Test the skill
    skill = ExtractContractDataSkill()
    sample_text = """
    Contract Agreement
    Vendor Name: Acme Corp
    Tax ID: 12-3456789
    Effective Date: 2023-01-01
    Contract Value: $50,000
    Contact Email: contact@acmecorp.com
    Terms: Net 30 days
    """
    result = skill.execute({"contract_text": sample_text})
    print(f"Extraction result: {result}")
    print(f"Status: {result.status if hasattr(result, 'status') else 'success'}")

