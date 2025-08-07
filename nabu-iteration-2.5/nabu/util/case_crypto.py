from __future__ import annotations

def encrypt(cipher, plainText: str, alphabet: str = "latin", preserve: bool = True) -> str:
    return cipher.encrypt(plainText)

def decrypt(cipher, cipherText: str, alphabet: str = "latin", preserve: bool = True) -> str:
    return cipher.decrypt(cipherText)
