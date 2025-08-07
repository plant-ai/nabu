from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from importlib.resources import files
from typing import Dict, FrozenSet

@dataclass(frozen=True)
class AlphabetPair:
    lower: str
    upper: str
    lowerSet: FrozenSet[str]
    lowerIndex: Dict[str, int]

@lru_cache(maxsize=None) # huge fix O(n) before
def loadAlphabetData() -> dict:
    txt = files("nabu.core").joinpath("alphabets.json").read_text(encoding="utf-8")
    return json.loads(txt)

@lru_cache(maxsize=None) # huge fix O(n) before
def getAlphabet(name: str = "latin") -> AlphabetPair:
    data = loadAlphabetData()
    if name not in data:
        raise ValueError(f"alphabet '{name}' not found")
    entry = data[name]
    lo, up = entry["lowercase"], entry["uppercase"]
    if len(lo) != len(up):
        raise ValueError("alphabet lower/upper length mismatch")
    for a, A in zip(lo, up):
        if a.upper() != A or A.lower() != a:
            raise ValueError(f"non-bijective case pair: {a!r} ↔ {A!r}")
    lowerIndex = {c: i for i, c in enumerate(lo)}
    return AlphabetPair(lower=lo, upper=up, lowerSet=frozenset(lo), lowerIndex=lowerIndex)
