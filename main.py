from flask import Flask, jsonify, render_template
import time

from stats.cpu import get_cpu_stats
from stats.ram import get_ram_stats
from stats.gpu import get_gpu_stats
from stats.storage import get_storage_stats

app = Flask(__name__)

# Serve frontend
@app.route("/")
def index():
    return render_template("index.html")


# API endpoints
@app.route("/api/cpu", methods=["GET"])
def cpu():
    return jsonify(get_cpu_stats())

@app.route("/api/ram", methods=["GET"])
def ram():
    return jsonify(get_ram_stats())

@app.route("/api/gpu", methods=["GET"])
def gpu():
    return jsonify(get_gpu_stats())

@app.route("/api/storage", methods=["GET"])
def storage():
    return jsonify(get_storage_stats())

@app.route("/api/stats", methods=["GET"])
def stats():
    return jsonify({
        "cpu": get_cpu_stats(),
        "ram": get_ram_stats(),
        "gpu": get_gpu_stats(),
        "storage": get_storage_stats(),
        "timestamp": int(time.time())
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)