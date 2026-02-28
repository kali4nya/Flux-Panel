import psutil

def get_storage_stats():
    partitions = psutil.disk_partitions()
    disks = []

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "mount": partition.mountpoint,
                "total_gb": round(usage.total / 1024 / 1024, 2),
                "used_gb": round(usage.used / 1024 / 1024, 2),
                "usage_percent": usage.percent
            })
        except PermissionError:
            # Skip partitions the user can't access
            continue

    return disks