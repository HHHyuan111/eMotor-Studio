"""Mock backend for developing eMotor-Studio without hardware."""

from __future__ import annotations

import math
import random
from time import monotonic, time
from typing import Any, Callable

from emotor_studio.backend.interfaces import BackendInterface
from emotor_studio.config import load_commands, load_fault_codes, load_parameters, load_signals
from emotor_studio.models import (
    AxdrControlState,
    AxdrRunState,
    AxdrSystemMode,
    FaultEvent,
    FaultLevel,
    MotorCommand,
    MotorMode,
    ParameterItem,
    TelemetrySample,
)


TelemetryCallback = Callable[[TelemetrySample], None]
FaultCallback = Callable[[FaultEvent], None]


class MockBackend(BackendInterface):
    """AxDr_L-aligned motor simulation for UI and tests."""

    def __init__(self, seed: int = 7) -> None:
        self.connected = False
        self.running = False
        self.enabled = False
        self.target_mechanical_speed = 125.0
        self.mechanical_speed = 0.0
        self.mechanical_position = 0.0
        self.electrical_angle = 0.0
        self.encoder_angle = 0.0
        self.target_rpm = self._rad_s_to_rpm(self.target_mechanical_speed)
        self.rpm = 0.0
        self.mode = MotorMode.IDLE
        self.control_state = AxdrControlState.RESET
        self.run_state = AxdrRunState.STOP
        self.system_mode = AxdrSystemMode.RELEASE
        self.debug_mode = "curr_cl"
        self.release_mode = "vel_mode"
        self.fault_word = 0
        self._fault_codes = load_fault_codes()
        self._signal_schema = load_signals()
        self._command_schema = load_commands()
        self._fault_by_code = {item["code"]: item for item in self._fault_codes}
        self._rng = random.Random(seed)
        self._started_at = monotonic()
        self._telemetry_callbacks: list[TelemetryCallback] = []
        self._fault_callbacks: list[FaultCallback] = []
        self.command_history: list[MotorCommand] = []
        self.fault_history: list[FaultEvent] = []
        self._parameters = self._load_parameter_items()

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.stop()
        self.connected = False

    def start(self) -> None:
        if not self.connected:
            self.connect()
        self.running = True
        self.enabled = True
        self.mode = MotorMode.SPEED
        self.control_state = AxdrControlState.OPERA
        self.run_state = AxdrRunState.RUNNING

    def stop(self) -> None:
        self.running = False
        self.enabled = False
        self.mode = MotorMode.IDLE
        self.control_state = AxdrControlState.RESET
        self.run_state = AxdrRunState.STOP

    def add_telemetry_callback(self, callback: TelemetryCallback) -> None:
        self._telemetry_callbacks.append(callback)

    def add_fault_callback(self, callback: FaultCallback) -> None:
        self._fault_callbacks.append(callback)

    def send_command(self, command: MotorCommand) -> None:
        self.command_history.append(command)
        if command.name in {"enable", "motor_enable"}:
            self.start()
        elif command.name in {"disable", "motor_stop"}:
            self.stop()
        elif command.name in {"reset_faults", "clear_fault"}:
            self.fault_history = [
                FaultEvent(
                    timestamp=fault.timestamp,
                    code=fault.code,
                    level=fault.level,
                    message=fault.message,
                    active=False,
                )
                for fault in self.fault_history
            ]
            self.fault_word = 0
            if self.mode == MotorMode.FAULT:
                self.mode = MotorMode.SPEED if self.enabled else MotorMode.IDLE
                self.run_state = AxdrRunState.RUNNING if self.enabled else AxdrRunState.STOP
        elif command.name in {"set_target", "set_speed_target"}:
            if "mechanical_speed" in command.payload:
                self.target_mechanical_speed = float(command.payload["mechanical_speed"])
            else:
                self.target_rpm = float(command.payload.get("rpm", self.target_rpm))
                self.target_mechanical_speed = self._rpm_to_rad_s(self.target_rpm)
            self.target_rpm = self._rad_s_to_rpm(self.target_mechanical_speed)
        elif command.name == "set_current_target":
            self._update_parameter_value("current_target_d", command.payload.get("id_set", 0.0))
            self._update_parameter_value("current_target_q", command.payload.get("iq_set", 0.0))
        elif command.name == "set_position_target":
            self._update_parameter_value(
                "position_target_mechanical",
                command.payload.get("mechanical_position", 0.0),
            )
        elif command.name == "set_system_mode":
            self.system_mode = AxdrSystemMode(str(command.payload.get("system_mode", self.system_mode.value)))
        elif command.name == "set_release_mode":
            self.release_mode = str(command.payload.get("release_mode", self.release_mode))
        elif command.name in {"inject_fault", "inject_mock_fault"}:
            self.inject_fault(
                code=str(command.payload.get("code", "ov_tmos")),
                message=str(command.payload.get("message", "Injected mock fault")),
            )

    def read_parameters(self) -> list[ParameterItem]:
        return list(self._parameters.values())

    def write_parameter(self, key: str, value: object) -> ParameterItem:
        if key not in self._parameters:
            raise KeyError(f"Unknown parameter: {key}")
        current = self._parameters[key]
        if current.readonly:
            raise ValueError(f"Parameter is read-only: {key}")
        if isinstance(value, (int, float)):
            numeric_value = float(value)
            if current.min_value is not None and numeric_value < current.min_value:
                raise ValueError(f"{key} below minimum {current.min_value}")
            if current.max_value is not None and numeric_value > current.max_value:
                raise ValueError(f"{key} above maximum {current.max_value}")
        updated = ParameterItem(
            key=current.key,
            name=current.name,
            value=value,
            unit=current.unit,
            min_value=current.min_value,
            max_value=current.max_value,
            readonly=current.readonly,
            description=current.description,
            group=current.group,
        )
        self._parameters[key] = updated
        return updated

    def read_signal_schema(self) -> list[dict[str, Any]]:
        return list(self._signal_schema)

    def read_command_schema(self) -> list[dict[str, Any]]:
        return list(self._command_schema)

    def read_fault_schema(self) -> list[dict[str, Any]]:
        return list(self._fault_codes)

    def tick(self, dt: float = 0.05) -> TelemetrySample:
        """Advance the AxDr_L-style mock motor model and emit telemetry."""

        target_speed = self.target_mechanical_speed if self.enabled and self.running else 0.0
        response = min(max(dt * 4.0, 0.02), 0.5)
        self.mechanical_speed += (target_speed - self.mechanical_speed) * response
        self.mechanical_speed += self._rng.uniform(-0.25, 0.25)
        self.mechanical_position += self.mechanical_speed * dt
        self.encoder_angle = self.mechanical_position % (2.0 * math.pi)
        self.electrical_angle = (self.encoder_angle * 7.0 + 2.34354496) % (2.0 * math.pi)
        self.rpm = self._rad_s_to_rpm(self.mechanical_speed)
        target_rpm = self._rad_s_to_rpm(target_speed)
        elapsed = monotonic() - self._started_at
        load_wave = 0.5 + 0.5 * math.sin(elapsed * 0.9)
        iq = abs(self.mechanical_speed) / 45.0 + load_wave * 0.9
        id_current = math.sin(elapsed * 1.3) * 0.18
        phase_current = math.sqrt(id_current * id_current + iq * iq)
        bus_current = phase_current * 0.55
        bus_voltage = 24.0 + math.sin(elapsed * 0.3) * 0.6
        mos_temperature = 32.0 + abs(self.mechanical_speed) / 14.0 + load_wave * 3.0
        coil_temperature = 30.0 + abs(self.mechanical_speed) / 18.0 + load_wave * 2.6
        power = bus_voltage * bus_current
        duty_center = 0.5 + min(max(self.mechanical_speed / 900.0, -0.35), 0.35)
        duty_a = self._clamp(duty_center + math.sin(self.electrical_angle) * 0.08, 0.02, 0.98)
        duty_b = self._clamp(duty_center + math.sin(self.electrical_angle - 2.094) * 0.08, 0.02, 0.98)
        duty_c = self._clamp(duty_center + math.sin(self.electrical_angle + 2.094) * 0.08, 0.02, 0.98)
        active_faults = tuple(fault.code for fault in self.fault_history if fault.active)
        if active_faults:
            self.mode = MotorMode.FAULT
            self.run_state = AxdrRunState.FAULT
            self.control_state = AxdrControlState.RESET
        elif self.enabled and self.running:
            self.mode = MotorMode.SPEED
            self.run_state = AxdrRunState.RUNNING
            self.control_state = AxdrControlState.OPERA
        else:
            self.mode = MotorMode.IDLE
            self.run_state = AxdrRunState.STOP
            self.control_state = AxdrControlState.RESET
        signals = {
            "bus_voltage": bus_voltage,
            "bus_current": bus_current,
            "phase_current_a": phase_current * 0.97,
            "phase_current_b": phase_current * 0.5,
            "phase_current_c": -phase_current * 0.48,
            "current_d": id_current,
            "current_q": iq,
            "current_abs": phase_current,
            "voltage_d": id_current * 0.35,
            "voltage_q": iq * 0.9,
            "electrical_angle": self.electrical_angle,
            "encoder_angle": self.encoder_angle,
            "mechanical_position_multi": self.mechanical_position,
            "rotor_speed_filtered": self.mechanical_speed,
            "mechanical_speed": self.mechanical_speed,
            "speed_target_mechanical": target_speed,
            "current_target_d": self._parameter_float("current_target_d", 0.0),
            "current_target_q": self._parameter_float("current_target_q", iq),
            "position_target_mechanical": self._parameter_float("position_target_mechanical", 0.0),
            "duty_a": duty_a,
            "duty_b": duty_b,
            "duty_c": duty_c,
            "mos_temperature": mos_temperature,
            "coil_temperature": coil_temperature,
            "control_state": self.control_state.value,
            "run_state": self.run_state.value,
            "system_mode": self.system_mode.value,
            "release_mode": self.release_mode,
            "fault_word": self.fault_word,
        }
        sample = TelemetrySample(
            timestamp=time(),
            rpm=self.rpm,
            target_rpm=target_rpm,
            bus_voltage=bus_voltage,
            phase_current=phase_current,
            iq=iq,
            id=id_current,
            temperature=max(mos_temperature, coil_temperature),
            power=power,
            mode=self.mode,
            faults=active_faults,
            signals=signals,
            control_state=self.control_state,
            run_state=self.run_state,
            system_mode=self.system_mode,
            release_mode=self.release_mode,
            fault_word=self.fault_word,
        )
        for callback in list(self._telemetry_callbacks):
            callback(sample)
        return sample

    def inject_fault(
        self,
        code: str = "ov_tmos",
        message: str = "Mock AxDr_L fault",
        level: FaultLevel = FaultLevel.WARNING,
    ) -> FaultEvent:
        fault_config = self._fault_by_code.get(code)
        if fault_config is not None:
            level = FaultLevel(str(fault_config.get("level", level.value)))
            message = message if message != "Mock AxDr_L fault" else str(fault_config.get("display_name", code))
            self.fault_word |= 1 << int(fault_config["bit"])
        fault = FaultEvent(
            timestamp=time(),
            code=code,
            level=level,
            message=message,
            active=True,
        )
        self.fault_history.append(fault)
        for callback in list(self._fault_callbacks):
            callback(fault)
        return fault

    def _load_parameter_items(self) -> dict[str, ParameterItem]:
        parameters: dict[str, ParameterItem] = {}
        for item in load_parameters():
            parameters[str(item["name"])] = ParameterItem(
                key=str(item["name"]),
                name=str(item["display_name"]),
                value=item.get("default"),
                unit=str(item.get("unit") or ""),
                min_value=item.get("min"),
                max_value=item.get("max"),
                readonly=bool(item.get("readonly", False)),
                description=str(item.get("description") or ""),
                group=str(item.get("group") or "General"),
            )
        parameters.setdefault(
            "current_target_d",
            ParameterItem(key="current_target_d", name="D Current Target", value=0.0, unit="A", group="Command"),
        )
        parameters.setdefault(
            "current_target_q",
            ParameterItem(key="current_target_q", name="Q Current Target", value=0.0, unit="A", group="Command"),
        )
        parameters.setdefault(
            "position_target_mechanical",
            ParameterItem(key="position_target_mechanical", name="Position Target", value=0.0, unit="rad", group="Command"),
        )
        return parameters

    def _update_parameter_value(self, key: str, value: object) -> None:
        current = self._parameters.get(key)
        if current is None:
            self._parameters[key] = ParameterItem(key=key, name=key, value=value)
            return
        self._parameters[key] = ParameterItem(
            key=current.key,
            name=current.name,
            value=value,
            unit=current.unit,
            min_value=current.min_value,
            max_value=current.max_value,
            readonly=current.readonly,
            description=current.description,
            group=current.group,
        )

    def _parameter_float(self, key: str, fallback: float) -> float:
        item = self._parameters.get(key)
        if item is None:
            return fallback
        try:
            return float(item.value)
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _rad_s_to_rpm(value: float) -> float:
        return value * 60.0 / (2.0 * math.pi)

    @staticmethod
    def _rpm_to_rad_s(value: float) -> float:
        return value * (2.0 * math.pi) / 60.0

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))
