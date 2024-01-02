import csv
import sqlite3

db_path = ('prsc.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM Passwords")
result = cursor.fetchall()

columns = [column[0] for column in cursor.description]
data = [dict(zip(columns, row)) for row in result]

with open('data.csv', 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(data)
