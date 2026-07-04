import sqlite3

# create (or open) the database file and make the table
def init_db():
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            time_taken REAL,
            ip_address TEXT,
            location TEXT
        )
    """)
    conn.commit()
    conn.close()

# save one login's behaviour
def save_login(username, time_taken, ip_address, location):
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logins (username, time_taken, ip_address, location) VALUES (?, ?, ?, ?)",
        (username, time_taken, ip_address, location)
    )
    conn.commit()
    conn.close()