"""Dashboard page."""

from __future__ import annotations

from PySide6 import QtWidgets

from emotor_studio.models import MotorCommand, TelemetrySample


def _signal(sample: TelemetrySample, name: str, fallback: object = "--") -> object:
    return sample.signals.get(name, fallback)


class DashboardPage(QtWidgets.QWidget):
    def __init__(self, backend=None, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.backend = backend
        root = QtWidgets.QVBoxLayout(self)
        control_row = QtWidgets.QHBoxLayout()
        for label, command in [
            ("Enable", "motor_enable"),
            ("Stop", "motor_stop"),
            ("Clear Fault", "clear_fault"),
            ("Inject Fault", "inject_mock_fault"),
        ]:
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(lambda _checked=False, name=command: self._send(name))
            control_row.addWidget(button)
        self.speed_spin = QtWidgets.QDoubleSpinBox()
        self.speed_spin.setRange(-900.0, 900.0)
        self.speed_spin.setValue(125.0)
        self.speed_spin.setSuffix(" rad/s")
        speed_button = QtWidgets.QPushButton("Set Speed")
        speed_button.clicked.connect(self._set_speed)
        control_row.addWidget(self.speed_spin)
        control_row.addWidget(speed_button)
        control_row.addStretch(1)
        root.addLayout(control_row)

        layout = QtWidgets.QGridLayout()
        root.addLayout(layout)
        self._labels: dict[str, QtWidgets.QLabel] = {}
        metrics = [
            ("run_state", "Run State"),
            ("system_mode", "System Mode"),
            ("speed", "Mechanical Speed"),
            ("speed_target", "Speed Target"),
            ("bus_voltage", "Bus Voltage"),
            ("bus_current", "Bus Current"),
            ("current_q", "Iq Feedback"),
            ("current_d", "Id Feedback"),
            ("electrical_angle", "Electrical Angle"),
            ("encoder_angle", "Encoder Angle"),
            ("duty", "PWM Duty"),
            ("temperature", "Temperature"),
            ("fault_word", "Fault Word"),
            ("faults", "Faults"),
        ]
        for index, (key, title) in enumerate(metrics):
            box = QtWidgets.QGroupBox(title)
            box_layout = QtWidgets.QVBoxLayout(box)
            value = QtWidgets.QLabel("--")
            value.setObjectName("metricValue")
            value.setMinimumHeight(32)
            box_layout.addWidget(value)
            self._labels[key] = value
            layout.addWidget(box, index // 2, index % 2)
        layout.setRowStretch(7, 1)

    def update_telemetry(self, sample: TelemetrySample) -> None:
        mechanical_speed = float(_signal(sample, "mechanical_speed", 0.0))
        target_speed = float(_signal(sample, "speed_target_mechanical", 0.0))
        self._labels["run_state"].setText(str(_signal(sample, "run_state", sample.run_state.value)))
        self._labels["system_mode"].setText(str(_signal(sample, "system_mode", sample.system_mode.value)))
        self._labels["speed"].setText(f"{mechanical_speed:.1f} rad/s  ({sample.rpm:,.0f} rpm)")
        self._labels["speed_target"].setText(f"{target_speed:.1f} rad/s  ({sample.target_rpm:,.0f} rpm)")
        self._labels["bus_voltage"].setText(f"{float(_signal(sample, 'bus_voltage', 0.0)):.1f} V")
        self._labels["bus_current"].setText(f"{float(_signal(sample, 'bus_current', 0.0)):.2f} A")
        self._labels["current_q"].setText(f"{float(_signal(sample, 'current_q', 0.0)):.2f} A")
        self._labels["current_d"].setText(f"{float(_signal(sample, 'current_d', 0.0)):.2f} A")
        self._labels["electrical_angle"].setText(f"{float(_signal(sample, 'electrical_angle', 0.0)):.3f} rad")
        self._labels["encoder_angle"].setText(f"{float(_signal(sample, 'encoder_angle', 0.0)):.3f} rad")
        self._labels["duty"].setText(
            f"A {float(_signal(sample, 'duty_a', 0.0)):.2f} / "
            f"B {float(_signal(sample, 'duty_b', 0.0)):.2f} / "
            f"C {float(_signal(sample, 'duty_c', 0.0)):.2f}"
        )
        self._labels["temperature"].setText(
            f"MOS {float(_signal(sample, 'mos_temperature', 0.0)):.1f} degC / "
            f"Coil {float(_signal(sample, 'coil_temperature', 0.0)):.1f} degC"
        )
        self._labels["fault_word"].setText(f"0x{sample.fault_word:08X}")
        self._labels["faults"].setText(", ".join(sample.faults) if sample.faults else "None")

    def _send(self, name: str) -> None:
        if self.backend is None:
            return
        payload = {}
        if name == "inject_mock_fault":
            payload = {"code": "ov_tmos", "message": "Injected from Dashboard"}
        self.backend.send_command(MotorCommand(name=name, payload=payload))

    def _set_speed(self) -> None:
        if self.backend is None:
            return
        self.backend.send_command(
            MotorCommand(name="set_speed_target", payload={"mechanical_speed": self.speed_spin.value()})
        )
