import os
import stat
import secrets
import string
from cryptography.fernet import Fernet

# Define the base directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths for key and passwords file
KEY_FILE = os.path.join(BASE_DIR, "key.key")
PASSWORD_FILE = os.path.join(BASE_DIR, "passwords.txt")

# Generate a secure random password
def generate_random_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

# Generate key and save to file (set to read-only)
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    
    # Make the key file read-only to prevent overwriting
    os.chmod(KEY_FILE, stat.S_IREAD)
    return key

# Load key from file with error handling
def load_key():
    try:
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("Encryption key not found! Please ensure 'key.key' exists in the project directory.")
        exit(1)  # Exit program if key is missing
    except Exception as e:
        print(f"An error occurred while loading the key: {e}")
        exit(1)

# Check if key exists, if not, generate a new one
if not os.path.exists(KEY_FILE):
    key = generate_key()
    print("Encryption key generated and saved (set to read-only)!")
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
    try:
        decrypted = fernet.decrypt(encrypted_password).decode()
        return decrypted
    except Exception as e:
        print(f"Error decrypting password: {e}")
        return "[Decryption Failed]"

# Save password to file
def save_password(account, password):
    try:
        encrypted_pw = encrypt_password(password)
        with open(PASSWORD_FILE, "a") as file:
            file.write(f"{account} | {encrypted_pw.decode()}\n")
        print(f"Password for {account} saved!")
    except Exception as e:
        print(f"An error occurred while saving this password: {e}")

# View stored passwords with error handling
def view_passwords():
    if not os.path.exists(PASSWORD_FILE):
        print("No passwords stored yet!")
        return

    search = input("Enter the account name to search (or press Enter to view all): ").strip().lower()

    try:
        with open(PASSWORD_FILE, "r") as file:
            found = False
            for line in file:
                try:
                    account, encrypted_pw = line.strip().split(" | ")
                    decrypted_pw = decrypt_password(encrypted_pw.encode())

                    if not search or search in account.lower():
                        print(f"Account: {account}, Password: {decrypted_pw}")
                        found = True
                except ValueError:
                    print(f"Skipping malformed line: {line.strip()}")

            if not found:
                print("No matching accounts found.")
    except Exception as e:
        print(f"An error occurred while reading passwords: {e}")

# Main menu with input validation
def main():
    while True:
        try:
            choice = input("\nDo you want to (A)dd a new password, (V)iew saved passwords, or (Q)uit? ").strip().lower()

            if choice == 'a':
                account = input("Enter the account name (e.g., Gmail, Facebook): ").strip()
                if not account:
                    print("Account name cannot be empty.")
                    continue

                # Ask if user wants to generate a password
                while True:
                    generate = input("Do you want to generate a secure random password? (Y/N): ").strip().lower()

                    if generate == 'y':
                        password = generate_random_password()
                        print(f"Generated Password for {account}: {password}")
                        break

                    elif generate == 'n':
                        password = input("Enter the password: ").strip()
                        if not password:
                            print("Password cannot be empty.")
                            continue
                        break

                    else:
                        print("Invalid choice. Please enter Y or N.")

                save_password(account, password)

            elif choice == 'v':
                view_passwords()

            elif choice == 'q':
                print("Exiting Password Manager. Stay secure!")
                break

            else:
                print("Invalid choice. Please enter A, V, or Q.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()