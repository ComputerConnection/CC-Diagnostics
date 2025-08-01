# CC Diagnostic Tool

The CC Diagnostic Tool is a lightweight, in-house system diagnostics utility developed for internal use at Computer Connection. It runs hardware and OS-level health checks, outputs clear system status summaries, and prepares reports for both technicians and customers.

---

## 🔧 Features

- ✔️ One-click hardware + software scan
- 📊 Clean JSON output for parsing or exporting
- 🖥️ Frontend integration with the Utility Hub (QML)
- 🚨 Recommendations based on thresholds (low RAM, full drive, etc.)
- 🧾 Customer-ready PDF/HTML report export (future feature)
- 🧠 Windows 11 readiness check
- 🔒 Read-only, non-destructive scan

---

## 🧱 Core Stack

| Layer     | Tech/Libs                                 |
|-----------|--------------------------------------------|
| Backend   | Python 3.11+, `psutil`, `platform`, `wmi` |
| Frontend  | PySide6 (QML) inside Utility Hub launcher  |
| Logging   | JSON to `/logs/diagnostics/`               |
| Output    | JSON report with optional PDF/HTML         |

---

## 🚀 How It Works

1. The Python script scans:
   - CPU, RAM, disk, OS version, Uptime
   - SMART status of drives (via `smartctl`)
   - Windows 11 compatibility
   - System temps (if supported)
2. Generates a report object in JSON:
   - ✅ Healthy, ⚠️ Warnings, ❌ Failures
   - Includes a list of human-readable recommendations
3. Saves the report to `/logs/diagnostics/[timestamp].json`
4. Feeds results back into the Utility Hub UI
5. (Optional) Generates PDF or HTML output for customers

---

## 🗂 File Structure

```text
cc_diagnostics/
├── diagnostics.py         # Core scanner script
├── output_parser.py       # Converts raw data to readable summaries
├── utils/                 # Helper functions (temperature, SMART, etc.)
├── report_templates/      # HTML or PDF templates (optional)
├── logs/
│   └── diagnostics/       # Saved JSON reports
└── assets/                # Icons, branding
```

---

## 🎨 Design Tokens

The `ui/Styles.qml` file centralizes colors, spacing and font sizes used across the UI.

| Token | Description |
|-------|-------------|
| `spacingSmall` | Small spacing (4 px) |
| `spacingMedium` | Default spacing (8 px) |
| `spacingLarge` | Large spacing (16 px) |
| `fontFamily` | Base font family |
| `fontSizeSmall` | Small text size |
| `fontSizeMedium` | Regular text size |
| `fontSizeLarge` | Heading text size |
| `primaryColor` | Main accent color |
| `secondaryColor` | Secondary accent |
| `tertiaryColor` | Success/tertiary color |
| `elevationLow/Medium/High` | Shadow elevation levels |
| `overlayOpacity` | Opacity for busy overlays |
| `disabledOpacity` | Opacity for disabled content |

---

## 📦 Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows use .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
This installs the `psutil` and `wmi` packages.

3. Run a test scan:
```bash
python -m cc_diagnostics.diagnostics
python -m cc_diagnostics.diagnostics --help
```

The script accepts `--output-dir` to change where the JSON report is saved and
`--verbose` to print progress details.

## 🛠 Packaging

The project ships with a `pyproject.toml` allowing it to be installed with
`pip`. Installing the package exposes two entry points:

```bash
pip install .
# cc-diagnostics      -> command line interface
# cc-diagnostics-gui  -> launches the Qt GUI
```

To create a self-contained executable you can use `PyInstaller`:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole \
  --add-data "ui/*.qml:ui" gui.py
```

The `--add-data` option ensures the QML assets are bundled. PyInstaller will
include dependencies such as `psutil` and `wmi` automatically.

---

## 📌 Requirements

- Windows 10/11
- Admin privileges (for SMART checks + full WMI access)
- Python 3.11+
- `smartctl` must be available in PATH or embedded locally

---

## 📥 Roadmap

- [x] Basic scan and system summary
- [x] JSON report output
- [ ] GUI integration with Utility Hub
- [ ] Customer-facing PDF report
- [ ] Interactive recommendation module
- [ ] Remote diagnostic hooks (for on-site services)

---

## 👨‍🔧 Built for Techs

This utility replaces 5+ individual tools with one clean diagnostic output. If a system needs work — this catches it. If it doesn’t — it proves it.

> “If it passes this tool, it's good enough to build on.”
