import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_diagnostics.report_renderer import (
    render_html_report,
    render_pdf_report,
    export_latest_report,
)


def test_render_html_report(tmp_path):
    report = {"status": "OK", "warnings": []}
    out_file = tmp_path / "report.html"
    render_html_report(report, out_file)
    assert out_file.exists()
    content = out_file.read_text()
    assert "OK" in content


def test_export_latest_report(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    sample = {"status": "OK", "warnings": []}
    json_file = log_dir / "diagnostic_1.json"
    json_file.write_text(json.dumps(sample))
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    result = export_latest_report(out_dir, log_dir=log_dir)
    assert Path(result).exists()


def test_render_pdf_report(tmp_path):
    report = {"status": "OK"}
    out_file = tmp_path / "report.pdf"
    render_pdf_report(report, out_file)
    assert out_file.exists()


def test_export_latest_report_pdf(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    sample = {"status": "OK"}
    json_file = log_dir / "diagnostic_1.json"
    json_file.write_text(json.dumps(sample))
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    result = export_latest_report(out_dir, log_dir=log_dir, fmt="pdf")
    assert Path(result).exists()


def test_export_latest_report_no_files(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    try:
        export_latest_report(out_dir, log_dir=log_dir)
    except FileNotFoundError as e:
        assert "No diagnostic reports found" in str(e)
    else:
        assert False, "Expected FileNotFoundError"

