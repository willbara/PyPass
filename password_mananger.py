import os
import stat
import secrets
import string
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

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
    os.chmod(KEY_FILE, stat.S_IREAD)
    return key

# Load key from file with error handling
def load_key():
    try:
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        messagebox.showerror("Error", "Encryption key not found! Please ensure 'key.key' exists in the project directory.")
        exit(1)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the key: {e}")
        exit(1)

# Check if key exists, if not, generate a new one
if not os.path.exists(KEY_FILE):
    key = generate_key()
else:
    key = load_key()

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
    except Exception:
        return "[Decryption Failed]"

# Save password to file
def save_password(account, password):
    try:
        encrypted_pw = encrypt_password(password)
        with open(PASSWORD_FILE, "a") as file:
            file.write(f"{account} | {encrypted_pw.decode()}\n")
        messagebox.showinfo("Success", f"Password for {account} saved!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the password: {e}")

# GUI Setup
def setup_gui():
    root = tk.Tk()
    root.title("Password Manager")
    root.geometry("600x400")

    # Frame for Adding Passwords
    add_frame = tk.Frame(root)
    add_frame.pack(pady=10)

    # Account Entry
    tk.Label(add_frame, text="Account Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    account_entry = tk.Entry(add_frame, width=40)
    account_entry.grid(row=0, column=1, padx=5, pady=5)

    # Password Entry
    tk.Label(add_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    password_entry = tk.Entry(add_frame, width=40, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    # Generate Password Button
    def generate_password():
        generated_password = generate_random_password()
        password_entry.delete(0, tk.END)
        password_entry.insert(0, generated_password)

    generate_btn = tk.Button(add_frame, text="Generate Password", command=generate_password)
    generate_btn.grid(row=2, column=0, padx=5, pady=5)

    # Save Password Button
    def save():
        account = account_entry.get().strip()
        password = password_entry.get().strip()
        if account and password:
            save_password(account, password)
            account_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            refresh_passwords()  # Refresh the password viewer after saving
        else:
            messagebox.showwarning("Input Error", "Both account and password fields must be filled.")

    save_btn = tk.Button(add_frame, text="Save Password", command=save)
    save_btn.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Separator
    ttk.Separator(root, orient='horizontal').pack(fill='x', pady=10)

    # Frame for Viewing Passwords
    view_frame = tk.Frame(root)
    view_frame.pack(pady=10)

    # Search Bar
    tk.Label(view_frame, text="Search Account:").grid(row=0, column=0, padx=5)
    search_entry = tk.Entry(view_frame, width=30)
    search_entry.grid(row=0, column=1, padx=5)

    def search_passwords():
        query = search_entry.get().strip().lower()
        refresh_passwords(query)

    search_btn = tk.Button(view_frame, text="Search", command=search_passwords)
    search_btn.grid(row=0, column=2, padx=5)

    # Treeview for displaying passwords
    tree = ttk.Treeview(view_frame, columns=("Account", "Password"), show='headings')
    tree.heading("Account", text="Account")
    tree.heading("Password", text="Password")
    tree.grid(row=1, column=0, columnspan=3, pady=10)

    # Scrollbar for Treeview
    scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=1, column=3, sticky='ns')

    # Refresh Passwords Display
    def refresh_passwords(query=""):
        for row in tree.get_children():
            tree.delete(row)

        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, "r") as file:
                for line in file:
                    try:
                        account, encrypted_pw = line.strip().split(" | ")
                        decrypted_pw = decrypt_password(encrypted_pw.encode())
                        if query in account.lower():
                            tree.insert("", "end", values=(account, decrypted_pw))
                    except ValueError:
                        continue

    # Copy password to clipboard
    def copy_password(event):
        selected_item = tree.selection()
        if selected_item:
            account, password = tree.item(selected_item)["values"]
            root.clipboard_clear()
            root.clipboard_append(password)
            messagebox.showinfo("Copied", f"Password for {account} copied to clipboard!")

    tree.bind("<Double-1>", copy_password)

    # Initially load passwords
    refresh_passwords()

    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    setup_gui()