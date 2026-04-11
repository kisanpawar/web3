"""
Practical No 09 — Plagiarism-style detection using deep text comparison

Aim: Compare a document to texts fetched from the web or local references
using TF-IDF cosine similarity (as in the practical file). The original PDF
scrapes DuckDuckGo HTML, which is brittle; this version uses optional
duckduckgo-search, and falls back to built-in reference paragraphs so the
lab always runs offline.

Dependencies: pip install requests beautifulsoup4 scikit-learn
Optional: pip install duckduckgo-search
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PRACTICAL_NAME = "Practical 09 — Plagiarism / similarity check"

text = """Python is a high-level, interpreted programming language known for its simplicity and readability.
It supports multiple programming paradigms including procedural, object-oriented, and functional programming.
Python has a rich ecosystem of libraries and frameworks that make it popular for web development, data analysis,
artificial intelligence, machine learning, and scientific computing. Its syntax emphasizes code readability,
allowing developers to express concepts in fewer lines of code compared to many other languages.
With a large and active community, Python continues to grow as one of the most widely used programming languages in the world."""

# Offline reference corpus (simulates “documents online” when search is unavailable)
REFERENCE_URLS_TEXT: dict[str, str] = {
    "https://example.edu/ref/python-intro.txt": (
        "Python is easy to read and is used in data science and machine learning. "
        "Developers like its libraries for web and AI."
    ),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WDA-Practical/1.0; +https://example.edu)"
}


def search_duckduckgo(q: str, max_results: int = 5) -> list[str]:
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            return [
                r["href"]
                for r in ddgs.text(q, max_results=max_results)
                if r.get("href")
            ]
    except Exception:
        return []


def get_text(url: str) -> str:
    try:
        if url in REFERENCE_URLS_TEXT:
            return REFERENCE_URLS_TEXT[url]
        s = BeautifulSoup(
            requests.get(url, timeout=5, headers=HEADERS).text, "html.parser"
        )
        for t in s(["script", "style"]):
            t.decompose()
        return s.get_text(" ")
    except Exception:
        return ""


def score(d1: str, d2: str) -> float:
    if not d1.strip() or not d2.strip():
        return 0.0
    v = TfidfVectorizer(stop_words="english")
    m = v.fit_transform([d1, d2])
    return float(cosine_similarity(m[0:1], m[1:2])[0, 0])


def main() -> None:
    print(PRACTICAL_NAME)
    results: list[tuple[str, float]] = []

    sentences = [x.strip() for x in text.split(".") if x.strip()][:5]
    seen_urls: set[str] = set()

    for s in sentences:
        for url in search_duckduckgo(s):
            if url in seen_urls:
                continue
            seen_urls.add(url)
            body = get_text(url)
            sc = score(text, body)
            if sc > 0.3:
                results.append((url, round(sc * 100, 2)))

    # Always also check bundled references (educational fallback)
    for url, body in REFERENCE_URLS_TEXT.items():
        sc = score(text, body)
        if sc > 0.05:
            results.append((url, round(sc * 100, 2)))

    if results:
        for u, v in sorted(results, key=lambda x: x[1], reverse=True):
            print(f"{u} -> Similarity: {v}%")
    else:
        print("No significant plagiarism detected (above threshold).")


if __name__ == "__main__":
    main()
