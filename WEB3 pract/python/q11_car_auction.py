"""
QUESTION 11 — Car auction network: A Hello World example with Hyperledger Fabric Node SDK and
IBM Blockchain Starter Plan. Use Hyperledger Fabric to invoke chaincode while storing results
and data in the starter plan.

    a. Understand the concept of a blockchain-based car auction system.

    b. Create blocks, implement hashing, and initialize the blockchain with a Genesis block
       to store auction data.

    c. Develop car auction functionalities.

    d. Implement querying and history tracking of auction data.

Run: python q11_car_auction.py
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

    def invoke(s, d):
        s.c.append(Block(len(s.c), d, s.c[-1].h))

    def query(s, k):
        return [b.d for b in s.c if isinstance(b.d, dict) and b.d.get("car_id") == k]


class Auction:
    def __init__(s):
        s.bc = Blockchain()
        s.cars = {}

    def add_car(s, car_id, owner, price):
        s.cars[car_id] = {"owner": owner, "price": price}
        s.bc.invoke({"car_id": car_id, "owner": owner, "price": price, "action": "add"})

    def bid(s, car_id, bidder, bid):
        car = s.cars.get(car_id)
        if car and bid > car["price"]:
            car["owner"] = bidder
            car["price"] = bid
            s.bc.invoke({"car_id": car_id, "owner": bidder, "price": bid, "action": "bid"})

    def history(s, car_id):
        return s.bc.query(car_id)


if __name__ == "__main__":
    app = Auction()
    app.add_car("C1", "Alice", 5000)
    app.bid("C1", "Bob", 5500)
    app.bid("C1", "Charlie", 5400)
    print(app.cars["C1"])
    print(app.history("C1"))
