"""
QUESTION 7 — Use blockchain to track fitness club rewards.

    a. Implement block creation and initialize the chain with a Genesis block.

    b. Design a rewards management system.

    c. Track and verify reward transactions using blockchain.

Run: python q07_fitness_rewards.py
"""
import hashlib
import time


class Block:
    def __init__(s, i, d, p):
        s.i, s.t, s.d, s.p = i, time.time(), d, p
        s.h = hashlib.sha256(f"{i}{s.t}{d}{p}".encode()).hexdigest()


class Chain:
    def __init__(s):
        s.c = [Block(0, "Genesis", "0")]

    def add(s, d):
        s.c.append(Block(len(s.c), d, s.c[-1].h))


class Rewards:
    def __init__(s):
        s.c, s.r = Chain(), {}

    def reward(s, m, p):
        s.r[m] = s.r.get(m, 0) + p
        s.c.add((m, p, s.r[m]))


if __name__ == "__main__":
    r = Rewards()
    r.reward("m1", 10)
    r.reward("m2", 20)
    r.reward("m1", 15)
    print(r.r)
    for b in r.c.c:
        print(b.i, b.d, b.h)
