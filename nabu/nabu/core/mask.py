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

    for ch in text:
        if alphabet.isLower(ch):
            stream.append(ch)
            mask.append(LOWER)
        elif alphabet.isUpper(ch):
            # Convert to lowercase for the stream
            idx = alphabet.upperIndex[ch]
            stream.append(alphabet.lower[idx])
            mask.append(UPPER)
        else:
            # Character not in alphabet
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
            if idx is not None:
                out.append(alphabet.upper[idx])
            else:
                # Fallback - shouldn't happen if mask was captured correctly
                out.append(ch)
        else:  # LOWER
            out.append(ch)

    return "".join(out)