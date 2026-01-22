import os
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets

# ==============================
# KEY GENERATION USING PASSWORD
# ==============================
def generate_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,               # 32 bytes = 256 bits
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


# ==============================
# FILE ENCRYPTION
# ==============================
def encrypt_file(file_path, password):
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(16)
    key = generate_key(password, salt)

    with open(file_path, 'rb') as f:
        data = f.read()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_file = file_path + ".enc"
    with open(encrypted_file, 'wb') as f:
        f.write(salt + iv + encrypted_data)

    return encrypted_file


# ==============================
# FILE DECRYPTION
# ==============================
def decrypt_file(file_path, password):
    with open(file_path, 'rb') as f:
        salt = f.read(16)
        iv = f.read(16)
        encrypted_data = f.read()

    key = generate_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    original_file = file_path.replace(".enc", "")
    with open(original_file, 'wb') as f:
        f.write(data)

    return original_file


# ==============================
# GUI FUNCTIONS
# ==============================
def encrypt_action():
    file_path = filedialog.askopenfilename()
    password = password_entry.get()

    if not file_path or not password:
        messagebox.showerror("Error", "File and password required")
        return

    try:
        encrypted = encrypt_file(file_path, password)
        messagebox.showinfo("Success", f"Encrypted:\n{encrypted}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def decrypt_action():
    file_path = filedialog.askopenfilename(filetypes=[("Encrypted Files", "*.enc")])
    password = password_entry.get()

    if not file_path or not password:
        messagebox.showerror("Error", "File and password required")
        return

    try:
        decrypted = decrypt_file(file_path, password)
        messagebox.showinfo("Success", f"Decrypted:\n{decrypted}")
    except Exception:
        messagebox.showerror("Error", "Wrong password or corrupted file")


# ==============================
# GUI DESIGN
# ==============================
app = tk.Tk()
app.title("AES-256 File Encryption Tool")
app.geometry("400x250")

tk.Label(app, text="File Encryption & Decryption", font=("Arial", 14)).pack(pady=10)

tk.Label(app, text="Enter Password").pack()
password_entry = tk.Entry(app, show="*", width=30)
password_entry.pack(pady=5)

tk.Button(app, text="Encrypt File", width=20, command=encrypt_action).pack(pady=10)
tk.Button(app, text="Decrypt File", width=20, command=decrypt_action).pack(pady=5)

tk.Label(app, text="AES-256 | Secure Encryption", font=("Arial", 9)).pack(pady=10)

app.mainloop()
