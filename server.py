from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False


app = Flask(__name__)


app.secret_key = os.environ.get("DECS_SECRET_KEY", "decs-secret-key")

# Demo password for the web
PASSWORD = os.environ.get("DECS_PASSWORD", "decs123")

# Demo device state (later will replace this with real CM5->plug control)
DEVICE_STATE = {"plug1": False}

# MQTT settings
MQTT_ENABLED = os.environ.get("DECS_MQTT_ENABLED", "0") == "1"
MQTT_BROKER = os.environ.get("DECS_MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("DECS_MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = os.environ.get("DECS_MQTT_TOPIC_PREFIX", "decs")

mqtt_client = None
if MQTT_ENABLED and MQTT_AVAILABLE:
    mqtt_client = mqtt.Client()


def publish_mqtt(device: str, on: bool) -> None:
    """Publish a simple ON/OFF command via MQTT if enabled."""
    if not (MQTT_ENABLED and mqtt_client):
        return
    topic = f"{MQTT_TOPIC_PREFIX}/{device}/control"
    payload = "ON" if on else "OFF"
    mqtt_client.publish(topic, payload)


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
    # Protect control endpoint behind login
    if not session.get("logged_in"):
        return jsonify(error="unauthorized"), 403

    data = request.get_json(silent=True) or {}
    device = data.get("device", "plug1")
    on = bool(data.get("on", False))

    DEVICE_STATE[device] = on
    publish_mqtt(device, on)

    return jsonify(device=device, on=on)


if __name__ == "__main__":
    # Connect MQTT only when enabled
    if MQTT_ENABLED and mqtt_client:
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as e:
            print(f"[MQTT] Could not connect to broker at {MQTT_BROKER}:{MQTT_PORT} -> {e}")

    # Runs on LAN too (good for CM5 + phone testing)
    app.run(host="0.0.0.0", port=5000)