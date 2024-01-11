from cryptography.fernet import Fernet
import os


def load_or_generate_key():
    db_folder = "data"
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    key_file = "data/key.key"
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, "wb") as key_file:
            key_file.write(key)
    else:
        with open(key_file, "rb") as key_file:
            key = key_file.read()
    return Fernet(key)


cipher = load_or_generate_key()


def rotate_key():
    key_file = "data/key.key"
    new_key = Fernet.generate_key()
    with open(key_file, "wb") as key_file:
        key_file.write(new_key)
    return Fernet(new_key)


def encrypt(master_password: str):
    return cipher.encrypt(master_password.encode())


def decrypt(encrypted_password: str):
    return cipher.decrypt(encrypted_password).decode()
