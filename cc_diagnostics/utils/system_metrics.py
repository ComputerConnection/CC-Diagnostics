from __future__ import annotations

"""Live system metrics helpers.

This module exposes :class:`SystemMetrics` which provides a snapshot of
current utilisation statistics for CPU, GPU, RAM, disk and network as
well as temperature data. All external libraries are optional – the code
falls back to *"Unavailable"* values when a dependency cannot be loaded
or information is not present on the running platform.

The class is designed to be extremely lightweight so it can be polled
frequently (e.g. every second) from the Qt GUI without incurring
noticeable overhead.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import platform
import time
import subprocess
import json
import logging

import psutil

logger = logging.getLogger(__name__)

try:
    import wmi  # type: ignore
except Exception:  # pragma: no cover – optional dep
    wmi = None  # type: ignore

try:
    from py3nvml import py3nvml  # type: ignore
except Exception:  # pragma: no cover – optional dep
    py3nvml = None  # type: ignore


@dataclass
class SystemMetrics:
    """Collect a snapshot of various utilisation metrics.

    Usage
    -----
    >>> metrics = SystemMetrics()
    >>> current = metrics.collect()
    >>> cpu_load = current["cpu"]["usage_percent"]
    """

    # Internal state used to calculate deltas for network throughput
    _last_net: psutil._common.snetio = field(default_factory=psutil.net_io_counters, init=False, repr=False)
    _last_time: float = field(default_factory=time.time, init=False, repr=False)

    def _gpu_metrics(self) -> Dict[str, Any]:
        """Return GPU utilisation and temperature if available."""

        # Prefer NVML because it provides both load and temperature
        if py3nvml is not None:
            try:
                py3nvml.nvmlInit()
                handle = py3nvml.nvmlDeviceGetHandleByIndex(0)
                util = py3nvml.nvmlDeviceGetUtilizationRates(handle)
                temp = py3nvml.nvmlDeviceGetTemperature(handle, py3nvml.NVML_TEMPERATURE_GPU)
                name = py3nvml.nvmlDeviceGetName(handle).decode()
                py3nvml.nvmlShutdown()
                return {
                    "name": name,
                    "usage_percent": util.gpu,
                    "memory_percent": util.memory,
                    "temperature_c": temp,
                }
            except Exception as exc:  # pragma: no cover – best-effort only
                logger.debug("NVML read failed: %s", exc)

        # Fallback to WMI on Windows if NVML not available
        if wmi is not None and platform.system() == "Windows":
            try:
                c = wmi.WMI(namespace="root\\CIMV2")
                gpus = c.Win32_VideoController()
                if gpus:
                    gpu = gpus[0]
                    return {
                        "name": getattr(gpu, "Name", "Unknown"),
                        "usage_percent": "Unavailable",
                        "memory_percent": "Unavailable",
                        "temperature_c": "Unavailable",
                    }
            except Exception as exc:  # pragma: no cover
                logger.debug("WMI GPU query failed: %s", exc)

        return {
            "name": "Unavailable",
            "usage_percent": "Unavailable",
            "memory_percent": "Unavailable",
            "temperature_c": "Unavailable",
        }

    def _cpu_metrics(self) -> Dict[str, Any]:
        return {
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False) or 0,
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
        }

    def _ram_metrics(self) -> Dict[str, Any]:
        vm = psutil.virtual_memory()
        return {
            "total_gb": round(vm.total / 1e9, 2),
            "used_percent": vm.percent,
            "available_gb": round(vm.available / 1e9, 2),
        }

    def _disk_metrics(self) -> Dict[str, Any]:
        root = Path("").anchor or "\\"  # cross-platform root path
        usage = psutil.disk_usage(root)
        return {
            "total_gb": round(usage.total / 1e9, 2),
            "used_percent": usage.percent,
            "free_gb": round(usage.free / 1e9, 2),
        }

    def _network_metrics(self) -> Dict[str, Any]:
        now = time.time()
        stats = psutil.net_io_counters()
        elapsed = max(now - self._last_time, 1e-3)
        sent_rate = (stats.bytes_sent - self._last_net.bytes_sent) / elapsed
        recv_rate = (stats.bytes_recv - self._last_net.bytes_recv) / elapsed
        self._last_net = stats
        self._last_time = now
        return {
            "bytes_sent": stats.bytes_sent,
            "bytes_recv": stats.bytes_recv,
            "sent_rate_bps": int(sent_rate),
            "recv_rate_bps": int(recv_rate),
        }

    def _temperatures(self) -> Dict[str, Any]:
        try:
            temps = psutil.sensors_temperatures()
        except Exception:  # pragma: no cover – unsupported platform
            temps = {}

        cpu = None
        for entries in temps.values():
            for entry in entries:
                label = (entry.label or "").lower()
                if cpu is None and ("package" in label or "cpu" in label):
                    cpu = entry.current
        return {
            "cpu_c": round(cpu, 1) if cpu is not None else "Unavailable",
        }

    def collect(self) -> Dict[str, Any]:
        """Return a nested mapping with metrics for all components."""
        return {
            "timestamp": time.time(),
            "cpu": self._cpu_metrics(),
            "gpu": self._gpu_metrics(),
            "ram": self._ram_metrics(),
            "disk": self._disk_metrics(),
            "network": self._network_metrics(),
            "temps": self._temperatures(),
        }