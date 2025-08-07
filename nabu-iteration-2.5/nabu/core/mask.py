from __future__ import annotations
from typing import List, Tuple
from nabu.core.alphabets import AlphabetPair

LOWER, UPPER, OTHER = 0, 1, 2
Mask = List[int]

def captureMask(text: str, alphabet: AlphabetPair) -> Tuple[Mask, str]:
    """
    returns a case mask given a piece of text
    """
    mask: Mask = []
    stream: List[str] = []
    lowSet = alphabet.lowerSet
    for ch in text:
        low = ch.lower()
        if low in lowSet:
            stream.append(low)
            mask.append(UPPER if ch.isupper() else LOWER)
        else:
            stream.append(ch)
            mask.append(OTHER)
    return mask, "".join(stream)

def restoreMask(stream: str, mask: Mask, alphabet: AlphabetPair) -> str:
    """
    fixes the normalised text by applying the mask
    """
    if len(stream) != len(mask):
        raise ValueError("stream/mask length mismatch")
    out: List[str] = []
    for tag, ch in zip(mask, stream):
        if tag == OTHER:
            out.append(ch)
        elif tag == UPPER:
            idx = alphabet.lowerIndex.get(ch)
            out.append(alphabet.upper[idx] if idx is not None else ch.upper())
        else:
            out.append(ch)
    return "".join(out)
