import psutil
import time
import os

def get_partition_speeds(interval=1):
    """
    Measure read/write speeds for all mounted partitions (like /, /boot, /mnt/md0)
    """
    # Get all mounted partitions
    partitions = [p for p in psutil.disk_partitions(all=False) if os.path.exists(p.mountpoint)]
    
    # Map mountpoint -> device name
    mount_to_device = {p.mountpoint: os.path.basename(p.device) for p in partitions}

    # Get initial IO stats
    io_start = psutil.disk_io_counters(perdisk=True)
    time.sleep(interval)
    io_end = psutil.disk_io_counters(perdisk=True)

    speeds = {}
    for mount, device in mount_to_device.items():
        if device not in io_start:
            # Sometimes devices are like mmcblk0p1 -> mmcblk0p1
            # Fall back to stripping partition number (e.g., mmcblk0p1 -> mmcblk0)
            stripped_device = ''.join(filter(str.isalpha, device))  # rough fallback
            if stripped_device in io_start:
                device = stripped_device
            else:
                # skip if no matching device
                continue

        read_bytes = io_end[device].read_bytes - io_start[device].read_bytes
        write_bytes = io_end[device].write_bytes - io_start[device].write_bytes

        speeds[mount] = {
            "read_MB_s": read_bytes / (1024 * 1024) / interval,
            "write_MB_s": write_bytes / (1024 * 1024) / interval
        }

    return speeds

if __name__ == "__main__":
    speeds = get_partition_speeds(interval=1)
    for mount, speed in speeds.items():
        print(f"{mount}: Read {speed['read_MB_s']:.2f} MB/s, Write {speed['write_MB_s']:.2f} MB/s")