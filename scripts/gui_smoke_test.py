"""Minimal offscreen GUI smoke test for eMotor-Studio."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets  # noqa: E402

from emotor_studio.ui.main_window import MainWindow  # noqa: E402


def main() -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.processEvents()
    window.close()
    app.processEvents()
    print("gui smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
