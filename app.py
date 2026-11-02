"""Skribble - couch co-op drawing & guessing game (website stage).
Run:  python app.py   ->  http://127.0.0.1:5000
"""
from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # needed for session (login state later)


@app.route("/")
def home():
    # Logged-in users see "Welcome, <name>" instead of the Log In button.
    return render_template("home.html", username=session.get("username"))


# ---- Placeholders: replaced page-by-page as designs arrive -----------------
def _soon(title):
    return render_template("coming_soon.html", title=title)

@app.route("/login")
def login():        return _soon("Log In")

@app.route("/register")
def register():     return _soon("Create Account")

@app.route("/how-to-play")
def how_to_play():
    return render_template("how_to_play.html")

@app.route("/setup")
def setup():        return _soon("Game Setup")

@app.route("/settings")
def settings():     return _soon("Settings")


# ---- Dev helper: flip the Home page between guest / logged-in view ---------
@app.route("/dev/toggle-login")
def toggle_login():
    if session.get("username"):
        session.pop("username")
    else:
        session["username"] = "Doodler"
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
