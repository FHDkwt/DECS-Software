from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get("DECS_SECRET_KEY", "decs-secret-key")

PASSWORD = os.environ.get("DECS_PASSWORD", "decs123")

# Track latest known state from server/UI
DEVICE_STATE = {
    "plug1": False,
    "plug1_status": "UNKNOWN",
    "plug1_heartbeat": "UNKNOWN",
}

MQTT_ENABLED = os.environ.get("DECS_MQTT_ENABLED", "0") == "1"
MQTT_BROKER = os.environ.get("DECS_MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("DECS_MQTT_PORT", "1883"))

mqtt_client = None
if MQTT_ENABLED and MQTT_AVAILABLE:
    mqtt_client = mqtt.Client()

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    if topic == "devices/plug1/status":
        DEVICE_STATE["plug1_status"] = payload
        if payload == "ON":
            DEVICE_STATE["plug1"] = True
        elif payload == "OFF":
            DEVICE_STATE["plug1"] = False

    elif topic == "devices/plug1/heartbeat":
        DEVICE_STATE["plug1_heartbeat"] = payload

def publish_mqtt(device: str, on: bool) -> None:
    if not (MQTT_ENABLED and mqtt_client):
        return

    topic = f"devices/{device}/cmd"
    payload = "ON" if on else "OFF"
    mqtt_client.publish(topic, payload)

@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        error = "Wrong password"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/health")
def health():
    return jsonify(status="ok", mqtt_enabled=MQTT_ENABLED)

@app.get("/status")
def status():
    return jsonify(DEVICE_STATE)

@app.post("/toggle")
def toggle():
    if not session.get("logged_in"):
        return jsonify(error="unauthorized"), 403

    data = request.get_json(silent=True) or {}
    device = data.get("device", "plug1")
    on = bool(data.get("on", False))

    DEVICE_STATE[device] = on
    publish_mqtt(device, on)

    return jsonify(
        device=device,
        on=on,
        mqtt_topic=f"devices/{device}/cmd"
    )

if __name__ == "__main__":
    if MQTT_ENABLED and mqtt_client:
        try:
            mqtt_client.on_message = on_message
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            mqtt_client.subscribe("devices/plug1/status")
            mqtt_client.subscribe("devices/plug1/heartbeat")
            mqtt_client.loop_start()
            print(f"[MQTT] Connected to broker at {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            print(f"[MQTT] Could not connect to broker at {MQTT_BROKER}:{MQTT_PORT} -> {e}")

    app.run(host="0.0.0.0", port=5000)
