import psutil
import platform
import time
import os

def get_storage_stats(interval=1):
    """
    Returns a list of dicts with storage info:
    - device: device path (e.g., /dev/sda1 or C:\)
    - fstype: filesystem type
    - mount: mount point
    - read_bytes / write_bytes: cumulative bytes since boot
    - read_speed_Bps / write_speed_Bps: measured over interval
    - total_mb / used_mb / usage_percent
    """
    os_type = platform.system()
    
    if os_type == "Windows":
        return _get_windows_storage_stats(interval)
    elif os_type == "Linux":
        return _get_linux_storage_stats(interval)
    else:
        raise NotImplementedError(f"Unsupported OS: {os_type}")


def _get_windows_storage_stats(interval=1):
    io_start = psutil.disk_io_counters(perdisk=True)
    time.sleep(interval)
    io_end = psutil.disk_io_counters(perdisk=True)

    stats = []
    partitions = psutil.disk_partitions(all=False)
    for p in partitions:
        device_name = p.device  # e.g., 'C:\\'
        mount = p.mountpoint    # e.g., 'C:\\'
        fstype = p.fstype

        base_device = device_name.rstrip('\\')  # 'C:'

        read_bytes = io_end.get(base_device, io_start[base_device]).read_bytes - io_start.get(base_device, io_start[base_device]).read_bytes if base_device in io_start else 0
        write_bytes = io_end.get(base_device, io_start[base_device]).write_bytes - io_start.get(base_device, io_start[base_device]).write_bytes if base_device in io_start else 0

        usage = psutil.disk_usage(mount)

        stats.append({
            "device": device_name,
            "fstype": fstype,
            "mount": mount,
            "read_bytes": usage.read_bytes if hasattr(usage, 'read_bytes') else 0,
            "read_speed_Bps": read_bytes / interval,
            "write_bytes": usage.write_bytes if hasattr(usage, 'write_bytes') else 0,
            "write_speed_Bps": write_bytes / interval,
            "total_mb": usage.total / (1024*1024),
            "used_mb": usage.used / (1024*1024),
            "usage_percent": usage.percent
        })
    return stats


def _get_linux_storage_stats(interval=1):
    partitions = [p for p in psutil.disk_partitions(all=False) if os.path.exists(p.mountpoint)]
    mount_to_device = {p.mountpoint: p.device for p in partitions}

    io_start = psutil.disk_io_counters(perdisk=True)
    time.sleep(interval)
    io_end = psutil.disk_io_counters(perdisk=True)

    stats = []
    for mount, device_path in mount_to_device.items():
        device = os.path.basename(device_path)
        io_device = device

        if io_device not in io_start:
            # fallback for devices like mmcblk0p1 -> mmcblk0
            io_device = ''.join(filter(str.isalpha, device))
            if io_device not in io_start:
                continue  # skip if no matching device

        read_bytes = io_end[io_device].read_bytes - io_start[io_device].read_bytes
        write_bytes = io_end[io_device].write_bytes - io_start[io_device].write_bytes

        usage = psutil.disk_usage(mount)

        stats.append({
            "device": device_path,  # raw device for internal use
            "fstype": next((p.fstype for p in partitions if p.mountpoint == mount), "unknown"),
            "mount": mount,         # **mount point used for label in frontend**
            "read_bytes": io_end[io_device].read_bytes,
            "read_speed_Bps": read_bytes / interval,
            "write_bytes": io_end[io_device].write_bytes,
            "write_speed_Bps": write_bytes / interval,
            "total_mb": usage.total / (1024*1024),
            "used_mb": usage.used / (1024*1024),
            "usage_percent": usage.percent
        })
    return stats