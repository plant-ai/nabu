from __future__ import annotations

def rotate(ring: str, element: str, rotation: int) -> str:
    table = {c: i for i, c in enumerate(ring)}
    if element in table:
        idx = table[element]
        return ring[(idx + rotation) % len(ring)]
    return element

def rotateTable(ring: str, rotations: int) -> dict[int, int]:
    m = len(ring)
    rotations %= m
    return str.maketrans(ring, ring[rotations:] + ring[:rotations])
