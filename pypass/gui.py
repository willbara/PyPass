import tkinter as tk
from tkinter import messagebox, ttk
import random
import string
from string import punctuation
from pypass.data_handler import save_password, load_passwords

def setup_gui():
    root = tk.Tk()
    root.title("Password Manager")
    root.geometry("700x500")

    # Apply a modern ttk theme
    style = ttk.Style(root)
    style.theme_use("clam")

    # Define styles for the password strength bar
    style.configure("Red.Horizontal.TProgressbar", foreground="red", background="red")
    style.configure("Orange.Horizontal.TProgressbar", foreground="orange", background="orange")
    style.configure("Yellow.Horizontal.TProgressbar", foreground="yellow", background="yellow")
    style.configure("LightGreen.Horizontal.TProgressbar", foreground="light green", background="light green")
    style.configure("Green.Horizontal.TProgressbar", foreground="green", background="green")

    # Menu Bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # File Menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Add Password", command=lambda: add_password_window(root))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Frame for Viewing Passwords
    view_frame = tk.Frame(root)
    view_frame.pack(pady=10, fill="both", expand=True)

    # Treeview for displaying passwords
    columns = ("Account", "Username", "Password")
    tree = ttk.Treeview(view_frame, columns=columns, show='headings', height=10)

    tree.heading("Account", text="Account")
    tree.heading("Username", text="Username")
    tree.heading("Password", text="Password")

    tree.column("Account", width=200)
    tree.column("Username", width=200)
    tree.column("Password", width=150)

    tree.pack(side="left", fill="both", expand=True)

    # Scrollbar for Treeview
    scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

       # Right-click context menu
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Reveal Password", command=lambda: reveal_password())
    context_menu.add_command(label="Hide Password", command=lambda: hide_password())
    context_menu.add_separator()
    context_menu.add_command(label="Copy Account", command=lambda: copy_to_clipboard("account"))
    context_menu.add_command(label="Copy Username", command=lambda: copy_to_clipboard("username"))
    context_menu.add_command(label="Copy Password", command=lambda: copy_to_clipboard("password"))

    # Show context menu on right-click
    def show_context_menu(event):
        selected_item = tree.selection()
        if selected_item:
            context_menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", show_context_menu)

    def copy_to_clipboard(field):
        selected_item = tree.selection()
        if selected_item:
            values = tree.item(selected_item, "values")
            index_map = {"account": 0, "username": 1, "password": 2}
            root.clipboard_clear()
            root.clipboard_append(values[index_map[field]])
            messagebox.showinfo("Copied", f"{field.capitalize()} copied to clipboard!")

    def reveal_password():
        selected_item = tree.selection()
        if selected_item:
            stored_password = tree.item(selected_item, "tags")[0]
            current_values = tree.item(selected_item)["values"]
            tree.item(selected_item, values=(current_values[0], current_values[1], stored_password))

    def hide_password():
        selected_item = tree.selection()
        if selected_item:
            current_values = tree.item(selected_item)["values"]
            tree.item(selected_item, values=(current_values[0], current_values[1], "******"))

    # Refresh Passwords Display
    def refresh_passwords():
        for row in tree.get_children():
            tree.delete(row)

        passwords = load_passwords()
        for account, username, password in passwords:
            item_id = tree.insert("", "end", values=(account, username, "******"))
            tree.item(item_id, tags=(password,))  # Store actual password in tags

    # Add Password Window
    def add_password_window(parent):
        add_win = tk.Toplevel(parent)
        add_win.title("Add New Password")
        add_win.geometry("350x320")

        tk.Label(add_win, text="Account Name:").pack(pady=5)
        account_entry = tk.Entry(add_win, width=30)
        account_entry.pack(pady=5)

        tk.Label(add_win, text="Username:").pack(pady=5)
        username_entry = tk.Entry(add_win, width=30)
        username_entry.pack(pady=5)

        tk.Label(add_win, text="Password:").pack(pady=5)
        password_entry = tk.Entry(add_win, width=30, show="*")
        password_entry.pack(pady=5)

        strength_label = tk.Label(add_win, text="Password Strength: ")
        strength_label.pack(pady=2)

        strength_bar = ttk.Progressbar(add_win, length=200, mode='determinate', style="Red.Horizontal.TProgressbar")
        strength_bar.pack(pady=5)

        def check_password_strength(event=None):
            password = password_entry.get()
            strength = 0
            if any(c.islower() for c in password): strength += 1
            if any(c.isupper() for c in password): strength += 1
            if any(c.isdigit() for c in password): strength += 1
            if any(c in string.punctuation for c in password): strength += 1
            if len(password) >= 12: strength += 1
            strength_percent = (strength / 5) * 100
            strength_bar["value"] = strength_percent

            if strength_percent <= 20:
                strength_bar.configure(style="Red.Horizontal.TProgressbar")
            elif strength_percent <= 40:
                strength_bar.configure(style="Orange.Horizontal.TProgressbar")
            elif strength_percent <= 60:
                strength_bar.configure(style="Yellow.Horizontal.TProgressbar")
            elif strength_percent <= 80:
                strength_bar.configure(style="LightGreen.Horizontal.TProgressbar")
            else:
                strength_bar.configure(style="Green.Horizontal.TProgressbar")

        password_entry.bind("<KeyRelease>", check_password_strength)

        def generate_password():
            characters = string.ascii_letters + string.digits + string.punctuation
            generated_password = ''.join(random.choice(characters) for _ in range(16))
            password_entry.delete(0, tk.END)
            password_entry.insert(0, generated_password)
            check_password_strength()

        generate_btn = tk.Button(add_win, text="Generate Password", command=generate_password)
        generate_btn.pack(pady=5)

        def save_and_close():
            account = account_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if account and username and password:
                save_password(account, username, password)
                add_win.destroy()
                refresh_passwords()
            else:
                messagebox.showwarning("Input Error", "All fields must be filled.")

        save_btn = tk.Button(add_win, text="Save", command=save_and_close)
        save_btn.pack(pady=10)

    # Initially load passwords
    refresh_passwords()

    root.mainloop()
