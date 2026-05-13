"""Serial backend placeholder for the future AxDr_L host protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from emotor_studio.backend.interfaces import BackendInterface
from emotor_studio.config import load_commands, load_fault_codes, load_parameters, load_signals
from emotor_studio.models import MotorCommand, ParameterItem


class ProtocolNotImplementedError(NotImplementedError):
    """Raised when a real AxDr_L wire operation is requested before V1.1."""


@dataclass(frozen=True)
class SerialConnectionSettings:
    port: str
    baudrate: int = 115200
    timeout: float = 0.1


class SerialBackend(BackendInterface):
    """Schema-aligned serial backend shell.

    Phase 6 deliberately keeps hardware I/O disabled. The class exists so UI
    pages and tests can target the same BackendInterface that V1.1 will use.
    """

    def __init__(self, settings: SerialConnectionSettings) -> None:
        self.settings = settings
        self.connected = False
        self.running = False
        self.command_history: list[MotorCommand] = []
        self._signal_schema = load_signals()
        self._command_schema = load_commands()
        self._fault_schema = load_fault_codes()
        self._parameters = self._load_parameter_items()

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.running = False
        self.connected = False

    def start(self) -> None:
        if not self.connected:
            self.connect()
        self.running = True

    def stop(self) -> None:
        self.running = False

    def send_command(self, command: MotorCommand) -> None:
        self.command_history.append(command)
        raise ProtocolNotImplementedError(
            "AxDr_L serial command transport is not implemented in Phase 6."
        )

    def read_parameters(self) -> list[ParameterItem]:
        return list(self._parameters.values())

    def write_parameter(self, key: str, value: object) -> ParameterItem:
        if key not in self._parameters:
            raise KeyError(f"Unknown parameter: {key}")
        raise ProtocolNotImplementedError(
            f"AxDr_L serial parameter write is not implemented in Phase 6: {key}={value!r}"
        )

    def read_signal_schema(self) -> list[dict[str, Any]]:
        return list(self._signal_schema)

    def read_command_schema(self) -> list[dict[str, Any]]:
        return list(self._command_schema)

    def read_fault_schema(self) -> list[dict[str, Any]]:
        return list(self._fault_schema)

    def build_command_frame(self, command: MotorCommand) -> bytes:
        """Reserved V1.1 hook for encoding commands after AxDr_L protocol lands."""

        raise ProtocolNotImplementedError(
            f"Frame encoding is waiting for the AxDr_L protocol: {command.name}"
        )

    def parse_telemetry_frame(self, frame: bytes) -> dict[str, object]:
        """Reserved V1.1 hook for decoding firmware telemetry frames."""

        raise ProtocolNotImplementedError(
            f"Telemetry frame decoding is waiting for the AxDr_L protocol: {frame!r}"
        )

    @staticmethod
    def _load_parameter_items() -> dict[str, ParameterItem]:
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
        return parameters
