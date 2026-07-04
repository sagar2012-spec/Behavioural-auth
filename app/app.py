from flask import Flask, render_template, request, redirect
from database import init_db, save_login
from scoring import timing_similarity
from scoring import timing_similarity, location_similarity
import random

app = Flask(__name__)
init_db()

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

       # score both signals against the user's past pattern
        timing_score = timing_similarity(username, time_taken)
        location_score = location_similarity(username, location)

        # save this login so patterns keep growing
        save_login(username, time_taken, ip_address, location)

        # only vote once we have enough history
        if timing_score is None or location_score is None:
            print(f"[{username}] Still learning, not enough data yet.")
        else:
            # each signal passes if it scores 60 or more
            votes = 0
            if timing_score >= 60:
                votes += 1
            if location_score >= 60:
                votes += 1

            print(f"[{username}] timing={timing_score} location={location_score} -> {votes}/2 signals passed")

            # with two signals for now, require both to pass
            if votes >= 2:
                print(f"[{username}] ACCEPTED")
            else:
                print(f"[{username}] FLAGGED - behaviour does not match")

        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return "<h1>Dashboard</h1><p>You are logged in.</p>"

if __name__ == "__main__":
    app.run(debug=True)