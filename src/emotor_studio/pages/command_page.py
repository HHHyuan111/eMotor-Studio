"""Command page."""

from __future__ import annotations

from typing import Any

from PySide6 import QtWidgets

from emotor_studio.backend import BackendInterface
from emotor_studio.config import load_commands
from emotor_studio.models import MotorCommand
from emotor_studio.ui.components import InfoBox, PageHeader, SectionCard


class CommandPage(QtWidgets.QWidget):
    def __init__(self, backend: BackendInterface, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.backend = backend
        self._command_schema = self._load_command_schema()
        self._payload_widgets: dict[str, QtWidgets.QWidget] = {}

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("控制命令", "当前命令只发送到 MockBackend。"))

        top = QtWidgets.QGridLayout()
        top.setHorizontalSpacing(12)
        top.setVerticalSpacing(12)
        layout.addLayout(top)

        quick_card = SectionCard("常用命令", "高风险动作使用独立颜色。")
        quick_row = QtWidgets.QHBoxLayout()
        quick_row.setSpacing(8)
        for label, command, variant in [
            ("电机使能", "motor_enable", "primary"),
            ("电机停止", "motor_stop", "warning"),
            ("清除故障", "clear_fault", "ghost"),
            ("注入模拟故障", "inject_mock_fault", "danger"),
        ]:
            button = QtWidgets.QPushButton(label)
            button.setProperty("variant", variant)
            button.setMinimumWidth(96)
            button.clicked.connect(lambda _checked=False, name=command: self._send(name))
            quick_row.addWidget(button)
        quick_row.addStretch(1)
        quick_card.body.addLayout(quick_row)
        quick_card.body.addWidget(InfoBox("模式提示", "当前为 Mock 模式，不会控制真实电机。"))
        top.addWidget(quick_card, 0, 0)

        setpoint_card = SectionCard("目标设定")
        setpoint_grid = QtWidgets.QGridLayout()
        setpoint_grid.setHorizontalSpacing(8)
        setpoint_grid.setVerticalSpacing(8)
        self.speed_spin = self._spin(-900.0, 900.0, 125.0, " rad/s")
        self.id_spin = self._spin(-100.0, 100.0, 0.0, " A")
        self.iq_spin = self._spin(-100.0, 100.0, 0.0, " A")
        self.position_spin = self._spin(-100000.0, 100000.0, 0.0, " rad")
        setpoint_grid.addWidget(QtWidgets.QLabel("速度目标"), 0, 0)
        setpoint_grid.addWidget(self.speed_spin, 0, 1)
        speed_button = QtWidgets.QPushButton("设置速度")
        speed_button.setProperty("variant", "primary")
        speed_button.clicked.connect(self._set_speed)
        setpoint_grid.addWidget(speed_button, 0, 2)
        setpoint_grid.addWidget(QtWidgets.QLabel("Id / Iq"), 1, 0)
        setpoint_grid.addWidget(self.id_spin, 1, 1)
        setpoint_grid.addWidget(QtWidgets.QLabel("Iq"), 1, 2)
        setpoint_grid.addWidget(self.iq_spin, 1, 3)
        current_button = QtWidgets.QPushButton("设置电流")
        current_button.clicked.connect(self._set_current)
        setpoint_grid.addWidget(current_button, 1, 4)
        setpoint_grid.addWidget(QtWidgets.QLabel("位置目标"), 2, 0)
        setpoint_grid.addWidget(self.position_spin, 2, 1)
        position_button = QtWidgets.QPushButton("设置位置")
        position_button.clicked.connect(self._set_position)
        setpoint_grid.addWidget(position_button, 2, 2)
        setpoint_card.body.addLayout(setpoint_grid)
        top.addWidget(setpoint_card, 0, 1)

        custom_card = SectionCard("自定义命令", "命令结构来自 configs/commands.json。")
        custom_layout = QtWidgets.QVBoxLayout()
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
        send_button = QtWidgets.QPushButton("发送命令")
        send_button.setProperty("variant", "primary")
        send_button.clicked.connect(self._send_custom)
        custom_layout.addWidget(send_button)
        custom_card.body.addLayout(custom_layout)
        layout.addWidget(custom_card)

        history_card = SectionCard("命令历史")
        self.status_label = QtWidgets.QLabel("命令状态：就绪")
        self.status_label.setObjectName("hintText")
        history_card.body.addWidget(self.status_label)
        self.history = QtWidgets.QTableWidget(0, 4)
        self.history.setHorizontalHeaderLabels(["时间", "命令", "参数", "结果"])
        self.history.horizontalHeader().setStretchLastSection(True)
        self.history.setAlternatingRowColors(True)
        self.history.verticalHeader().setDefaultSectionSize(32)
        self.history.setColumnWidth(0, 132)
        self.history.setColumnWidth(1, 190)
        self.history.setColumnWidth(2, 460)
        history_card.body.addWidget(self.history)
        layout.addWidget(history_card, 1)
        self._rebuild_payload_form()

    def _send(self, name: str) -> None:
        payload = {}
        if name == "inject_mock_fault":
            payload = {"code": "ov_tmos", "message": "Command 页面注入的模拟故障"}
        self._send_command(MotorCommand(name=name, payload=payload))

    def _send_command(self, command: MotorCommand) -> None:
        self.backend.send_command(command)
        row = self.history.rowCount()
        self.history.insertRow(row)
        values = [f"{command.timestamp:.3f}", command.name, str(command.payload), "已发送到 MockBackend"]
        for column, value in enumerate(values):
            self.history.setItem(row, column, QtWidgets.QTableWidgetItem(value))
        self.status_label.setText(f"命令状态：已发送 {command.name}")

    def _set_speed(self) -> None:
        self._send_command(MotorCommand(name="set_speed_target", payload={"mechanical_speed": self.speed_spin.value()}))

    def _set_current(self) -> None:
        self._send_command(
            MotorCommand(
                name="set_current_target",
                payload={"id_set": self.id_spin.value(), "iq_set": self.iq_spin.value()},
            )
        )

    def _set_position(self) -> None:
        self._send_command(
            MotorCommand(
                name="set_position_target",
                payload={"mechanical_position": self.position_spin.value()},
            )
        )

    def _send_from_schema(self, command_schema: dict[str, Any], payload: dict[str, Any]) -> None:
        name = str(command_schema["name"])
        if name == "inject_mock_fault" and not payload:
            payload = {"code": "ov_tmos", "message": "Command 页面注入的模拟故障"}
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
            self.payload_form.addRow(QtWidgets.QLabel("无载荷"))
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
            spin = CommandPage._spin(-1000000.0, 1000000.0, 0.0, f" {item.get('unit')}" if item.get("unit") else "")
            spin.setDecimals(4)
            return spin
        return QtWidgets.QLineEdit()

    @staticmethod
    def _spin(minimum: float, maximum: float, value: float, suffix: str) -> QtWidgets.QDoubleSpinBox:
        spin = QtWidgets.QDoubleSpinBox()
        spin.setDecimals(3)
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        spin.setSuffix(suffix)
        return spin

    def _load_command_schema(self) -> list[dict[str, Any]]:
        if hasattr(self.backend, "read_command_schema"):
            return self.backend.read_command_schema()
        return load_commands()
