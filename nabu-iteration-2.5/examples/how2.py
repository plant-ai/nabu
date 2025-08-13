
from nabu.ciphers import CaesarCipher, MonoSubCipher, CaseMode
from nabu.core.key import generateRandomKey

def main() -> None:
    text = "A very OBJECTIVE test?"

    caesar = CaesarCipher(rotation=5, caseMode=CaseMode.PRESERVE) # append your preffered casing in all caps
    ciphertext = caesar.encrypt(text) # base class method
    print("Caesar enc:", ciphertext)
    print("Caesar dec:", caesar.decrypt(ciphertext))

    key = generateRandomKey(seed=290) # optional seed, for reproducibility
    mono = MonoSubCipher(key=key, caseMode=CaseMode.PRESERVE)
    encryption = mono.encrypt(text)
    print("MonoSub enc:", encryption)
    print("MonoSub dec:", mono.decrypt(encryption))

if __name__ == "__main__":
    main()
