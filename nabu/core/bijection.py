from __future__ import annotations
from typing import Dict

def validateOneToOneBijection(key: str, ring: str) -> None:
    if len(key) != len(ring):
        raise ValueError(f"length mismatch: key={len(key)} ring={len(ring)}")
    if len(set(ring)) != len(ring):
        raise ValueError("ring must contain unique symbols")
    if len(set(key)) != len(key):
        raise ValueError("key must contain unique symbols")

def bijectionTable(key: str, ring: str) -> Dict[int, int]:
    return str.maketrans(ring, key)

def invertBijectionTable(table: Dict[int, int]) -> Dict[int, int]:
    # literally swaps keys and values around
    return {v: k for k, v in table.items()}
