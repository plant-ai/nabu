# nabu/eval/keyspace.py
from __future__ import annotations
import random
from typing import Dict, List, Tuple, Optional

class MonoSubKeyspace:
    """
    Monoalphabetic substitution keyspace utilities:
      - random key generation (permutation of alphabet)
      - Cayley (transposition) distance between keys (minimum # of swaps)
      - neighbour generation by applying r random swaps to a given key
      - encrypt/decrypt under a given key
    Keys are represented as strings of length |alphabet| that permute the alphabet.
    """
    def __init__(self, alphabet: str, rngSeed: Optional[int] = None) -> None:
        self.alphabet = alphabet
        self.A = len(alphabet)
        self._rng = random.Random(rngSeed)

    # ---------- Keys ----------
    def identity_key(self) -> str:
        return self.alphabet

    def random_key(self) -> str:
        arr = list(self.alphabet)
        self._rng.shuffle(arr)
        return ''.join(arr)

    def cayley_distance(self, keyA: str, keyB: str) -> int:
        """
        Minimum number of transpositions (i j) to transform keyA into keyB.
        For permutations, this equals A - #cycles in the index permutation mapping.
        """
        if len(keyA) != self.A or len(keyB) != self.A:
            raise ValueError("Key length mismatch")
        posB = {ch: i for i, ch in enumerate(keyB)}
        # perm[i] = target index of the symbol currently at position i in keyA
        perm = [posB[ch] for ch in keyA]
        visited = [False]*self.A
        cycles = 0
        for i in range(self.A):
            if visited[i]:
                continue
            # follow cycle starting at i
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
            cycles += 1
        return self.A - cycles

    def neighbour_by_swaps(self, key: str, radius: int) -> str:
        """
        Apply 'radius' random transpositions to 'key' (not guaranteed to be distinct pairs).
        """
        if radius < 0:
            raise ValueError("radius must be >= 0")
        arr = list(key)
        for _ in range(radius):
            i = self._rng.randrange(self.A)
            j = self._rng.randrange(self.A - 1)
            if j >= i:
                j += 1
            arr[i], arr[j] = arr[j], arr[i]
        return ''.join(arr)

    # ---------- Cipher ----------
    def encrypt(self, plaintext: str, key: str) -> str:
        enc: Dict[str, str] = {p: c for p, c in zip(self.alphabet, key)}
        return ''.join(enc.get(ch, ch) for ch in plaintext)

    def decrypt(self, ciphertext: str, key: str) -> str:
        dec: Dict[str, str] = {c: p for p, c in zip(self.alphabet, key)}
        return ''.join(dec.get(ch, ch) for ch in ciphertext)
