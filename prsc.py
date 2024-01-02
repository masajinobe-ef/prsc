from flask import Flask, render_template, request, redirect, url_for, session
from crypt import encrypt_password, decrypt_password
from database import db_create
import sqlite3
import secrets

app = Flask(__name__)

# Генерация случайного секретного ключа для подписи сессии
app.secret_key = secrets.token_hex(16)

# Создание .db если не существует
db_create()


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
            else:
                return render_template('index.html',
                                       error="Отказано в доступе!")

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
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080)
    app.run(debug=True)
