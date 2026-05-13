"""Application bootstrap."""

from __future__ import annotations

import sys

from PySide6 import QtCore, QtWidgets

from emotor_studio.ui.main_window import MainWindow


def run() -> int:
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("eMotor-Studio")
    window = MainWindow()
    window.show()
    return app.exec()
