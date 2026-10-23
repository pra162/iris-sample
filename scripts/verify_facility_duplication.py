import json
from collections import Counter


with open(
    "data/processed/datacentermap/facilities_clean.json",
    encoding="utf-8",
) as f:
    facilities = json.load(f)

counter = Counter()

for item in facilities:
    company = item.get("company") or "Unknown"
    name = item.get("name") or "Unnamed Facility"

    counter[(company, name)] += 1

duplicates = {
    key: count
    for key, count in counter.items()
    if count > 1
}

print(f"Found {len(duplicates)} duplicate keys")

for (company, name), count in duplicates.items():
    print(f"{count}x -> {company} | {name}")