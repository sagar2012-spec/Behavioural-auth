import sqlite3
import statistics

def get_user_times(username):
    """Fetch all past time_taken values for a user."""
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute("SELECT time_taken FROM logins WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    # rows look like [(3.2,), (4.1,)] so pull out the numbers
    return [r[0] for r in rows]

def timing_similarity(username, new_time):
    """Return a similarity score from 0 to 100 for a new login time."""
    times = get_user_times(username)

    # need at least a few past logins to have a pattern
    if len(times) < 3:
        return None  # not enough data yet

    average = statistics.mean(times)
    # standard deviation = how much the times normally vary
    spread = statistics.pstdev(times)

    # if the user is extremely consistent, avoid dividing by zero
    if spread == 0:
        spread = 0.5

    # how many "units of normal variation" away is the new time?
    distance = abs(new_time - average) / spread

    # turn distance into a 0-100 score: close = high, far = low
    # within 1 unit is very good, beyond 3 units is very poor
    score = max(0, 100 - (distance * 33))
    return round(score, 1)