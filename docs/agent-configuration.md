# Agent Configuration Documentation

## 1. Vendor Onboarding Agent
**Purpose**: Streamline vendor registration and validation.
**Key Prompts**:
- Welcome: "Hello! I am the Vendor Onboarding Agent..."
- Data Collection: Asks for Name, Tax ID, Address.
**Flow**:
1. Ask Name
2. Ask Tax ID (Validate format)
3. Ask Address
4. Confirm & Trigger Compliance Check

## 2. Requisition Agent
**Purpose**: Facilitate purchase requests.
**Key Prompts**:
- Welcome: "Hi! I'm here to help you buy what you need..."
- Data Collection: Item Name, Quantity, Delivery Date.
**Validation**:
- Quantity must be > 0.
- Budget check must pass.

## 3. Compliance Agent
**Purpose**: Ensure policy adherence.
**Policies**:
- **POL-001**: Max transaction limit $5000.
- **POL-002**: Vendor validity check.
**Responses**:
- Alerts on violation.
- Grants approval if passed.

## Testing Instructions
To test these agents locally, run the simulation script:
`python tests/simulate_agents.py`
