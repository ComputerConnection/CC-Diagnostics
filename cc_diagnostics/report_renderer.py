"""Render diagnostic reports to HTML using Jinja2."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
import pdfkit

TEMPLATE_DIR = Path(__file__).parent / "report_templates"
LOG_DIR = Path(__file__).parent / "logs" / "diagnostics"

_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_html_report(report: dict[str, Any], output_path: str | Path, template_name: str = "default.html") -> str:
    """Render ``report`` to ``output_path`` using ``template_name``."""
    template = _env.get_template(template_name)
    html = template.render(report=report)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)


def render_pdf_report(report: dict[str, Any], output_path: str | Path, template_name: str = "default.html") -> str:
    """Render ``report`` to ``output_path`` as PDF using ``template_name``."""
    template = _env.get_template(template_name)
    html = template.render(report=report)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pdfkit.from_string(html, str(out))
    return str(out)


def export_latest_report(
    output_dir: str | Path,
    log_dir: str | Path | None = None,
    template_name: str = "default.html",
    fmt: str = "html",
) -> str:
    """Render the newest JSON report in ``log_dir`` to ``output_dir`` as ``fmt``."""
    log_dir = Path(log_dir) if log_dir else LOG_DIR
    latest_json = max(log_dir.glob("diagnostic_*.json"), key=lambda p: p.stat().st_mtime)
    report = json.loads(latest_json.read_text())

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = latest_json.stem

    if fmt.lower() == "pdf":
        out_path = output_dir / f"{base_name}.pdf"
        return render_pdf_report(report, out_path, template_name)
    else:
        out_path = output_dir / f"{base_name}.html"
        return render_html_report(report, out_path, template_name)
