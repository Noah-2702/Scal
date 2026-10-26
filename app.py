import os, sqlite3, secrets, string
from flask import Flask, request, jsonify, session, render_template, g
from dotenv import load_dotenv
from analyzer import analyze_message, FALLBACK
from scanner import quick_scan
import hashlib


load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
DB = "scamshield.db"

# Database helpers
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e):
    d = g.pop("db", None)
    if d:
        d.close()


def init_db():
    with sqlite3.connect(DB) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS circles(code TEXT PRIMARY KEY, name TEXT);
        CREATE TABLE IF NOT EXISTS alerts(
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, sender TEXT,
            message TEXT, verdict TEXT, explanation TEXT,
            handled INTEGER DEFAULT 0, note TEXT,
            created TEXT DEFAULT CURRENT_TIMESTAMP);
        """)



#Flask routes
SEVERITY = {"looks_safe": 0, "suspicious": 1, "scam": 2}

import json, os
CACHE_FILE = "check_cache.json"
cache = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}

def merge(local, ai):
    if ai is FALLBACK:
        return local
    final = ai["verdict"]
    if local.get("score", 0) >= 60 and SEVERITY.get(final, 1) < 2:
        final = "scam"                      # strong local evidence overrides
    flags = [] if final == "looks_safe" else list(dict.fromkeys(local["red_flags"] + ai.get("red_flags", [])))
    base = ai if final == ai["verdict"] else local
    return {**base, "verdict": final, "red_flags": flags}

@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/me")
def me():
    return jsonify(code=session.get("code"), name=session.get("name"), circle=session.get("circle"))


@app.post("/api/circle/create")
def create_circle():
    d = request.get_json()
    code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    db().execute("INSERT INTO circles VALUES (?, ?)", (code, d["circle"][:60]))
    db().commit()
    session.update(code=code, name=d["name"][:40], circle=d["circle"][:60])
    return jsonify(ok=True, code=code)


@app.post("/api/circle/join")
def join_circle():
    d = request.get_json()
    code = d["code"].strip().upper()
    row = db().execute("SELECT * FROM circles WHERE code=?", (code,)).fetchone()
    if not row:
        return jsonify(ok=False, error="Code not found"), 404
    session.update(code=code, name=d["name"][:40], circle=row["name"])
    return jsonify(ok=True)


@app.post("/api/quickscan")
def quickscan():
    text = (request.get_json().get("text") or "").strip()[:4000]
    if not text:
        return jsonify(error="Paste a message first"), 400
    return jsonify(quick_scan(text))

@app.post("/api/check")
def check():
    text = (request.get_json().get("text") or "").strip()[:4000]
    if not text:
        return jsonify(error="Paste a message first"), 400
    key = hashlib.sha256(text.encode()).hexdigest()
    if key in cache:
        return jsonify(cache[key])
    local = quick_scan(text)
    ai = analyze_message(text)
    result = merge(local, ai)
    if ai is not FALLBACK:                  # don't cache failures
        cache[key] = result
        json.dump(cache, open(CACHE_FILE, "w"))
    return jsonify(result)


@app.post("/api/alert")
def alert():
    if "code" not in session:
        return jsonify(error="Join a family circle first"), 401
    d = request.get_json()
    db().execute(
        "INSERT INTO alerts(code, sender, message, verdict, explanation) VALUES (?,?,?,?,?)",
        (session["code"], session["name"], d["message"][:4000], d["verdict"], d["explanation"][:1000]),
    )
    db().commit()
    return jsonify(ok=True)


@app.get("/api/alerts")
def alerts():
    if "code" not in session:
        return jsonify([])
    rows = db().execute("SELECT * FROM alerts WHERE code=? ORDER BY id DESC", (session["code"],)).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/alerts/<int:aid>/handle")
def handle(aid):
    note = (request.get_json().get("note") or "")[:300]
    db().execute("UPDATE alerts SET handled=1, note=? WHERE id=? AND code=?", (note, aid, session.get("code")))
    db().commit()
    return jsonify(ok=True)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)