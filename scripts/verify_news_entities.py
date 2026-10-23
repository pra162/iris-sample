import json
from pathlib import Path

file = Path(
    "data/processed/news/news_entities.json"
)

with open(file, encoding="utf-8") as f:
    entities = json.load(f)

print(f"Total Entities : {len(entities)}")

print()

print("First Entity")

print("-" * 80)

for key, value in entities[0].items():
    print(f"{key}: {value}")