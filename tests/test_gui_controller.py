import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gui import DiagnosticController
from cc_diagnostics import diagnostics


def test_load_latest_report(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    old = {"status": "OK"}
    new = {"status": "WARN", "warnings": ["w"]}
    old_file = log_dir / "diagnostic_1.json"
    new_file = log_dir / "diagnostic_2.json"
    old_file.write_text(json.dumps(old))
    new_file.write_text(json.dumps(new))
    monkeypatch.setattr(diagnostics, "LOG_DIR", str(log_dir))

    controller = DiagnosticController()
    result = controller.loadLatestReport()
    assert result["status"] == "WARN"
    assert result["warnings"] == ["w"]


def test_load_latest_report_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(diagnostics, "LOG_DIR", str(tmp_path))
    controller = DiagnosticController()
    assert controller.loadLatestReport() == {}
