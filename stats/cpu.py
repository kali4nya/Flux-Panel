import psutil

# Initialize once
psutil.cpu_percent()  # Ignore first call

def get_cpu_stats():
    return {
        "usage_percent": psutil.cpu_percent(interval=0.15),  # small blocking interval
        "cores": psutil.cpu_count()
    }