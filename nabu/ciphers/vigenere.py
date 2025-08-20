from __future__ import annotations
from typing import List, Dict
from nabu.ciphers.basecipher import Cipher, CaseMode
from nabu.core.rotate import rotateTable

class VigenereCipher(Cipher):
    """
    Classic Vigenère cipher over an arbitrary ring (default: alphabet.lower)
      - Key is normalised to lowercase and filtered to symbols in the ring.
      - Non-ring characters are passed through unchanged and DO NOT consume key index.
      - This is important distinction, might want to add an always advancing version?
      - Per-position translation tables (and inverses) are precomputed from the key. (per letter in key)
    """

    def __init__(self, key: str, ring: str | None = None, *,
                 caseMode: CaseMode = CaseMode.PRESERVE,
                 alphabet: str = "latin") -> None:
        super().__init__(caseMode=caseMode, alphabet=alphabet)

        # ring and helpers
        self.ring: str = ring if ring is not None else self.alphabet.lower
        self._ringIndex: Dict[str, int] = {c: i for i, c in enumerate(self.ring)}
        self._ringSet = set(self.ring)
        self.key: str = "".join([c for c in key.lower()])
        self.keyLength: int = len(self.key)

        # goes and makes a caesar cipher style trans tbl for every letter in the key (fwd and inv)
        rotations: List[int] = [self._ringIndex[c] for c in self.key]
        self._tables: List[Dict[int, int]] = [rotateTable(self.ring, r) for r in rotations]
        self._inverseTables: List[Dict[int, int]] = [rotateTable(self.ring, -r) for r in rotations]


    def _apply(self, streamLower: str, tables: List[Dict[int, int]]) -> str:
        outChars: List[str] = []
        append = outChars.append
        ringSet = self._ringSet
        keyLength = self.keyLength

        #works like an index register, tracks position in key, rather than a padding function
        k = 0
        for ch in streamLower:
            if ch in ringSet:
                append(ch.translate(tables[k]))
                k = (k + 1) % keyLength
            else:
                append(ch)
        return "".join(outChars)


    def _encryptCore(self, streamLower: str) -> str:
        return self._apply(streamLower, self._tables)

    def _decryptCore(self, streamLower: str) -> str:
        return self._apply(streamLower, self._inverseTables)