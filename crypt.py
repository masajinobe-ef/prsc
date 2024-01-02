from cryptography.fernet import Fernet
import os

# Шифрование
# Загрузка ключа шифрования из файла
# (или создание нового при первом запуске)


def load_or_generate_key():
    key_file = "key.key"
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, "wb") as key_file:
            key_file.write(key)
    else:
        with open(key_file, "rb") as key_file:
            key = key_file.read()
    return Fernet(key)


cipher = load_or_generate_key()


def encrypt_password(master_password: str) -> str:
    return cipher.encrypt(master_password.encode())


def decrypt_password(encrypted_password: str) -> str:
    return cipher.decrypt(encrypted_password).decode()
