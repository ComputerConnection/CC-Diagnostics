"""Command-line entry point for running diagnostics."""

import argparse
import json
import os
from datetime import datetime
from typing import Callable, Sequence
from pathlib import Path
from urllib import request, error
from functools import lru_cache

# Lazy imports to speed up startup
_system_info = None
_storage_health = None
_win11_check = None
_temperature = None
_output_parser = None

def _get_system_info():
    """Lazy import system_info module."""
    global _system_info
    if _system_info is None:
        from cc_diagnostics.utils.system_info import get_system_info
        _system_info = get_system_info
    return _system_info

def _get_storage_health():
    """Lazy import storage_health module."""
    global _storage_health
    if _storage_health is None:
        from cc_diagnostics.utils.storage_health import check_disk_health
        _storage_health = check_disk_health
    return _storage_health

def _get_win11_check():
    """Lazy import win11_check module."""
    global _win11_check
    if _win11_check is None:
        from cc_diagnostics.utils.win11_check import check_windows11_compat
        _win11_check = check_windows11_compat
    return _win11_check

def _get_temperature():
    """Lazy import temperature module."""
    global _temperature
    if _temperature is None:
        from cc_diagnostics.utils.temperature import get_temperatures
        _temperature = get_temperatures
    return _temperature

def _get_output_parser():
    """Lazy import output_parser module."""
    global _output_parser
    if _output_parser is None:
        from cc_diagnostics.output_parser import interpret_report
        _output_parser = interpret_report
    return _output_parser


LOG_DIR = os.path.join(os.path.dirname(__file__), "logs", "diagnostics")
SETTINGS_FILE = Path(__file__).resolve().parent.parent / "settings.json"

# Cache for settings to avoid repeated file reads
_settings_cache = None
_settings_cache_time = 0

@lru_cache(maxsize=1)
def _load_settings() -> dict:
    """Load settings.json from the project root if available with caching."""
    global _settings_cache, _settings_cache_time
    current_time = os.path.getmtime(SETTINGS_FILE) if SETTINGS_FILE.exists() else 0
    
    # Use cache if file hasn't changed
    if _settings_cache is not None and current_time <= _settings_cache_time:
        return _settings_cache.copy()
    
    try:
        _settings_cache = json.loads(SETTINGS_FILE.read_text())
        _settings_cache_time = current_time
        return _settings_cache.copy()
    except Exception:
        _settings_cache = {}
        _settings_cache_time = current_time
        return {}


def _upload_report(endpoint: str, report: dict) -> tuple[bool, str | None]:
    """Send ``report`` as JSON to ``endpoint`` via HTTP POST.

    Returns a tuple ``(success, error)`` where ``error`` is ``None`` when the
    upload succeeds or the stringified exception if it fails.
    """
    # Optimize JSON serialization with separators and ensure_ascii=False
    data = json.dumps(report, separators=(',', ':'), ensure_ascii=False).encode("utf-8")
    req = request.Request(endpoint, data=data, headers={
        "Content-Type": "application/json; charset=utf-8",
        "Content-Length": str(len(data))
    })
    try:
        with request.urlopen(req, timeout=10) as response:
            return True, None
    except Exception as exc:  # pragma: no cover - network
        return False, str(exc)


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Return parsed CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Run system diagnostics and write a JSON report."
    )
    parser.add_argument(
        "--output-dir",
        default=LOG_DIR,
        help="Directory to write diagnostic report JSON.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress information to stdout.",
    )
    parser.add_argument(
        "--server-endpoint",
        default=None,
        help="URL to POST the report JSON to. Overrides settings.json if provided.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the generated HTML report in a browser.",
    )
    return parser.parse_args(args)


# ``progress`` ranges from 0.0 to 1.0 while ``message`` provides a description
# of the current step.
ProgressCallback = Callable[[float, str], None]


def main(
    argv: Sequence[str] | None = None,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    opts = parse_args(argv)
    settings = _load_settings()
    endpoint = opts.server_endpoint if opts.server_endpoint is not None else settings.get("server_endpoint")

    def emit(progress: float, message: str) -> None:
        if progress_callback:
            progress_callback(progress, message)
        elif opts.verbose:
            percent = int(progress * 100)
            print(f"[{percent}%] {message}")

    log_dir = os.path.abspath(opts.output_dir)

    if opts.verbose and not progress_callback:
        print(f"Using output directory: {log_dir}")

    # Use lazy imports for faster startup
    emit(0.0, "Collecting system information")
    system = _get_system_info()()
    emit(0.25, "Checking disk health")
    storage = _get_storage_health()()
    emit(0.5, "Checking Windows 11 compatibility")
    windows11 = _get_win11_check()()
    emit(0.75, "Retrieving temperature data")
    temps = _get_temperature()()

    # Build report more efficiently
    timestamp_str = datetime.now().isoformat()
    report = {
        "timestamp": timestamp_str,
        "system": system,
        "storage": storage,
        "windows11": windows11,
        "temps": temps,
    }

    emit(0.9, "Interpreting results")
    summary = _get_output_parser()(report)
    report.update(summary)

    # Ensure output directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate filename more efficiently
    timestamp_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = os.path.join(log_dir, f"diagnostic_{timestamp_filename}.json")
    
    # Optimize JSON writing with efficient settings
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, separators=(',', ': '), ensure_ascii=False)

    # Render HTML report next to the JSON output
    html_path = os.path.splitext(out_file)[0] + ".html"
    try:
        from cc_diagnostics.report_renderer import render_html_report

        render_html_report(report, html_path)
        if not opts.no_browser:
            import webbrowser

            webbrowser.open(f"file://{html_path}")
    except Exception:  # pragma: no cover – rendering is best-effort
        pass

    upload_ok: bool | None = None
    upload_error: str | None = None
    if endpoint:
        emit(0.95, "Uploading report")
        upload_ok, upload_error = _upload_report(endpoint, report)
        if upload_ok:
            emit(0.97, "Upload successful")
        else:
            msg = f"Upload failed: {upload_error}"
            emit(0.97, msg)

    emit(1.0, f"Report written to {out_file}")
    if endpoint:
        report["upload_status"] = "success" if upload_ok else "failed"
        if not upload_ok and upload_error is not None:
            report["upload_error"] = upload_error
    else:
        report["upload_status"] = "disabled"
    return report


if __name__ == "__main__":
    main()
