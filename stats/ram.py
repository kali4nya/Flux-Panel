import psutil

def get_ram_stats():
    memory = psutil.virtual_memory()

    return {
        "total_mb": round(memory.total / 1024 / 1024, 2),
        "used_mb": round(memory.used / 1024 / 1024, 2),
        "usage_percent": memory.percent
    }