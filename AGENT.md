# Agent Task: CC Diagnostic Tool Buildout

---

## 🎯 Objective

Build a fully functioning Python-based diagnostics tool that scans system hardware/software status, generates structured reports, and interfaces with the existing Utility Hub.

---

## 🧱 Modules to Build

### 1. `diagnostics.py`
> Central script that orchestrates the diagnostic process.

- Use `psutil`, `platform`, `subprocess`, and `wmi` to gather:
  - CPU brand, core count, usage
  - RAM total/available
  - Disk health + space (SMART optional via `smartctl`)
  - OS version
  - Uptime, hostname, user
  - Windows 11 compatibility checks:
    - TPM check
    - Secure Boot
    - OS version/build

- Output a dictionary like:
```json
{
  "status": "OK",
  "warnings": ["Low RAM", "Drive near full"],
  "system": {
    "OS": "Windows 10 Pro",
    "CPU": "Intel Core i7-11700",
    "RAM": "16 GB",
    "FreeDisk": "88 GB",
    ...
  },
  "recommendations": [
    "Upgrade to Windows 11",
    "Add more memory (below 8 GB)"
  ]
}
