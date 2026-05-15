"""Reusable Qt widgets for the eMotor-Studio workbench UI."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class PageHeader(QtWidgets.QWidget):
    def __init__(self, title: str, subtitle: str = "", parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("pageTitle")
        layout.addWidget(title_label)
        if subtitle:
            subtitle_label = QtWidgets.QLabel(subtitle)
            subtitle_label.setObjectName("pageSubtitle")
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)


class PageScrollArea(QtWidgets.QScrollArea):
    """Consistent scroll container for workbench pages.

    Many motor-control pages contain wide tables or grouped controls. A stable
    scroll container prevents widgets from compressing until labels are clipped.
    """

    def __init__(self, page: QtWidgets.QWidget, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageScrollArea")
        self.setWidgetResizable(True)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        page.setMinimumWidth(980)
        self.setWidget(page)


class SectionCard(QtWidgets.QFrame):
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("sectionCard")
        self.body = QtWidgets.QVBoxLayout(self)
        self.body.setContentsMargins(15, 13, 15, 15)
        self.body.setSpacing(10)
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("sectionTitle")
        self.body.addWidget(title_label)
        if subtitle:
            subtitle_label = QtWidgets.QLabel(subtitle)
            subtitle_label.setObjectName("sectionSubtitle")
            subtitle_label.setWordWrap(True)
            self.body.addWidget(subtitle_label)


class KpiCard(QtWidgets.QFrame):
    def __init__(
        self,
        title: str,
        unit: str = "",
        state: str = "idle",
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.setProperty("state", state)
        self.setMinimumHeight(82)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setObjectName("kpiTitle")
        self.value_label = QtWidgets.QLabel("--")
        self.value_label.setObjectName("kpiValue")
        self.value_label.setWordWrap(False)
        self.unit_label = QtWidgets.QLabel(unit)
        self.unit_label.setObjectName("kpiUnit")
        self.unit_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)
        layout.addStretch(1)

    def set_value(self, value: str, unit: str = "", state: str | None = None) -> None:
        self.value_label.setText(value)
        self.unit_label.setText(unit)
        if state is not None:
            self.setProperty("state", state)
            self.style().unpolish(self)
            self.style().polish(self)


class StatusChip(QtWidgets.QLabel):
    def __init__(self, text: str, state: str = "muted", parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setProperty("role", "statusChip")
        self.setMinimumHeight(29)
        self.set_state(state)

    def set_state(self, state: str) -> None:
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)


class InfoBox(QtWidgets.QFrame):
    def __init__(self, title: str, body: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("infoBox")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(13, 10, 13, 10)
        layout.setSpacing(6)
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("infoTitle")
        body_label = QtWidgets.QLabel(body)
        body_label.setObjectName("infoBody")
        body_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(body_label)


class ToolStripButton(QtWidgets.QToolButton):
    """Compact toolbar button used for VESC-like global actions."""

    def __init__(
        self,
        text: str,
        tooltip: str = "",
        checkable: bool = False,
        enabled: bool = True,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("toolStripButton")
        self.setText(text)
        self.setToolTip(tooltip or text)
        self.setCheckable(checkable)
        self.setEnabled(enabled)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.setMinimumWidth(88)


class CommandStrip(QtWidgets.QFrame):
    """Bottom quick-control strip mirroring VESC Tool's always-visible controls."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("commandStrip")
        self.setMaximumHeight(86)
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(6)

        self.duty_box = QtWidgets.QDoubleSpinBox()
        self.duty_box.setRange(-1.0, 1.0)
        self.duty_box.setDecimals(3)
        self.duty_box.setPrefix("D ")
        self.duty_box.setSuffix(" duty")

        self.current_box = QtWidgets.QDoubleSpinBox()
        self.current_box.setRange(-100.0, 100.0)
        self.current_box.setDecimals(2)
        self.current_box.setPrefix("Iq ")
        self.current_box.setSuffix(" A")

        self.speed_box = QtWidgets.QDoubleSpinBox()
        self.speed_box.setRange(-100000.0, 100000.0)
        self.speed_box.setDecimals(0)
        self.speed_box.setPrefix("ω ")
        self.speed_box.setSuffix(" rpm")
        self.speed_box.setValue(1000)

        self.position_box = QtWidgets.QDoubleSpinBox()
        self.position_box.setRange(-100000.0, 100000.0)
        self.position_box.setDecimals(3)
        self.position_box.setPrefix("P ")
        self.position_box.setSuffix(" rad")

        self.brake_box = QtWidgets.QDoubleSpinBox()
        self.brake_box.setRange(0.0, 100.0)
        self.brake_box.setDecimals(2)
        self.brake_box.setPrefix("B ")
        self.brake_box.setSuffix(" A")

        widgets = [
            (self.duty_box, "Duty"),
            (self.current_box, "Iq"),
            (self.speed_box, "Speed"),
            (self.position_box, "Pos"),
            (self.brake_box, "Brake"),
        ]
        for column, (spin, button_text) in enumerate(widgets):
            spin.setObjectName("stripSpin")
            spin.setEnabled(False)
            button = QtWidgets.QPushButton(button_text)
            button.setObjectName("stripButton")
            button.setEnabled(False)
            layout.addWidget(spin, 0, column)
            layout.addWidget(button, 1, column)

        stop_button = QtWidgets.QPushButton("STOP")
        stop_button.setObjectName("stripStopButton")
        stop_button.setEnabled(False)
        layout.addWidget(stop_button, 0, 5, 2, 1)

        self.duty_bar = QtWidgets.QProgressBar()
        self.duty_bar.setObjectName("stripBar")
        self.duty_bar.setRange(0, 100)
        self.duty_bar.setValue(0)
        self.duty_bar.setFormat("Duty %p%")

        self.current_bar = QtWidgets.QProgressBar()
        self.current_bar.setObjectName("stripBar")
        self.current_bar.setRange(0, 100)
        self.current_bar.setValue(0)
        self.current_bar.setFormat("Current %p%")

        layout.addWidget(self.duty_bar, 0, 6)
        layout.addWidget(self.current_bar, 1, 6)
        layout.setColumnStretch(6, 1)

        note = QtWidgets.QLabel("框架占位，真实输出待接入")
        note.setObjectName("hintText")
        layout.addWidget(note, 0, 7, 2, 1)
