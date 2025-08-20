from __future__ import annotations

def rotate(ring: str, element: str, rotation: int) -> str:
    idx = ring.find(element)
    if idx != -1:
        return ring[(idx + rotation) % len(ring)]
    return element

def rotateTable(ring: str, rotations: int) -> dict[int, int]:
    m = len(ring)
    rotations %= m
    if rotations == 0:
        return {}
    return str.maketrans(ring, ring[rotations:] + ring[:rotations])