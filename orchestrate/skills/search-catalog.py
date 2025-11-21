def search_catalog(query):
    """
    Searches the product catalog for items matching the query.
    Mock implementation.
    """
    catalog = [
        {"id": "1", "name": "Laptop", "price": 1200},
        {"id": "2", "name": "Monitor", "price": 300},
        {"id": "3", "name": "Keyboard", "price": 50},
        {"id": "4", "name": "Mouse", "price": 25}
    ]
    
    results = [item for item in catalog if query.lower() in item['name'].lower()]
    return results

if __name__ == "__main__":
    print(search_catalog("lap"))
