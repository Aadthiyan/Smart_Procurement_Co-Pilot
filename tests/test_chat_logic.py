import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mocking Streamlit for testing logic
class MockSessionState(dict):
    def __init__(self):
        self.messages = []

def test_chat_logic():
    from backend.orchestrator import orchestrator
    
    print("\n=== Testing Chat Logic (via Orchestrator) ===")
    
    # Test 1: Vendor Intent
    input1 = "I want to add a new vendor"
    result1 = orchestrator.route_message(input1)
    response1 = result1["response"]
    print(f"Input: {input1}")
    print(f"Response: {response1}")
    assert "Vendor Name" in response1
    
    # Test 2: Purchase Intent
    input2 = "I need to buy some laptops"
    result2 = orchestrator.route_message(input2)
    response2 = result2["response"]
    print(f"\nInput: {input2}")
    print(f"Response: {response2}")
    assert "help with that purchase" in response2
    
    # Test 3: Fallback
    input3 = "The weather is nice"
    result3 = orchestrator.route_message(input3)
    response3 = result3["response"]
    print(f"\nInput: {input3}")
    print(f"Response: {response3}")
    assert "Could you please clarify" in response3

if __name__ == "__main__":
    test_chat_logic()
