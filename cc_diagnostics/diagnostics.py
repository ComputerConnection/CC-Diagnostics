"""Command-line entry point for running diagnostics."""

import argparse
import json
import os
from datetime import datetime
from typing import Callable, Sequence
from pathlib import Path
from urllib import request, error

from cc_diagnostics.utils.system_info import get_system_info
from cc_diagnostics.utils.storage_health import check_disk_health
from cc_diagnostics.utils.win11_check import check_windows11_compat
from cc_diagnostics.utils.temperature import get_temperatures
from cc_diagnostics.output_parser import interpret_report


LOG_DIR = os.path.join(os.path.dirname(__file__), "logs", "diagnostics")
SETTINGS_FILE = Path(__file__).resolve().parent.parent / "settings.json"


def _load_settings() -> dict:
    """Load settings.json from the project root if available."""
    try:
        return json.loads(SETTINGS_FILE.read_text())
    except Exception:
        return {}


def _upload_report(endpoint: str, report: dict) -> bool:
    """Send ``report`` as JSON to ``endpoint`` via HTTP POST."""
    data = json.dumps(report).encode("utf-8")
    req = request.Request(endpoint, data=data, headers={"Content-Type": "application/json"})
    try:
        request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False


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

    emit(0.0, "Collecting system information")
    system = get_system_info()
    emit(0.25, "Checking disk health")
    storage = check_disk_health()
    emit(0.5, "Checking Windows 11 compatibility")
    windows11 = check_windows11_compat()
    emit(0.75, "Retrieving temperature data")
    temps = get_temperatures()

    report = {
        "timestamp": datetime.now().isoformat(),
        "system": system,
        "storage": storage,
        "windows11": windows11,
        "temps": temps,
    }

    emit(0.9, "Interpreting results")
    summary = interpret_report(report)
    report.update(summary)

    os.makedirs(log_dir, exist_ok=True)
    out_file = os.path.join(
        log_dir, f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)

    upload_ok: bool | None = None
    if endpoint:
        emit(0.95, "Uploading report")
        upload_ok = _upload_report(endpoint, report)
        msg = "Upload successful" if upload_ok else "Upload failed"
        emit(0.97, msg)

    emit(1.0, f"Report written to {out_file}")
    if endpoint:
        report["upload_status"] = "success" if upload_ok else "failed"
    else:
        report["upload_status"] = "disabled"
    return report


if __name__ == "__main__":
    main()
