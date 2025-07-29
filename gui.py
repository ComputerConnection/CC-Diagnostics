from __future__ import annotations

import os
import json
import sys
from pathlib import Path

try:  # pragma: no cover - optional GUI dependencies
    from PySide6.QtCore import QObject, Slot, Signal, QUrl, QThread
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtWidgets import QApplication
    from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType
except Exception:  # PySide6 may be missing or fail to load
    QObject = object
    def Slot(*args, **kwargs):  # type: ignore[misc]
        def decorator(func):
            return func
        return decorator
    class Signal:  # minimal stub for tests
        def __init__(self, *a, **k):
            pass
        def connect(self, *a, **k):  # pragma: no cover - dummy
            pass
        def emit(self, *a, **k):  # pragma: no cover - dummy
            pass
    QUrl = type("QUrl", (), {})  # type: ignore[misc]
    QThread = object
    class QDesktopServices:  # type: ignore[misc]
        @staticmethod
        def openUrl(url):
            pass
    QApplication = None
    QQmlApplicationEngine = None
    def qmlRegisterSingletonType(*args, **kwargs):  # type: ignore[misc]
        return 0

from cc_diagnostics import diagnostics
from cc_diagnostics.report_renderer import export_latest_report

# reuse settings loader from diagnostics
from cc_diagnostics.diagnostics import _load_settings, SETTINGS_FILE


class DiagnosticWorker(QThread):
    """Background thread to run ``diagnostics.main``."""

    progress = Signal(int, str)
    log = Signal(str)
    finished = Signal(dict)

    def __init__(self, args: list[str] | None = None) -> None:
        super().__init__()
        self._args = args or []

    def run(self) -> None:  # pragma: no cover - threads hard to test
        def cb(pct: float, msg: str) -> None:
            percent = int(pct * 100)
            self.progress.emit(percent, msg)
            self.log.emit(msg)

        report = diagnostics.main(self._args, progress_callback=cb)
        self.finished.emit(report)


class DiagnosticController(QObject):
    """Expose diagnostics functionality to QML."""

    progress = Signal(int, str)
    log = Signal(str)
    completed = Signal(str)
    recommendationsUpdated = Signal(list)
    uploadStatus = Signal(str)
    loading = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._remote_enabled = False
        self._worker: DiagnosticWorker | None = None

    @Slot(result="QVariant")
    def loadLatestReport(self) -> dict:
        """Return parsed data from the newest diagnostic JSON report."""
        log_dir = Path(diagnostics.LOG_DIR)
        try:
            latest = max(
                log_dir.glob("diagnostic_*.json"),
                key=lambda p: (p.stat().st_mtime, p.name),
            )
        except ValueError:
            return {}
        try:
            report = json.loads(latest.read_text())
        except Exception:
            return {}
        return {
            "status": report.get("status", ""),
            "warnings": report.get("warnings", []),
            "recommendations": report.get("recommendations", []),
            "system": report.get("system", {}),
            "storage": report.get("storage", {}),
        }

    @Slot(str, result="QVariant")
    def loadSetting(self, key: str):
        """Return value of ``key`` from settings.json if present."""
        settings = _load_settings()
        return settings.get(key)

    @Slot()
    def runScan(self) -> None:
        self.loading.emit(True)
        args = []
        if self._remote_enabled:
            endpoint = _load_settings().get("server_endpoint")
            if endpoint:
                args.extend(["--server-endpoint", endpoint])

        worker = DiagnosticWorker(args)
        self._worker = worker  # keep reference
        worker.progress.connect(self.progress)
        worker.log.connect(self.log)
        worker.finished.connect(self._on_worker_finished)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _on_worker_finished(self, report: dict) -> None:
        """Handle worker completion."""
        self.recommendationsUpdated.emit(report.get("recommendations", []))
        self.completed.emit("Scan complete")
        self.uploadStatus.emit(report.get("upload_status", "disabled"))
        self.loading.emit(False)
        self._worker = None

    @Slot(bool)
    def setRemoteEnabled(self, enabled: bool) -> None:
        self._remote_enabled = enabled

    @Slot(str, str)
    def exportReport(self, directory: str, fmt: str = "html") -> None:
        """Export the most recent JSON report to ``directory`` as HTML or PDF."""
        try:
            path = export_latest_report(directory, fmt=fmt)
            self.log.emit(f"Report exported to {path}")
        except Exception as exc:  # pragma: no cover - user feedback
            self.log.emit(f"Export failed: {exc}")

    @Slot(str)
    def runAction(self, action_id: str) -> None:
        """Launch helper script or open documentation for ``action_id``."""
        links = {
            "upgrade_ram": "https://example.com/upgrade_ram",
            "disk_cleanup": "https://example.com/disk_cleanup",
        }

        url = links.get(action_id)
        if url:
            QDesktopServices.openUrl(QUrl(url))

    @Slot(str, "QVariant")
    def updateSetting(self, key: str, value) -> None:
        """Update ``key`` in settings.json with ``value``."""
        settings = _load_settings()
        settings[key] = value
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2))


def main() -> None:
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Material")
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    controller = DiagnosticController()
    engine.rootContext().setContextProperty("diagnostics", controller)

    styles_path = Path(__file__).parent / "ui" / "Styles.qml"
    qmlRegisterSingletonType(
        QUrl.fromLocalFile(str(styles_path.resolve())),
        "App.Styles", 1, 0, "Styles"
    )

    qml_path = Path(__file__).parent / "ui" / "Main.qml"
    engine.load(qml_path.as_posix())

    if not engine.rootObjects():
        sys.exit(-1)

    controller.completed.connect(lambda msg: print(msg))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
