import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import builtins
import types
import importlib

import psutil
import pytest

from cc_diagnostics.utils.system_metrics import SystemMetrics


class DummySnet(SimpleNamespace):
    bytes_sent: int = 1000
    bytes_recv: int = 2000


def test_collect_basic(monkeypatch):
    """SystemMetrics.collect should return all top-level keys and never raise."""

    # Stub psutil functions to return deterministic output
    monkeypatch.setattr(psutil, "cpu_count", lambda logical=True: 8 if logical else 4)
    monkeypatch.setattr(psutil, "cpu_percent", lambda interval: 12.5)

    class DummyFreq(SimpleNamespace):
        current = 3500
    monkeypatch.setattr(psutil, "cpu_freq", lambda: DummyFreq())

    class DummyVM(SimpleNamespace):
        total = 16 * 1e9
        percent = 42.0
        available = 9 * 1e9
    monkeypatch.setattr(psutil, "virtual_memory", lambda: DummyVM())

    class DummyDU(SimpleNamespace):
        total = 512 * 1e9
        percent = 50.0
        free = 256 * 1e9
    monkeypatch.setattr(psutil, "disk_usage", lambda _: DummyDU())

    monkeypatch.setattr(psutil, "net_io_counters", lambda: DummySnet())

    # No temperatures available
    monkeypatch.setattr(psutil, "sensors_temperatures", lambda: {})

    metrics = SystemMetrics()
    data = metrics.collect()

    # Validate presence of expected keys
    assert set(data.keys()) == {"timestamp", "cpu", "gpu", "ram", "disk", "network", "temps"}
    assert data["cpu"]["usage_percent"] == 12.5
    assert data["ram"]["total_gb"] == 16
    assert data["disk"]["used_percent"] == 50.0
    assert data["network"]["bytes_sent"] == 1000
    # Temperature unavailable should be string
    assert data["temps"]["cpu_c"] == "Unavailable"