import json
from pathlib import Path

file = Path("data/raw/news/news_raw.json")

with open(file, encoding="utf-8") as f:
    news = json.load(f)

print(f"Total Articles : {len(news)}")

print()

print("First Article")

print("-" * 80)

for key, value in news[0].items():
    print(f"{key}:")
    print(value)
    print()