"""Command-line entry point for running diagnostics."""

import argparse
import json
import os
from datetime import datetime
from typing import Sequence

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


def main(argv: Sequence[str] | None = None) -> None:
    opts = parse_args(argv)

    log_dir = os.path.abspath(opts.output_dir)

    if opts.verbose:
        print(f"Using output directory: {log_dir}")

    report = {
        "timestamp": datetime.now().isoformat(),
        "system": get_system_info(),
        "storage": check_disk_health(),
        "windows11": check_windows11_compat(),
        "temps": get_temperatures(),
    }

    summary = interpret_report(report)
    report.update(summary)

    os.makedirs(log_dir, exist_ok=True)
    out_file = os.path.join(
        log_dir, f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)

    if opts.verbose:
        print(f"Report written to {out_file}")


if __name__ == "__main__":
    main()
