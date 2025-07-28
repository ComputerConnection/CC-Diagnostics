import json
import os
from datetime import datetime

from utils.system_info import get_system_info
from utils.storage_health import check_disk_health
from utils.win11_check import check_windows11_compat
from utils.temperature import get_temperatures
from output_parser import interpret_report


LOG_DIR = os.path.join(os.path.dirname(__file__), "logs", "diagnostics")


def main():
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": get_system_info(),
        "storage": check_disk_health(),
        "windows11": check_windows11_compat(),
        "temps": get_temperatures(),
    }

    summary = interpret_report(report)
    report.update(summary)

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(
        os.path.join(
            LOG_DIR,
            f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        ),
        "w",
    ) as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
