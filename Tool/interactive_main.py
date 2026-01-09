from src.core.encryption import BlowfishEncryptor

def main():
    enc = BlowfishEncryptor()

    while True:
        print("\n1 Encrypt  2 Decrypt  3 Verify Integrity  4 Exit")
        ch = input("> ").strip()

        if ch == "1":
            path = input("File path: ")
            pwd = input("Password: ").encode()
            keep = input("Keep original name (no extension)? (y/n): ").lower() == "y"
            delete = input("Secure delete original file? (y/n): ").lower() == "y"
            enc.encrypt_file(path, pwd, keep, delete)

        elif ch == "2":
            path = input("Encrypted file path: ")
            pwd = input("Password: ").encode()
            delete = input("Secure delete encrypted file? (y/n): ").lower() == "y"
            enc.decrypt_file(path, pwd, delete)

        elif ch == "3":
            path = input("File path to verify: ")
            ok, info = enc.verify_file(path)
            print("Integrity OK" if ok else "Integrity FAILED", info)

        elif ch == "4":
            break

if __name__ == "__main__":
    main()
