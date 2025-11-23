# Demo Video Script (3-5 Minutes)

## Intro (0:00 - 0:30)
**Visual:** Title Slide -> Split screen with User and App.
**Audio:** "Hi, we are Team [Name], and this is the Smart Procurement Co-Pilot. Procurement today is bogged down by manual emails and spreadsheets. We built an Agentic AI solution using IBM watsonx to automate the chaos."

## Scenario 1: Supplier Onboarding (Autonomous) (0:30 - 1:30)
**Visual:** Streamlit Chat Interface.
**Action:** User types "I want to onboard a new vendor."
**Audio:** "Let's start with Vendor Onboarding. I'll add 'Quantum Systems Inc', a new tech hardware supplier."
**Action:** User enters "Quantum Systems Inc", Tax ID "99-8877665", Industry "Technology Hardware".
**Audio:** "The Vendor Agent autonomously validates the Tax ID and checks our internal policies for hardware suppliers. Using watsonx.ai, it assesses the risk profile."
**Visual:** Bot responds "✅ Vendor 'Quantum Systems Inc' has been successfully onboarded."
**Audio:** "In seconds, the vendor is approved and ready for business, without manual paperwork."

## Scenario 2: Purchase Request & Budget Check (1:30 - 2:30)
**Visual:** Chat Interface.
**Action:** User types "I need to buy 5 ergonomic chairs for IT."
**Audio:** "Now, let's make a purchase. The Requisition Agent understands I need chairs for the IT department."
**Visual:** Bot shows budget check and catalog results.
**Audio:** "It instantly checks the IT budget—we have $150k available—and finds the best price from our catalog: 'Herman Miller Aeron' at $1,200."
**Action:** User confirms purchase.
**Visual:** Bot responds "Request REQ-101 created. Pending Approval."
**Audio:** "Since the total is $6,000, it automatically routes this to a manager for approval, enforcing our spending policy."

## Scenario 3: Policy Compliance (2:30 - 3:15)
**Visual:** Chat Interface.
**Action:** User types "Order a $12,000 espresso machine."
**Audio:** "What if I try to buy something non-compliant? Watch the Compliance Agent intervene."
**Visual:** Bot responds "⚠️ Policy Violation Detected."
**Audio:** "The agent autonomously blocks the request, citing the luxury item policy. It protects the company from unauthorized spend."

## Scenario 4: Observability (3:15 - 3:45)
**Visual:** Dashboard Tab.
**Audio:** "Finally, managers get full visibility. We can track REQ-101's status and see the audit trail of every AI decision."

## Technical Deep Dive (3:30 - 4:30)
**Visual:** Architecture Diagram.
**Audio:** "Under the hood, we use a multi-agent architecture orchestrated by Python. We use IBM Cloudant for data persistence and IBM NLU for understanding user sentiment. We implemented strict Pydantic contracts to ensure reliability."

## Conclusion (4:30 - 5:00)
**Visual:** "Future Roadmap" Slide.
**Audio:** "This is just the beginning. We plan to add Voice interaction and predictive analytics next. Thank you for watching!"
