import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_diagnostics.output_parser import interpret_report


def test_interpret_report_ok():
    report = {
        "system": {"RAM_GB": 16},
        "storage": {"used_percent": 50},
    }
    summary = interpret_report(report)
    assert summary["status"] == "OK"
    assert summary["warnings"] == []
    assert summary["recommendations"] == []


def test_interpret_report_warns():
    report = {
        "system": {"RAM_GB": 4},
        "storage": {"used_percent": 95},
    }
    summary = interpret_report(report)
    assert summary["status"] == "WARN"
    assert "Low Memory" in summary["warnings"]
    assert "Disk Almost Full" in summary["warnings"]
    texts = [r["text"] for r in summary["recommendations"]]
    actions = [r["action"] for r in summary["recommendations"]]
    assert "Recommend upgrading RAM" in texts
    assert "Free up space or upgrade drive" in texts
    assert "upgrade_ram" in actions
    assert "disk_cleanup" in actions
