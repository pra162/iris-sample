import json
from pprint import pprint

with open("data/raw/mastr/merged.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 80)
print(f"Total records: {len(data)}")

print("\nAvailable Fields:")
for field in sorted(data[0].keys()):
    print(field)

print("\nFirst Record:")
pprint(data[0])