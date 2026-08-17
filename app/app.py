from flask import Flask, render_template, request, redirect
from database import init_db, save_login, init_patterns, save_pattern, get_pattern, init_results, save_result, get_results
from scoring import timing_similarity, location_similarity, ip_similarity
from patterns import build_timing_pattern, enrol_pattern, verify_pattern, update_pattern
from keystroke_signal import keystroke_score, columns
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, save_login, init_patterns, save_pattern, get_pattern, init_results, save_result, get_results, init_users, create_user, get_user, get_all_users_stats, get_overall_stats
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
init_users()

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/admin")
def admin():
    user_stats = get_all_users_stats()
    overall = get_overall_stats()
    return render_template("admin.html", user_stats=user_stats, overall=overall)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        if create_user(username, password_hash):
            print(f"New user registered: {username}")
            return redirect("/login")
        else:
            return "Username already taken. <a href='/register'>Try again</a>"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # verify the password first (base authentication)
        stored_hash = get_user(username)
        if stored_hash is None or not check_password_hash(stored_hash, password):
            print(f"[{username}] Login failed: wrong username or password")
            return "Invalid username or password. <a href='/login'>Try again</a>"

        time_taken = float(request.form["time_taken"])

       # each user has a stable "home" location and IP, with occasional variation
        home_locations = {"sagar": "Preston", "friend1": "Manchester", "friend2": "Leeds"}
        home_ips = {"sagar": "192.168.0.10", "friend1": "192.168.0.11", "friend2": "10.0.0.5"}

        home_location = home_locations.get(username, "Preston")
        home_ip = home_ips.get(username, "192.168.0.10")

        # 80% of the time they log in from home, 20% somewhere else (realistic variation)
        if random.random() < 0.8:
            location = home_location
            ip_address = home_ip
        else:
            location = random.choice(["Preston", "Manchester", "Leeds", "London"])
            ip_address = random.choice(["192.168.0.10", "192.168.0.11", "10.0.0.5"])

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
        # signal 3: location familiarity
        location_score = location_similarity(username, location)
        # signal 4: IP familiarity
        ip_score = ip_similarity(username, ip_address)

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

        if location_score is not None:
            total += 1
            if location_score >= 60:
                votes += 1

        if ip_score is not None:
            total += 1
            if ip_score >= 60:
                votes += 1

        # need a majority of signals to pass AND the integrity check intact
        passed = intact and votes > total / 2

        print(f"[{username}] timing={timing_score} keystroke={ks_score} location={location_score} ip={ip_score} intact={intact} -> {votes}/{total} passed -> {'PASS' if passed else 'FAIL'}")
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