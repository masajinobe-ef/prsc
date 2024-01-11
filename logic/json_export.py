import json
import sqlite3

db_path = ('../data/prsc.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM Passwords")
result = cursor.fetchall()

columns = [column[0] for column in cursor.description]
data = [dict(zip(columns, row)) for row in result]
json_data = json.dumps(data, indent=2)

with open('data.json', 'w') as file:
    file.write(json_data)
