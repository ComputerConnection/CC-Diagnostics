from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

from cc_diagnostics import diagnostics


class DiagnosticController(QObject):
    """Expose diagnostics functionality to QML."""

    progress = Signal(int, str)
    log = Signal(str)
    completed = Signal(str)

    @Slot()
    def runScan(self) -> None:
        def cb(pct: float, msg: str) -> None:
            percent = int(pct * 100)
            self.progress.emit(percent, msg)
            self.log.emit(msg)

        diagnostics.main([], progress_callback=cb)
        self.completed.emit("Scan complete")


def main() -> None:
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    controller = DiagnosticController()
    engine.rootContext().setContextProperty("diagnostics", controller)

    qml_path = Path(__file__).parent / "ui" / "Main.qml"
    engine.load(qml_path.as_posix())

    if not engine.rootObjects():
        sys.exit(-1)

    controller.completed.connect(lambda msg: print(msg))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
