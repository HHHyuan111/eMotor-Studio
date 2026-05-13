import pytest

from emotor_studio.backend import (
    ProtocolNotImplementedError,
    SerialBackend,
    SerialConnectionSettings,
)
from emotor_studio.models import MotorCommand


def test_serial_backend_loads_shared_schemas() -> None:
    backend = SerialBackend(SerialConnectionSettings(port="COM_TEST"))

    assert any(signal["name"] == "mechanical_speed" for signal in backend.read_signal_schema())
    assert any(command["name"] == "motor_enable" for command in backend.read_command_schema())
    assert any(fault["code"] == "ov_tmos" for fault in backend.read_fault_schema())
    assert any(parameter.key == "motor_phase_resistance" for parameter in backend.read_parameters())


def test_serial_backend_state_transitions_without_hardware_io() -> None:
    backend = SerialBackend(SerialConnectionSettings(port="COM_TEST"))

    backend.connect()
    backend.start()
    backend.stop()
    backend.disconnect()

    assert backend.connected is False
    assert backend.running is False


def test_serial_backend_wire_operations_are_explicit_todos() -> None:
    backend = SerialBackend(SerialConnectionSettings(port="COM_TEST"))
    command = MotorCommand(name="motor_enable")

    with pytest.raises(ProtocolNotImplementedError):
        backend.send_command(command)
    with pytest.raises(ProtocolNotImplementedError):
        backend.write_parameter("position_kp", 2.0)
    with pytest.raises(ProtocolNotImplementedError):
        backend.build_command_frame(command)
    with pytest.raises(ProtocolNotImplementedError):
        backend.parse_telemetry_frame(b"")

    assert backend.command_history[-1] is command
