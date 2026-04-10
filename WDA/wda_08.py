"""
WDA 8 — Simple crawler: user keyword, fetch page, find occurrences in HTML text.

Dependencies: pip install requests beautifulsoup4
"""

from __future__ import annotations

import re
import sys

import requests
from bs4 import BeautifulSoup


def fetch(url: str) -> str:
    r = requests.get(url, timeout=15, headers={"User-Agent": "WDA-education/1.0"})
    r.raise_for_status()
    return r.text


def find_snippets(text: str, keyword: str, context: int = 40, max_hits: int = 15) -> list[str]:
    low = text.lower()
    key = keyword.lower()
    snippets = []
    start = 0
    while True:
        i = low.find(key, start)
        if i == -1:
            break
        a = max(0, i - context)
        b = min(len(text), i + len(keyword) + context)
        snippets.append(text[a:b].replace("\n", " ").strip())
        start = i + len(keyword)
        if len(snippets) >= max_hits:
            break
    return snippets


def main() -> None:
    keyword = input("Enter keyword: ").strip()
    if not keyword:
        print("Empty keyword.")
        sys.exit(1)
    url = input("Enter URL (default quotes.toscrape.com): ").strip() or "https://quotes.toscrape.com/"
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    visible = soup.get_text("\n", strip=True)
    count = len(re.findall(re.escape(keyword), visible, flags=re.IGNORECASE))
    snippets = find_snippets(visible, keyword)

    print(f"\nURL: {url}")
    print(f"Occurrences (case-insensitive, visible text): {count}")
    print("\nRelevant sections (snippets):")
    for i, s in enumerate(snippets, 1):
        print(f"  {i}. ...{s}...")


if __name__ == "__main__":
    main()
