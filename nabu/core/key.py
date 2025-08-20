from __future__ import annotations
import random
import string

def generateRandomKey(ring: str = string.ascii_lowercase, seed: int | None = None) -> str:
    rng = random.Random(seed)
    chars = list(ring)
    rng.shuffle(chars)
    return "".join(chars)

def keywordToKey(keyword: str, ring: str = string.ascii_lowercase) -> str:
    seen = set()
    kept = []
    for c in keyword:
        lc = c.lower()
        if lc in ring and lc not in seen:
            seen.add(lc)
            kept.append(lc)
    remainder = [c for c in ring if c not in seen]
    return "".join(kept + remainder)