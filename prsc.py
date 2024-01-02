from flask import Flask, render_template, request, redirect, url_for, session
from logic.crypt import encrypt_password, decrypt_password
from logic.database import db_create
import sqlite3
import secrets
import os

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

db_path = os.path.join(os.path.dirname(__file__), 'data', 'prsc.db')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        master_password = request.form['master_password']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT encrypted_password FROM MasterPassword LIMIT 1")
        stored_encrypted_password = cursor.fetchone()
        conn.close()

        if stored_encrypted_password:
            stored_encrypted_password = stored_encrypted_password[0]
            decrypted_password = decrypt_password(stored_encrypted_password)

            if master_password == decrypted_password:
                session['authenticated'] = True
                return redirect(url_for('db'))
            else:
                return render_template('index.html',
                                       error="Отказано в доступе!")

    return render_template('index.html')


# Создание .db, если не найден
db_create()


@app.route('/db', methods=['GET', 'POST'])
def db():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Passwords')
    passwords = cursor.fetchall()
    conn.close()

    return render_template('db.html', passwords=passwords)


@app.route('/add_password', methods=['GET', 'POST'])
def add_password():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        website = request.form['website']
        login = request.form['login']
        password = request.form['password']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Passwords (website, login, password)\
            VALUES (?, ?, ?)",
                       (website, login, password))
        conn.commit()
        conn.close()

        return redirect(url_for('db'))

    return render_template('add_password.html')


@app.route('/del_password', methods=['GET', 'POST'])
def del_password():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        id = request.form.get('id')

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Passwords WHERE id = ?", (id,))
        conn.commit()
        conn.close()

        return redirect(url_for('db'))

    return render_template('del_password.html')


@app.route('/master', methods=['GET', 'POST'])
def master():
    if request.method == 'POST':
        master_password = request.form['master_password']
        confirm_master_password = request.form['confirm_master_password']

        if master_password == confirm_master_password:
            encrypted_password = encrypt_password(master_password)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE MasterPassword SET encrypted_password = ?\
                    WHERE id = 1",
                (encrypted_password,))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))
        else:
            return render_template('master.html', error="Пароли не совпадают!")

    return render_template('master.html')


if __name__ == '__main__':
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080)
    app.run(debug=True)
