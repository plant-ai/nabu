from __future__ import annotations
from typing import Dict
from nabu.ciphers.basecipher import Cipher, CaseMode
from nabu.core.bijection import validateOneToOneBijection, bijectionTable, invertBijectionTable

class MonoSubCipher(Cipher):
    """
    generalised monosub cipher! works on arbitrary rings
    """
    def __init__(self, keyAlphabet: str, ring: str | None = None, *,
                 caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin") -> None:
        super().__init__(caseMode=caseMode, alphabet=alphabet)
        # ring and key params
        self.ring = ring if ring is not None else self.alphabet.lower
        self.key = keyAlphabet # a substitution alphabet

        # checks if the translation will succeed
        validateOneToOneBijection(self.key, self.ring)

        # builds translation tables
        self._table: Dict[int, int] = bijectionTable(keyAlphabet, self.ring)
        self._inverseTable: Dict[int, int] = invertBijectionTable(self._table)

    def _encryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self._table)

    def _decryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self._inverseTable)