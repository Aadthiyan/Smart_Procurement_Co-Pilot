# Skills Inventory & Formal Definitions

## Overview

This document provides formal specifications for all digital skills in the Smart Procurement Co-Pilot. Each skill is defined with strict input/output contracts, error handling, and integration mappings.

---

## Skill Inventory Summary

| Skill ID | Agent | Purpose | Category | Status |
|----------|-------|---------|----------|--------|
| `validate_vendor_skill` | Vendor Agent | Validate vendor information | Core | ✅ Implemented |
| `check_budget_skill` | Requisition Agent | Verify budget availability | Core | ✅ Implemented |
| `search_catalog_skill` | Requisition Agent | Search product catalog | Core | ✅ Implemented |
| `policy_check_skill` | Compliance Agent | Validate policy compliance | Core | ✅ Implemented |
| `extract_contract_skill` | Vendor Agent | Parse contract documents | Utility | ✅ Implemented |
| `send_notification_skill` | Communication Agent | Send alerts/notifications | Utility | ✅ Implemented |

---

## 1. Validate Vendor Skill

### 1.1 Specification

**Skill ID:** `validate_vendor_skill`  
**Agent:** Vendor Onboarding Agent  
**Category:** Core - Vendor Management  
**Description:** Validates vendor information including tax ID, business registration, financial health, and compliance status.

### 1.2 Input Contract

```json
{
  "skill_id": "validate_vendor_skill",
  "input_schema": {
    "type": "object",
    "required": ["vendor_name", "tax_id", "industry"],
    "properties": {
      "vendor_name": {
        "type": "string",
        "description": "Official vendor business name",
        "minLength": 2,
        "maxLength": 255
      },
      "tax_id": {
        "type": "string",
        "description": "Government-issued tax ID (EIN for US)",
        "pattern": "^[0-9]{9}$|^[0-9]{2}-[0-9]{7}$"
      },
      "industry": {
        "type": "string",
        "description": "Primary business industry",
        "enum": ["manufacturing", "wholesale", "retail", "services", "technology", "other"]
      },
      "contact_email": {
        "type": "string",
        "format": "email",
        "description": "Primary contact email"
      },
      "annual_revenue": {
        "type": "number",
        "description": "Annual revenue in USD",
        "minimum": 0
      },
      "years_in_business": {
        "type": "integer",
        "description": "Number of years business has operated",
        "minimum": 0
      },
      "certifications": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of relevant certifications (ISO9001, SOC2, etc.)"
      },
      "documents": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "document_type": {
              "type": "string",
              "enum": ["tax_return", "business_license", "insurance", "financial_statement"]
            },
            "document_url": {
              "type": "string",
              "format": "uri"
            }
          }
        },
        "description": "Supporting documentation URLs"
      }
    }
  },
  "timeout": 30000,
  "retry_policy": {
    "max_attempts": 3,
    "backoff": "exponential",
    "backoff_multiplier": 2
  }
}
```

### 1.3 Output Contract

```json
{
  "output_schema": {
    "type": "object",
    "required": ["vendor_id", "validation_status", "validation_score", "timestamp"],
    "properties": {
      "vendor_id": {
        "type": "string",
        "description": "Unique vendor identifier (UUID)",
        "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
      },
      "validation_status": {
        "type": "string",
        "enum": ["approved", "review_required", "rejected"],
        "description": "Overall validation result"
      },
      "validation_score": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Vendor quality score (0-1)"
      },
      "checks_performed": {
        "type": "object",
        "properties": {
          "tax_id_valid": {
            "type": "boolean",
            "description": "Tax ID format and registry check"
          },
          "business_registration_valid": {
            "type": "boolean",
            "description": "Business registration status"
          },
          "financial_health": {
            "type": "string",
            "enum": ["excellent", "good", "fair", "poor", "unknown"],
            "description": "Financial stability assessment"
          },
          "certifications_verified": {
            "type": "boolean",
            "description": "Relevant certifications verified"
          },
          "documentation_complete": {
            "type": "boolean",
            "description": "All required documents provided"
          }
        }
      },
      "risk_assessment": {
        "type": "object",
        "properties": {
          "risk_level": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Overall vendor risk"
          },
          "risk_factors": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Identified risk factors"
          }
        }
      },
      "recommendations": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Follow-up actions recommended"
      },
      "timestamp": {
        "type": "string",
        "format": "date-time",
        "description": "Validation completion timestamp"
      }
    }
  }
}
```

