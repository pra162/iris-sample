import json

with open("data/raw/overpass/page_1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data.keys())
print()
print("Total Elements:", len(data["elements"]))
print()
print(data["elements"][0])