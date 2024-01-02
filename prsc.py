from flask import Flask, render_template, request, redirect, url_for, session
from cryptography.fernet import Fernet
import sqlite3
import secrets
import os

app = Flask(__name__)

# Генерация случайного секретного ключа для подписи сессии
app.secret_key = secrets.token_hex(16)

# Шифрование
# Загрузка ключа шифрования из файла
# (или создание нового при первом запуске)
key_file = "key.key"
if not os.path.exists(key_file):
    key = Fernet.generate_key()
    with open(key_file, "wb") as key_file:
        key_file.write(key)
else:
    with open(key_file, "rb") as key_file:
        key = key_file.read()

cipher = Fernet(key)


def encrypt_password(master_password: str) -> str:
    return cipher.encrypt(master_password.encode())


def decrypt_password(encrypted_password: str) -> str:
    return cipher.decrypt(encrypted_password).decode()


# Страница установки мастер-пароля
@app.route('/master', methods=['GET', 'POST'])
def master():
    if request.method == 'POST':
        master_password = request.form['master_password']
        confirm_master_password = request.form['confirm_master_password']

        if master_password == confirm_master_password:
            encrypted_password = encrypt_password(master_password)

            # Сохранение зашифрованного пароля в базе данных
            conn = sqlite3.connect('prsc.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE MasterPassword SET encrypted_password = ?\
                    WHERE id = 1",
                (encrypted_password,))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))
        else:
            return render_template('master.html', error="Пароли не совпадают")

    return render_template('master.html')


# Страница входа
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        master_password = request.form['master_password']

        # Проверка совпадения мастер-пароля с базой данных
        conn = sqlite3.connect('prsc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT encrypted_password FROM MasterPassword LIMIT 1")
        stored_encrypted_password = cursor.fetchone()
        conn.close()

        if stored_encrypted_password:
            stored_encrypted_password = stored_encrypted_password[0]
            decrypted_password = decrypt_password(stored_encrypted_password)

            if master_password == decrypted_password:
                session['authenticated'] = True
                return redirect(url_for('display_db'))

    return render_template('index.html')


@app.route('/db', methods=['GET', 'POST'])
def display_db():
    # Проверка, является ли пользователь аутентифицирован
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('prsc.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Passwords')
    passwords = cursor.fetchall()
    conn.close()

    return render_template('db.html', passwords=passwords)


if __name__ == '__main__':
    app.run(debug=True)
