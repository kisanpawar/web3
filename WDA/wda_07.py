"""
WDA 7 — Apriori: frequent itemsets + association rules (market basket).

Dependencies: none (pure Python)
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterable


def load_transactions() -> list[frozenset[str]]:
    """Toy market-basket transactions."""
    raw = [
        ["milk", "bread", "eggs"],
        ["milk", "bread"],
        ["milk", "diaper"],
        ["bread", "eggs"],
        ["milk", "bread", "eggs", "butter"],
        ["bread", "butter"],
    ]
    return [frozenset(t) for t in raw]


def support(itemset: frozenset[str], transactions: list[frozenset[str]]) -> float:
    n = len(transactions)
    if n == 0:
        return 0.0
    return sum(1 for t in transactions if itemset <= t) / n


def apriori(transactions: list[frozenset[str]], min_sup: float) -> list[frozenset[str]]:
    items = {i for t in transactions for i in t}
    frequent: list[frozenset[str]] = []
    # L1
    current = [frozenset([i]) for i in sorted(items) if support(frozenset([i]), transactions) >= min_sup]
    frequent.extend(current)
    k = 2
    while current:
        candidates: set[frozenset[str]] = set()
        for a, b in combinations(current, 2):
            u = a | b
            if len(u) == k:
                candidates.add(u)
        next_level = [c for c in candidates if support(c, transactions) >= min_sup]
        frequent.extend(next_level)
        current = next_level
        k += 1
    return frequent


def confidence(rule_left: frozenset[str], rule_right: frozenset[str], transactions: list[frozenset[str]]) -> float:
    denom = support(rule_left, transactions)
    if denom == 0:
        return 0.0
    return support(rule_left | rule_right, transactions) / denom


def association_rules(
    frequent: Iterable[frozenset[str]], transactions: list[frozenset[str]], min_conf: float
) -> list[tuple[frozenset[str], frozenset[str], float]]:
    rules: list[tuple[frozenset[str], frozenset[str], float]] = []
    for itemset in frequent:
        if len(itemset) < 2:
            continue
        items = list(itemset)
        for r in range(1, len(items)):
            for left_tuple in combinations(items, r):
                left = frozenset(left_tuple)
                right = itemset - left
                if not right:
                    continue
                conf = confidence(left, right, transactions)
                if conf >= min_conf:
                    rules.append((left, right, conf))
    return rules


def main() -> None:
    transactions = load_transactions()
    min_sup = 0.4
    min_conf = 0.6
    freq = apriori(transactions, min_sup)
    print(f"Transactions: {len(transactions)} | min_support={min_sup}\n")
    print("Frequent itemsets:")
    for s in sorted(freq, key=lambda x: (len(x), sorted(x))):
        print(f"  {sorted(s)}  support={support(s, transactions):.2f}")

    rules = association_rules(freq, transactions, min_conf)
    print(f"\nAssociation rules (min_confidence={min_conf}):")
    for left, right, conf in sorted(rules, key=lambda x: -x[2]):
        print(f"  {set(left)} => {set(right)}  confidence={conf:.2f}")


if __name__ == "__main__":
    main()
