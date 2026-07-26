import sqlite3
from patterns import build_timing_pattern, enrol_pattern, verify_pattern
from database import get_pattern

USER = "sagar"   # change to whatever username you've been logging in with

pattern = build_timing_pattern(USER)
print("Built pattern:", pattern)

pattern_id = enrol_pattern(USER, "timing", pattern)
print("Anchored on chain as:", pattern_id)

print("Integrity check:", verify_pattern(pattern_id))   # expect True

# now tamper with the local pattern, simulating an attacker
conn = sqlite3.connect("behaviour.db")
conn.execute(
    "UPDATE patterns SET value = ? WHERE pattern_id = ?",
    ('{"mean": 99.0, "samples": 3, "spread": 0.1}', pattern_id),
)
conn.commit()
conn.close()
print("Local pattern secretly altered")

print("Integrity check after tampering:", verify_pattern(pattern_id))  # expect False