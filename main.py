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
        # index config variables
        "index.html",
        default_interval=config.DEFAULT_INTERVAL_MS,
        min_interval_ms=config.MIN_INTERVAL_MS,
        max_interval_ms=config.MAX_INTERVAL_MS,
        interval_step_ms=config.INTERVAL_STEP_MS,
        
        index_max_graph_points=config.INDEX_MAX_GRAPH_POINTS,
        index_cpu_graph_color=config.INDEX_CPU_GRAPH_COLOR,
        index_ram_graph_color=config.INDEX_RAM_GRAPH_COLOR,
        
        index_dynamic_drive_capacity_colors=config.INDEX_DYNAMIC_DRIVE_CAPACITY_COLORS,
        index_dynamic_drive_capacity_color_low=config.INDEX_DYNAMIC_DRIVE_CAPACITY_COLOR_LOW,
        index_dynamic_drive_capacity_color_medium=config.INDEX_DYNAMIC_DRIVE_CAPACITY_COLOR_MEDIUM,
        index_dynamic_drive_capacity_color_high=config.INDEX_DYNAMIC_DRIVE_CAPACITY_COLOR_HIGH,
        
        index_storage_alert=config.INDEX_STORAGE_ALERT,
        index_storage_alert_threshold_percent=config.INDEX_STORAGE_ALERT_THRESHOLD_PERCENT,
        index_storage_alert_color=config.INDEX_STORAGE_ALERT_COLOR
    )

@app.route("/storage")
def storage_page():
    # Sorage config variables
    return render_template(
        "storage.html",
        default_interval=config.DEFAULT_INTERVAL_MS,
        min_interval_ms=config.MIN_INTERVAL_MS,
        max_interval_ms=config.MAX_INTERVAL_MS,
        interval_step_ms=config.INTERVAL_STEP_MS,
        
        storage_max_graph_points=config.STORAGE_MAX_GRAPH_POINTS,
        
        storage_bar_color=config.STORAGE_BAR_COLOR,
        
        storage_dynamic_drive_capacity_colors=config.STORAGE_DYNAMIC_DRIVE_CAPACITY_COLORS,
        storage_dynamic_drive_capacity_color_low=config.STORAGE_DYNAMIC_DRIVE_CAPACITY_COLOR_LOW,
        storage_dynamic_drive_capacity_color_medium=config.STORAGE_DYNAMIC_DRIVE_CAPACITY_COLOR_MEDIUM,
        storage_dynamic_drive_capacity_color_high=config.STORAGE_DYNAMIC_DRIVE_CAPACITY_COLOR_HIGH,
        
        storage_storage_alert=config.STORAGE_STORAGE_ALERT,
        storage_storage_alert_threshold_percent=config.STORAGE_STORAGE_ALERT_THRESHOLD_PERCENT,
        storage_storage_alert_color=config.STORAGE_STORAGE_ALERT_COLOR,
        
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