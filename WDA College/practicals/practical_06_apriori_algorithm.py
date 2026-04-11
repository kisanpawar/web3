"""
Practical No 06 — Apriori algorithm (case study)

Aim: Mine frequent itemsets from transactions with a minimum support count.

Dependencies: stdlib only
"""

from __future__ import annotations

from itertools import combinations

PRACTICAL_NAME = "Practical 06 — Apriori frequent itemsets"

transactions = [
    {"milk", "bread", "butter"},
    {"bread", "butter"},
    {"milk", "bread"},
    {"milk", "butter"},
    {"bread", "butter"},
]

min_support = 2


def get_support(itemset: set) -> int:
    return sum(1 for t in transactions if itemset.issubset(t))


def main() -> None:
    print(PRACTICAL_NAME)
    items = set().union(*transactions)
    freq_itemsets: list[set] = []

    L1 = [{item} for item in items if get_support({item}) >= min_support]
    freq_itemsets.extend(L1)

    k = 2
    current_L = L1

    while current_L:
        candidates = [set(c) for c in combinations(set().union(*current_L), k)]
        next_L: list[set] = []
        for c in candidates:
            if get_support(c) >= min_support and c not in next_L:
                next_L.append(c)
        freq_itemsets.extend(next_L)
        current_L = next_L
        k += 1

    print("Frequent Itemsets:")
    for itemset in freq_itemsets:
        print(itemset, "Support:", get_support(itemset))


if __name__ == "__main__":
    main()
