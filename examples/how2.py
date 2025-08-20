from nabu.ciphers import CaesarCipher, MonoSubCipher, CaseMode, VigenereCipher, AffineCipher
from nabu.core.key import generateRandomKey

def main() -> None:
    text = "A very OBJECTIVE test?"

    caesar = CaesarCipher(rotation=10, caseMode=CaseMode.PRESERVE) # append your preferred casing in all caps
    ciphertext = caesar.encrypt(text) # located in base class method
    print("Caesar enc:", ciphertext)
    print("Caesar dec:", caesar.decrypt(ciphertext))

    key = generateRandomKey(seed=290) # optional seed, for reproducibility
    mono = MonoSubCipher(keyAlphabet=key, caseMode=CaseMode.PRESERVE)
    encryption = mono.encrypt(text)
    print("MonoSub enc:", encryption)
    print("MonoSub dec:", mono.decrypt(encryption))

    vig = VigenereCipher(key="a", caseMode=CaseMode.PRESERVE)
    encryption = vig.encrypt(text)
    print("VigenereCipher enc:", encryption)
    print("VigenereCipher dec:", vig.decrypt(encryption))

    aff = AffineCipher(multiKey=3, addKey=7, caseMode=CaseMode.PRESERVE)
    encryption = aff.encrypt(text)
    print("Affine enc:", encryption)
    print("Affine dec:", aff.decrypt(encryption))

if __name__ == "__main__":
    main()