### 1.4 Tools & External Services

```yaml
Primary Tools:
  - Dun & Bradstreet API: Credit check, business registration
  - SAP System: Check existing vendor records
  - Internal Database: Vendor history lookup

Fallback Services:
  - Public business registry (county/state level)
  - Manual verification queue

Integration Details:
  Authentication: OAuth2 + API Key (from Secrets Manager)
  Rate Limit: 100 requests/minute
  Timeout: 30 seconds
  Retry Strategy: Exponential backoff (max 3 attempts)
```

### 1.5 Error Handling

```json
{
  "error_handlers": [
    {
      "error_type": "INVALID_TAX_ID",
      "http_status": 400,
      "description": "Tax ID format invalid or not found",
      "recovery_actions": [
        "request_corrected_tax_id",
        "queue_for_manual_review"
      ]
    },
    {
      "error_type": "EXTERNAL_API_TIMEOUT",
      "http_status": 504,
      "description": "Dun & Bradstreet API timeout",
      "recovery_actions": [
        "retry_with_backoff",
        "use_cached_data_if_available",
        "escalate_to_human"
      ]
    },
    {
      "error_type": "DOCUMENT_RETRIEVAL_FAILED",
      "http_status": 400,
      "description": "Cannot access provided document URLs",
      "recovery_actions": [
        "request_document_reupload",
        "continue_with_available_docs"
      ]
    },
    {
      "error_type": "DATABASE_CONNECTION_ERROR",
      "http_status": 500,
      "description": "Cannot connect to vendor database",
      "recovery_actions": [
        "retry_connection",
        "use_fallback_database",
        "queue_for_later_processing"
      ]
    }
  ]
}
```

### 1.6 Example Execution

```python
# Request
{
  "vendor_name": "TechSupply Corp",
  "tax_id": "98-7654321",
  "industry": "technology",
  "contact_email": "procurement@techsupply.com",
  "annual_revenue": 5000000,
  "years_in_business": 8,
  "certifications": ["ISO9001", "SOC2"],
  "documents": [
    {
      "document_type": "tax_return",
      "document_url": "https://docs.example.com/tax2024.pdf"
    }
  ]
}

# Response (Success)
{
  "vendor_id": "v-550e8400-e29b-41d4-a716-446655440000",
  "validation_status": "approved",
  "validation_score": 0.92,
  "checks_performed": {
    "tax_id_valid": true,
    "business_registration_valid": true,
    "financial_health": "excellent",
    "certifications_verified": true,
    "documentation_complete": true
  },
  "risk_assessment": {
    "risk_level": "low",
    "risk_factors": []
  },
  "recommendations": [
    "Proceed with contract negotiation",
    "Schedule initial meeting within 5 business days"
  ],
  "timestamp": "2025-11-23T10:30:00Z"
}
```

---

## 2. Check Budget Skill

### 2.1 Specification

**Skill ID:** `check_budget_skill`  
**Agent:** Requisition Agent  
**Category:** Core - Financial  
**Description:** Verifies department budget availability and checks spending limits against purchase requests.

### 2.2 Input Contract

```json
{
  "input_schema": {
    "type": "object",
    "required": ["department_id", "requested_amount"],
    "properties": {
      "department_id": {
        "type": "string",
        "description": "Department identifier from ERP"
      },
      "requested_amount": {
        "type": "number",
        "description": "Amount requested in USD",
        "minimum": 0.01
      },
      "cost_center": {
        "type": "string",
        "description": "Cost center for allocation"
      },
      "fiscal_year": {
        "type": "string",
        "description": "Fiscal year (YYYY format)",
        "pattern": "^[0-9]{4}$"
      },
      "priority": {
        "type": "string",
        "enum": ["critical", "high", "normal", "low"],
        "description": "Purchase priority"
      }
    }
  }
}
```

### 2.3 Output Contract

