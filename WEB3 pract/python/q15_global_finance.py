"""
QUESTION 15 — Create a global finance blockchain application with IBM Blockchain Platform
Extension for VS Code. Develop a Node.js smart contract and web app for a Global Finance with
blockchain use case.

    a. Create blocks with attributes (index, timestamp, data, previous hash, hash).

    b. Initialize the blockchain with a Genesis block.

    c. Develop transaction functionality for global finance.

    d. Display and analyze blockchain data.

(This Python script mirrors the same data model; Node.js chaincode would live in a Fabric project.)

Run: python q15_global_finance.py
"""
import hashlib
import time


class Block:
    def __init__(self, i, t, d, p):
        self.i, self.t, self.d, self.p = i, t, d, p
        self.h = hashlib.sha256(f"{i}{t}{d}{p}".encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.c = [Block(0, time.time(), "Genesis", "0")]

    def add(self, d):
        b = self.c[-1]
        self.c.append(Block(len(self.c), time.time(), d, b.h))

    def show(self):
        for b in self.c:
            print(b.i, b.d, b.h, b.p, sep="\n")
            print("-" * 30)


if __name__ == "__main__":
    bc = Blockchain()
    bc.add("USA sends $2000 to INDIA")
    bc.add("INDIA sends $500 to UK")
    bc.add("UK sends $1000 to USA")
    bc.show()
