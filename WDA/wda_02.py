"""
Write a Python program to scrape data from an online social media website (or any public webpage for simulation purposes).
    a. Send a request to a webpage using appropriate libraries (e.g., requests).
    b. Parse the HTML content using a library such as BeautifulSoup.
    c. Extract specific data such as user names, posts, or comments.
    d. Store the extracted data in a structured format (e.g., list, JSON, or CSV).
    e. Display the extracted data.
Dependencies: pip install requests beautifulsoup4
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class PostItem:
    user_name: str
    post_text: str


def fetch_page(url: str) -> str:
    headers = {"User-Agent": "WDA-education-bot/1.0"}
    r = requests.get(url, timeout=15, headers=headers)
    r.raise_for_status()
    return r.text


def parse_quotes(html: str) -> list[PostItem]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[PostItem] = []
    for div in soup.select("div.quote"):
        author = div.select_one("small.author")
        text = div.select_one("span.text")
        if author and text:
            items.append(
                PostItem(
                    user_name=author.get_text(strip=True),
                    post_text=text.get_text(strip=True).strip('"'),
                )
            )
    return items


def save_structured(items: list[PostItem], base: str = "wda02_output") -> None:
    # list in memory already; also JSON + CSV
    as_dicts = [{"user_name": i.user_name, "post_text": i.post_text} for i in items]
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(as_dicts, f, indent=2, ensure_ascii=False)
    with open(base + ".csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["user_name", "post_text"])
        w.writeheader()
        w.writerows(as_dicts)


def main() -> None:
    url = "https://quotes.toscrape.com/"
    print(f"GET {url}")
    html = fetch_page(url)
    items = parse_quotes(html)
    print(f"Extracted {len(items)} items.\n")
    save_structured(items)

    print("--- Sample (JSON path: wda02_output.json) ---")
    for row in items[:5]:
        print(f"User: {row.user_name}\nPost: {row.post_text[:120]}...\n")


if __name__ == "__main__":
    main()
