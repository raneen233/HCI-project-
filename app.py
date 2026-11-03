"""Skribble - couch co-op drawing & guessing game (website stage).
Run:  python app.py   ->  http://127.0.0.1:5000
"""
import base64
import json
import time
import uuid
from pathlib import Path

from flask import Flask, render_template, session, redirect, url_for, request, flash, send_file, abort, jsonify
from bluetooth_scanner import scanner
from game_words import pick_words, answer_options
from markupsafe import Markup
import word_icons
import players

app = Flask(__name__)
# {{ word_icon("Piano") }} in a template draws that word's line icon
app.jinja_env.globals["word_icon"] = lambda word: Markup(word_icons.svg(word))
app.secret_key = "dev-only-change-me"  # needed for session (login state later)


@app.route("/")
def home():
    # Logged-in users see "Welcome, <name>" instead of the Log In button.
    return render_template("home.html", username=session.get("username"))


# ---- Professional theme --------------------------------------------------------
# Every in-game page (word choosing -> drawing -> guessing -> results) uses the dark
# "ink" look when the game is on Professional. Game Setup switches live in setup.js.
GAME_PAGES = {"game", "draw", "guess", "game_over"}

@app.context_processor
def theme():
    g = session.get("game") or {}
    return {"pro_theme": request.endpoint in GAME_PAGES and g.get("difficulty") == "professional"}


# ---- Placeholders: replaced page-by-page as designs arrive -----------------
def _soon(title):
    return render_template("coming_soon.html", title=title)

# ---- Bluetooth sign-in -----------------------------------------------------
# Players are hardcoded in players.py. A player signs in when their phone is nearby.
SHOW_BT_SIMULATOR = True   # "pretend a phone is nearby" panel on the login page (testing only)

def safe_next(url):
    """Only allow redirects to our own pages (e.g. ?next=/setup)."""
    return url if url.startswith("/") and not url.startswith("//") else ""

def nearby_players():
    nearby = scanner.nearby()
    return [p for p in players.PLAYERS if players.normalize(p["bt_address"]) in nearby]

@app.route("/login")
def login():
    next_url = safe_next(request.args.get("next", ""))
    if session.get("username"):
        return redirect(next_url or url_for("home"))
    scanner.start()
    return render_template(
        "login.html",
        next=next_url,
        players=players.PLAYERS,
        show_simulator=SHOW_BT_SIMULATOR and app.debug,
    )

@app.route("/login/bluetooth", methods=["POST"])
def login_bluetooth():
    next_url = safe_next(request.form.get("next", ""))
    player = players.by_id(request.form.get("player_id", ""))
    # Double-check on the server: the phone must really be nearby right now.
    if not player or player not in nearby_players():
        flash("We lost your phone's signal. Bring it closer and try again.")
        return redirect(url_for("login", next=next_url) if next_url else url_for("login"))
    session["username"] = player["name"]
    session["player_id"] = player["id"]
    flash(f"Welcome back, {player['name']}! Signed in with your phone.")
    return redirect(next_url or url_for("home"))

@app.route("/api/bluetooth/nearby")
def api_nearby():
    """Polled by the login and setup pages every few seconds."""
    scanner.start()
    near = {p["id"] for p in nearby_players()}
    return jsonify({
        "status": scanner.status,
        "error": scanner.error,
        "players": [{"id": p["id"], "name": p["name"], "tone": p["tone"], "nearby": p["id"] in near}
                    for p in players.PLAYERS],
        "simulated": [p["id"] for p in players.PLAYERS
                      if players.normalize(p["bt_address"]) in scanner.simulated],
    })

@app.route("/dev/bluetooth/simulate", methods=["POST"])
def dev_simulate():
    """Testing without phones: toggle 'this phone is nearby'. Only works in debug mode."""
    if not (SHOW_BT_SIMULATOR and app.debug):
        abort(404)
    player = players.by_id((request.get_json(silent=True) or {}).get("player_id", ""))
    if not player:
        abort(400)
    scanner.toggle_simulated(player["bt_address"])
    return jsonify({"ok": True})

@app.route("/how-to-play")
def how_to_play():
    return render_template("how_to_play.html")

# ---- Game Setup -----------------------------------------------------------
DIFFICULTIES = {
    "casual":       {"name": "Casual",       "seconds": 60},
    "professional": {"name": "Professional", "seconds": 45},
}
ROUND_OPTIONS = [4, 6, 8, 10]

