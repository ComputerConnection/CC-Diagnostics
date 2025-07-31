"""Parse and interpret diagnostic report data into actionable summaries."""

from typing import Dict, Any, List, Optional
from functools import lru_cache

# Pre-compiled constants for better performance
TEMP_THRESHOLDS = {
    "cpu_warning": 80,
    "cpu_critical": 90,
    "gpu_warning": 85,
    "gpu_critical": 95,
}

DISK_THRESHOLDS = {
    "warning": 80,
    "critical": 90,
}

RAM_THRESHOLDS = {
    "warning": 85,
    "critical": 95,
}

# Reusable status constants
STATUS_GOOD = "Good"
STATUS_WARNING = "Warning"
STATUS_CRITICAL = "Critical"

@lru_cache(maxsize=32)
def _get_status_for_percentage(value: float, warning_threshold: float, critical_threshold: float) -> str:
    """Get status string for a percentage value with caching."""
    if value >= critical_threshold:
        return STATUS_CRITICAL
    elif value >= warning_threshold:
        return STATUS_WARNING
    else:
        return STATUS_GOOD

def _analyze_temperatures(temps: Dict[str, Any]) -> tuple[str, List[str]]:
    """Analyze temperature data and return status and warnings."""
    warnings = []
    worst_status = STATUS_GOOD
    
    cpu_temp = temps.get("cpu_c")
    if isinstance(cpu_temp, (int, float)):
        if cpu_temp >= TEMP_THRESHOLDS["cpu_critical"]:
            warnings.append(f"CPU temperature critical: {cpu_temp}°C")
            worst_status = STATUS_CRITICAL
        elif cpu_temp >= TEMP_THRESHOLDS["cpu_warning"]:
            warnings.append(f"CPU temperature high: {cpu_temp}°C")
            if worst_status != STATUS_CRITICAL:
                worst_status = STATUS_WARNING
    
    return worst_status, warnings

def _analyze_storage(storage: Dict[str, Any]) -> tuple[str, List[str]]:
    """Analyze storage data and return status and warnings."""
    warnings = []
    worst_status = STATUS_GOOD
    
    # Check main disk usage
    usage = storage.get("usage", {})
    used_percent = usage.get("used_percent", 0)
    
    if isinstance(used_percent, (int, float)):
        status = _get_status_for_percentage(
            used_percent, 
            DISK_THRESHOLDS["warning"], 
            DISK_THRESHOLDS["critical"]
        )
        
        if status == STATUS_CRITICAL:
            warnings.append(f"Disk space critically low: {used_percent}% used")
            worst_status = STATUS_CRITICAL
        elif status == STATUS_WARNING:
            warnings.append(f"Disk space running low: {used_percent}% used")
            worst_status = STATUS_WARNING
    
    # Check SMART health
    smart_data = storage.get("smart", {})
    failed_drives = []
    for drive, smart_info in smart_data.items():
        if isinstance(smart_info, dict) and smart_info.get("healthy") != "PASSED":
            failed_drives.append(drive)
    
    if failed_drives:
        warnings.append(f"SMART health check failed for drives: {', '.join(failed_drives)}")
        worst_status = STATUS_CRITICAL
    
    return worst_status, warnings

def _analyze_system(system: Dict[str, Any]) -> tuple[str, List[str]]:
    """Analyze system data and return status and warnings."""
    warnings = []
    worst_status = STATUS_GOOD
    
    # Check RAM usage
    ram_gb = system.get("RAM_GB", 0)
    if isinstance(ram_gb, (int, float)) and ram_gb < 8:
        warnings.append(f"Low RAM detected: {ram_gb} GB")
        worst_status = STATUS_WARNING
    
    # Check core count
    cores = system.get("Cores", 0)
    if isinstance(cores, int) and cores < 4:
        warnings.append(f"Low CPU core count: {cores} cores")
        if worst_status != STATUS_CRITICAL:
            worst_status = STATUS_WARNING
    
    return worst_status, warnings

def _generate_recommendations(
    storage_warnings: List[str], 
    temp_warnings: List[str], 
    system_warnings: List[str],
    storage_data: Dict[str, Any]
) -> List[str]:
    """Generate actionable recommendations based on analysis."""
    recommendations = []
    
    # Storage recommendations
    usage = storage_data.get("usage", {})
    used_percent = usage.get("used_percent", 0)
    
    if used_percent >= DISK_THRESHOLDS["critical"]:
        recommendations.extend([
            "Urgent: Free up disk space immediately",
            "Run disk cleanup utility",
            "Consider upgrading to a larger drive",
        ])
    elif used_percent >= DISK_THRESHOLDS["warning"]:
        recommendations.extend([
            "Run disk cleanup to free up space",
            "Move large files to external storage",
            "Uninstall unused programs",
        ])
    
    # SMART recommendations
    smart_data = storage_data.get("smart", {})
    if any(info.get("healthy") != "PASSED" for info in smart_data.values() if isinstance(info, dict)):
        recommendations.extend([
            "Back up important data immediately",
            "Consider replacing the failing drive",
            "Run extended drive diagnostics",
        ])
    
    # Temperature recommendations
    if temp_warnings:
        recommendations.extend([
            "Check system cooling and clean dust from fans",
            "Ensure proper ventilation around the computer",
            "Consider updating thermal paste on CPU",
        ])
    
    # System recommendations
    if system_warnings:
        if any("RAM" in warning for warning in system_warnings):
            recommendations.append("Consider upgrading RAM for better performance")
        if any("core" in warning for warning in system_warnings):
            recommendations.append("Consider upgrading CPU for better performance")
    
    return recommendations

def interpret_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Interpret diagnostic report and generate summary with recommendations."""
    
    # Extract data sections efficiently
    temps = report.get("temps", {})
    storage = report.get("storage", {})
    system = report.get("system", {})
    
    # Analyze each component
    temp_status, temp_warnings = _analyze_temperatures(temps)
    storage_status, storage_warnings = _analyze_storage(storage)
    system_status, system_warnings = _analyze_system(system)
    
    # Combine all warnings
    all_warnings = temp_warnings + storage_warnings + system_warnings
    
    # Determine overall status (worst case)
    statuses = [temp_status, storage_status, system_status]
    if STATUS_CRITICAL in statuses:
        overall_status = STATUS_CRITICAL
    elif STATUS_WARNING in statuses:
        overall_status = STATUS_WARNING
    else:
        overall_status = STATUS_GOOD
    
    # Generate recommendations
    recommendations = _generate_recommendations(
        storage_warnings, temp_warnings, system_warnings, storage
    )
    
    # Create summary with minimal object creation
    summary = {
        "status": overall_status,
        "warnings": all_warnings,
        "recommendations": recommendations,
        "component_status": {
            "temperatures": temp_status,
            "storage": storage_status,
            "system": system_status,
        },
        "health_score": _calculate_health_score(temp_status, storage_status, system_status),
    }
    
    return summary

@lru_cache(maxsize=64)
def _calculate_health_score(temp_status: str, storage_status: str, system_status: str) -> int:
    """Calculate overall health score (0-100) with caching."""
    score = 100
    
    # Deduct points based on component status
    status_penalties = {
        STATUS_CRITICAL: 30,
        STATUS_WARNING: 15,
        STATUS_GOOD: 0,
    }
    
    score -= status_penalties.get(temp_status, 0)
    score -= status_penalties.get(storage_status, 0)
    score -= status_penalties.get(system_status, 0)
    
    return max(0, score)
