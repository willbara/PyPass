import os
import stat
from cryptography.fernet import Fernet

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "key.key")

# Generate a new encryption key and save it
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    os.chmod(KEY_FILE, stat.S_IREAD)  # Make it read-only
    return key

# Load an existing encryption key
def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

# Initialize Fernet with the key
key = load_key()
fernet = Fernet(key)

# Encrypt a password
def encrypt_password(password):
    return fernet.encrypt(password.encode())

# Decrypt a password
def decrypt_password(encrypted_password):
    try:
        return fernet.decrypt(encrypted_password).decode()
    except Exception:
        return "[Decryption Failed]"