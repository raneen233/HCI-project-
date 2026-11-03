"""Skribble - couch co-op drawing & guessing game (website stage).
Run:  python app.py   ->  http://127.0.0.1:5000
"""
from flask import Flask, render_template, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # needed for session (login state later)


@app.route("/")
def home():
    # Logged-in users see "Welcome, <name>" instead of the Log In button.
    return render_template("home.html", username=session.get("username"))


# ---- Placeholders: replaced page-by-page as designs arrive -----------------
def _soon(title):
    return render_template("coming_soon.html", title=title)

# TEMPORARY test account until Create Account saves real users
# (swap check_login for the real check in core/users.py when it's ready).
DEMO_USERS = {"doodle@example.com": {"username": "DoodleBuddy", "password": "doodle123"}}

def check_login(email, password):
    user = DEMO_USERS.get(email)
    if user and user["password"] == password:
        return user["username"]
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        username = check_login(email, password)
        if username:
            session["username"] = username
            return redirect(url_for("home"))
        return render_template("login.html", email=email,
                               error="That email and password don't match. Try again.")
    return render_template("login.html")

@app.route("/forgot-password")
def forgot_password():  return _soon("Forgot Password")

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
