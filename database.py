import sqlite3
import os


def db_create():
    database_file = "prsc.db"
    if not os.path.exists(database_file):
        conn = sqlite3.connect(database_file)
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
                        login TEXT NOT NULL,\
                            password TEXT NOT NULL,\
                                PRIMARY KEY("'id'" AUTOINCREMENT),\
                                    UNIQUE(id))"
        )
        cursor.execute(
            "INSERT INTO Passwords (website, login, password)\
                VALUES (?, ?, ?)", ('google.com', 'John_Doe', 'gOJ8ab4zHleP1s')
        )
        conn.commit()
        conn.close()
