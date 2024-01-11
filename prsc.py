from flask import Flask, \
    render_template, \
    request, \
    redirect, \
    url_for, \
    session, \
    abort
from logic.crypt import encrypt, decrypt, rotate_key
from logic.database import db_create
import sqlite3
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Создание .db, если не найден
db_create()
db_path = os.path.join(os.path.dirname(__file__), 'data', 'prsc.db')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            master_password = request.form['master_password']

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT encrypted_password\
                        FROM MasterPassword LIMIT 1")
                stored_encrypted_password = cursor.fetchone()

            if stored_encrypted_password:
                stored_encrypted_password = stored_encrypted_password[0]
                decrypted_password = decrypt(stored_encrypted_password)

                if master_password == decrypted_password:
                    session['authenticated'] = True
                    return redirect(url_for('db'))
                else:
                    return render_template('login.html',
                                           error="Отказано в доступе!")
        except Exception as e:
            print(f"Ошибка входа {e}")
            return render_template('login.html',
                                   error="Произошла ошибка при входе.")

    return render_template('login.html')


@app.route('/db', methods=['GET', 'POST'])
def db():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, website, encrypted_login, encrypted_password\
                    FROM Passwords')
            data = cursor.fetchall()

        decrypted_login_password = []

        for record in data:
            decrypted_login = decrypt(record[2])
            decrypted_password = decrypt(record[3])
            decrypted_login_password.append(
                (record[0], record[1],
                 decrypted_login, decrypted_password))

        return render_template('db.html', data=decrypted_login_password)

    except Exception as e:
        print(f"Произошла ошибка при запросе данных: {e}")
        abort(500, "Ошибка при запросе данных")


@app.route('/add_password', methods=['GET', 'POST'])
def add_password():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            website = request.form['website']
            login = request.form['login']
            password = request.form['password']

            encrypted_login = encrypt(login)
            encrypted_password = encrypt(password)

            with sqlite3.connect(db_path) as conn:
                conn.execute("INSERT INTO Passwords\
                    (website, encrypted_login, encrypted_password)\
                        VALUES (?, ?, ?)",
                             (website, encrypted_login, encrypted_password))

            return redirect(url_for('db'))

        except Exception as e:
            print(f"Произошла ошибка при добавлении пароля: {e}")
            abort(500, "Ошибка при добавлении пароля")

    return render_template('add_password.html')


@app.route('/del_password', methods=['GET', 'POST'])
def del_password():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            id = request.form.get('id')

            with sqlite3.connect(db_path) as conn:
                conn.execute("DELETE FROM Passwords WHERE id = ?", (id,))

            return redirect(url_for('db'))

        except Exception as e:
            print(f"Произошла ошибка при удалении пароля: {e}")
            abort(500, "Ошибка при удалении пароля")

    return render_template('del_password.html')


@app.route('/master_password', methods=['GET', 'POST'])
def master_password():
    if request.method == 'POST':
        try:
            master_password = request.form['master_password']
            confirm_master_password = request.form['confirm_master_password']

            if master_password == confirm_master_password:
                encrypted_password = encrypt(master_password)

                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE MasterPassword\
                            SET encrypted_password = ?\
                                WHERE id = 1",
                        (encrypted_password,))
                    cursor.execute("DELETE FROM Passwords")
                    conn.commit()

                rotate_key()

                return redirect(url_for('login'))
            else:
                return render_template('master_password.html',
                                       error="Пароли не совпадают!")

        except Exception as e:
            print(f"Произошла ошибка при изменении мастер-пароля: {e}")
            abort(500, "Ошибка при изменении мастер-пароля")

    return render_template('master_password.html')


if __name__ == '__main__':
    from waitress import serve
    print("Запущен сервер!")
    serve(app, host="0.0.0.0", port=8080)
    # app.run(debug=True)
