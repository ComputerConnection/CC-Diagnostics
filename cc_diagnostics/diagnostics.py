"""Command-line entry point for running diagnostics."""

import argparse
import json
import os
from datetime import datetime
from typing import Callable, Sequence

from cc_diagnostics.utils.system_info import get_system_info
from cc_diagnostics.utils.storage_health import check_disk_health
from cc_diagnostics.utils.win11_check import check_windows11_compat
from cc_diagnostics.utils.temperature import get_temperatures
from cc_diagnostics.output_parser import interpret_report


LOG_DIR = os.path.join(os.path.dirname(__file__), "logs", "diagnostics")


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
    return parser.parse_args(args)


# ``progress`` ranges from 0.0 to 1.0 while ``message`` provides a description
# of the current step.
ProgressCallback = Callable[[float, str], None]


def main(
    argv: Sequence[str] | None = None,
    progress_callback: ProgressCallback | None = None,
) -> None:
    opts = parse_args(argv)

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

    emit(1.0, f"Report written to {out_file}")


if __name__ == "__main__":
    main()
