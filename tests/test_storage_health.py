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


def test_check_disk_health_windows_root(monkeypatch):
    usage = sdiskusage(total=1_000_000_000, used=400_000_000, free=600_000_000, percent=40.0)

    def fake_abspath(path):
        assert path == os.sep
        return "C:\\"

    called = {}

    def fake_disk_usage(path):
        called["path"] = path
        return usage

    monkeypatch.setattr(storage_health.os.path, "abspath", fake_abspath)
    monkeypatch.setattr(storage_health.psutil, "disk_usage", fake_disk_usage)
    monkeypatch.setattr(storage_health.psutil, "disk_partitions", lambda all=False: [])
    monkeypatch.setattr(storage_health, "_collect_smart_status", lambda dev: "PASSED")

    info = storage_health.check_disk_health()
    assert called["path"] == "C:\\"
    assert info["total_gb"] == 1.0
    assert info["free_gb"] == 0.6
    assert info["used_percent"] == 40.0
    assert info["smart"] == {}
