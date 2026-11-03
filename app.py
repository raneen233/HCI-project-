"""Skribble - couch co-op drawing & guessing game (website stage).
Run:  python app.py   ->  http://127.0.0.1:5000
"""
import json
import re
from pathlib import Path

from flask import Flask, render_template, session, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from game_words import pick_words

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # needed for session (login state later)


@app.route("/")
def home():
    # Logged-in users see "Welcome, <name>" instead of the Log In button.
    return render_template("home.html", username=session.get("username"))


# ---- Placeholders: replaced page-by-page as designs arrive -----------------
def _soon(title):
    return render_template("coming_soon.html", title=title)

# ---- Accounts: saved in data/accounts.json (passwords are hashed) ----------
# Simple file storage for now. If core/users.py ends up handling users,
# these helpers can be swapped for its functions.
ACCOUNTS_FILE = Path(__file__).parent / "data" / "accounts.json"

def load_accounts():
    if ACCOUNTS_FILE.exists():
        return json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    return {}

def save_accounts(accounts):
    ACCOUNTS_FILE.parent.mkdir(exist_ok=True)
    ACCOUNTS_FILE.write_text(json.dumps(accounts, indent=2), encoding="utf-8")

def check_login(email, password):
    """Return the username if the email + password are right, else None."""
    account = load_accounts().get(email)
    if account and check_password_hash(account["password"], password):
        return account["username"]
    return None

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")

@app.route("/login", methods=["GET", "POST"])
def login():
    # ?next=/setup means "go back there after logging in" (only our own pages allowed)
    next_url = request.args.get("next", "")
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        username = check_login(email, password)
        if username:
            session["username"] = username
            return redirect(next_url or url_for("home"))
        return render_template("login.html", email=email, next=next_url,
                               error="That email and password don't match. Try again.")
    return render_template("login.html", next=next_url)

@app.route("/forgot-password")
def forgot_password():  return _soon("Forgot Password")

@app.route("/terms")
def terms():        return _soon("Terms of Service")

@app.route("/privacy")
def privacy():      return _soon("Privacy Policy")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    form = {
        "username": request.form.get("username", "").strip(),
        "email": request.form.get("email", "").strip().lower(),
        "terms": request.form.get("terms") == "yes",
    }
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")
    accounts = load_accounts()

    # Same checks as register.js, repeated here because the browser can't be trusted.
    errors = {}
    if not USERNAME_RE.match(form["username"]):
        errors["username"] = "Use 3-20 letters, numbers or _."
    elif any(a["username"].lower() == form["username"].lower() for a in accounts.values()):
        errors["username"] = "That username is taken. Try another one."
    if not EMAIL_RE.match(form["email"]):
        errors["email"] = "Enter a valid email, like doodle@example.com."
    elif form["email"] in accounts:
        errors["email"] = "That email already has an account. Log in instead?"
    if len(password) < 6:
        errors["password"] = "Use at least 6 characters."
    if confirm != password:
        errors["confirm"] = "Passwords don't match."
    if not form["terms"]:
        errors["terms"] = "Please agree to the terms to join the fun."

    if errors:
        return render_template("register.html", form=form, errors=errors)

    accounts[form["email"]] = {
        "username": form["username"],
        "password": generate_password_hash(password),
    }
    save_accounts(accounts)
    session["username"] = form["username"]   # log them straight in
    return redirect(url_for("home"))

@app.route("/how-to-play")
def how_to_play():
    return render_template("how_to_play.html")

# ---- Game Setup -----------------------------------------------------------
DIFFICULTIES = {
    "casual":       {"name": "Casual",       "seconds": 60},
    "professional": {"name": "Professional", "seconds": 45},
}
ROUND_OPTIONS = [4, 6, 8, 10]

def find_account(accounts, username):
    for account in accounts.values():
        if account["username"] == username:
            return account
    return None

@app.route("/setup", methods=["GET", "POST"])
def setup():
    player1 = session.get("username")
    if not player1:
        flash("Log in first to set up a game.")
        return redirect(url_for("login", next=url_for("setup")))

    accounts = load_accounts()
    account = find_account(accounts, player1)
    others = sorted(a["username"] for a in accounts.values() if a["username"] != player1)

    if request.method == "POST":
        difficulty = request.form.get("difficulty")
        rounds = request.form.get("rounds", type=int)
        player2 = request.form.get("player2", "").strip()
        if (difficulty not in DIFFICULTIES or rounds not in ROUND_OPTIONS
                or player2 not in others + ["Guest"]):
            flash("Something was missing. Check your setup and try again.")
            return redirect(url_for("setup"))

        session["game"] = {
            "player1": player1,
            "player2": player2,
            "difficulty": difficulty,
            "seconds": DIFFICULTIES[difficulty]["seconds"],
            "rounds": rounds,
            "round": 1,
            "scores": {player1: 0, player2: 0},
        }
        # Context: remember this player's choices for next time.
        if account:
            account["last_setup"] = {"difficulty": difficulty, "rounds": rounds, "player2": player2}
            save_accounts(accounts)
        return redirect(url_for("game"))

    last = (account or {}).get("last_setup") or {}
    player2 = last.get("player2")
    if player2 not in others + ["Guest"]:
        player2 = None
    return render_template(
        "setup.html",
        player1=player1,
        others=others,
        player2=player2,
        difficulty=last.get("difficulty", "casual"),
        rounds=last.get("rounds", 6),
        round_options=ROUND_OPTIONS,
        remembered=bool(last),
    )

# ---- In-game screens --------------------------------------------------------
def roles(g):
    """Odd rounds: Player 1 draws. Even rounds: Player 2 draws."""
    if g["round"] % 2 == 1:
        return g["player1"], g["player2"]
    return g["player2"], g["player1"]

def game_context(g, you):
    """Values every in-game page needs for the shared header/footer."""
    return {
        "game": g,
        "you": you,
        "you_score": g["scores"].get(you, 0),
        "difficulty_name": DIFFICULTIES[g["difficulty"]]["name"],
    }

@app.route("/game")
def game():
    g = session.get("game")
    if not g:
        return redirect(url_for("setup"))
    # The server picks the 6 words once per round, so refreshing can't reroll them.
    if not g.get("choices"):
        g["choices"] = pick_words(g["difficulty"], exclude=g.get("used", []))
        session["game"] = g
    drawer, guesser = roles(g)
    return render_template("word.html", drawer=drawer, guesser=guesser,
                           choices=g["choices"], **game_context(g, drawer))

@app.route("/game/word", methods=["POST"])
def choose_word():
    g = session.get("game")
    if not g:
        return redirect(url_for("setup"))
    word = request.form.get("word", "")
    if word not in [c["word"] for c in g.get("choices") or []]:
        return redirect(url_for("game"))
    g["word"] = word
    g.setdefault("used", []).append(word)
    g["choices"] = None              # next round gets fresh words
    session["game"] = g
    return redirect(url_for("draw"))

@app.route("/game/draw")
def draw():
    g = session.get("game")
    if not g or not g.get("word"):
        return redirect(url_for("game"))
    return _soon("Drawing")

@app.route("/game/quit", methods=["POST"])
def quit_game():
    session.pop("game", None)
    flash("Game ended. Set up a new one whenever you're ready.")
    return redirect(url_for("setup"))

@app.route("/settings")
def settings():     return _soon("Settings")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("You've been logged out. See you soon!")
    return redirect(url_for("home"))


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
