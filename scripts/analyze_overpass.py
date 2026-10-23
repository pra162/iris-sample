import json
from collections import Counter

with open("data/raw/overpass/page_1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

elements = data["elements"]

print("=" * 60)
print(f"Total Elements: {len(elements)}")

# ----------------------------------------------------
# Element Types
# ----------------------------------------------------
types = Counter(e["type"] for e in elements)

print("\nElement Types")
for key, value in types.items():
    print(f"{key:<12} {value}")

# ----------------------------------------------------
# Power Types
# ----------------------------------------------------
power = Counter()

for e in elements:
    tags = e.get("tags", {})
    if "power" in tags:
        power[tags["power"]] += 1

print("\nPower Types")
for key, value in power.most_common():
    print(f"{key:<20} {value}")

# ----------------------------------------------------
# Most Common Tags
# ----------------------------------------------------
tag_counter = Counter()

for e in elements:
    for key in e.get("tags", {}):
        tag_counter[key] += 1

print("\nTop 25 Tags")
for key, value in tag_counter.most_common(25):
    print(f"{key:<25} {value}")