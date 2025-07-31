from __future__ import annotations

import os
import json
import sys
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any, Optional

# Lazy imports for faster startup
_pyside6_imports = None

def _get_pyside6():
    """Lazy import PySide6 modules to speed up startup."""
    global _pyside6_imports
    if _pyside6_imports is None:
        try:  # pragma: no cover - optional GUI dependencies
            from PySide6.QtCore import QObject, Slot, Signal, QUrl, QThread, QTimer
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtWidgets import QApplication
            from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType
            _pyside6_imports = {
                'QObject': QObject,
                'Slot': Slot,
                'Signal': Signal,
                'QUrl': QUrl,
                'QThread': QThread,
                'QTimer': QTimer,
                'QDesktopServices': QDesktopServices,
                'QApplication': QApplication,
                'QQmlApplicationEngine': QQmlApplicationEngine,
                'qmlRegisterSingletonType': qmlRegisterSingletonType,
            }
        except Exception:  # PySide6 may be missing or fail to load
            # Create minimal stubs for testing
            class MinimalSignal:
                def __init__(self, *a, **k):
                    pass
                def connect(self, *a, **k):  # pragma: no cover - dummy
                    pass
                def emit(self, *a, **k):  # pragma: no cover - dummy
                    pass
            
            def minimal_slot(*args, **kwargs):  # type: ignore[misc]
                def decorator(func):
                    return func
                return decorator
            
            class MinimalDesktopServices:  # type: ignore[misc]
                @staticmethod
                def openUrl(url):
                    pass
            
            _pyside6_imports = {
                'QObject': object,
                'Slot': minimal_slot,
                'Signal': MinimalSignal,
                'QUrl': type("QUrl", (), {}),  # type: ignore[misc]
                'QThread': object,
                'QTimer': object,
                'QDesktopServices': MinimalDesktopServices,
                'QApplication': None,
                'QQmlApplicationEngine': None,
                'qmlRegisterSingletonType': lambda *args, **kwargs: 0,  # type: ignore[misc]
            }
    return _pyside6_imports

# Get PySide6 components
qt = _get_pyside6()
QObject = qt['QObject']
Slot = qt['Slot']
Signal = qt['Signal']
QUrl = qt['QUrl']
QThread = qt['QThread']
QTimer = qt['QTimer']
QDesktopServices = qt['QDesktopServices']
QApplication = qt['QApplication']
QQmlApplicationEngine = qt['QQmlApplicationEngine']
qmlRegisterSingletonType = qt['qmlRegisterSingletonType']

# Lazy import diagnostics modules
_diagnostics = None
_export_latest_report = None
_settings_loader = None

def _get_diagnostics():
    """Lazy import diagnostics module."""
    global _diagnostics
    if _diagnostics is None:
        from cc_diagnostics import diagnostics
        _diagnostics = diagnostics
    return _diagnostics

def _get_export_latest_report():
    """Lazy import report export function."""
    global _export_latest_report
    if _export_latest_report is None:
        from cc_diagnostics.report_renderer import export_latest_report
        _export_latest_report = export_latest_report
    return _export_latest_report

def _get_settings_loader():
    """Lazy import settings loader."""
    global _settings_loader
    if _settings_loader is None:
        from cc_diagnostics.diagnostics import _load_settings, SETTINGS_FILE
        _settings_loader = (_load_settings, SETTINGS_FILE)
    return _settings_loader


class DiagnosticWorker(QThread):
    """Background thread to run ``diagnostics.main``."""

    progress = Signal(int, str)
    log = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, args: list[str] | None = None) -> None:
        super().__init__()
        self._args = args or []
        self._should_stop = False

    def stop(self) -> None:
        """Request the worker to stop."""
        self._should_stop = True

    def run(self) -> None:  # pragma: no cover - threads hard to test
        try:
            def cb(pct: float, msg: str) -> None:
                if self._should_stop:
                    return
                percent = int(pct * 100)
                self.progress.emit(percent, msg)
                self.log.emit(msg)

            diagnostics = _get_diagnostics()
            report = diagnostics.main(self._args, progress_callback=cb)
            
            if not self._should_stop:
                self.finished.emit(report)
        except Exception as exc:
            if not self._should_stop:
                self.error.emit(str(exc))


