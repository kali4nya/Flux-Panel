import psutil
import platform
import time
import os

def get_windows_disk_speeds(interval=1):
    """
    Measure read/write speeds for all drives on Windows
    """
    io_start = psutil.disk_io_counters(perdisk=True)
    time.sleep(interval)
    io_end = psutil.disk_io_counters(perdisk=True)

    speeds = {}
    for disk in io_start:
        read_bytes = io_end[disk].read_bytes - io_start[disk].read_bytes
        write_bytes = io_end[disk].write_bytes - io_start[disk].write_bytes

        speeds[disk] = {
            "read_MB_s": read_bytes / (1024 * 1024) / interval,
            "write_MB_s": write_bytes / (1024 * 1024) / interval
        }
    return speeds

def get_linux_partition_speeds(interval=1):
    """
    Measure read/write speeds for all mounted partitions on Linux
    """
    partitions = [p for p in psutil.disk_partitions(all=False) if os.path.exists(p.mountpoint)]
    mount_to_device = {p.mountpoint: os.path.basename(p.device) for p in partitions}

    io_start = psutil.disk_io_counters(perdisk=True)
    time.sleep(interval)
    io_end = psutil.disk_io_counters(perdisk=True)

    speeds = {}
    for mount, device in mount_to_device.items():
        if device not in io_start:
            # fallback: strip trailing digits/letters for devices like mmcblk0p1 or sda1
            base_device = ''.join(filter(str.isalpha, device))
            if base_device in io_start:
                device = base_device
            else:
                continue  # skip if no match

        read_bytes = io_end[device].read_bytes - io_start[device].read_bytes
        write_bytes = io_end[device].write_bytes - io_start[device].write_bytes

        speeds[mount] = {
            "read_MB_s": read_bytes / (1024 * 1024) / interval,
            "write_MB_s": write_bytes / (1024 * 1024) / interval
        }

    return speeds

if __name__ == "__main__":
    os_type = platform.system()
    if os_type == "Windows":
        speeds = get_windows_disk_speeds(interval=1)
    elif os_type == "Linux":
        speeds = get_linux_partition_speeds(interval=1)
    else:
        raise NotImplementedError(f"Unsupported OS: {os_type}")

    for key, speed in speeds.items():
        print(f"{key}: Read {speed['read_MB_s']:.2f} MB/s, Write {speed['write_MB_s']:.2f} MB/s")