```json
{
  "output_schema": {
    "type": "object",
    "required": ["budget_available", "available_amount", "timestamp"],
    "properties": {
      "budget_available": {
        "type": "boolean",
        "description": "Is budget available for request?"
      },
      "available_amount": {
        "type": "number",
        "description": "Current available budget"
      },
      "total_budget": {
        "type": "number",
        "description": "Total department budget"
      },
      "spent_amount": {
        "type": "number",
        "description": "Amount already spent"
      },
      "pending_amount": {
        "type": "number",
        "description": "Amount pending approval"
      },
      "budget_utilization_percent": {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "description": "Budget utilization percentage"
      },
      "approval_required": {
        "type": "boolean",
        "description": "Higher approval needed?"
      },
      "approval_chain": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "approval_level": { "type": "integer" },
            "approver_name": { "type": "string" },
            "approver_email": { "type": "string" }
          }
        }
      },
      "message": {
        "type": "string",
        "description": "Human-readable budget status message"
      },
      "timestamp": {
        "type": "string",
        "format": "date-time"
      }
    }
  }
}
```

### 2.4 Tools & External Services

```yaml
Primary Tools:
  - SAP Finance Module: Budget and spending data
  - Oracle Fusion: Alternative ERP source
  - Internal Budget Management System

Fallback:
  - Cache of last 24 hours budget data
  - Manual approval process
```

### 2.5 Example Execution

```json
// Request
{
  "department_id": "DEPT-001",
  "requested_amount": 25000,
  "cost_center": "CC-5001",
  "fiscal_year": "2025",
  "priority": "high"
}

// Response
{
  "budget_available": true,
  "available_amount": 75500,
  "total_budget": 150000,
  "spent_amount": 65000,
  "pending_amount": 9500,
  "budget_utilization_percent": 49.3,
  "approval_required": false,
  "approval_chain": [],
  "message": "Budget available. Purchase can proceed.",
  "timestamp": "2025-11-23T10:31:00Z"
}
```

---

## 3. Search Catalog Skill

### 3.1 Specification

**Skill ID:** `search_catalog_skill`  
**Agent:** Requisition Agent  
**Category:** Core - Product Management  
**Description:** Searches internal and external product catalogs for matching items based on criteria.

### 3.2 Input Contract

```json
{
  "input_schema": {
    "type": "object",
    "required": ["search_query"],
    "properties": {
      "search_query": {
        "type": "string",
        "description": "Product name or description",
        "minLength": 2
      },
      "category": {
        "type": "string",
        "description": "Product category filter"
      },
      "max_price": {
        "type": "number",
        "description": "Maximum acceptable price"
      },
      "supplier_id": {
        "type": "string",
        "description": "Filter to specific supplier"
      },
      "in_stock_only": {
        "type": "boolean",
        "description": "Only return in-stock items"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum results to return",
        "default": 10,
        "maximum": 100
      }
    }
  }
}
```

### 3.3 Output Contract

```json
{
  "output_schema": {
    "type": "object",
    "required": ["results", "total_count"],
    "properties": {
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "product_id": { "type": "string" },
            "product_name": { "type": "string" },
            "category": { "type": "string" },
            "description": { "type": "string" },
            "price": { "type": "number" },
            "currency": { "type": "string" },
            "supplier_id": { "type": "string" },
            "supplier_name": { "type": "string" },
            "in_stock": { "type": "boolean" },
            "stock_quantity": { "type": "integer" },
            "lead_time_days": { "type": "integer" },
            "specifications": { "type": "object" },
            "availability": { "type": "string" },
            "image_url": { "type": "string" }
          }
        }
      },
      "total_count": {
        "type": "integer",
        "description": "Total matching products"
      },
      "search_time_ms": {
        "type": "integer",
        "description": "Search execution time"
      }
    }
  }
}
```

### 3.4 Tools & External Services

```yaml
Primary Tools:
  - SAP Ariba Catalog: Supplier catalog network
  - Internal Product Database: Company approved products
  - Vendor APIs: Real-time inventory from vendors

Integration:
  Timeout: 5 seconds (aggregate timeout)
  Caching: 1 hour for catalog data
  Batch Size: 50 products per call
```

---

## 4. Policy Check Skill

### 4.1 Specification

**Skill ID:** `policy_check_skill`  
**Agent:** Compliance Agent  
**Category:** Core - Compliance  
**Description:** Validates transactions against company procurement policies, compliance rules, and regulatory requirements.

### 4.2 Input Contract

