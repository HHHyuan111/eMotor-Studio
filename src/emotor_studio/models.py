"""Shared data models for eMotor-Studio."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any


class MotorMode(str, Enum):
    IDLE = "idle"
    SPEED = "speed"
    CURRENT = "current"
    FAULT = "fault"


class AxdrControlState(str, Enum):
    RESET = "reset"
    START = "start"
    OPERA = "opera"


class AxdrRunState(str, Enum):
    STOP = "stop"
    PRECHARGE = "prech"
    RUNNING = "runing"
    FAULT = "fault"


class AxdrSystemMode(str, Enum):
    DEBUG = "debug_mode"
    RELEASE = "release_mode"
    CALIBRATION = "calibrat_mode"
    HALT = "halt_mode"


class FaultLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TelemetrySample:
    timestamp: float
    rpm: float
    target_rpm: float
    bus_voltage: float
    phase_current: float
    iq: float
    id: float
    temperature: float
    power: float
    mode: MotorMode
    faults: tuple[str, ...] = field(default_factory=tuple)
    signals: dict[str, float | int | str | bool] = field(default_factory=dict)
    control_state: AxdrControlState = AxdrControlState.RESET
    run_state: AxdrRunState = AxdrRunState.STOP
    system_mode: AxdrSystemMode = AxdrSystemMode.RELEASE
    release_mode: str = "vel_mode"
    fault_word: int = 0


@dataclass(frozen=True)
class ParameterItem:
    key: str
    name: str
    value: float | int | str | bool
    unit: str = ""
    min_value: float | None = None
    max_value: float | None = None
    readonly: bool = False
    description: str = ""
    group: str = "General"


@dataclass(frozen=True)
class FaultEvent:
    timestamp: float
    code: str
    level: FaultLevel
    message: str
    active: bool = True


@dataclass(frozen=True)
class MotorCommand:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)
