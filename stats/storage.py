import psutil
import platform
import time
import os

# --------------------------------------------------
# GLOBAL STATE
# --------------------------------------------------
_previous_io = None
_previous_time = None
_win_counters = {}

def get_storage_stats():
    global _previous_io, _previous_time

    os_type = platform.system()
    current_io = psutil.disk_io_counters(perdisk=True)
    current_time = time.time()

    if _previous_io is None:
        _previous_io = current_io
        _previous_time = current_time

    delta_time = current_time - _previous_time
    if delta_time <= 0:
        delta_time = 1

    if os_type == "Windows":
        # Pass the global state data to the windows function
        stats = _get_windows_storage_stats(current_io, delta_time)
    elif os_type == "Linux":
        stats = _get_linux_storage_stats(current_io, delta_time)
    else:
        raise NotImplementedError(f"Unsupported OS: {os_type}")

    _previous_io = current_io
    _previous_time = current_time
    return stats

# --------------------------------------------------
# WINDOWS implementation
# --------------------------------------------------

def _get_windows_storage_stats(current_io, delta_time):
    
    #needed only for windows storage stats
    import win32pdh # From pywin32
    
    global _win_counters
    stats = []
    mb_factor = 1024 * 1024
    
    partitions = psutil.disk_partitions(all=False)

    for part in partitions:
        drive_letter = part.mountpoint.strip("\\") # "C:"
        
        # We initialize counters for this specific drive letter if they don't exist
        if drive_letter not in _win_counters:
            try:
                query = win32pdh.OpenQuery()
                # These paths target the specific logical disk counters
                r_path = win32pdh.MakeCounterPath((None, "LogicalDisk", drive_letter, None, 0, "Disk Read Bytes/sec"))
                w_path = win32pdh.MakeCounterPath((None, "LogicalDisk", drive_letter, None, 0, "Disk Write Bytes/sec"))
                
                _win_counters[drive_letter] = {
                    "query": query,
                    "read": win32pdh.AddCounter(query, r_path),
                    "write": win32pdh.AddCounter(query, w_path)
                }
                # Initial collect to prime the counter
                win32pdh.CollectQueryData(query)
            except:
                continue

        # Get current speed values directly from Windows Performance Counters
        try:
            drive_obj = _win_counters[drive_letter]
            win32pdh.CollectQueryData(drive_obj["query"])
            
            # The PDH returns the current rate (Bytes/sec) directly
            _, r_speed = win32pdh.GetFormattedCounterValue(drive_obj["read"], win32pdh.PDH_FMT_DOUBLE)
            _, w_speed = win32pdh.GetFormattedCounterValue(drive_obj["write"], win32pdh.PDH_FMT_DOUBLE)
        except:
            r_speed, w_speed = 0.0, 0.0

        try:
            usage = psutil.disk_usage(part.mountpoint)
            
            stats.append({
                "device": part.device,
                "fstype": part.fstype,
                "mount": part.mountpoint,
                # We use the raw current speeds provided by Windows
                "read_bytes": 0, # Cumulative bytes are harder via PDH, so we focus on speed
                "read_speed_Bps": r_speed,
                "write_bytes": 0,
                "write_speed_Bps": w_speed,
                "total_mb": usage.total / mb_factor,
                "used_mb": usage.used / mb_factor,
                "usage_percent": usage.percent
            })
        except:
            continue

    return stats

# --------------------------------------------------
# LINUX implementation (as you provided)
# --------------------------------------------------

def _get_linux_storage_stats(current_io, delta_time):
    stats = []
    partitions = [
        p for p in psutil.disk_partitions(all=False)
        if os.path.exists(p.mountpoint)
    ]
    
    for p in partitions:
        device_path = p.device
        mount = p.mountpoint
        device = os.path.basename(device_path)
        io_device = device

        if io_device not in current_io:
            io_device = ''.join(filter(str.isalpha, device))
            if io_device not in current_io:
                continue

        io_data = current_io[io_device]
        read_bytes = io_data.read_bytes
        write_bytes = io_data.write_bytes

        prev = _previous_io.get(io_device)
        read_speed = (read_bytes - prev.read_bytes) / delta_time if prev else 0
        write_speed = (write_bytes - prev.write_bytes) / delta_time if prev else 0

        try:
            usage = psutil.disk_usage(mount)
            stats.append({
                "device": device_path,
                "fstype": p.fstype,
                "mount": mount,
                "read_bytes": read_bytes,
                "read_speed_Bps": read_speed,
                "write_bytes": write_bytes,
                "write_speed_Bps": write_speed,
                "total_mb": usage.total / (1024 * 1024),
                "used_mb": usage.used / (1024 * 1024),
                "usage_percent": usage.percent
            })
        except OSError:
            continue

    return stats

if __name__ == "__main__":
    # Test loop to see the speeds change
    import json
    print("Initializing baseline (first run will show 0 speed)...")
    get_storage_stats() 
    
    while True:
        time.sleep(1)
        data = get_storage_stats()
        print(json.dumps({"storage": data}, indent=4))