```json
{
  "input_schema": {
    "type": "object",
    "required": ["transaction_type", "vendor_id", "amount"],
    "properties": {
      "transaction_type": {
        "type": "string",
        "enum": ["purchase_order", "contract", "vendor_registration", "payment"],
        "description": "Type of transaction to validate"
      },
      "vendor_id": {
        "type": "string",
        "description": "Vendor identifier"
      },
      "amount": {
        "type": "number",
        "description": "Transaction amount in USD"
      },
      "department": {
        "type": "string",
        "description": "Requesting department"
      },
      "product_category": {
        "type": "string",
        "description": "Product or service category"
      },
      "contract_terms": {
        "type": "object",
        "description": "Key contract terms for validation"
      },
      "requester_id": {
        "type": "string",
        "description": "User requesting transaction"
      }
    }
  }
}
```

### 4.3 Output Contract

```json
{
  "output_schema": {
    "type": "object",
    "required": ["compliant", "checks_passed"],
    "properties": {
      "compliant": {
        "type": "boolean",
        "description": "Does transaction comply with policies?"
      },
      "checks_passed": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "check_name": { "type": "string" },
            "status": { "type": "string", "enum": ["passed", "failed", "warning"] },
            "details": { "type": "string" }
          }
        }
      },
      "violations": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "violation_type": { "type": "string" },
            "severity": { "type": "string", "enum": ["critical", "high", "medium", "low"] },
            "policy_reference": { "type": "string" },
            "remediation": { "type": "string" }
          }
        }
      },
      "approvals_required": {
        "type": "array",
        "items": { "type": "string" }
      }
    }
  }
}
```

### 4.4 Policies Checked

```yaml
Procurement Policies:
  1. Vendor Authorization
     - Vendor must be approved
     - No blocked vendors
     - Valid tax compliance
  
  2. Spending Limits
     - Within department budget
     - Within transaction limits
     - Within contract value
  
  3. Approval Authority
     - Requester has authority
     - Proper approval chain followed
     - Documentation complete
  
  4. Vendor Requirements
     - Insurance coverage valid
     - Certifications current
     - No conflicts of interest
  
  5. Regulatory Compliance
     - Export control (ECRA, EAR)
     - Sanctions screening (OFAC)
     - Country of origin verification
     - Child labor compliance
  
  6. Environmental & Social
     - Diversity supplier status
     - Sustainability certifications
     - Labor practice compliance
```

---

## 5. Extract Contract Skill

### 5.1 Specification

**Skill ID:** `extract_contract_skill`  
**Agent:** Vendor Agent  
**Category:** Utility - Document Processing  
**Description:** Extracts and parses key information from contract documents using NLP and OCR.

### 5.2 Input Contract

```json
{
  "input_schema": {
    "type": "object",
    "required": ["document_url"],
    "properties": {
      "document_url": {
        "type": "string",
        "format": "uri",
        "description": "URL to contract document (PDF, DOCX)"
      },
      "extraction_fields": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Specific fields to extract",
        "examples": [
          "contract_value",
          "start_date",
          "end_date",
          "payment_terms",
          "renewal_clause"
        ]
      }
    }
  }
}
```

### 5.3 Output Contract

```json
{
  "output_schema": {
    "type": "object",
    "properties": {
      "extracted_data": {
        "type": "object",
        "properties": {
          "contract_value": { "type": "number" },
          "currency": { "type": "string" },
          "start_date": { "type": "string", "format": "date" },
          "end_date": { "type": "string", "format": "date" },
          "payment_terms": { "type": "string" },
          "renewal_clause": { "type": "string" },
          "termination_clause": { "type": "string" },
          "vendor_name": { "type": "string" },
          "key_contacts": { "type": "array" }
        }
      },
      "confidence_scores": {
        "type": "object",
        "description": "Confidence for each extracted field (0-1)"
      },
      "extracted_successfully": {
        "type": "boolean"
      }
    }
  }
}
```

### 5.4 Tools & External Services

```yaml
Primary Tools:
  - IBM Watson Document Understanding: Advanced NLP
  - AWS Textract: OCR for scanned documents
  - Spacy: Named entity recognition

Processing:
  Max file size: 50MB
  Timeout: 60 seconds
  Supported formats: PDF, DOCX, PPTX, Images (JPG, PNG)
```

