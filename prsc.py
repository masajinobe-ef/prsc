from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)

# Генерация случайного секретного ключа для подписи сессии
app.secret_key = os.urandom(24)


def create_user(username, password):
    con = sqlite3.connect('prsc.db')
    cur = con.cursor()

    # Хеширование пароля перед сохранением в базе данных
    hashed_password = generate_password_hash(password,
                                             method='pbkdf2:sha256',
                                             salt_length=16)

    # Вставка нового пользователя в таблицу users
    cur.execute('INSERT INTO Users (username, password) VALUES (?, ?)',
                (username, hashed_password))

    con.commit()
    con.close()


def get_user(username):
    con = sqlite3.connect('prsc.db')
    cur = con.cursor()

    # Получение пользователя из базы данных по имени пользователя
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()

    # Закрытие соединения
    con.close()

    return user


def check_master_password(password, hashed_password):
    return check_password_hash(hashed_password, password)


def is_user_authenticated():
    return session.get('authenticated', False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        master_password = request.form.get('master_password')

        user = get_user(session.get('username'))

        if user and check_master_password(master_password, user[1]):
            # Устанавливает флаг аутентификации в сессии
            session['authenticated'] = True

            # Подключение к базе данных
            con = sqlite3.connect('prsc.db')
            cur = con.cursor()

            # Получение паролей из базы данных
            cur.execute('SELECT * FROM Passwords')
            passwords = cur.fetchall()

            # Закрытие соединения
            con.close()

            # Передача данных в шаблон и отображение таблицы
            return render_template('index.html', passwords=passwords)
        else:
            return render_template('login.html',
                                   message='Неверный мастер-пароль')

    return render_template('login.html', message=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Создание нового пользователя
        create_user(username, password)

        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    # Удаляет флаг аутентификации из сессии при выходе
    session.pop('authenticated', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
