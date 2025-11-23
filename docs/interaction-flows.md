# User Interaction Flows

## 1. Vendor Onboarding Flow
**User**: "I want to add a new vendor."
**Bot**: "I can help you onboard a new vendor. Please provide the Vendor Name and Tax ID."
**User**: "Acme Corp, 123-456"
**Bot**: "Thank you. I have registered Acme Corp. Sending welcome email..."

## 2. Purchase Request Flow
**User**: "I need to buy 5 laptops."
**Bot**: "I can help with that purchase. What item do you need and how many?" (Context aware: "I see you want 5 laptops.")
**Bot**: "Checking budget... Budget approved. Request REQ-101 created."

## 3. Status Check Flow
**User**: "What is the status of REQ-001?"
**Bot**: "Request REQ-001 is currently **Approved**."

## 4. Fallback Flow
**User**: "Hello"
**Bot**: "I understood that you are feeling neutral. Could you please clarify your request? Try saying 'I want to buy a laptop'."
