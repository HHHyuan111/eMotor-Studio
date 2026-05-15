"""Dashboard page for quick motor-system judgement."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from emotor_studio.models import MotorCommand, TelemetrySample
from emotor_studio.ui.components import KpiCard, PageHeader, SectionCard


def _signal(sample: TelemetrySample, name: str, fallback: object = "--") -> object:
    return sample.signals.get(name, fallback)


class DashboardPage(QtWidgets.QWidget):
    """Compact status console for the most common bring-up questions."""

    def __init__(self, backend=None, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.backend = backend
        self._cards: dict[str, KpiCard] = {}

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        root.addWidget(PageHeader("仪表盘", "一屏判断连接、运行、故障、电源、电流和温度状态。"))

        top_split = QtWidgets.QHBoxLayout()
        top_split.setSpacing(12)
        top_split.addWidget(self._build_state_overview(), 3)
        top_split.addWidget(self._build_control_panel(), 2)
        root.addLayout(top_split)

        root.addWidget(self._build_realtime_metrics(), 1)
        root.addStretch(1)

    def _build_state_overview(self) -> SectionCard:
        card = SectionCard("系统状态", "Mock 当前可运行；真实硬件连接、写入和安全确认留到后续协议阶段。")
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        specs = [
            ("connection", "连接", "后端状态"),
            ("run_state", "运行", "run_state"),
            ("system_mode", "模式", "system_mode"),
            ("fault_word", "故障", "fault_word"),
            ("transport", "通信路线", "V1.1"),
            ("sample_rate", "刷新", "Mock tick"),
        ]
        for index, (key, title, unit) in enumerate(specs):
            widget = KpiCard(title, unit)
            widget.setMinimumWidth(160)
            widget.setMaximumHeight(108)
            self._cards[key] = widget
            grid.addWidget(widget, index // 3, index % 3)
        card.body.addLayout(grid)
        return card

    def _build_control_panel(self) -> SectionCard:
        card = SectionCard("快速控制", "这里只放高频安全动作，完整命令请进入“控制命令”页。")
        command_grid = QtWidgets.QGridLayout()
        command_grid.setHorizontalSpacing(8)
        command_grid.setVerticalSpacing(8)
        commands = [
            ("电机使能", "motor_enable", "primary"),
            ("电机停止", "motor_stop", "warning"),
            ("清除故障", "clear_fault", "ghost"),
            ("注入模拟故障", "inject_mock_fault", "danger"),
        ]
        for index, (label, command, variant) in enumerate(commands):
            button = QtWidgets.QPushButton(label)
            button.setProperty("variant", variant)
            button.clicked.connect(lambda _checked=False, name=command: self._send(name))
            command_grid.addWidget(button, index // 2, index % 2)
        card.body.addLayout(command_grid)

        setpoint_row = QtWidgets.QHBoxLayout()
        setpoint_row.setSpacing(8)
        setpoint_row.addWidget(QtWidgets.QLabel("目标速度"))
        self.speed_spin = QtWidgets.QDoubleSpinBox()
        self.speed_spin.setRange(-900.0, 900.0)
        self.speed_spin.setDecimals(2)
        self.speed_spin.setValue(125.0)
        self.speed_spin.setSuffix(" rad/s")
        self.speed_spin.setMinimumWidth(150)
        setpoint_row.addWidget(self.speed_spin, 1)
        speed_button = QtWidgets.QPushButton("发送")
        speed_button.setProperty("variant", "primary")
        speed_button.clicked.connect(self._set_speed)
        setpoint_row.addWidget(speed_button)
        card.body.addLayout(setpoint_row)

        self.control_hint = QtWidgets.QLabel("当前为 Mock 模式，不会驱动真实电机。")
        self.control_hint.setObjectName("hintText")
        self.control_hint.setWordWrap(True)
        card.body.addWidget(self.control_hint)
        return card

    def _build_realtime_metrics(self) -> SectionCard:
        card = SectionCard("实时指标", "按电机调试优先级组织：速度、电源、电流、温度、PWM。")
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        metrics = [
            ("speed", "实际转速", "rpm / rad/s"),
            ("speed_target", "目标转速", "rpm / rad/s"),
            ("bus_voltage", "母线电压", "V"),
            ("bus_current", "母线电流", "A"),
            ("current_q", "q轴电流", "A"),
            ("current_d", "d轴电流", "A"),
            ("mos_temperature", "MOS温度", "degC"),
            ("coil_temperature", "线圈温度", "degC"),
            ("duty", "PWM Duty", "A / B / C"),
            ("power", "功率", "W"),
            ("angle", "电角度", "rad"),
            ("encoder", "编码器角度", "rad"),
        ]
        for index, (key, title, unit) in enumerate(metrics):
            widget = KpiCard(title, unit)
            widget.setMinimumWidth(174)
            widget.setMaximumHeight(112)
            self._cards[key] = widget
            grid.addWidget(widget, index // 4, index % 4)
        card.body.addLayout(grid)
        return card

    def update_telemetry(self, sample: TelemetrySample) -> None:
        mechanical_speed = float(_signal(sample, "mechanical_speed", 0.0))
        target_speed = float(_signal(sample, "speed_target_mechanical", 0.0))
        bus_voltage = float(_signal(sample, "bus_voltage", 0.0))
        bus_current = float(_signal(sample, "bus_current", 0.0))
        current_q = float(_signal(sample, "current_q", 0.0))
        current_d = float(_signal(sample, "current_d", 0.0))
        mos_temp = float(_signal(sample, "mos_temperature", 0.0))
        coil_temp = float(_signal(sample, "coil_temperature", 0.0))
        duty_a = float(_signal(sample, "duty_a", 0.0))
        duty_b = float(_signal(sample, "duty_b", 0.0))
        duty_c = float(_signal(sample, "duty_c", 0.0))
        angle = float(_signal(sample, "electrical_angle", 0.0))
        encoder = float(_signal(sample, "encoder_angle", 0.0))
        run_state = str(_signal(sample, "run_state", sample.run_state.value))
        run_state_text = self._run_state_text(run_state)
        faults = ", ".join(sample.faults) if sample.faults else "无故障"
        run_state_color = "fault" if sample.faults else ("ok" if run_state == "runing" else "stop")

        self._cards["connection"].set_value("Mock 已连接", "本地仿真", "ok")
        self._cards["run_state"].set_value(run_state_text, run_state, run_state_color)
        self._cards["system_mode"].set_value(str(_signal(sample, "system_mode", sample.system_mode.value)), "mode", "idle")
        self._cards["fault_word"].set_value(f"0x{sample.fault_word:08X}", faults, "fault" if sample.faults else "ok")
        self._cards["transport"].set_value("串口优先", "Type-C COM / J1 UART", "idle")
        self._cards["sample_rate"].set_value("20 Hz", "UI refresh", "idle")
        self._cards["speed"].set_value(f"{sample.rpm:,.0f}", f"rpm | {mechanical_speed:.1f} rad/s", run_state_color)
        self._cards["speed_target"].set_value(f"{sample.target_rpm:,.0f}", f"rpm | {target_speed:.1f} rad/s", "idle")
        self._cards["bus_voltage"].set_value(f"{bus_voltage:.1f}", "V", "ok" if 18.0 <= bus_voltage <= 30.0 else "warning")
        self._cards["bus_current"].set_value(f"{bus_current:.2f}", "A", "idle")
        self._cards["current_q"].set_value(f"{current_q:.2f}", "A", "idle")
        self._cards["current_d"].set_value(f"{current_d:.2f}", "A", "idle")
        self._cards["mos_temperature"].set_value(f"{mos_temp:.1f}", "degC", "warning" if mos_temp > 70.0 else "ok")
        self._cards["coil_temperature"].set_value(f"{coil_temp:.1f}", "degC", "warning" if coil_temp > 70.0 else "ok")
        self._cards["duty"].set_value(f"{duty_a:.2f} / {duty_b:.2f} / {duty_c:.2f}", "phase A/B/C", "idle")
        self._cards["power"].set_value(f"{sample.power:.1f}", "W", "idle")
        self._cards["angle"].set_value(f"{angle:.3f}", "rad", "idle")
        self._cards["encoder"].set_value(f"{encoder:.3f}", "rad", "idle")

    def _send(self, name: str) -> None:
        if self.backend is None:
            return
        payload = {}
        if name == "inject_mock_fault":
            payload = {"code": "ov_tmos", "message": "Dashboard 注入的模拟故障"}
        self.backend.send_command(MotorCommand(name=name, payload=payload))

    def _set_speed(self) -> None:
        if self.backend is None:
            return
        self.backend.send_command(
            MotorCommand(name="set_speed_target", payload={"mechanical_speed": self.speed_spin.value()})
        )

    @staticmethod
    def _run_state_text(value: str) -> str:
        return {
            "runing": "运行",
            "stop": "停止",
            "fault": "故障",
            "prech": "预充",
        }.get(value, value)
