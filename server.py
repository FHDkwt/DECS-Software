from flask import Flask, request, jsonify, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "decs-secret-key"  

DEVICE_STATE = {"plug1": False}

PASSWORD = "decs123"

@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        return "Wrong password", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/status")
def status():
    return jsonify(DEVICE_STATE)

@app.post("/toggle")
def toggle():
    if not session.get("logged_in"):
        return jsonify(error="unauthorized"), 403

    data = request.get_json()
    plug = data.get("device", "plug1")
    state = data.get("on", False)

    DEVICE_STATE[plug] = state
    return jsonify(device=plug, on=state)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
from flask import Flask, request, jsonify

import secrets

app = Flask(__name__)

API_KEY = "decs-demo-key"

@app.route("/health")

def health():

    return {"status": "ok"}

@app.route("/login", methods=["POST"])

def login():

    data = request.json

    if not data or data.get("key") != API_KEY:

        return jsonify({"error": "unauthorized"}), 401

    token = secrets.token_hex(16)

    return jsonify({"token": token})

@app.route("/outlet/on", methods=["POST"])

def outlet_on():

    return jsonify({"status": "outlet ON command sent"})

@app.route("/outlet/off", methods=["POST"])

def outlet_off():

    return jsonify({"status": "outlet OFF command sent"})

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
