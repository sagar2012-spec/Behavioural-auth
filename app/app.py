from flask import Flask, render_template, request, redirect
from database import init_db, save_login, init_patterns, save_pattern, get_pattern
from scoring import timing_similarity
from scoring import timing_similarity, location_similarity
from patterns import build_timing_pattern, enrol_pattern, verify_pattern
from database import get_pattern
import random

app = Flask(__name__)
init_db()
init_patterns()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        time_taken = float(request.form["time_taken"])

        fake_ips = ["192.168.0.10", "192.168.0.11", "10.0.0.5"]
        fake_locations = ["Preston", "Manchester", "Leeds"]
        ip_address = random.choice(fake_ips)
        location = random.choice(fake_locations)

        pattern_id = f"{username}_timing"
        stored = get_pattern(pattern_id)

        if stored is None:
            # no pattern yet, still enrolling
            save_login(username, time_taken, ip_address, location)
            pattern = build_timing_pattern(username)
            if pattern:
                enrol_pattern(username, "timing", pattern)
                print(f"[{username}] Pattern created and anchored on chain")
            else:
                print(f"[{username}] Enrolling, need more logins")
            return redirect("/dashboard")

        # STEP 1: similarity check (local)
        score = timing_similarity(username, time_taken)

        # STEP 2: integrity check (blockchain)
        intact = verify_pattern(pattern_id)

        # a signal only passes if BOTH are true
        passed = (score is not None and score >= 60) and intact

        print(f"[{username}] similarity={score} intact={intact} -> {'PASS' if passed else 'FAIL'}")
        if not intact:
            print(f"[{username}] WARNING: stored pattern has been tampered with")

        save_login(username, time_taken, ip_address, location)
        return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return "<h1>Dashboard</h1><p>You are logged in.</p>"

if __name__ == "__main__":
    app.run(debug=True)