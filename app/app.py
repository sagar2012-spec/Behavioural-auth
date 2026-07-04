from flask import Flask, render_template, request, redirect
from database import init_db, save_login
from scoring import timing_similarity
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

        # score this attempt against the user's past pattern
        score = timing_similarity(username, time_taken)
        if score is None:
            print(f"[{username}] Not enough data yet, still learning. Time: {time_taken}")
        else:
            print(f"[{username}] Timing similarity score: {score} (time: {time_taken})")

        # save this login so the pattern keeps growing
        save_login(username, time_taken, ip_address, location)

        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return "<h1>Dashboard</h1><p>You are logged in.</p>"

if __name__ == "__main__":
    app.run(debug=True)