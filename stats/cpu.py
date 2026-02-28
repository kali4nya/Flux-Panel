import psutil
import platform

# Initialize psutil to prime CPU percent
psutil.cpu_percent()

def get_cpu_temperature_linux():
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for key in ["coretemp", "cpu_thermal"]:
                if key in temps:
                    core_temps = temps[key]
                    if core_temps:
                        avg = sum([t.current for t in core_temps]) / len(core_temps)
                        return round(avg, 1)
            for sensor_list in temps.values():
                if sensor_list:
                    avg = sum([t.current for t in sensor_list]) / len(sensor_list)
                    return round(avg, 1)
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