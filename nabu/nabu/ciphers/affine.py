# nabu/ciphers/affine.py
from __future__ import annotations
from .basecipher import Cipher, CaseMode
from typing import Dict
from nabu.core.mod import affineTable, invAffineTable, validateAffineParams

class AffineCipher(Cipher):
    def __init__(self, multiKey: int, addKey: int, ring: str | None = None, *,
                 caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin") -> None:
        super().__init__(caseMode=caseMode, alphabet=alphabet)

        # ring and params
        self.ring = ring if ring is not None else self.alphabet.lower
        self._ringLength = len(self.ring)
        self.multiKey = multiKey
        self.addKey = addKey

        # sees if affine table will build successfully
        validateAffineParams(self.multiKey, self._ringLength)

        # builds tables
        self._table : Dict[int, int] = affineTable(ring=self.ring, ringLength=self._ringLength, multiKey=self.multiKey, addKey=self.addKey)
        self._invTable = invAffineTable(ring=self.ring, ringLength=self._ringLength, multiKey=self.multiKey, addKey=self.addKey)

    def _encryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self._table)

    def _decryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self._invTable)
