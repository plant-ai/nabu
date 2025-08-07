from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Final
from nabu.core.alphabets import AlphabetPair, getAlphabet
from nabu.core.mask import captureMask, restoreMask

class CaseMode(str, Enum):
    PRESERVE = "preserve"
    LOWER    = "lower"
    UPPER    = "upper"

class Cipher(ABC):
    caseMode: Final[CaseMode]
    alphabet: Final[AlphabetPair]

    def __init__(self, *, caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin") -> None:
        self.caseMode = caseMode
        self.alphabet = getAlphabet(alphabet)

    def encrypt(self, plainText: str) -> str:
        mode = self.caseMode
        if mode is CaseMode.LOWER:
            return self._encryptCore(plainText.lower())
        if mode is CaseMode.UPPER:
            return self._encryptCore(plainText.lower()).upper()
        mask, stream = captureMask(plainText, self.alphabet)
        return restoreMask(self._encryptCore(stream), mask, self.alphabet)

    def decrypt(self, cipherText: str) -> str:
        mode = self.caseMode
        if mode is CaseMode.LOWER:
            return self._decryptCore(cipherText.lower())
        if mode is CaseMode.UPPER:
            return self._decryptCore(cipherText.lower()).upper()
        mask, stream = captureMask(cipherText, self.alphabet)
        return restoreMask(self._decryptCore(stream), mask, self.alphabet)

    @abstractmethod
    def _encryptCore(self, streamLower: str) -> str: ...

    @abstractmethod
    def _decryptCore(self, streamLower: str) -> str: ...
