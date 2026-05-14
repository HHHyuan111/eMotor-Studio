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


@dataclass(frozen=True)
class ExperimentTask:
    name: str
    title: str
    target: str
    duration_s: float
    sample_rate_hz: float
    parameters: dict[str, float | int | str | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentTrace:
    time_s: tuple[float, ...]
    target: tuple[float, ...]
    response: tuple[float, ...]
    unit: str = ""


@dataclass(frozen=True)
class StepResponseMetrics:
    initial_value: float
    final_value: float
    target_value: float
    rise_time_s: float | None
    settling_time_s: float | None
    overshoot_percent: float
    steady_state_error: float


@dataclass(frozen=True)
class ExperimentResult:
    task: ExperimentTask
    trace: ExperimentTrace
    metrics: StepResponseMetrics
    summary: str
    generated_at: float = field(default_factory=time)


@dataclass(frozen=True)
class IdentificationTask:
    name: str
    title: str
    module: str
    duration_s: float
    sample_rate_hz: float
    signals: tuple[str, ...]
    safety_limits: dict[str, float | int | str | bool] = field(default_factory=dict)
    parameters: dict[str, float | int | str | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class IdentificationEstimate:
    key: str
    value: float | int | str
    unit: str = ""
    confidence: float | None = None
    status: str = "suggested"
    description: str = ""


@dataclass(frozen=True)
class IdentificationTrace:
    time_s: tuple[float, ...]
    channels: dict[str, tuple[float, ...]]
    units: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class IdentificationResult:
    task: IdentificationTask
    trace: IdentificationTrace
    estimates: tuple[IdentificationEstimate, ...]
    summary: str
    generated_at: float = field(default_factory=time)


@dataclass(frozen=True)
class CurrentLoopPiSuggestion:
    axis: str
    kp: float
    ki: float
    target_bandwidth_hz: float
    resistance_ohm: float
    inductance_h: float
    unit_kp: str = "V/A"
    unit_ki: str = "V/(A*s)"
    note: str = ""
