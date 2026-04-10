"""
WDA 9 — Plagiarism-style similarity: preprocess input + compare to reference docs
using TF-IDF cosine similarity (simulates multi-source check with a local corpus).

Dependencies: pip install scikit-learn
"""

from __future__ import annotations

import re
import string

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", " ", text)
    words = text.split()
    # small inline stopword list to avoid nltk dependency
    sw = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "is",
        "are",
        "was",
        "were",
        "it",
        "that",
        "this",
        "with",
        "as",
        "at",
        "by",
    }
    return " ".join(w for w in words if w not in sw and len(w) > 1)


def reference_corpus() -> list[str]:
    """Simulated 'online' documents stored locally."""
    return [
        "Machine learning models learn patterns from labeled training data and generalize to new examples.",
        "Deep neural networks use many layers to represent hierarchical features from raw inputs.",
        "Natural language processing helps computers understand and generate human language text.",
        "Random forests combine decision trees and aggregate votes to improve prediction stability.",
    ]


def segment_chunks(text: str, max_words: int = 40) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words) if words[i : i + max_words]]


def main() -> None:
    print("Paste your document (end with a blank line):")
    lines: list[str] = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    raw = "\n".join(lines).strip()
    if not raw:
        raw = (
            "Machine learning models learn patterns from training data "
            "and generalize to new examples in production."
        )
        print("(Using demo text — you can run again and paste your own.)\n")

    cleaned = preprocess(raw)
    refs = [preprocess(r) for r in reference_corpus()]
    all_docs = [cleaned] + refs
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(all_docs)
    sims = cosine_similarity(matrix[0:1], matrix[1:])[0]

    print("\n--- Preprocessed input (truncated) ---")
    print(cleaned[:400] + ("..." if len(cleaned) > 400 else ""))

    print("\n--- Cosine similarity vs each reference ---")
    for i, (s, ref_plain) in enumerate(zip(sims, reference_corpus())):
        print(f"  Ref {i + 1}: score={s:.3f}  |  {ref_plain[:70]}...")

    best_idx = int(sims.argmax())
    best_score = float(sims[best_idx])
    print(f"\nBest match: reference #{best_idx + 1} (cosine={best_score:.3f})")

    # Flag overlapping sentences / chunks
    chunks = segment_chunks(cleaned)
    if chunks:
        chunk_mat = vectorizer.transform(chunks)
        ref_mat = vectorizer.transform(refs)
        chunk_sims = cosine_similarity(chunk_mat, ref_mat)
        threshold = 0.35
        print(f"\n--- Chunks with similarity >= {threshold} to any reference ---")
        for ci, row in enumerate(chunk_sims):
            j = int(row.argmax())
            if row[j] >= threshold:
                print(f"  Chunk {ci + 1} ~ ref {j + 1} (sim={row[j]:.3f}): {chunks[ci][:120]}...")


if __name__ == "__main__":
    main()
