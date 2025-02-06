import os
from pypass.encryption import encrypt_password, decrypt_password

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORD_FILE = os.path.join(BASE_DIR, "passwords.txt")

# Save a password to file
def save_password(account, username, password):
    encrypted_pw = encrypt_password(password)
    with open(PASSWORD_FILE, "a") as file:
        file.write(f"{account} | {username} | {encrypted_pw.decode()}\n")

# Load stored passwords
def load_passwords():
    passwords = []
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as file:
            for line in file:
                try:
                    account, username, encrypted_pw = line.strip().split(" | ")
                    decrypted_pw = decrypt_password(encrypted_pw.encode())
                    passwords.append((account, username, decrypted_pw))
                except ValueError:
                    continue  # Skip malformed lines
    return passwords