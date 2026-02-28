from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import time

from stats.cpu import get_cpu_stats
from stats.ram import get_ram_stats
from stats.gpu import get_gpu_stats
from stats.storage import get_storage_stats

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ----------------------------
# CLIENT CONFIG STORAGE
# ----------------------------

# { session_id: { "interval": 1000 } }
clients = {}


# ----------------------------
# FRONTEND
# ----------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ----------------------------
# OPTIONAL REST ENDPOINTS
# (Still available if needed)
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

    # Default config
    clients[sid] = {
        "interval": 1000
    }

    socketio.start_background_task(stream_stats, sid)


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    print(f"Client disconnected: {sid}")

    if sid in clients:
        del clients[sid]


@socketio.on("set_config")
def handle_set_config(data):
    """
    Expected payload:
    { "interval": 500 }
    """

    sid = request.sid

    if sid in clients:
        interval = int(data.get("interval", 1000))

        # Safety clamp
        interval = max(100, min(interval, 5000))

        clients[sid]["interval"] = interval

        print(f"Updated interval for {sid}: {interval}ms")

        emit("config_updated", {"interval": interval})


def stream_stats(sid):
    """
    Individual stream loop per client
    """
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
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)