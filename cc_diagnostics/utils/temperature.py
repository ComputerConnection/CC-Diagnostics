"""Helpers for retrieving system temperature information."""

from __future__ import annotations

import platform
from typing import Any

import psutil


def _read_psutil_temps() -> tuple[float | None, float | None]:
    """Try to read temperatures using :func:`psutil.sensors_temperatures`."""

    try:
        temps: dict[str, Any] = psutil.sensors_temperatures()
    except Exception:  # pragma: no cover - psutil may raise on unsupported OS
        return None, None

    cpu = None
    gpu = None

    for name, entries in temps.items():
        lname = name.lower()
        for entry in entries:
            label = (entry.label or "").lower()

            if cpu is None and (
                "cpu" in label
                or "package" in label
                or "core" in label
                or lname.startswith("cpu")
                or lname.startswith("core")
            ):
                if entry.current is not None:
                    cpu = float(entry.current)

            if gpu is None and (
                "gpu" in label
                or lname.startswith("gpu")
                or "gpu" in lname
            ):
                if entry.current is not None:
                    gpu = float(entry.current)

    return cpu, gpu


def _read_wmi_temp() -> float | None:
    """Windows WMI fallback for CPU temperature."""

    try:
        import wmi  # type: ignore

        w = wmi.WMI(namespace="root\\wmi")
        temps = [
            (sensor.CurrentTemperature / 10.0) - 273.15
            for sensor in w.MSAcpi_ThermalZoneTemperature()
        ]
        return sum(temps) / len(temps) if temps else None
    except Exception:  # pragma: no cover - best effort only
        return None


def get_temperatures() -> dict[str, float | str]:
    """Return CPU and GPU temperatures if available."""

    cpu_temp, gpu_temp = _read_psutil_temps()

    if cpu_temp is None and platform.system() == "Windows":
        cpu_temp = _read_wmi_temp()

    return {
        "CPU_Temp_C": round(cpu_temp, 1) if cpu_temp is not None else "Unavailable",
        "GPU_Temp_C": round(gpu_temp, 1) if gpu_temp is not None else "Unavailable",
    }

