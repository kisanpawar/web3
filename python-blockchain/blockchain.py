"""
Simple proof-of-work-free blockchain: genesis, append blocks, print chain, validate links.
Run: python blockchain.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


@dataclass
class Block:
    index: int
    timestamp: str
    data: Any
    previous_hash: str
    block_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "block_hash": self.block_hash,
        }


def compute_block_hash(
    index: int,
    timestamp: str,
    data: Any,
    previous_hash: str,
) -> str:
    payload = json.dumps(
        {"index": index, "timestamp": timestamp, "data": data, "previous_hash": previous_hash},
        sort_keys=True,
        separators=(",", ":"),
    )
    return _sha256_hex(payload)


def create_genesis_block() -> Block:
    timestamp = _utc_now_iso()
    genesis = Block(
        index=0,
        timestamp=timestamp,
        data="Genesis Block",
        previous_hash="0",
        block_hash="",
    )
    h = compute_block_hash(
        genesis.index, genesis.timestamp, genesis.data, genesis.previous_hash
    )
    return Block(
        index=genesis.index,
        timestamp=genesis.timestamp,
        data=genesis.data,
        previous_hash=genesis.previous_hash,
        block_hash=h,
    )


class Blockchain:
    def __init__(self) -> None:
        self.chain: list[Block] = [create_genesis_block()]

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Any) -> Block:
        prev = self.get_latest_block()
        idx = prev.index + 1
        ts = _utc_now_iso()
        prev_hash = prev.block_hash
        block_hash = compute_block_hash(idx, ts, data, prev_hash)
        block = Block(
            index=idx,
            timestamp=ts,
            data=data,
            previous_hash=prev_hash,
            block_hash=block_hash,
        )
        self.chain.append(block)
        return block

    def display(self) -> None:
        print("Blockchain contents:")
        for b in self.chain:
            print(json.dumps(b.to_dict(), indent=2))
            print("-" * 40)


def validate_blockchain(chain: list[Block]) -> bool:
    if not chain:
        return False
    genesis = chain[0]
    if genesis.index != 0 or genesis.previous_hash != "0":
        return False
    expected = compute_block_hash(
        genesis.index, genesis.timestamp, genesis.data, genesis.previous_hash
    )
    if genesis.block_hash != expected:
        return False
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]
        if current.index != previous.index + 1:
            return False
        if current.previous_hash != previous.block_hash:
            return False
        recalc = compute_block_hash(
            current.index, current.timestamp, current.data, current.previous_hash
        )
        if current.block_hash != recalc:
            return False
    return True


def main() -> None:
    bc = Blockchain()
    bc.add_block({"tx": "payment-1", "amount": 10})
    bc.add_block({"tx": "payment-2", "amount": 25})
    bc.display()
    ok = validate_blockchain(bc.chain)
    print(f"Blockchain valid: {ok}")


if __name__ == "__main__":
    main()
