from cryptography.fernet import Fernet
import os

# Generate key and save to file
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    return key

# Load key from file
def load_key():
    with open("key.key", "rb") as key_file:
        return key_file.read()

# Check if key exists, if not, generate a new one
if not os.path.exists("key.key"):
    key = generate_key()
    print("Encryption key generated and saved!")
else:
    key = load_key()
    print("Encryption key loaded.")

# Initialize Fernet with the loaded key
fernet = Fernet(key)

# Encrypt password
def encrypt_password(password):
    encrypted = fernet.encrypt(password.encode())
    return encrypted

# Decrypt password
def decrypt_password(encrypted_password):
    decrypted = fernet.decrypt(encrypted_password).decode()
    return decrypted

# Example Usage
if __name__ == "__main__":
    password = input("Enter a password to encrypt: ")
    encrypted_pw = encrypt_password(password)
    print(f"Encrypted: {encrypted_pw}")

    decrypted_pw = decrypt_password(encrypted_pw)
    print(f"Decrypted: {decrypted_pw}")