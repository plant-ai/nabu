# Nabu — Classical Cipher Toolkit (A-Level project)

Nabu is a small, dependency-free Python library for classical cryptography. It provides
clean, composable implementations of common ciphers and a uniform interface for encryption
and decryption with robust case handling and alphabet control. It is written to support an
A-Level Computer Science project and to act as a compact teaching/experiment platform.

> Package import path: `nabu` (module layout shown below).  
> Supported Python: 3.10+ (uses modern type hints and `pow(a, -1, m)` for modular inverse).  
> External dependencies: none.

---

## Quick start

Clone the repo and run the example from the project root:

```bash
python examples/how2.py
```

Or use the library directly:

```python
from nabu.ciphers import CaesarCipher, MonoSubCipher, VigenereCipher, AffineCipher, CaseMode
from nabu.core.key import generateRandomKey, keywordToKey

text = "A very OBJECTIVE test?"

# Caesar (rotation over a ring; non-ring chars pass through)
caesar = CaesarCipher(rotation=10, caseMode=CaseMode.PRESERVE)
c1 = caesar.encrypt(text)
assert caesar.decrypt(c1) == text

# Monoalphabetic substitution (key is a 1–1 permutation of the ring)
key = generateRandomKey(seed=290)  # reproducible shuffle
mono = MonoSubCipher(keyAlphabet=key, caseMode=CaseMode.PRESERVE)
c2 = mono.encrypt(text)
assert mono.decrypt(c2) == text

# Vigenère (key advances only when a ring character is consumed)
vig = VigenereCipher(key="vigenere", caseMode=CaseMode.PRESERVE)
c3 = vig.encrypt(text)
assert vig.decrypt(c3) == text

# Affine (y = a*x + b mod m) — require gcd(a, m) = 1
aff = AffineCipher(multiKey=3, addKey=7, caseMode=CaseMode.PRESERVE)
c4 = aff.encrypt(text)
assert aff.decrypt(c4) == text
```

---

## Installation

```bash
pip install -r requirements.txt
```

or is dependence free if you ignore the eval folder

---

## What the API guarantees

Case handling. All ciphers inherit from a shared base with three modes:

- `CaseMode.PRESERVE`: original casing is restored after encryption/decryption.  
- `CaseMode.LOWER`: force lowercase output.  
- `CaseMode.UPPER`: force uppercase output.  

Non-alphabet characters. Characters not in the current ring/alphabet are passed
through unchanged. In `VigenereCipher`, these characters do not consume key index
(this is an intentional design choice for cryptanalysis on real text).

Alphabets and rings. The library separates case mapping from the ring used by
a cipher:

- `alphabet="latin"` (default) or `"greek"` controls the case pair and case-aware behaviour.  
- A cipher’s `ring` parameter (optional) lets you override the lowercase symbol set used
  for translation. By default, `ring` is the lower member of the chosen alphabet.

```python
# Greek example
from nabu.ciphers import CaesarCipher
greek = CaesarCipher(rotation=3, alphabet="greek")  # ring = greek lowercase by default
```
You can also supply a custom ring string to operate over digits, subsets, etc.

---

## Modules and key functions

```bash
nabu/
  ciphers/
    __init__.py              # re-exports below
    basecipher.py            # base class with case handling
    caesar.py                # CaesarCipher(rotation, ring=None, *, caseMode, alphabet)
    monosub.py               # MonoSubCipher(keyAlphabet, ring=None, *, caseMode, alphabet)
    vigenere.py              # VigenereCipher(key, ring=None, *, caseMode, alphabet)
    affine.py                # AffineCipher(multiKey, addKey, ring=None, *, caseMode, alphabet)
  core/
    alphabets.py             # AlphabetPair + getAlphabet("latin"|"greek")
    bijection.py             # validateOneToOneBijection, bijectionTable, invertBijectionTable
    rotate.py                # rotateTable(ring, rotation)
    mod.py                   # validateAffineParams, affineTable, invAffineTable
    key.py                   # generateRandomKey, keywordToKey
```

---

## Constructor signatures (for reference)

```python
from nabu.ciphers import CaseMode

CaesarCipher(rotation: int, ring: str | None = None, *, caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin")

MonoSubCipher(keyAlphabet: str, ring: str | None = None, *, caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin")

VigenereCipher(key: str, ring: str | None = None, *, caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin")

AffineCipher(multiKey: int, addKey: int, ring: str | None = None, *, caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin")
```

---

## Utilities

```python
from nabu.core.key import generateRandomKey, keywordToKey

# Random permutation of a ring; optional seed for reproducibility
generateRandomKey(ring: str = string.ascii_lowercase, seed: int | None = None) -> str

# Turn a keyword into a valid monosub key (deduplicated letters + remaining ring)
keywordToKey(keyword: str, ring: str = string.ascii_lowercase) -> str
```

---

## Extending Nabu (add your own cipher)

Every cipher implements two core methods that operate on a lowercase stream.
The base class handles case masking and non-alphabet passthrough for you:

```python
from nabu.ciphers.basecipher import Cipher, CaseMode

class MyCipher(Cipher):
    def __init__(self, *, caseMode: CaseMode = CaseMode.PRESERVE, alphabet: str = "latin") -> None:
        super().__init__(caseMode=caseMode, alphabet=alphabet)
        # build self._table and self._inverseTable over your ring

    def _encryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self._table)

    def _decryptCore(self, streamLower: str) -> str:
        return streamLower.translate(self._inverseTable)
```
For affine-style ciphers over a ring of length m, prefer `nabu.core.mod` helpers and
validate your parameters up front (e.g. `validateAffineParams(a, m)`).

---

## Notes on correctness & behaviour

- `AffineCipher` raises on invalid parameters where `gcd(multiKey, ringLength) != 1`.  
- `VigenereCipher` advances its key only when a character from the ring is processed.  
- All ciphers are pure and stateless with respect to input text; you can reuse instances safely.  

---

## License

This project is released under the Apache License 2.0. See LICENSE.

---

## Acknowledgements

Built as part of an A-Level Computer Science project, with an emphasis on
clarity, correctness, and ease of extension for cryptanalysis experiments.
