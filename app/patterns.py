import hashlib
import json
import sqlite3
import statistics

from database import save_pattern, get_pattern
from chain import store_hash, get_hash


def make_hash(value):
    """SHA-256 hash of a pattern string."""
    return hashlib.sha256(value.encode()).hexdigest()


def build_timing_pattern(username):
    """Turn a user's login history into a stored pattern."""
    conn = sqlite3.connect("behaviour.db")
    cursor = conn.cursor()
    cursor.execute("SELECT time_taken FROM logins WHERE username = ?", (username,))
    times = [r[0] for r in cursor.fetchall()]
    conn.close()

    if len(times) < 3:
        return None

    pattern = {
        "mean": round(statistics.mean(times), 3),
        "spread": round(statistics.pstdev(times), 3),
        "samples": len(times),
    }
    # sort_keys makes the text identical every time for the same data
    return json.dumps(pattern, sort_keys=True)


def enrol_pattern(username, signal, value):
    """Save the pattern locally and anchor its hash on the blockchain."""
    pattern_id = f"{username}_{signal}"
    save_pattern(pattern_id, username, signal, value)
    store_hash(pattern_id, make_hash(value))
    return pattern_id


def verify_pattern(pattern_id):
    """Integrity check: does the local pattern still match the chain?"""
    stored = get_pattern(pattern_id)
    if stored is None:
        return False
    return make_hash(stored) == get_hash(pattern_id)

def pattern_drift(username):
    """
    Measure how far the user's current behaviour has drifted from their stored pattern.
    Returns the drift as a number, or None if there isn't enough to compare.
    """
    stored = get_pattern(f"{username}_timing")
    if stored is None:
        return None

    # rebuild a fresh pattern from current data
    fresh = build_timing_pattern(username)
    if fresh is None:
        return None

    stored_mean = json.loads(stored)["mean"]
    fresh_mean = json.loads(fresh)["mean"]

    # drift = how much the average has moved
    return abs(fresh_mean - stored_mean)


def update_pattern(username):
    """
    After a PASSED login, update the stored pattern if drift is moderate.
    Small drift: ignore. Moderate: update and re-anchor. Large: don't learn (suspicious).
    """
    drift = pattern_drift(username)
    if drift is None:
        return "no update"

    LOW = 0.3   # below this, no meaningful change
    HIGH = 2.0  # above this, too big to trust as natural drift

    if drift < LOW:
        return "stable"          # nothing to do
    elif drift > HIGH:
        return "large drift, flagged"   # do NOT learn from this
    else:
        # moderate drift: update the working pattern and re-anchor its hash
        fresh = build_timing_pattern(username)
        enrol_pattern(username, "timing", fresh)
        return "updated"