---

## 6. Send Notification Skill

### 6.1 Specification

**Skill ID:** `send_notification_skill`  
**Agent:** Communication Agent  
**Category:** Utility - Communication  
**Description:** Sends notifications to stakeholders via email, SMS, or in-app messages.

### 6.2 Input Contract

```json
{
  "input_schema": {
    "type": "object",
    "required": ["recipient", "notification_type", "content"],
    "properties": {
      "recipient": {
        "type": "object",
        "properties": {
          "email": { "type": "string", "format": "email" },
          "name": { "type": "string" }
        }
      },
      "notification_type": {
        "type": "string",
        "enum": ["approval_request", "status_update", "alert", "confirmation"]
      },
      "content": {
        "type": "object",
        "properties": {
          "subject": { "type": "string" },
          "body": { "type": "string" },
          "action_url": { "type": "string" },
          "data": { "type": "object" }
        }
      },
      "priority": {
        "type": "string",
        "enum": ["urgent", "high", "normal", "low"],
        "default": "normal"
      },
      "channel": {
        "type": "string",
        "enum": ["email", "sms", "in_app", "all"],
        "default": "email"
      }
    }
  }
}
```

### 6.3 Output Contract

```json
{
  "output_schema": {
    "type": "object",
    "required": ["notification_id", "sent_successfully"],
    "properties": {
      "notification_id": { "type": "string" },
      "sent_successfully": { "type": "boolean" },
      "timestamp": { "type": "string", "format": "date-time" },
      "channels_sent": { "type": "array", "items": { "type": "string" } },
      "delivery_status": {
        "type": "object",
        "properties": {
          "email": { "type": "string", "enum": ["sent", "failed", "queued"] },
          "sms": { "type": "string", "enum": ["sent", "failed", "queued"] },
          "in_app": { "type": "string", "enum": ["sent", "failed", "queued"] }
        }
      }
    }
  }
}
```

### 6.4 Tools & External Services

```yaml
Email Service:
  Provider: SendGrid
  Rate Limit: 1000/minute
  Retry Policy: Exponential backoff
  Templates: Pre-defined for common notifications

SMS Service:
  Provider: Twilio
  Rate Limit: 100/minute
  Character Limit: 160 (SMS), 1600 (MMS)

In-App Notifications:
  Database: Redis (Pub/Sub)
  TTL: 7 days
```

---

## 7. Skill Execution Framework

### 7.1 Calling a Skill

```python
# Orchestrator calls skill
class SkillExecutor:
    def execute_skill(self, skill_id, inputs, context):
        """
        Execute a skill within orchestrator context
        
        Args:
            skill_id: Unique skill identifier
            inputs: Dict matching input_schema
            context: Execution context (agent, workflow, user)
        
        Returns:
            Dict matching output_schema
        
        Raises:
            SkillExecutionError: On skill failure
            ValidationError: On schema mismatch
        """
        
        # 1. Validate inputs
        validator = SchemaValidator(self.get_schema(skill_id, "input"))
        if not validator.validate(inputs):
            raise ValidationError("Input validation failed")
        
        # 2. Get skill implementation
        skill = self.load_skill(skill_id)
        
        # 3. Execute with timeout
        try:
            result = timeout(
                skill.execute(inputs, context),
                timeout=skill.timeout
            )
        except TimeoutError:
            return self._handle_timeout(skill_id, inputs, context)
        except Exception as e:
            return self._handle_error(skill_id, inputs, e, context)
        
        # 4. Validate output
        validator = SchemaValidator(self.get_schema(skill_id, "output"))
        if not validator.validate(result):
            raise ValidationError("Output validation failed")
        
        # 5. Log execution
        self.log_execution(skill_id, inputs, result, context)
        
        return result
```

---

## 8. Skill Management Best Practices

1. **Input Validation**: Always validate inputs against schema
2. **Output Validation**: Ensure outputs match contract
3. **Error Handling**: Implement all error handlers
4. **Timeouts**: Always set and respect timeouts
5. **Logging**: Log all executions for audit trail
6. **Caching**: Cache external API responses where appropriate
7. **Retry Logic**: Implement exponential backoff for failures
8. **Monitoring**: Track success rates and performance metrics

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Ready for Implementation
