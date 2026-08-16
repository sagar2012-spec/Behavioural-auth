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

def init_patterns():
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patterns (
            pattern_id TEXT PRIMARY KEY,
            username TEXT,
            signal TEXT,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_pattern(pattern_id, username, signal, value):
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO patterns (pattern_id, username, signal, value) VALUES (?, ?, ?, ?)",
        (pattern_id, username, signal, value)
    )
    conn.commit()
    conn.close()


def get_pattern(pattern_id):
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM patterns WHERE pattern_id = ?", (pattern_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def init_results():
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timing_score REAL,
            keystroke_score REAL,
            intact INTEGER,
            votes INTEGER,
            total INTEGER,
            passed INTEGER,
            drift TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_result(username, timing_score, keystroke_score, intact, votes, total, passed, drift):
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    from datetime import datetime
    cursor.execute(
        "INSERT INTO results (username, timing_score, keystroke_score, intact, votes, total, passed, drift, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (username, timing_score, keystroke_score, int(intact), votes, total, int(passed), drift, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_results():
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, timing_score, keystroke_score, intact, votes, total, passed, drift, timestamp FROM results ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return rows