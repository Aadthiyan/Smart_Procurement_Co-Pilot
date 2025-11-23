"""
Search Catalog Skill - Searches product catalog for items
"""
import sys
import os
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.skill_base import BaseSkill, SkillInput, SkillOutput, SkillStatus
from backend.security.audit_logger import get_audit_logger, AuditEventType


class SearchCatalogSkill(BaseSkill):
    """
    Searches the product catalog for items matching a query.
    
    Input: query (str)
    Output: results (list of matching items)
    """
    
    def __init__(self):
        super().__init__("search_catalog")
        self.audit_logger = get_audit_logger()
        
        # Mock catalog data
        self.catalog = [
            {"id": "1", "name": "Laptop", "price": 1200, "category": "Electronics"},
            {"id": "2", "name": "Monitor", "price": 300, "category": "Electronics"},
            {"id": "3", "name": "Keyboard", "price": 50, "category": "Accessories"},
            {"id": "4", "name": "Mouse", "price": 25, "category": "Accessories"},
            {"id": "5", "name": "Printer", "price": 400, "category": "Equipment"},
            {"id": "6", "name": "Desk", "price": 150, "category": "Furniture"},
            {"id": "7", "name": "Chair", "price": 200, "category": "Furniture"},
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate required field: query"""
        if not input_data:
            raise ValueError("Input data is required")
        
        if "query" not in input_data:
            raise ValueError("Missing required field: query")
        
        if not isinstance(input_data["query"], str):
            raise ValueError("query must be a string")
        
        if len(input_data["query"].strip()) == 0:
            raise ValueError("query cannot be empty")
        
        return True
    
    def _execute_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute catalog search logic"""
        query = input_data["query"].lower().strip()
        
        # Search catalog
        results = [
            item for item in self.catalog 
            if query in item['name'].lower() or query in item['category'].lower()
        ]
        
        # Log to audit
        try:
            self.audit_logger.log_event(
                event_type=AuditEventType.CATALOG_SEARCHED,
                user_id="system",
                resource_type="catalog",
                resource_id="catalog_main",
                action="search",
                details={
                    "query": query,
                    "results_count": len(results),
                    "results": results
                }
            )
        except Exception as e:
            self.logger.warning(f"Failed to log catalog search: {str(e)}")
        
        return {
            "query": query,
            "results_count": len(results),
            "results": results,
            "success": len(results) > 0
        }


# Backward compatibility wrapper
def search_catalog(query: str) -> List[Dict[str, Any]]:
    """
    Legacy function-based interface for backward compatibility.
    
    Args:
        query: Search query string
        
    Returns:
        List of matching catalog items
    """
    skill = SearchCatalogSkill()
    try:
        output = skill.execute({"query": query})
        result_dict = output.dict() if hasattr(output, 'dict') else output
        return result_dict.get("results", [])
    except Exception as e:
        return []


if __name__ == "__main__":
    # Test the skill
    skill = SearchCatalogSkill()
    result = skill.execute({"query": "laptop"})
    print(f"Search result: {result}")
    print(f"Status: {result.status if hasattr(result, 'status') else 'success'}")

