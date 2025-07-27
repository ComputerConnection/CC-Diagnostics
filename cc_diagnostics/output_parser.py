
def interpret_report(report):
    warnings = []
    recommendations = []

    if report["system"].get("RAM_GB", 0) < 8:
        warnings.append("Low Memory")
        recommendations.append("Recommend upgrading RAM")

    if report["storage"].get("used_percent", 0) > 90:
        warnings.append("Disk Almost Full")
        recommendations.append("Free up space or upgrade drive")

    return {
        "status": "WARN" if warnings else "OK",
        "warnings": warnings,
        "recommendations": recommendations,
    }
