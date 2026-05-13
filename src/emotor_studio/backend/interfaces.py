"""Backend contracts used by UI pages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from emotor_studio.models import MotorCommand, ParameterItem


class BackendInterface(ABC):
    """Transport-independent backend contract."""

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_command(self, command: MotorCommand) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_parameters(self) -> list[ParameterItem]:
        raise NotImplementedError

    @abstractmethod
    def write_parameter(self, key: str, value: object) -> ParameterItem:
        raise NotImplementedError

    @abstractmethod
    def read_signal_schema(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def read_command_schema(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def read_fault_schema(self) -> list[dict[str, Any]]:
        raise NotImplementedError
