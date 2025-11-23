from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
from datetime import date

# --- Vendor Schemas ---

class VendorInput(BaseModel):
    vendor_name: str = Field(..., min_length=2, description="Official vendor business name")
    tax_id: str = Field(..., description="Government-issued tax ID")
    industry: str = Field(..., description="Primary business industry")
    contact_email: Optional[str] = Field(None, description="Primary contact email")
    annual_revenue: Optional[float] = Field(None, ge=0)
    
    @validator('tax_id')
    def validate_tax_id(cls, v):
        if len(v) < 3:
            raise ValueError('Tax ID too short')
        return v

class VendorOutput(BaseModel):
    vendor_id: str
    validation_status: str
    validation_score: float
    checks_performed: dict
    timestamp: str

# --- Requisition Schemas ---

class RequisitionInput(BaseModel):
    item_name: str
    quantity: int = Field(..., gt=0)
    department: str
    budget_code: Optional[str]

# --- Compliance Schemas ---

class PolicyCheckInput(BaseModel):
    vendor_id: str
    amount: float
    transaction_type: str
