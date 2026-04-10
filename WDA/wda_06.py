"""
WDA 6 — Fetch page (or local HTML), extract meta tags, preprocess text.

Dependencies: pip install requests beautifulsoup4 nltk
(first run may need: python -c "import nltk; nltk.download('stopwords')")
"""

from __future__ import annotations

import os
import re
import string

import requests
from bs4 import BeautifulSoup

try:
    from nltk.corpus import stopwords
except ImportError:
    stopwords = None  # type: ignore


def get_stopwords():
    if stopwords is None:
        return set()
    try:
        return set(stopwords.words("english"))
    except LookupError:
        print("Run: python -c \"import nltk; nltk.download('stopwords')\"")
        return set()


def fetch_or_load() -> str:
    path = os.environ.get("WDA_LOCAL_HTML")
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    url = os.environ.get("WDA_PAGE_URL", "https://quotes.toscrape.com/")
    r = requests.get(url, timeout=15, headers={"User-Agent": "WDA-education/1.0"})
    r.raise_for_status()
    return r.text


def extract_meta(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    out: dict[str, str] = {}
    if soup.title and soup.title.string:
        out["title"] = soup.title.string.strip()
    for meta in soup.find_all("meta"):
        name = (meta.get("name") or meta.get("property") or "").lower()
        content = meta.get("content") or ""
        if name == "description":
            out["meta_description"] = content.strip()
        if name == "keywords":
            out["meta_keywords"] = content.strip()
    return out


def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", " ", text)
    words = text.split()
    sw = get_stopwords()
    if sw:
        words = [w for w in words if w not in sw and len(w) > 1]
    return " ".join(words)


def main() -> None:
    html = fetch_or_load()
    meta = extract_meta(html)
    combined = " ".join(meta.values())
    processed = preprocess(combined) if combined.strip() else preprocess(
        BeautifulSoup(html, "html.parser").get_text(" ", strip=True)[:2000]
    )

    print("--- Extracted meta ---")
    for k, v in meta.items():
        print(f"{k}: {v[:200]}{'...' if len(v) > 200 else ''}")
    if not meta:
        print("(no title/meta description/keywords; used body snippet for mining)")

    print("\n--- Processed text (lowercase, no stopwords/punct) ---")
    print(processed[:800] + ("..." if len(processed) > 800 else ""))


if __name__ == "__main__":
    main()
