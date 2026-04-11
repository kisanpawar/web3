"""
Practical No 05 — Text mining and webpage pre-processing (meta information)

Aim: Fetch a web page (local or online), extract meta tags and visible text,
remove stopwords, and show word frequency.

Dependencies: pip install requests beautifulsoup4 nltk
"""

from __future__ import annotations

import re
from collections import Counter

import nltk
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

PRACTICAL_NAME = "Practical 05 — Text mining & meta tags"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WDA-Practical/1.0; +https://example.edu)"
}


def main() -> None:
    print(PRACTICAL_NAME)
    nltk.download("stopwords", quiet=True)

    url = "https://www.wikipedia.org/"
    soup = BeautifulSoup(
        requests.get(url, headers=HEADERS, timeout=20).text, "html.parser"
    )

    meta = {"title": soup.title.string if soup.title else "N/A"}
    for m in soup.find_all("meta"):
        if m.get("name"):
            meta[m.get("name").lower()] = m.get("content")

    for t in soup(["script", "style"]):
        t.decompose()

    text = soup.get_text(" ").lower()
    text = re.sub(r"[^a-z\s]", "", text)

    tokens = [w for w in text.split() if w not in stopwords.words("english")]
    freq = Counter(tokens)

    print("META INFO\n", meta)
    print("\nTOP WORDS\n", freq.most_common(10))


if __name__ == "__main__":
    main()
