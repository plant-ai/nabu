from __future__ import annotations
from nabu.ciphers.basecipher import Cipher, CaseMode
from nabu.core.rotate import rotateTable

class CaesarCipher(Cipher):
    def __init__(self, rotation: int, ring: str | None = None, *,
                 caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin") -> None:
        super().__init__(caseMode=caseMode, alphabet=alphabet)
        self.ring = ring if ring is not None else self.alphabet.lower # breaks alphabet pair obj

        # builds translation tables
        self._table = rotateTable(self.ring, rotation)
        self._inverseTable = rotateTable(self.ring, -rotation)

    def _encryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self._table)

    def _decryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self._inverseTable)
