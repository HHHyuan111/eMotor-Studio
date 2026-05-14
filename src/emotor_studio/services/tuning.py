"""Loop-tuning helpers for Mock and future hardware workflows."""

from __future__ import annotations

from math import pi
from pathlib import Path
from time import time

from emotor_studio.models import CurrentLoopPiSuggestion, ExperimentResult
from emotor_studio.services.experiments import CurrentLoopStepExperiment


def suggest_current_loop_pi(
    resistance_ohm: float,
    d_inductance_h: float,
    q_inductance_h: float,
    target_bandwidth_hz: float,
) -> tuple[CurrentLoopPiSuggestion, CurrentLoopPiSuggestion]:
    """Suggest d/q current-loop PI gains from Rs/Ld/Lq and target bandwidth.

    The formula is a conservative first-order plant matching rule:

    Kp = L * wc
    Ki = R * wc

    where wc = 2*pi*bandwidth. Real firmware deployment must still validate
    sampling delay, PWM limits, current sensor offset, voltage saturation and
    stability margins.
    """

    _validate_positive("resistance_ohm", resistance_ohm)
    _validate_positive("d_inductance_h", d_inductance_h)
    _validate_positive("q_inductance_h", q_inductance_h)
    _validate_positive("target_bandwidth_hz", target_bandwidth_hz)

    wc = 2.0 * pi * target_bandwidth_hz
    note = "Mock 初值建议；真实硬件写入前必须经过阶跃/扫频验证和限幅检查。"
    return (
        CurrentLoopPiSuggestion(
            axis="d",
            kp=d_inductance_h * wc,
            ki=resistance_ohm * wc,
            target_bandwidth_hz=target_bandwidth_hz,
            resistance_ohm=resistance_ohm,
            inductance_h=d_inductance_h,
            note=note,
        ),
        CurrentLoopPiSuggestion(
            axis="q",
            kp=q_inductance_h * wc,
            ki=resistance_ohm * wc,
            target_bandwidth_hz=target_bandwidth_hz,
            resistance_ohm=resistance_ohm,
            inductance_h=q_inductance_h,
            note=note,
        ),
    )


def validate_current_loop_pi(
    suggestion: CurrentLoopPiSuggestion,
    target_current_a: float = 5.0,
    duration_s: float = 0.25,
) -> ExperimentResult:
    """Generate a Mock current-step validation for a PI suggestion."""

    _validate_positive("target_current_a", target_current_a)
    _validate_positive("duration_s", duration_s)
    natural_frequency_hz = max(20.0, min(2000.0, suggestion.target_bandwidth_hz))
    damping_ratio = _damping_from_gain_ratio(suggestion)
    return CurrentLoopStepExperiment(
        target_current_a=target_current_a,
        duration_s=duration_s,
        sample_rate_hz=4000.0,
        natural_frequency_hz=natural_frequency_hz,
        damping_ratio=damping_ratio,
        noise_a=0.01,
    ).run()


def build_current_loop_tuning_report(
    suggestions: tuple[CurrentLoopPiSuggestion, CurrentLoopPiSuggestion],
    validation: ExperimentResult,
) -> str:
    """Build a Markdown tuning report from PI suggestions and validation."""

    if len(suggestions) != 2:
        raise ValueError("Current loop tuning report expects d/q suggestions.")
    metrics = validation.metrics
    return "\n".join(
        [
            "# eMotor-Studio Current Loop Tuning Report",
            "",
            "## Scope",
            "",
            "This report is generated from Mock identification and Mock step validation.",
            "It is not a real hardware tuning report and must not be written to AxDr_L without safety checks.",
            "",
            "## Input Identification Values",
            "",
            "| Axis | Rs (ohm) | L (H) | Target Bandwidth (Hz) |",
            "|---|---:|---:|---:|",
            *[
                f"| {item.axis} | {item.resistance_ohm:.6g} | {item.inductance_h:.6g} | {item.target_bandwidth_hz:.3f} |"
                for item in suggestions
            ],
            "",
            "## PI Suggestions",
            "",
            "| Axis | Kp | Ki | Kp Unit | Ki Unit |",
            "|---|---:|---:|---|---|",
            *[
                f"| {item.axis} | {item.kp:.6g} | {item.ki:.6g} | {item.unit_kp} | {item.unit_ki} |"
                for item in suggestions
            ],
            "",
            "## Mock Step Validation",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Rise time | {_format_seconds(metrics.rise_time_s)} |",
            f"| Settling time | {_format_seconds(metrics.settling_time_s)} |",
            f"| Overshoot | {metrics.overshoot_percent:.2f} % |",
            f"| Steady-state error | {metrics.steady_state_error:.6g} {validation.trace.unit} |",
            "",
            "## Safety Notes",
            "",
            "- The current values are suggestions only.",
            "- Real hardware write-back requires protocol support, range checks, safe state checks and manual confirmation.",
            "- After real write-back, validate with current-loop step response and frequency response before enabling higher loops.",
            "",
        ]
    )


def save_current_loop_tuning_report(
    suggestions: tuple[CurrentLoopPiSuggestion, CurrentLoopPiSuggestion],
    validation: ExperimentResult,
    directory: str | Path,
) -> Path:
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"current_loop_tuning_{int(time())}.md"
    path.write_text(build_current_loop_tuning_report(suggestions, validation), encoding="utf-8")
    return path


def _damping_from_gain_ratio(suggestion: CurrentLoopPiSuggestion) -> float:
    ideal_kp = suggestion.inductance_h * 2.0 * pi * suggestion.target_bandwidth_hz
    if ideal_kp <= 0.0:
        return 0.5
    ratio = suggestion.kp / ideal_kp
    return max(0.45, min(1.05, 0.72 + (ratio - 1.0) * 0.2))


def _format_seconds(value: float | None) -> str:
    return "--" if value is None else f"{value:.6g} s"


def _validate_positive(name: str, value: float) -> None:
    if value <= 0.0:
        raise ValueError(f"{name} must be positive.")
