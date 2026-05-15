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

    visited_pages = 0
    for row in range(window.nav.count()):
        item = window.nav.item(row)
        if item.data(0x0100) is None:
            continue
        window.nav.setCurrentRow(row)
        app.processEvents()
        visited_pages += 1

    system_tabs = window.system_tools_page.findChild(QtWidgets.QTabWidget)
    visited_tools = 0
    if system_tabs is not None:
        for index in range(system_tabs.count()):
            system_tabs.setCurrentIndex(index)
            app.processEvents()
            visited_tools += 1

    window.close()
    app.processEvents()
    print(f"gui smoke ok: pages={visited_pages}, system_tools={visited_tools}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
