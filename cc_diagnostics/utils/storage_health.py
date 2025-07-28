"""Helpers for querying drive health using psutil and ``smartctl``."""

from __future__ import annotations

import re
import subprocess

import os
import psutil


_PASSED_PAT = re.compile(r"SMART.*(PASSED|OK)", re.IGNORECASE)
_FAILED_PAT = re.compile(r"(FAILED|BAD)", re.IGNORECASE)


def _parse_smart_health(output: str) -> str:
    """Return a simplified SMART health status string."""

    if _PASSED_PAT.search(output):
        return "PASSED"
    if _FAILED_PAT.search(output):
        return "FAILED"
    return "Unknown"


def _collect_smart_status(device: str) -> str:
    """Return SMART health status for ``device`` using ``smartctl``."""

    try:
        result = subprocess.run(
            ["smartctl", "-H", device],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except FileNotFoundError:  # smartctl not installed
        return "Unavailable"

    return _parse_smart_health(result.stdout)


def check_disk_health() -> dict[str, object]:
    """Return overall disk usage and SMART health for detected drives."""

    root_path = os.path.abspath(os.sep)
    usage = psutil.disk_usage(root_path)

    health: dict[str, str] = {}
    seen: set[str] = set()

    for part in psutil.disk_partitions(all=False):
        dev = part.device
        if dev and dev not in seen:
            seen.add(dev)
            health[dev] = _collect_smart_status(dev)

    return {
        "total_gb": round(usage.total / 1e9, 2),
        "used_percent": usage.percent,
        "free_gb": round(usage.free / 1e9, 2),
        "smart": health,
    }
