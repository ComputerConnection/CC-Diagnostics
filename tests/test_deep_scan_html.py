import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import importlib

from cc_diagnostics import diagnostics


def test_html_report_generation(tmp_path, monkeypatch):
    # Patch diagnostics.LOG_DIR to temporary directory
    monkeypatch.setattr(diagnostics, "LOG_DIR", str(tmp_path))

    # Stub expensive renderer
    called = {}

    def fake_render(report, output_path, template_name="default.html"):
        called["path"] = output_path
        # write minimal html file
        Path(output_path).write_text("<html></html>")
        return output_path

    monkeypatch.setattr(diagnostics, "_load_settings", lambda: {})
    module = importlib.import_module("cc_diagnostics.report_renderer")
    monkeypatch.setattr(module, "render_html_report", fake_render, raising=False)

    # Run diagnostics.main with --no-browser so no webbrowser attempt
    report = diagnostics.main(["--no-browser", "--output-dir", str(tmp_path)])
    # Ensure html file path recorded and exists
    html_files = list(tmp_path.glob("*.html"))
    assert html_files, "HTML report was not generated"
    assert Path(called["path"]).exists(), "Renderer not called with correct path"