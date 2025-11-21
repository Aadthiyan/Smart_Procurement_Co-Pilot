def check_budget(department_id, amount):
    """
    Checks if the department has enough budget for the amount.
    Mock implementation.
    """
    # Mock budget data
    budgets = {
        "IT": 50000,
        "HR": 10000,
        "Marketing": 20000
    }
    
    current_budget = budgets.get(department_id, 0)
    return {
        "approved": current_budget >= amount,
        "remaining_budget": current_budget - amount if current_budget >= amount else current_budget
    }

if __name__ == "__main__":
    print(check_budget("IT", 5000))
