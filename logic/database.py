import sqlite3
import os


def db_create():
    db_path = "data/prsc.db"
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS MasterPassword\
                (id INTEGER NOT NULL UNIQUE,\
                    user TEXT NOT NULL,\
                        encrypted_password TEXT NOT NULL,\
                            PRIMARY KEY("'id'" AUTOINCREMENT),\
                                UNIQUE(id))"
        )
        cursor.execute(
            "INSERT INTO MasterPassword (user, encrypted_password)\
                VALUES (?, ?)", ('user', '0000')
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS Passwords\
                (id INTEGER NOT NULL UNIQUE,\
                    website TEXT NOT NULL,\
                        encrypted_login TEXT NOT NULL,\
                            encrypted_password TEXT NOT NULL,\
                                PRIMARY KEY("'id'" AUTOINCREMENT),\
                                    UNIQUE(id))"
        )
        cursor.execute(
            "INSERT INTO Passwords\
                (website, encrypted_login, encrypted_password)\
                VALUES (?, ?, ?)", ('google.com', 'John_Doe', 'gOJ8ab4zHleP1s')
        )
        conn.commit()
        conn.close()
