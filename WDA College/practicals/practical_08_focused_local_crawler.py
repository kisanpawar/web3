"""
Practical No 08 — Focused crawler for local search

Aim: Create local HTML files, then rank them by how often comma-separated
keywords appear in the visible text (simple relevance score).

Dependencies: pip install beautifulsoup4
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict

from bs4 import BeautifulSoup

PRACTICAL_NAME = "Practical 08 — Focused local crawler"

folder_path = "local_pages"


def main() -> None:
    print(PRACTICAL_NAME)
    os.makedirs(folder_path, exist_ok=True)

    html_files = {
        "page1.html": "<html><body><h1>Rose Wood Furniture</h1><p>Rose wood is used for premium furniture.</p></body></html>",
        "page2.html": "<html><body><h1>Flower Shop</h1><p>Fresh rose flowers available here.</p></body></html>",
        "page3.html": "<html><body><h1>Carpentry</h1><p>Quality wood and teak furniture manufacturing.</p></body></html>",
    }

    for name, content in html_files.items():
        with open(os.path.join(folder_path, name), "w", encoding="utf-8") as f:
            f.write(content)

    raw = (
        sys.argv[1]
        if len(sys.argv) > 1
        else input("Enter keywords (comma separated): ")
    )
    keywords = raw.lower().split(",")

    results: dict[str, int] = defaultdict(int)

    for file in os.listdir(folder_path):
        if file.endswith(".html"):
            path = os.path.join(folder_path, file)
            with open(path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            text = soup.get_text(" ").lower()
            score = sum(text.count(k.strip()) for k in keywords)
            if score > 0:
                results[file] = score

    print("\nFocused Local Search Results:\n")
    for page, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(page, "-> Relevance Score:", score)


if __name__ == "__main__":
    main()
