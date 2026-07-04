from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        time_taken = request.form["time_taken"]

        # simulated context signals (dummy values for the proof of concept)
        fake_ips = ["192.168.0.10", "192.168.0.11", "10.0.0.5"]
        fake_locations = ["Preston", "Manchester", "Leeds"]
        ip_address = random.choice(fake_ips)
        location = random.choice(fake_locations)

        # print everything we captured so we can see it working
        print("----- Login attempt -----")
        print("Username:", username)
        print("Time taken (s):", time_taken)
        print("Simulated IP:", ip_address)
        print("Simulated location:", location)

        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return "<h1>Dashboard</h1><p>You are logged in.</p>"

if __name__ == "__main__":
    app.run(debug=True)