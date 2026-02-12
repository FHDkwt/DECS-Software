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