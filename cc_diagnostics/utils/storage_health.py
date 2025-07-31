"""Check disk health using ``psutil`` and ``smartctl`` if available."""

import subprocess
import platform
from typing import Dict, Any, List, Optional
from functools import lru_cache
import time
import os

# Lazy import psutil to reduce startup time
_psutil = None

def _get_psutil():
    """Lazy import psutil to reduce startup time."""
    global _psutil
    if _psutil is None:
        import psutil
        _psutil = psutil
    return _psutil

# Cache for smart data that doesn't change frequently
_smart_cache: Dict[str, tuple[Dict[str, Any], float]] = {}
SMART_CACHE_DURATION = 300  # 5 minutes


@lru_cache(maxsize=8)
def _get_smartctl_path() -> Optional[str]:
    """Find smartctl executable with caching."""
    if platform.system() != "Windows":
        return None
    
    # Common paths for smartctl on Windows
    paths = [
        "smartctl",  # If in PATH
        r"C:\Program Files\smartmontools\bin\smartctl.exe",
        r"C:\Program Files (x86)\smartmontools\bin\smartctl.exe",
        r"C:\smartmontools\bin\smartctl.exe",
    ]
    
    for path in paths:
        try:
            subprocess.run([path, "--version"], 
                         capture_output=True, timeout=5, check=True)
            return path
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            continue
    return None


def _get_smart_data(device: str) -> Dict[str, Any]:
    """Get SMART data for a specific device with caching."""
    current_time = time.time()
    
    # Check cache first
    if device in _smart_cache:
        cached_data, cache_time = _smart_cache[device]
        if current_time - cache_time < SMART_CACHE_DURATION:
            return cached_data.copy()
    
    result = {"available": False, "healthy": "Unknown", "details": {}}
    
    smartctl_path = _get_smartctl_path()
    if not smartctl_path:
        _smart_cache[device] = (result, current_time)
        return result
    
    try:
        # Run smartctl with optimized parameters
        cmd = [smartctl_path, "-H", "-A", device]
        proc = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=10,  # Reduced timeout
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        
        if proc.returncode in (0, 4):  # 0 = OK, 4 = some SMART errors but disk OK
            result["available"] = True
            result["healthy"] = "PASSED" if "PASSED" in proc.stdout else "Unknown"
            
            # Parse key SMART attributes efficiently
            lines = proc.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if any(attr in line for attr in ['Temperature', 'Reallocated', 'Pending', 'Uncorrectable']):
                    parts = line.split()
                    if len(parts) >= 10:
                        attr_name = parts[1]
                        raw_value = parts[9] if parts[9].isdigit() else parts[9].split()[0]
                        result["details"][attr_name] = raw_value
        
        # Cache the result
        _smart_cache[device] = (result.copy(), current_time)
        
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        # Cache negative result too
        _smart_cache[device] = (result, current_time)
    
    return result


@lru_cache(maxsize=1)
def _get_system_drives() -> List[str]:
    """Get list of system drives with caching."""
    psutil = _get_psutil()
    drives = []
    
    if platform.system() == "Windows":
        for part in psutil.disk_partitions(all=False):
            if part.fstype and 'cdrom' not in part.opts:
                # Convert C:\ to \\.\PhysicalDrive0 format for SMART
                drive_letter = part.device[0]
                drives.append(f"\\\\.\\{drive_letter}:")
    else:
        # For Linux/Mac, use device names
        for part in psutil.disk_partitions(all=False):
            if part.device.startswith('/dev/'):
                drives.append(part.device)
    
    return drives


def check_disk_health() -> Dict[str, Any]:
    """Return disk usage and SMART health for system drives."""
    psutil = _get_psutil()
    
    # Get disk usage efficiently
    if platform.system() == "Windows":
        root_path = "C:\\"
    else:
        root_path = "/"
    
    try:
        usage = psutil.disk_usage(root_path)
        usage_info = {
            "total_gb": round(usage.total / 1e9, 2),
            "used_gb": round(usage.used / 1e9, 2),
            "free_gb": round(usage.free / 1e9, 2),
            "used_percent": round(100 * usage.used / usage.total, 1),
        }
    except OSError:
        usage_info = {
            "total_gb": 0,
            "used_gb": 0,
            "free_gb": 0,
            "used_percent": 0,
        }
    
    # Get drive information with caching
    drives_info = {}
    try:
        for partition in psutil.disk_partitions(all=False):
            if partition.fstype and 'cdrom' not in partition.opts.lower():
                drive_letter = partition.device
                try:
                    part_usage = psutil.disk_usage(partition.mountpoint)
                    drives_info[drive_letter] = {
                        "total_gb": round(part_usage.total / 1e9, 2),
                        "free_gb": round(part_usage.free / 1e9, 2),
                        "used_percent": round(100 * part_usage.used / part_usage.total, 1),
                        "filesystem": partition.fstype,
                    }
                except (OSError, PermissionError):
                    continue
    except OSError:
        pass
    
    # Get SMART data for main drives (limit to avoid long delays)
    smart_results = {}
    system_drives = _get_system_drives()[:3]  # Limit to first 3 drives
    
    for drive in system_drives:
        smart_data = _get_smart_data(drive)
        if smart_data["available"]:
            smart_results[drive] = smart_data
    
    return {
        "usage": usage_info,
        "drives": drives_info,
        "smart": smart_results,
        "summary": _generate_health_summary(usage_info, smart_results),
    }


def _generate_health_summary(usage_info: Dict[str, Any], smart_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a health summary from usage and SMART data."""
    issues = []
    health_score = 100
    
    # Check disk space
    if usage_info["used_percent"] > 90:
        issues.append("Disk space critically low")
        health_score -= 30
    elif usage_info["used_percent"] > 80:
        issues.append("Disk space running low")
        health_score -= 15
    
    # Check SMART status
    failed_drives = 0
    for drive, smart_data in smart_results.items():
        if smart_data["healthy"] != "PASSED":
            failed_drives += 1
            issues.append(f"SMART health check failed for {drive}")
            health_score -= 25
    
    # Determine overall status
    if health_score >= 90:
        status = "Excellent"
    elif health_score >= 70:
        status = "Good"
    elif health_score >= 50:
        status = "Fair"
    else:
        status = "Poor"
    
    return {
        "status": status,
        "health_score": max(0, health_score),
        "issues": issues,
        "recommendations": _generate_recommendations(usage_info, smart_results),
    }


def _generate_recommendations(usage_info: Dict[str, Any], smart_results: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations based on health data."""
    recommendations = []
    
    if usage_info["used_percent"] > 85:
        recommendations.append("Run disk cleanup to free up space")
        recommendations.append("Consider moving large files to external storage")
        recommendations.append("Uninstall unused programs")
    
    if usage_info["used_percent"] > 95:
        recommendations.append("Urgent: Free up disk space immediately")
        recommendations.append("Consider upgrading to a larger drive")
    
    failed_smart = any(data["healthy"] != "PASSED" for data in smart_results.values())
    if failed_smart:
        recommendations.append("Back up important data immediately")
        recommendations.append("Consider replacing the failing drive")
        recommendations.append("Run extended SMART tests")
    
    if not smart_results:
        recommendations.append("Install smartmontools for drive health monitoring")
    
    return recommendations
