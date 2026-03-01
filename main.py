from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import time

from stats.cpu import get_cpu_stats
from stats.ram import get_ram_stats
from stats.gpu import get_gpu_stats
from stats.storage import get_storage_stats

import config

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
    return render_template(
        "index.html",
        min_interval_ms=config.MIN_INTERVAL_MS,
        max_interval_ms=config.MAX_INTERVAL_MS,
        interval_step_ms=config.INTERVAL_STEP_MS,
        default_interval=config.DEFAULT_INTERVAL_MS,
        storage_alert=config.STORAGE_ALERT,
        storage_alert_threshold_percent=config.STORAGE_ALERT_THRESHOLD_PERCENT,
        storage_alert_color=config.STORAGE_ALERT_COLOR,
        max_graph_points=config.MAX_GRAPH_POINTS,
        dynamic_drive_capacity_colors=config.DYNAMIC_DRIVE_CAPACITY_COLORS,
        dynamic_drive_capacity_color_low=config.DYNAMIC_DRIVE_CAPACITY_COLOR_LOW,
        dynamic_drive_capacity_color_medium=config.DYNAMIC_DRIVE_CAPACITY_COLOR_MEDIUM,
        dynamic_drive_capacity_color_high=config.DYNAMIC_DRIVE_CAPACITY_COLOR_HIGH
    )

@app.route("/storage")
def storage_page():
    # Added missing variables to match index.html expectations
    return render_template(
        "storage.html",
        default_interval=config.DEFAULT_INTERVAL_MS,
        min_interval_ms=config.MIN_INTERVAL_MS,
        max_interval_ms=config.MAX_INTERVAL_MS,
        interval_step_ms=config.INTERVAL_STEP_MS,
        max_graph_points=config.MAX_GRAPH_POINTS, # Needed if storage has graphs
        storage_alert=config.STORAGE_ALERT,
        storage_alert_threshold_percent=config.STORAGE_ALERT_THRESHOLD_PERCENT,
        storage_alert_color=config.STORAGE_ALERT_COLOR,
        dynamic_drive_capacity_colors=config.DYNAMIC_DRIVE_CAPACITY_COLORS,
        dynamic_drive_capacity_color_low=config.DYNAMIC_DRIVE_CAPACITY_COLOR_LOW,
        dynamic_drive_capacity_color_medium=config.DYNAMIC_DRIVE_CAPACITY_COLOR_MEDIUM,
        dynamic_drive_capacity_color_high=config.DYNAMIC_DRIVE_CAPACITY_COLOR_HIGH,
        fs_theme=config.FS_THEME
    )

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
    # Initialize client with default interval
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
        try:
            interval = int(data.get("interval", config.DEFAULT_INTERVAL_MS))
            # Safety clamp based on config.py
            interval = max(config.MIN_INTERVAL_MS, min(interval, config.MAX_INTERVAL_MS))
            clients[sid]["interval"] = interval
            print(f"Interval for {sid} set to {interval}ms")
            emit("config_updated", {"interval": interval})
        except (ValueError, TypeError):
            pass

def stream_stats(sid):
    # This loop runs in the background. It checks the dictionary 
    # every cycle to see if the interval has changed.
    while sid in clients:
        # Fetch data
        data = {
            "cpu": get_cpu_stats(),
            "ram": get_ram_stats(),
            "gpu": get_gpu_stats(),
            "storage": get_storage_stats(),
            "timestamp": int(time.time())
        }
        # Send only to the specific client's room
        socketio.emit("stats_update", data, room=sid)
        
        # Sleep for the CURRENT interval value
        current_interval = clients[sid]["interval"] / 1000.0
        socketio.sleep(current_interval)

if __name__ == "__main__":
    socketio.run(
        app, 
        host=config.HOST, 
        port=config.PORT, 
        debug=config.DEBUG, 
        allow_unsafe_werkzeug=True
    )