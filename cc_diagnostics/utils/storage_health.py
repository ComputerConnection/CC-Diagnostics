import psutil


def check_disk_health():
    usage = psutil.disk_usage('/')
    return {
        "total_gb": round(usage.total / 1e9, 2),
        "used_percent": usage.percent,
        "free_gb": round(usage.free / 1e9, 2),
    }
