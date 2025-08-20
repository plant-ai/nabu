from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import json
from importlib.resources import files
from typing import Dict, FrozenSet, Optional


@dataclass(frozen=True)
class AlphabetPair:
    """
    Works similar to .lower() and .upper(), but better
    """
    lower: str
    upper: str
    lowerSet: FrozenSet[str]
    upperSet: FrozenSet[str]
    lowerIndex: Dict[str, int]
    upperIndex: Dict[str, int]

    def toLower(self, ch: str) -> Optional[str]:
        """Converts a single character, returns None if not in alphabet"""
        if ch in self.lowerSet:
            return ch
        idx = self.upperIndex.get(ch)
        return self.lower[idx] if idx is not None else None

    def toUpper(self, ch: str) -> Optional[str]:
        """Converts a single character, returns None if not in alphabet"""
        if ch in self.upperSet:
            return ch
        idx = self.lowerIndex.get(ch)
        return self.upper[idx] if idx is not None else None

    def isLower(self, ch: str) -> bool:
        return ch in self.lowerSet

    def isUpper(self, ch: str) -> bool:
        return ch in self.upperSet

    def contains(self, ch: str) -> bool:
        """Check if char in alphabet and works for either case"""
        return ch in self.lowerSet or ch in self.upperSet


@lru_cache(maxsize=None)
def loadAlphabetData() -> dict:
    txt = files("nabu.core").joinpath("alphabets.json").read_text(encoding="utf-8")
    return json.loads(txt)


@lru_cache(maxsize=None)
def getAlphabet(name: str = "latin") -> AlphabetPair:
    data = loadAlphabetData()
    if name not in data:
        raise ValueError(f"alphabet '{name}' not found")
    entry = data[name]
    lo, up = entry["lowercase"], entry["uppercase"]
    if len(lo) != len(up):
        raise ValueError("alphabet lower/upper length mismatch")

    lowerIndex = {c: i for i, c in enumerate(lo)}
    upperIndex = {c: i for i, c in enumerate(up)}

    return AlphabetPair(
        lower=lo,
        upper=up,
        lowerSet=frozenset(lo),
        upperSet=frozenset(up),
        lowerIndex=lowerIndex,
        upperIndex=upperIndex
    )