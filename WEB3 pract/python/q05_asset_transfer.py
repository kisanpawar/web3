"""
QUESTION 5 — Deploy an asset-transfer app using blockchain. Learn app development within a
Hyperledger Fabric network.

    a. Implement block creation and initialize the blockchain with a Genesis block.

    b. Implement asset creation and ownership transfer functionalities.

    c. Execute transactions, store them in the blockchain, and observe how the system
       records and maintains asset ownership.

Run: python q05_asset_transfer.py
"""
import hashlib
import time


class B:
    def __init__(s, i, d, p):
        s.i, s.d, s.p = i, d, p
        s.h = hashlib.sha256(f"{i}{time.time()}{d}{p}".encode()).hexdigest()


class BC:
    def __init__(s):
        s.c = [B(0, "Genesis", "0")]

    def add(s, d):
        s.c.append(B(len(s.c), d, s.c[-1].h))


class App:
    def __init__(s):
        s.bc, s.a = BC(), {}

    def create(s, i, o, v):
        s.a[i] = {"owner": o, "value": v}
        s.bc.add(("create", i, o, v))

    def transfer(s, i, n):
        s.a[i]["owner"] = n
        s.bc.add(("transfer", i, n))


if __name__ == "__main__":
    app = App()
    app.create("A1", "Alice", 500)
    app.transfer("A1", "Bob")
    print(app.a["A1"])
    print(app.bc.c[1].d, app.bc.c[2].d)
