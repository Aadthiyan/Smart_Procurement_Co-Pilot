import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

def load_agent(name):
    path = f"orchestrate/agents/{name}-agent.json"
    with open(path, 'r') as f:
        return json.load(f)

def simulate_vendor_onboarding():
    agent = load_agent("vendor-onboarding")
    print(f"\n--- Testing {agent['agent_name']} ---")
    print(f"Agent: {agent['prompts']['welcome']}")
    print("User: Acme Corp")
    print(f"Agent: {agent['prompts']['collect_tax_id'].format(vendor_name='Acme Corp')}")
    print("User: 123-456-789")
    print(f"Agent: {agent['prompts']['collect_address'].format(vendor_name='Acme Corp')}")
    print("User: 123 Business Rd")
    print(f"Agent: {agent['prompts']['confirmation'].format(vendor_name='Acme Corp', tax_id='123-456-789', address='123 Business Rd')}")

def simulate_requisition():
    agent = load_agent("requisition")
    print(f"\n--- Testing {agent['agent_name']} ---")
    print(f"Agent: {agent['prompts']['welcome']}")
    print("User: Laptops")
    print(f"Agent: {agent['prompts']['collect_quantity'].format(item_name='Laptops')}")
    print("User: 5")
    print(f"Agent: {agent['prompts']['success'].format(quantity=5, item_name='Laptops')}")

def simulate_compliance():
    agent = load_agent("compliance")
    print(f"\n--- Testing {agent['agent_name']} ---")
    print(f"Agent: {agent['prompts']['policy_check_start'].format(request_id='REQ-001')}")
    print(f"Agent: {agent['prompts']['approval_grant']}")

if __name__ == "__main__":
    simulate_vendor_onboarding()
    simulate_requisition()
    simulate_compliance()
