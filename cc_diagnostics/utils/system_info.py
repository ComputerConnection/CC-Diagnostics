import platform
import time
import socket
import getpass
import psutil


def get_system_info():
    return {
        "OS": platform.platform(),
        "CPU": platform.processor(),
        "Cores": psutil.cpu_count(logical=True),
        "RAM_GB": round(psutil.virtual_memory().total / 1e9, 2),
        "Uptime_Hours": round((time.time() - psutil.boot_time()) / 3600, 2),
        "Hostname": socket.gethostname(),
        "User": getpass.getuser(),
    }
