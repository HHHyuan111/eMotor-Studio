"""Application bootstrap."""

from __future__ import annotations

import os
import sys

from PySide6 import QtCore, QtGui, QtWidgets

from emotor_studio.ui.main_window import MainWindow


def _apply_windows_qt_defaults() -> None:
    if sys.platform != "win32":
        return
    os.environ.setdefault("QT_OPENGL", "software")
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_QPA_PLATFORM", "windows")


def _show_window(window: QtWidgets.QMainWindow) -> None:
    screen = QtGui.QGuiApplication.primaryScreen()
    if screen is not None:
        available = screen.availableGeometry()
        frame = window.frameGeometry()
        frame.moveCenter(available.center())
        window.move(frame.topLeft())
    window.showNormal()
    window.raise_()
    window.activateWindow()


def _print_startup_diagnostics(window: QtWidgets.QMainWindow) -> None:
    if os.environ.get("EMOTOR_STUDIO_DEBUG") != "1":
        return
    geometry = window.geometry()
    screen = QtGui.QGuiApplication.primaryScreen()
    screen_name = screen.name() if screen is not None else "none"
    print(
        "eMotor-Studio started: "
        f"platform={QtGui.QGuiApplication.platformName()} "
        f"QT_OPENGL={os.environ.get('QT_OPENGL', '')} "
        f"screen={screen_name} "
        f"geometry={geometry.x()},{geometry.y()},{geometry.width()}x{geometry.height()}",
        flush=True,
    )


def run() -> int:
    _apply_windows_qt_defaults()
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("eMotor-Studio")
    window = MainWindow()
    _show_window(window)
    QtCore.QTimer.singleShot(100, lambda: _show_window(window))
    QtCore.QTimer.singleShot(150, lambda: _print_startup_diagnostics(window))
    return app.exec()
