from cryptography.fernet import Fernet
import os
import secrets
import string

# Generate a secure random password
def generate_random_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

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

# Save password to file
def save_password(account, password):
    encrypted_pw = encrypt_password(password)
    with open("passwords.txt", "a") as file:
        file.write(f"{account} | {encrypted_pw.decode()}\n")
    print(f"Password for {account} saved!")

# View stored passwords with optional search
def view_passwords():
    if not os.path.exists("passwords.txt"):
        print("No passwords stored yet!")
        return

    search = input("Enter the account name to search (or press Enter to view all): ").strip().lower()

    with open("passwords.txt", "r") as file:
        found = False
        for line in file:
            account, encrypted_pw = line.strip().split(" | ")
            decrypted_pw = decrypt_password(encrypted_pw.encode())

            if not search or search in account.lower():
                print(f"Account: {account}, Password: {decrypted_pw}")
                found = True

        if not found:
            print("No matching accounts found.")

# Main menu for user interaction
def main():
    while True:
        choice = input("\nDo you want to (A)dd a new password, (V)iew saved passwords, or (Q)uit? ").lower()

        if choice == 'a':
            account = input("Enter the account name (e.g., Gmail, Facebook): ")

            # Ask if user wants to generate a password
            generate = input("Do you want to generate a secure random password? (Y/N): ").lower()
            if generate == 'y':
                password = generate_random_password()
                print(f"Generated Password for {account}: {password}")
            else:
                password = input("Enter the password: ")

            save_password(account, password)

        elif choice == 'v':
            view_passwords()

        elif choice == 'q':
            print("Exiting Password Manager. Stay secure!")
            break

        else:
            print("Invalid choice. Please enter A, V, or Q.")

if __name__ == "__main__":
    main()