import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'orchestrate/skills'))

# Mock Agent Responses for Simulation
def mock_agent_action(agent, action, context):
    print(f"  [{agent}] performing '{action}'...")
    
    if action == "collect_vendor_data":
        return {"vendor_name": "Acme Corp", "tax_id": "123-456"}
    
    elif action == "validate_data":
        return {"valid": True}
    
    elif action == "check_sanctions_and_policy":
        # Simulate conditional logic
        if context.get("vendor_name") == "Banned Corp":
            return {"compliance_passed": False}
        return {"compliance_passed": True}
    
    elif action == "send_welcome_email":
        print(f"  -> Email sent to {context.get('vendor_name')}")
        return {}
        
    elif action == "intake_request":
        return {"item": "Laptop", "cost": 2000}
        
    elif action == "check_budget":
        # Simulate budget check
        if context.get("cost") > 50000:
            return {"budget_available": False}
        return {"budget_available": True}
        
    elif action == "validate_policy":
        return {"policy_passed": True}
        
    elif action == "route_for_approval":
        print("  -> Routed to Manager")
        return {}
        
    elif action == "notify_approvers":
        print("  -> Notification sent")
        return {}

    return {}

def run_workflow(workflow_file):
    with open(workflow_file, 'r') as f:
        workflow = json.load(f)
        
    print(f"\n=== Running {workflow['workflow_name']} ===")
    
    context = {}
    current_step_id = workflow['steps'][0]['id']
    
    while current_step_id != "end":
        # Find step definition
        step = next((s for s in workflow['steps'] if s['id'] == current_step_id), None)
        if not step:
            print(f"Error: Step {current_step_id} not found.")
            break
            
        # Execute Action
        result = mock_agent_action(step['agent'], step['action'], context)
        context.update(result)
        
        # Determine Next Step
        next_step = step.get('next')
        
        if isinstance(next_step, dict):
            # Conditional Logic
            condition_key = next_step['condition']
            condition_value = context.get(condition_key)
            
            if condition_value:
                current_step_id = next_step['true']
                print(f"  -> Condition '{condition_key}' is True. Going to {current_step_id}")
            else:
                current_step_id = next_step['false']
                print(f"  -> Condition '{condition_key}' is False. Going to {current_step_id}")
        else:
            current_step_id = next_step
            
    print("=== Workflow Completed ===\n")

if __name__ == "__main__":
    run_workflow("orchestrate/workflows/supplier-onboarding-workflow.json")
    run_workflow("orchestrate/workflows/purchase-request-workflow.json")