# Each player's last setup, so the page can remember it ("context").
PREFS_FILE = Path(__file__).parent / "data" / "player_prefs.json"

def load_prefs():
    if PREFS_FILE.exists():
        return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
    return {}

def save_prefs(prefs):
    PREFS_FILE.parent.mkdir(exist_ok=True)
    PREFS_FILE.write_text(json.dumps(prefs, indent=2), encoding="utf-8")

@app.route("/setup", methods=["GET", "POST"])
def setup():
    player1 = session.get("username")
    if not player1:
        flash("Log in first to set up a game.")
        return redirect(url_for("login", next=url_for("setup")))

    scanner.start()
    others = [p["name"] for p in players.PLAYERS if p["name"] != player1]
    prefs = load_prefs()

    if request.method == "POST":
        difficulty = request.form.get("difficulty")
        rounds = request.form.get("rounds", type=int)
        player2 = request.form.get("player2", "").strip()
        if (difficulty not in DIFFICULTIES or rounds not in ROUND_OPTIONS
                or player2 not in others + ["Guest"]):
            flash("Something was missing. Check your setup and try again.")
            return redirect(url_for("setup"))

        session["game"] = {
            "id": uuid.uuid4().hex,
            "player1": player1,
            "player2": player2,
            "difficulty": difficulty,
            "seconds": DIFFICULTIES[difficulty]["seconds"],
            "rounds": rounds,
            "round": 1,
            "scores": {player1: 0, player2: 0},
        }
        # Context: remember this player's choices for next time.
        prefs[player1] = {"difficulty": difficulty, "rounds": rounds, "player2": player2}
        save_prefs(prefs)
        return redirect(url_for("game"))

    last = prefs.get(player1) or {}
    player2 = last.get("player2")
    if player2 not in others + ["Guest"]:
        player2 = None
    return render_template(
        "setup.html",
        player1=player1,
        others=[p for p in players.PLAYERS if p["name"] != player1],
        player2=player2,
        difficulty=last.get("difficulty", "casual"),
        pro_theme=last.get("difficulty") == "professional",
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
    if g.get("finished"):
        return redirect(url_for("game_over"))
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
    g["drawing_done"] = False
    g.pop("draw_started", None)
    g.setdefault("used", []).append(word)
    g["choices"] = None              # next round gets fresh words
    session["game"] = g
    return redirect(url_for("draw"))

# Casual gets 6 colours; Professional gets 4 extra ("more drawing options")
CASUAL_COLORS = [("Ink", "#2a2840"), ("Coral", "#ef7f72"), ("Sky", "#6db3e8"),
                 ("Leaf", "#6bb89a"), ("Sun", "#f6c85f"), ("Grape", "#8460d6")]
PRO_EXTRA_COLORS = [("Slate", "#4a5878"), ("Lavender", "#b7a3e3"),
                    ("Sand", "#e8dcc4"), ("Stone", "#cfcfd4")]
DRAWINGS_DIR = Path(__file__).parent / "data" / "drawings"

def drawing_path(g):
    return DRAWINGS_DIR / f"{g['id']}_round{g['round']}.png"

@app.route("/game/draw")
def draw():
    g = session.get("game")
    if not g or not g.get("word"):
        return redirect(url_for("game"))
    if g.get("drawing_done"):
        return redirect(url_for("guess"))

    # The clock starts when the canvas first opens; refreshing doesn't reset it.
    if not g.get("draw_started"):
        g["draw_started"] = time.time()
        session["game"] = g
    remaining = max(5, int(g["seconds"] - (time.time() - g["draw_started"])))

    pro = g["difficulty"] == "professional"
    drawer, guesser = roles(g)
    return render_template(
        "draw.html",
        word=g["word"], guesser=guesser, remaining=remaining, pro=pro,
        colors=CASUAL_COLORS + (PRO_EXTRA_COLORS if pro else []),
        default_color=0 if pro else 5,
        **game_context(g, drawer),
    )

@app.route("/game/draw", methods=["POST"])
def submit_drawing():
    g = session.get("game")
    if not g or not g.get("word"):
        return redirect(url_for("setup"))
    data = request.form.get("drawing", "")
    prefix = "data:image/png;base64,"
    if not data.startswith(prefix) or len(data) > 10_000_000:
        flash("That drawing couldn't be sent. Try again.")
        return redirect(url_for("draw"))

    g.setdefault("id", uuid.uuid4().hex)
    DRAWINGS_DIR.mkdir(parents=True, exist_ok=True)
    drawing_path(g).write_bytes(base64.b64decode(data[len(prefix):]))

    g["drawing_done"] = True
    g.pop("draw_started", None)
    session["game"] = g
    drawer, guesser = roles(g)
    if request.form.get("reason") == "timeout":
        flash(f"Time's up! Your drawing was sent to {guesser}.")
    else:
        flash(f"Turn submitted! Pass the laptop to {guesser}.")
    return redirect(url_for("guess"))

@app.route("/game/drawing.png")
def drawing_image():
    """The current round's drawing (the Guessing page shows it)."""
    g = session.get("game")
    if not g or not g.get("drawing_done") or not drawing_path(g).exists():
        abort(404)
    return send_file(drawing_path(g), mimetype="image/png", max_age=0)

# ---- Guessing ---------------------------------------------------------------
GUESSER_POINTS = 20   # for guessing right
DRAWER_POINTS = 10    # for drawing something your friend could guess

@app.route("/game/guess")
def guess():
    g = session.get("game")
    if not g or not g.get("drawing_done"):
        return redirect(url_for("game"))
    # 4 answers, picked once per round so refreshing doesn't change them
    if not g.get("options"):
        g["options"] = answer_options(g["difficulty"], g["word"])
        session["game"] = g
    drawer, guesser = roles(g)
    return render_template(
        "guess.html",
        drawer=drawer, guesser=guesser,
        options=g["options"],
        guess=g.get("guess"), guess_correct=g.get("guess_correct"), word=g["word"],
        last_round=g["round"] >= g["rounds"],
        **game_context(g, guesser),
    )

@app.route("/game/guess", methods=["POST"])
def submit_guess():
    g = session.get("game")
    if not g or not g.get("drawing_done") or not g.get("options"):
        abort(400)
    drawer, guesser = roles(g)

    if not g.get("guess"):                       # only the first guess counts
        answer = (request.get_json(silent=True) or {}).get("answer", "")
        if answer not in g["options"]:
            abort(400)
        correct = answer == g["word"]
        if correct:
            g["scores"][guesser] = g["scores"].get(guesser, 0) + GUESSER_POINTS
            g["scores"][drawer] = g["scores"].get(drawer, 0) + DRAWER_POINTS
        g["guess"], g["guess_correct"] = answer, correct
        session["game"] = g

    return jsonify({
        "guess": g["guess"],
        "correct": g["guess_correct"],
        "word": g["word"],
        "points": GUESSER_POINTS if g["guess_correct"] else 0,
        "score": g["scores"].get(guesser, 0),
    })

@app.route("/game/next", methods=["POST"])
def next_round():
    g = session.get("game")
    if not g:
        return redirect(url_for("setup"))
    if not g.get("guess"):
        return redirect(url_for("guess"))
    for key in ("word", "choices", "options", "guess", "guess_correct", "draw_started"):
        g.pop(key, None)
    g["drawing_done"] = False
    if g["round"] >= g["rounds"]:
        g["finished"] = True
        session["game"] = g
        return redirect(url_for("game_over"))
    g["round"] += 1
    session["game"] = g
    return redirect(url_for("game"))

# ---- Game over --------------------------------------------------------------
@app.route("/game/over")
def game_over():
    g = session.get("game")
    if not g:
        return redirect(url_for("setup"))
    if not g.get("finished"):
        return redirect(url_for("game"))
    names = [g["player1"], g["player2"]]
    results = [(n, g["scores"].get(n, 0)) for n in names]
    top = max(score for _, score in results)
    winners = [n for n, score in results if score == top]
    tones = {n: (players.by_name(n) or {}).get("tone", "gray") for n in names}
    return render_template("game_over.html", game=g, results=results,
                           winner=winners[0], tie=len(winners) > 1, tones=tones)

@app.route("/game/again", methods=["POST"])
def play_again():
    """End this game and go back to Game Setup (last choices are pre-selected there)."""
    session.pop("game", None)
    return redirect(url_for("setup"))

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
    session.pop("player_id", None)
    flash("You've been logged out. See you soon!")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