class DiagnosticController(QObject):
    """Expose diagnostics functionality to QML."""

    progress = Signal(int, str)
    log = Signal(str)
    completed = Signal(str)
    recommendationsUpdated = Signal(list)
    uploadStatus = Signal(str)
    loading = Signal(bool)
    error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._remote_enabled = False
        self._worker: DiagnosticWorker | None = None
        self._latest_report_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp = 0
        
        # Timer for periodic cache invalidation
        if QTimer != object:  # Only create if PySide6 is available
            self._cache_timer = QTimer()
            self._cache_timer.timeout.connect(self._invalidate_cache)
            self._cache_timer.start(30000)  # Invalidate cache every 30 seconds

    def _invalidate_cache(self) -> None:
        """Invalidate the report cache."""
        self._latest_report_cache = None
        self._cache_timestamp = 0

    @lru_cache(maxsize=32)
    def _get_latest_report_file(self) -> Optional[Path]:
        """Get the latest report file with caching."""
        diagnostics = _get_diagnostics()
        log_dir = Path(diagnostics.LOG_DIR)
        try:
            latest = max(
                log_dir.glob("diagnostic_*.json"),
                key=lambda p: (p.stat().st_mtime, p.name),
            )
            return latest
        except ValueError:
            return None

    @Slot(result="QVariant")
    def loadLatestReport(self) -> dict:
        """Return parsed data from the newest diagnostic JSON report."""
        latest_file = self._get_latest_report_file()
        if not latest_file:
            return {}
        
        # Check if we can use cached result
        current_mtime = latest_file.stat().st_mtime
        if (self._latest_report_cache is not None and 
            current_mtime <= self._cache_timestamp):
            return self._latest_report_cache.copy()
        
        try:
            report_text = latest_file.read_text(encoding='utf-8')
            report = json.loads(report_text)
            
            # Cache the parsed result
            result = {
                "status": report.get("status", ""),
                "warnings": report.get("warnings", []),
                "recommendations": report.get("recommendations", []),
                "system": report.get("system", {}),
                "storage": report.get("storage", {}),
            }
            self._latest_report_cache = result.copy()
            self._cache_timestamp = current_mtime
            return result
        except Exception:
            return {}

    @Slot(str, result="QVariant")
    def loadSetting(self, key: str):
        """Return value of ``key`` from settings.json if present."""
        _load_settings, _ = _get_settings_loader()
        settings = _load_settings()
        return settings.get(key)

    @Slot()
    def runScan(self) -> None:
        # Stop any existing worker
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(1000)  # Wait up to 1 second
            
        self.loading.emit(True)
        args = []
        if self._remote_enabled:
            _load_settings, _ = _get_settings_loader()
            endpoint = _load_settings().get("server_endpoint")
            if endpoint:
                args.extend(["--server-endpoint", endpoint])

        worker = DiagnosticWorker(args)
        self._worker = worker  # keep reference
        worker.progress.connect(self.progress)
        worker.log.connect(self.log)
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(worker.deleteLater)
        
        # Clear cache when starting new scan
        self._invalidate_cache()
        self._get_latest_report_file.cache_clear()
        
        worker.start()

    def _on_worker_finished(self, report: dict) -> None:
        """Handle worker completion."""
        self.recommendationsUpdated.emit(report.get("recommendations", []))
        self.completed.emit("Scan complete")
        self.uploadStatus.emit(report.get("upload_status", "disabled"))
        self.loading.emit(False)
        self._worker = None

    def _on_worker_error(self, error_msg: str) -> None:
        """Handle worker error."""
        self.error.emit(f"Scan failed: {error_msg}")
        self.loading.emit(False)
        self._worker = None

    @Slot(bool)
    def setRemoteEnabled(self, enabled: bool) -> None:
        self._remote_enabled = enabled

    @Slot(str, str)
    def exportReport(self, directory: str, fmt: str = "html") -> None:
        """Export the most recent JSON report to ``directory`` as HTML or PDF."""
        try:
            export_func = _get_export_latest_report()
            path = export_func(directory, fmt=fmt)
            self.log.emit(f"Report exported to {path}")
        except Exception as exc:  # pragma: no cover - user feedback
            self.log.emit(f"Export failed: {exc}")

    @Slot(str)
    def runAction(self, action_id: str) -> None:
        """Launch helper script or open documentation for ``action_id``."""
        # Use a more comprehensive action mapping
        links = {
            "upgrade_ram": "https://example.com/upgrade_ram",
            "disk_cleanup": "https://example.com/disk_cleanup",
            "update_drivers": "https://example.com/update_drivers",
            "check_temps": "https://example.com/check_temps",
            "optimize_startup": "https://example.com/optimize_startup",
        }

        url = links.get(action_id)
        if url:
            QDesktopServices.openUrl(QUrl(url))

    @Slot(str, "QVariant")
    def updateSetting(self, key: str, value) -> None:
        """Update ``key`` in settings.json with ``value``."""
        _load_settings, SETTINGS_FILE = _get_settings_loader()
        settings = _load_settings()
        settings[key] = value
        
        # Write with better formatting and error handling
        try:
            SETTINGS_FILE.write_text(
                json.dumps(settings, indent=2, separators=(',', ': '), ensure_ascii=False), 
                encoding='utf-8'
            )
            # Clear settings cache after update
            _load_settings.cache_clear()
        except Exception as exc:
            self.error.emit(f"Failed to save settings: {exc}")


def main() -> None:
    # Set environment variables for better performance
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Material")
    os.environ.setdefault("QT_QUICK_CONTROLS_MATERIAL_VARIANT", "Dense")
    
    if QApplication is None:
        print("PySide6 not available. GUI mode disabled.")
        return
    
    app = QApplication(sys.argv)
    app.setOrganizationName("Computer Connection")
    app.setApplicationName("CC Diagnostics")
    app.setApplicationVersion("1.0")
    
    engine = QQmlApplicationEngine()
    controller = DiagnosticController()
    engine.rootContext().setContextProperty("diagnostics", controller)

    styles_path = Path(__file__).parent / "ui" / "Styles.qml"
    if styles_path.exists():
        qmlRegisterSingletonType(
            QUrl.fromLocalFile(str(styles_path.resolve())),
            "App.Styles", 1, 0, "Styles"
        )

    qml_path = Path(__file__).parent / "ui" / "Main.qml"
    if qml_path.exists():
        engine.load(QUrl.fromLocalFile(str(qml_path.resolve())))
    else:
        print(f"QML file not found: {qml_path}")
        sys.exit(-1)

    if not engine.rootObjects():
        print("Failed to load QML interface")
        sys.exit(-1)

    controller.completed.connect(lambda msg: print(msg))
    
    # Handle cleanup on exit
    def cleanup():
        if controller._worker and controller._worker.isRunning():
            controller._worker.stop()
            controller._worker.wait(2000)
    
    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
