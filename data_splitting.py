import json
import os

input_file = "articles.json"
output_dir = "./data"

os.makedirs(output_dir, exist_ok=True)

with open(input_file, "r", encoding="utf-8") as f:
    articles = json.load(f)

for article in articles:
    pmcid = article.get("pmcid")
    if pmcid:
        output_path = os.path.join(output_dir, f"{pmcid}.json")
        with open(output_path, "w", encoding="utf-8") as out_f:
            json.dump(article, out_f, ensure_ascii=False, indent=2)