from flask import Flask, render_template, request, redirect
from database import init_db, save_login, init_patterns, save_pattern, get_pattern, init_results, save_result, get_results
from scoring import timing_similarity, location_similarity
from patterns import build_timing_pattern, enrol_pattern, verify_pattern, update_pattern
from keystroke_signal import keystroke_score, columns
import pandas as pd
import random

# load CMU data once so we can pull a keystroke sample per login
keystroke_data = pd.read_csv("../ml/DSL-StrongPasswordData.csv")

def get_keystroke_sample(genuine=True):
    """Return one keystroke timing sample. genuine=True uses the enrolled profile."""
    subject = "s002" if genuine else "s020"
    row = keystroke_data[keystroke_data["subject"] == subject][columns].sample(1)
    return row.iloc[0].tolist()

app = Flask(__name__)
init_db()
init_patterns()
init_results()

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

        # still enrolling if no pattern yet
        if stored is None:
            save_login(username, time_taken, ip_address, location)
            pattern = build_timing_pattern(username)
            if pattern:
                enrol_pattern(username, "timing", pattern)
                print(f"[{username}] Pattern created and anchored on chain")
            else:
                print(f"[{username}] Enrolling, need more logins")
            return redirect("/dashboard")

        # --- SIGNALS ---

        # signal 1: timing similarity (local)
        timing_score = timing_similarity(username, time_taken)

        # signal 2: keystroke (scored against enrolled CMU profile)
        ks_sample = get_keystroke_sample(genuine=True)
        ks_score = keystroke_score(ks_sample)

        # integrity check (blockchain)
        intact = verify_pattern(pattern_id)

        # --- VOTE: majority of implemented signals must pass ---
        votes = 0
        total = 0

        if timing_score is not None:
            total += 1
            if timing_score >= 60:
                votes += 1

        if ks_score is not None:
            total += 1
            if ks_score >= 60:
                votes += 1

        # need a majority of signals to pass AND the integrity check intact
        passed = intact and votes > total / 2

        print(f"[{username}] timing={timing_score} keystroke={ks_score} intact={intact} -> {votes}/{total} passed -> {'PASS' if passed else 'FAIL'}")
        if not intact:
            print(f"[{username}] WARNING: stored pattern has been tampered with")

        # save this login
        save_login(username, time_taken, ip_address, location)

       # adaptive learning: only learn from logins that passed
        drift_result = "not checked"
        if passed:
            drift_result = update_pattern(username)
            print(f"[{username}] drift check: {drift_result}")

        # record this login's outcome for the dashboard
        save_result(username, timing_score, ks_score, intact, votes, total, passed, drift_result)

        return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    results = get_results()
    return render_template("dashboard.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)