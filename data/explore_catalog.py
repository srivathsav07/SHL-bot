import json

# Load the catalog
with open('data/shl_tests.json', 'r', encoding='utf-8') as f:
    tests = json.load(f)

# Show how many tests
print(f"Total tests in catalog: {len(tests)}")

# Show first 3 tests with correct field names
print("\nFirst 3 tests:")
for i, test in enumerate(tests[:3]):
    name = test.get('name', 'No name')
    link = test.get('link', 'No URL')
    print(f"{i+1}. {name}")
    print(f"   Link: {link}")
    print()