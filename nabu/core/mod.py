from __future__ import annotations
from math import gcd

def validateAffineParams(multiKey: int, ringLength: int) -> None:
    if ringLength <= 0:
        raise ValueError("the ring must have at least one element")
    if gcd(multiKey, ringLength) != 1:
        raise ValueError("multiKey must be coprime with ring length")

def affineTable(ring: str, ringLength : int, multiKey: int, addKey: int) -> dict[int, int]:
    # normalising
    multiKey %= ringLength
    addKey %= ringLength
    # affine formula, like y = (mx + b), but rhs is mod ringLength
    mappedChars = [ring[(multiKey * i + addKey) % ringLength] for i in range(ringLength)]
    return str.maketrans(ring, "".join(mappedChars))

def invAffineTable(ring: str, ringLength : int, multiKey: int, addKey: int) -> dict[int, int]:
    # normalising
    multiKey %= ringLength
    addKey %= ringLength

    # modular inverse exists because gcd(a, m) == 1
    addKeyInv = pow(multiKey, -1, ringLength)  # Python’s built-in modular inverse

    # For each observed ciphertext index y, recover plaintext index x = a^{-1}(y - b) mod m
    mappedChars = []
    for y in range(ringLength):
        x = (addKeyInv * (y - addKey)) % ringLength
        mappedChars.append(ring[x])
    return str.maketrans(ring, "".join(mappedChars))