"""
Practical No 07 — Basic web crawler for user-defined keywords

Aim: Starting from a seed URL, crawl linked pages (bounded count), and list
URLs whose visible text contains the keyword.

Dependencies: pip install requests beautifulsoup4
"""

from __future__ import annotations

import sys

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

PRACTICAL_NAME = "Practical 07 — Keyword web crawler"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WDA-Practical/1.0; +https://example.edu)"
}


def main() -> None:
    print(PRACTICAL_NAME)
    keyword = (
        sys.argv[1].lower()
        if len(sys.argv) > 1
        else input("Enter keyword to search: ").lower()
    )
    start_url = "https://www.wikipedia.org/"
    max_pages = 10

    visited: set[str] = set()
    to_visit: list[str] = [start_url]
    matched_pages: list[str] = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            visited.add(url)

            text = soup.get_text(" ").lower()
            if keyword in text:
                matched_pages.append(url)

            for link in soup.find_all("a", href=True):
                next_url = urljoin(url, link["href"])
                if urlparse(next_url).scheme in ("http", "https"):
                    if next_url not in visited and next_url not in to_visit:
                        to_visit.append(next_url)

        except Exception:
            continue

    print("\nPages containing keyword:", keyword)
    for page in matched_pages:
        print(page)


if __name__ == "__main__":
    main()
