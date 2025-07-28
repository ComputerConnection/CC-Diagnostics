import os
import sys
from psutil._common import sdiskusage, sdiskpart

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_diagnostics.utils import storage_health


def test_check_disk_health(monkeypatch):
    usage = sdiskusage(total=2_000_000_000, used=500_000_000, free=1_500_000_000, percent=25.0)
    monkeypatch.setattr(storage_health.psutil, "disk_usage", lambda path: usage)

    parts = [
        sdiskpart(device="/dev/sda1", mountpoint="/", fstype="ext4", opts=""),
        sdiskpart(device="/dev/sda1", mountpoint="/home", fstype="ext4", opts=""),
    ]
    monkeypatch.setattr(storage_health.psutil, "disk_partitions", lambda all=False: parts)
    monkeypatch.setattr(storage_health, "_collect_smart_status", lambda dev: "PASSED")

    info = storage_health.check_disk_health()
    assert info["total_gb"] == 2.0
    assert info["free_gb"] == 1.5
    assert info["used_percent"] == 25.0
    assert info["smart"] == {"/dev/sda1": "PASSED"}
