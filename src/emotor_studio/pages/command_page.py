"""Command page."""

from __future__ import annotations

from typing import Any

from PySide6 import QtWidgets

from emotor_studio.backend import BackendInterface
from emotor_studio.config import load_commands
from emotor_studio.models import MotorCommand


class CommandPage(QtWidgets.QWidget):
    def __init__(self, backend: BackendInterface, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.backend = backend
        self._command_schema = self._load_command_schema()
        self._payload_widgets: dict[str, QtWidgets.QWidget] = {}
        layout = QtWidgets.QVBoxLayout(self)

        quick_group = QtWidgets.QGroupBox("Quick Commands")
        quick_row = QtWidgets.QHBoxLayout(quick_group)
        for command in self._quick_commands():
            button = QtWidgets.QPushButton(str(command.get("display_name") or command["name"]))
            button.clicked.connect(lambda _checked=False, item=command: self._send_from_schema(item, {}))
            quick_row.addWidget(button)
        quick_row.addStretch(1)
        layout.addWidget(quick_group)

        target_row = QtWidgets.QHBoxLayout()
        self.target_spin = QtWidgets.QDoubleSpinBox()
        self.target_spin.setRange(-900, 900)
        self.target_spin.setValue(125)
        self.target_spin.setSuffix(" rad/s")
        target_button = QtWidgets.QPushButton("Set Speed")
        target_button.clicked.connect(self._set_target)
        target_row.addWidget(self.target_spin)
        target_row.addWidget(target_button)
        layout.addLayout(target_row)

        custom_group = QtWidgets.QGroupBox("Command Builder")
        custom_layout = QtWidgets.QVBoxLayout(custom_group)
        self.command_combo = QtWidgets.QComboBox()
        for command in self._command_schema:
            self.command_combo.addItem(
                f"{command.get('display_name') or command['name']} [{command['name']}]",
                command,
            )
        self.command_combo.currentIndexChanged.connect(self._rebuild_payload_form)
        custom_layout.addWidget(self.command_combo)
        self.payload_form = QtWidgets.QFormLayout()
        custom_layout.addLayout(self.payload_form)
        send_button = QtWidgets.QPushButton("Send Command")
        send_button.clicked.connect(self._send_custom)
        custom_layout.addWidget(send_button)
        layout.addWidget(custom_group)

        self.history = QtWidgets.QPlainTextEdit()
        self.history.setReadOnly(True)
        layout.addWidget(self.history)
        self._rebuild_payload_form()

    def _send(self, name: str) -> None:
        payload = {}
        if name == "inject_mock_fault":
            payload = {"code": "ov_tmos", "message": "Injected from Command page"}
        self._send_command(MotorCommand(name=name, payload=payload))

    def _send_command(self, command: MotorCommand) -> None:
        self.backend.send_command(command)
        self.history.appendPlainText(f"{command.timestamp:.3f} {command.name} {command.payload}")

    def _set_target(self) -> None:
        command = MotorCommand(name="set_speed_target", payload={"mechanical_speed": self.target_spin.value()})
        self._send_command(command)

    def _send_from_schema(self, command_schema: dict[str, Any], payload: dict[str, Any]) -> None:
        name = str(command_schema["name"])
        if name == "inject_mock_fault" and not payload:
            payload = {"code": "ov_tmos", "message": "Injected from Command page"}
        self._send_command(MotorCommand(name=name, payload=payload))

    def _send_custom(self) -> None:
        command_schema = self.command_combo.currentData()
        if not isinstance(command_schema, dict):
            return
        payload = {}
        for item in command_schema.get("payload", []):
            name = str(item["name"])
            widget = self._payload_widgets.get(name)
            if widget is None:
                continue
            if isinstance(widget, QtWidgets.QComboBox):
                payload[name] = widget.currentData()
            elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                payload[name] = widget.value()
            elif isinstance(widget, QtWidgets.QLineEdit):
                payload[name] = widget.text()
        self._send_from_schema(command_schema, payload)

    def _rebuild_payload_form(self) -> None:
        while self.payload_form.rowCount():
            self.payload_form.removeRow(0)
        self._payload_widgets = {}
        command_schema = self.command_combo.currentData()
        if not isinstance(command_schema, dict):
            return
        payload_schema = command_schema.get("payload") or []
        if not payload_schema:
            self.payload_form.addRow(QtWidgets.QLabel("No payload"))
            return
        for item in payload_schema:
            widget = self._widget_for_payload(item)
            name = str(item["name"])
            unit = str(item.get("unit") or "")
            label = f"{name} ({unit})" if unit else name
            self._payload_widgets[name] = widget
            self.payload_form.addRow(label, widget)

    @staticmethod
    def _widget_for_payload(item: dict[str, Any]) -> QtWidgets.QWidget:
        item_type = str(item.get("type") or "string")
        if item_type == "enum":
            combo = QtWidgets.QComboBox()
            for value in item.get("values", []):
                combo.addItem(str(value), value)
            return combo
        if item_type in {"float", "double"}:
            spin = QtWidgets.QDoubleSpinBox()
            spin.setDecimals(4)
            spin.setRange(-1000000.0, 1000000.0)
            spin.setSingleStep(1.0)
            if item.get("unit"):
                spin.setSuffix(f" {item['unit']}")
            return spin
        return QtWidgets.QLineEdit()

    def _load_command_schema(self) -> list[dict[str, Any]]:
        if hasattr(self.backend, "read_command_schema"):
            return self.backend.read_command_schema()
        return load_commands()

    def _quick_commands(self) -> list[dict[str, Any]]:
        quick_names = {"motor_enable", "motor_stop", "clear_fault", "inject_mock_fault"}
        return [command for command in self._command_schema if command.get("name") in quick_names]
