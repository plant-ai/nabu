from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Final
from nabu.core.alphabets import AlphabetPair, getAlphabet
from nabu.core.mask import captureMask, restoreMask


class CaseMode(str, Enum):
    PRESERVE = "preserve"
    LOWER = "lower"
    UPPER = "upper"


class Cipher(ABC):
    caseMode: Final[CaseMode]
    alphabet: Final[AlphabetPair]

    def __init__(self, *, caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin") -> None:
        self.caseMode = caseMode
        self.alphabet = getAlphabet(alphabet)

    def encrypt(self, plainText: str) -> str:
        mode = self.caseMode

        if mode is CaseMode.LOWER:
            # Convert all alphabet chars to lowercase
            normalised = self._normaliseToLower(plainText)
            return self._encryptCore(normalised)

        if mode is CaseMode.UPPER:
            # Convert to lowercase, encrypt, then convert result to uppercase
            normalised = self._normaliseToLower(plainText)
            encrypted = self._encryptCore(normalised)
            return self._normaliseToUpper(encrypted)

        # PRESERVE mode
        mask, stream = captureMask(plainText, self.alphabet)
        return restoreMask(self._encryptCore(stream), mask, self.alphabet)

    def decrypt(self, cipherText: str) -> str:
        mode = self.caseMode

        if mode is CaseMode.LOWER:
            normalised = self._normaliseToLower(cipherText)
            return self._decryptCore(normalised)

        if mode is CaseMode.UPPER:
            normalised = self._normaliseToLower(cipherText)
            decrypted = self._decryptCore(normalised)
            return self._normaliseToUpper(decrypted)

        # PRESERVE mode
        mask, stream = captureMask(cipherText, self.alphabet)
        return restoreMask(self._decryptCore(stream), mask, self.alphabet)

    def _normaliseToLower(self, text: str) -> str:
        """Convert all alphabet characters to lowercase"""
        result = []
        for ch in text:
            lower_ch = self.alphabet.toLower(ch)
            result.append(lower_ch if lower_ch is not None else ch)
        return "".join(result)

    def _normaliseToUpper(self, text: str) -> str:
        """Convert all alphabet characters to uppercase"""
        result = []
        for ch in text:
            upper_ch = self.alphabet.toUpper(ch)
            result.append(upper_ch if upper_ch is not None else ch)
        return "".join(result)

    # forces all child classes to have these methods
    @abstractmethod
    def _encryptCore(self, streamLower: str) -> str: ...

    @abstractmethod
    def _decryptCore(self, streamLower: str) -> str: ...