from __future__ import annotations
from typing import Dict
from nabu.ciphers.basecipher import Cipher, CaseMode
from nabu.core.bijection import validateOneToOneKey, bijectionTable, invertBijectionTable

class MonoSubCipher(Cipher):
    def __init__(self, key: str, ring: str | None = None, *,
                 caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin") -> None:
        super().__init__(caseMode=caseMode, alphabet=alphabet)
        self.ring = ring if ring is not None else self.alphabet.lower
        self.key = key
        self.table: Dict[int, int] = bijectionTable(key, self.ring)
        self.inverseTable: Dict[int, int] = invertBijectionTable(self.table)

    def _encryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self.table)

    def _decryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self.inverseTable)
