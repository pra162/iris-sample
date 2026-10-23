import json
from pathlib import Path

file = Path(
    "data/processed/news/matched_news.json"
)

with open(file, encoding="utf-8") as f:
    matches = json.load(f)

print(f"Total Matches : {len(matches)}")

print()

if matches:

    print("First Match")

    print("-" * 80)

    for key, value in matches[0].items():
        print(f"{key}: {value}")