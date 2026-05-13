import pytest

from emotor_studio.backend import MockBackend
from emotor_studio.config import load_commands, load_fault_codes, load_parameters, load_signals
from emotor_studio.models import AxdrRunState, MotorCommand, MotorMode


def test_mock_backend_generates_telemetry() -> None:
    backend = MockBackend(seed=1)
    backend.connect()
    backend.start()

    sample = backend.tick(0.05)

    assert backend.connected is True
    assert backend.running is True
    assert sample.mode is MotorMode.SPEED
    assert sample.run_state is AxdrRunState.RUNNING
    assert sample.bus_voltage > 0
    assert sample.phase_current >= 0
    assert sample.signals["bus_voltage"] == sample.bus_voltage
    assert "mechanical_speed" in sample.signals
    assert "fault_word" in sample.signals


def test_mock_backend_accepts_target_command() -> None:
    backend = MockBackend()
    backend.send_command(MotorCommand(name="set_speed_target", payload={"mechanical_speed": 150.0}))

    assert backend.target_mechanical_speed == 150.0
    assert backend.command_history[-1].name == "set_speed_target"


def test_mock_backend_accepts_current_and_position_commands() -> None:
    backend = MockBackend()

    backend.send_command(MotorCommand(name="set_current_target", payload={"id_set": 0.25, "iq_set": 1.5}))
    backend.send_command(MotorCommand(name="set_position_target", payload={"mechanical_position": 2.0}))
    parameters = {item.key: item for item in backend.read_parameters()}

    assert parameters["current_target_d"].value == 0.25
    assert parameters["current_target_q"].value == 1.5
    assert parameters["position_target_mechanical"].value == 2.0


def test_mock_backend_parameter_write_validates_range() -> None:
    backend = MockBackend()

    updated = backend.write_parameter("position_kp", 1.25)

    assert updated.value == 1.25
    with pytest.raises(ValueError):
        backend.write_parameter("position_kp", -1.0)


def test_mock_backend_fault_injection() -> None:
    backend = MockBackend()
    fault = backend.inject_fault(code="ov_tmos")
    sample = backend.tick()

    assert fault.code == "ov_tmos"
    assert sample.mode is MotorMode.FAULT
    assert "ov_tmos" in sample.faults
    assert sample.fault_word == 0x08


def test_axdr_l_configs_load() -> None:
    signals = load_signals()
    parameters = load_parameters()
    faults = load_fault_codes()
    commands = load_commands()

    assert any(signal["name"] == "current_q" for signal in signals)
    assert any(parameter["name"] == "motor_phase_resistance" for parameter in parameters)
    assert any(fault["code"] == "ov_tmos" for fault in faults)
    assert any(command["name"] == "motor_enable" for command in commands)


def test_backend_exposes_phase4_schemas() -> None:
    backend = MockBackend()

    assert any(signal["name"] == "mechanical_speed" for signal in backend.read_signal_schema())
    assert any(command["name"] == "set_speed_target" for command in backend.read_command_schema())
    assert any(fault["code"] == "ov_tmos" for fault in backend.read_fault_schema())
