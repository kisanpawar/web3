"""
QUESTION 3 — Interact with a blockchain network. Execute transactions and requests against a
blockchain network by creating an app to test the network and its rules

    a. Create a Block class and explain how block attributes (index, timestamp, data,
       previous hash, hash) are initialized.

    b. Initialize a blockchain by creating a Blockchain class.

    c. Implement transaction functionality using the transact() method.

    d. Write the valid() function used to verify blockchain integrity.

Block attributes in this program:
    - index (i): block position; set in __init__.
    - timestamp (t): set with time.time() when the block is created.
    - data (d): transaction payload passed into __init__.
    - previous hash (p): hash of the parent block, passed in.
    - hash (h): SHA-256 over index, timestamp, data, and previous hash.

Run: python q03_transact_validate.py
"""
import hashlib
import time


class Block:
    def __init__(s, i, d, p):
        s.i, s.t, s.d, s.p = i, time.time(), d, p
        s.h = hashlib.sha256(f"{i}{s.t}{d}{p}".encode()).hexdigest()


class Blockchain:
    def __init__(s):
        s.c = [Block(0, "Genesis", "0")]

    def transact(s, d):
        s.c.append(Block(len(s.c), d, s.c[-1].h))

    def query(s, i):
        return s.c[i].d if i < len(s.c) else None

    def valid(s):
        return all(s.c[i].p == s.c[i - 1].h for i in range(1, len(s.c)))


if __name__ == "__main__":
    bc = Blockchain()
    bc.transact({"user": "A", "amount": 100})
    bc.transact({"user": "B", "amount": 50})

    print(bc.query(1))
    print(bc.query(2))
    print(bc.valid())
