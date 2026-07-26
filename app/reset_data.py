import sqlite3

conn = sqlite3.connect("behaviour.db")
conn.execute("DELETE FROM logins")
conn.execute("DELETE FROM patterns")
conn.commit()
conn.close()

print("Data cleared")