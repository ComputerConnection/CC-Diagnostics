import os
import sys
import time
import psutil
import socket
import getpass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cc_diagnostics.utils.system_info import get_system_info

def test_uptime_hours(monkeypatch):
    fake_boot = 1000
    fake_time = 1000 + 7200  # 2 hours later
    monkeypatch.setattr(psutil, "boot_time", lambda: fake_boot)
    monkeypatch.setattr(time, "time", lambda: fake_time)
    info = get_system_info()
    assert info["Uptime_Hours"] == 2.0


def test_hostname_and_user(monkeypatch):
    monkeypatch.setattr(socket, "gethostname", lambda: "testhost")
    monkeypatch.setattr(getpass, "getuser", lambda: "testuser")
    info = get_system_info()
    assert info["Hostname"] == "testhost"
    assert info["User"] == "testuser"

