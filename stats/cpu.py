import psutil
import platform

# Initialize psutil to prime CPU percent
psutil.cpu_percent()

def get_cpu_temperature_linux():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None

        cpu_temp = None
        ignored_sensors = {"nvme", "bat", "pch", "acpitz", "thinkpad-isa-0000"}

        for sensor_name, entries in temps.items():
            if sensor_name.lower() in ignored_sensors:
                continue
            for entry in entries:
                # Consider labels that look like CPU cores or packages
                if entry.label and any(x in entry.label.lower() for x in ["core", "tctl", "package", "cpu"]):
                    if cpu_temp is None or entry.current > cpu_temp:
                        cpu_temp = entry.current
                # Fallback if label is empty but sensor name looks CPU-ish
                elif entry.current and "cpu" in sensor_name.lower():
                    if cpu_temp is None or entry.current > cpu_temp:
                        cpu_temp = entry.current

        if cpu_temp is not None:
            return round(cpu_temp, 1)

    except Exception:
        pass
    return None

def get_cpu_temperature_windows():
    # I tried to do it but i gave up, womp womp
    return None

def get_cpu_stats():
    usage = psutil.cpu_percent(interval=0.15)
    cores = psutil.cpu_count()
    temp = None

    system = platform.system()
    if system == "Linux":
        temp = get_cpu_temperature_linux()
    elif system == "Windows":
        temp = get_cpu_temperature_windows()

    return {
        "usage_percent": usage,
        "cores": cores,
        "temperature_c": temp
    }