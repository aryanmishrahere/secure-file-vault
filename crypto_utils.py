from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)

def load_key():
    return open(KEY_FILE, "rb").read()

generate_key()
fernet = Fernet(load_key())

def encrypt_file(data):
    return fernet.encrypt(data)

def decrypt_file(data):
    return fernet.decrypt(data)
