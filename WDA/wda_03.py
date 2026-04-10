"""
WDA 3 — PageRank via random walk on a small graph (page1..page4).

Dependencies: pip install numpy (optional; pure Python fallback below)
"""

from __future__ import annotations

import random
from collections import defaultdict

# Pages and outgoing links (empty list = dangling; we teleport uniformly)
GRAPH: dict[str, list[str]] = {
    "page1": ["page2", "page3"],
    "page2": ["page3", "page4"],
    "page3": ["page1"],
    "page4": ["page2", "page3"],
}

PAGES = list(GRAPH.keys())
TELEPORT = 0.15
STEPS = 50_000
BURN_IN = 1_000


def random_walk_counts() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    current = random.choice(PAGES)
    for step in range(STEPS + BURN_IN):
        if random.random() < TELEPORT:
            current = random.choice(PAGES)
        else:
            outs = GRAPH[current]
            if not outs:
                current = random.choice(PAGES)
            else:
                current = random.choice(outs)
        if step >= BURN_IN:
            counts[current] += 1
    return dict(counts)


def main() -> None:
    random.seed(42)
    counts = random_walk_counts()
    total = sum(counts.values())
    print("Graph:", GRAPH)
    print(f"Random walk steps (after burn-in {BURN_IN}): {STEPS}\n")
    print("Final PageRank estimates (visit frequency):")
    for p in PAGES:
        pr = counts.get(p, 0) / total if total else 0.0
        print(f"  {p}: {pr:.4f}")


if __name__ == "__main__":
    main()
