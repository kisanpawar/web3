"""
QUESTION 9 — Build a web app that uses Hyperledger Fabric to track and trace member rewards

    a. Understand the role of blockchain in web-based reward tracking systems.

    b. Create blocks, implement hashing, and initialize the chain with a Genesis block.

    c. Implement methods to assign reward points to members and update their total rewards.

    d. Implement tracking and tracing of member rewards.

(This script simulates the on-chain behaviour in Python; a full web UI would call Fabric APIs.)

Run: python q09_member_rewards_trace.py
"""
import hashlib
import time


class Block:
    def __init__(s, i, d, p):
        s.h = hashlib.sha256(f"{i}{time.time()}{d}{p}".encode()).hexdigest()
        s.d = d


class RewardChain:
    def __init__(s):
        s.c = [Block(0, "Genesis", "0")]
        s.r = {}

    def reward(s, m, p):
        s.r[m] = s.r.get(m, 0) + p
        s.c.append(Block(len(s.c), {"member": m, "points": p, "total": s.r[m]}, s.c[-1].h))

    def trace(s, m):
        return [b.d for b in s.c if isinstance(b.d, dict) and b.d["member"] == m]


if __name__ == "__main__":
    rc = RewardChain()
    rc.reward("M1", 10)
    rc.reward("M2", 20)
    rc.reward("M1", 15)

    print("Member M1 trace:", rc.trace("M1"))
    print("Member M2 trace:", rc.trace("M2"))
