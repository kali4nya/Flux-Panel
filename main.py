from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import time

from stats.cpu import get_cpu_stats
from stats.ram import get_ram_stats
from stats.gpu import get_gpu_stats
from stats.storage import get_storage_stats

import config  # <-- import the config file

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=config.CORS_ALLOWED_ORIGINS)

# ----------------------------
# CLIENT CONFIG STORAGE
# ----------------------------
clients = {}  # { session_id: { "interval": 1000 } }

# ----------------------------
# FRONTEND
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ----------------------------
# OPTIONAL REST ENDPOINTS
# ----------------------------
@app.route("/api/stats", methods=["GET"])
def stats():
    return jsonify({
        "cpu": get_cpu_stats(),
        "ram": get_ram_stats(),
        "gpu": get_gpu_stats(),
        "storage": get_storage_stats(),
        "timestamp": int(time.time())
    })

# ----------------------------
# SOCKET EVENTS
# ----------------------------
@socketio.on("connect")
def handle_connect():
    sid = request.sid
    print(f"Client connected: {sid}")

    clients[sid] = {"interval": config.DEFAULT_INTERVAL_MS}
    socketio.start_background_task(stream_stats, sid)

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    print(f"Client disconnected: {sid}")
    clients.pop(sid, None)

@socketio.on("set_config")
def handle_set_config(data):
    sid = request.sid
    if sid in clients:
        interval = int(data.get("interval", config.DEFAULT_INTERVAL_MS))
        # Safety clamp
        interval = max(config.MIN_INTERVAL_MS, min(interval, config.MAX_INTERVAL_MS))
        clients[sid]["interval"] = interval
        print(f"Updated interval for {sid}: {interval}ms")
        emit("config_updated", {"interval": interval})

def stream_stats(sid):
    while sid in clients:
        interval = clients[sid]["interval"]
        data = {
            "cpu": get_cpu_stats(),
            "ram": get_ram_stats(),
            "gpu": get_gpu_stats(),
            "storage": get_storage_stats(),
            "timestamp": int(time.time())
        }
        socketio.emit("stats_update", data, room=sid)
        socketio.sleep(interval / 1000.0)

if __name__ == "__main__":
    socketio.run(
        app, 
        host=config.HOST, 
        port=config.PORT, 
        debug=config.DEBUG, 
        allow_unsafe_werkzeug=True
    )