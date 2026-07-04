import sqlite3

conn = sqlite3.connect("behaviour.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM logins")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()