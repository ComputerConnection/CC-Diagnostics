"""Windows 11 compatibility helpers."""

import subprocess


def _run_powershell(cmd: str) -> str:
    """Run a PowerShell command and return its stdout."""
    output = subprocess.check_output(
        ["powershell", "-Command", cmd],
        stderr=subprocess.STDOUT,
        text=True,
    )
    return output.strip()


def _check_tpm() -> bool | None:
    """Return True if TPM 2.0 is present, False if not, None if unknown."""
    try:
        import wmi  # type: ignore

        c = wmi.WMI(namespace="root\\CIMV2\\Security\\MicrosoftTpm")
        tpm = c.Win32_Tpm()[0]
        spec = getattr(tpm, "SpecVersion", "")
        return "2.0" in str(spec)
    except Exception:
        try:
            spec = _run_powershell("(Get-Tpm).SpecVersion")
            return "2.0" in spec
        except Exception:
            return None


def _check_secure_boot() -> bool | None:
    """Return Secure Boot state."""
    try:
        result = _run_powershell("Confirm-SecureBootUEFI")
        return "True" in result
    except Exception:
        return None


def _get_os_build() -> str | None:
    """Return the OS build number if available."""
    try:
        return _run_powershell("(Get-CimInstance Win32_OperatingSystem).BuildNumber")
    except Exception:
        return None


def check_windows11_compat() -> dict:
    """Check for basic Windows 11 readiness information."""
    return {
        "TPM_2_0": _check_tpm(),
        "SecureBoot": _check_secure_boot(),
        "OS_Build": _get_os_build() or "Unknown",
    }

