from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.post("/outlet/1/on")
def on():
    print("Outlet ON")
    return jsonify(status="on")

@app.post("/outlet/1/off")
def off():
    print("Outlet OFF")
    return jsonify(status="off")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)