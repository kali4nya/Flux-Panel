import psutil
import time

def get_disk_speeds(interval=1):
    """
    Measure read/write speeds for all drives over the given interval (in seconds)
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

if __name__ == "__main__":
    speeds = get_disk_speeds(interval=1)
    for disk, speed in speeds.items():
        print(f"{disk}: Read {speed['read_MB_s']:.2f} MB/s, Write {speed['write_MB_s']:.2f} MB/s")