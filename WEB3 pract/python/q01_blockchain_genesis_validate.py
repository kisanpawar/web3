"""
QUESTION 1 — Create and deploy a blockchain network using Hyperledger Fabric SDK for Java

    a. Write the code snippet for block creation.
       (On a real Fabric network, blocks are produced by the orderer; the Java SDK reads
       committed blocks. See: fabric-java/src/main/java/com/example/fabric/FabricBlockSnippet.java)

    b. Write a Python program to initialize a blockchain and create the Genesis Block

    c. Add at least two blocks and display the blockchain contents.

    d. Write a function to validate the blockchain.

Run: python q01_blockchain_genesis_validate.py
"""
import hashlib
import json
import time


class Block:
    def __init__(self, i, d, p):
        self.i = i
        self.t = time.time()
        self.d = d
        self.p = p
        self.h = hashlib.sha256(f"{i}{self.t}{json.dumps(d)}{p}".encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.c = [Block(0, "Genesis", "0")]

    def add(self, d):
        self.c.append(Block(len(self.c), d, self.c[-1].h))

    def valid(self):
        for i in range(1, len(self.c)):
            if self.c[i].p != self.c[i - 1].h:
                return False
        return True


if __name__ == "__main__":
    bc = Blockchain()
    bc.add({"Asset": "A1", "Owner": "Tom"})
    bc.add({"Asset": "A2", "Owner": "Alice"})

    for b in bc.c:
        print(b.i, b.d, b.h)

    print("Valid:", bc.valid())
