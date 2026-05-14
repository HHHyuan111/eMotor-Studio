"""Mock experiment generation and analysis services."""

from __future__ import annotations

import csv
from pathlib import Path
from math import atan2, exp, pi, sin
from statistics import mean
from io import StringIO

from emotor_studio.models import (
    ExperimentResult,
    ExperimentTask,
    ExperimentTrace,
    StepResponseMetrics,
)


class CurrentLoopStepExperiment:
    """Generate and analyze a Mock q-axis current step response.

    The service is intentionally independent from Qt and backend transport so
    it can later consume real telemetry without rewriting the analysis path.
    """

    def __init__(
        self,
        target_current_a: float = 5.0,
        duration_s: float = 0.5,
        sample_rate_hz: float = 2000.0,
        natural_frequency_hz: float = 42.0,
        damping_ratio: float = 0.72,
        noise_a: float = 0.015,
    ) -> None:
        self.task = ExperimentTask(
            name="mock_current_loop_step",
            title="Mock q轴电流环阶跃响应",
            target="current_q",
            duration_s=duration_s,
            sample_rate_hz=sample_rate_hz,
            parameters={
                "target_current_a": target_current_a,
                "natural_frequency_hz": natural_frequency_hz,
                "damping_ratio": damping_ratio,
                "noise_a": noise_a,
            },
        )

    def run(self) -> ExperimentResult:
        target_current = float(self.task.parameters["target_current_a"])
        natural_frequency = float(self.task.parameters["natural_frequency_hz"])
        damping = float(self.task.parameters["damping_ratio"])
        noise = float(self.task.parameters["noise_a"])
        sample_count = max(2, int(self.task.duration_s * self.task.sample_rate_hz))
        dt = 1.0 / self.task.sample_rate_hz
        omega_n = 2.0 * pi * natural_frequency
        omega_d = omega_n * max(0.0, 1.0 - damping * damping) ** 0.5

        times: list[float] = []
        targets: list[float] = []
        response: list[float] = []
        for index in range(sample_count):
            t = index * dt
            command = target_current if t >= 0.02 else 0.0
            if t < 0.02:
                y = 0.0
            else:
                tau = t - 0.02
                if omega_d > 0.0:
                    envelope = exp(-damping * omega_n * tau)
                    phase_term = sin(omega_d * tau + atan2((1.0 - damping * damping) ** 0.5, damping))
                    y = target_current * (1.0 - envelope / max((1.0 - damping * damping) ** 0.5, 1e-9) * phase_term)
                else:
                    y = target_current * (1.0 - exp(-omega_n * tau))
            y += noise * sin(index * 0.47) + noise * 0.4 * sin(index * 0.071)
            times.append(t)
            targets.append(command)
            response.append(y)

        trace = ExperimentTrace(
            time_s=tuple(times),
            target=tuple(targets),
            response=tuple(response),
            unit="A",
        )
        metrics = analyze_step_response(trace)
        summary = _summary(metrics)
        return ExperimentResult(task=self.task, trace=trace, metrics=metrics, summary=summary)


def analyze_step_response(trace: ExperimentTrace, tolerance: float = 0.02) -> StepResponseMetrics:
    if not trace.time_s or len(trace.time_s) != len(trace.response) or len(trace.target) != len(trace.response):
        raise ValueError("Trace time, target, and response arrays must be non-empty and equal length.")

    target_value = _final_target(trace.target)
    initial_value = trace.response[0]
    final_window = max(1, min(len(trace.response), int(len(trace.response) * 0.1)))
    final_value = mean(trace.response[-final_window:])
    amplitude = target_value - initial_value
    abs_amplitude = abs(amplitude)
    if abs_amplitude < 1e-12:
        return StepResponseMetrics(initial_value, final_value, target_value, None, None, 0.0, final_value - target_value)

    lower = initial_value + 0.1 * amplitude
    upper = initial_value + 0.9 * amplitude
    rise_start = _first_crossing(trace.time_s, trace.response, lower, amplitude)
    rise_end = _first_crossing(trace.time_s, trace.response, upper, amplitude)
    rise_time = None if rise_start is None or rise_end is None else max(0.0, rise_end - rise_start)

    peak = max(trace.response) if amplitude >= 0 else min(trace.response)
    overshoot = max(0.0, (peak - target_value) / abs_amplitude * 100.0) if amplitude >= 0 else max(0.0, (target_value - peak) / abs_amplitude * 100.0)
    band = max(abs_amplitude * tolerance, 1e-9)
    settling_time = _settling_time(trace.time_s, trace.response, target_value, band)
    steady_state_error = final_value - target_value

    return StepResponseMetrics(
        initial_value=initial_value,
        final_value=final_value,
        target_value=target_value,
        rise_time_s=rise_time,
        settling_time_s=settling_time,
        overshoot_percent=overshoot,
        steady_state_error=steady_state_error,
    )


def build_experiment_report(result: ExperimentResult) -> str:
    metrics = result.metrics
    rise = _format_optional(metrics.rise_time_s, "s")
    settling = _format_optional(metrics.settling_time_s, "s")
    return "\n".join(
        [
            f"# {result.task.title}",
            "",
            "## 实验配置",
            "",
            f"- Task: `{result.task.name}`",
            f"- Target signal: `{result.task.target}`",
            f"- Duration: {result.task.duration_s:.3f} s",
            f"- Sample rate: {result.task.sample_rate_hz:.1f} Hz",
            f"- Parameters: {result.task.parameters}",
            "",
            "## 阶跃响应指标",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Target | {metrics.target_value:.4g} {result.trace.unit} |",
            f"| Final value | {metrics.final_value:.4g} {result.trace.unit} |",
            f"| Rise time | {rise} |",
            f"| Settling time | {settling} |",
            f"| Overshoot | {metrics.overshoot_percent:.2f} % |",
            f"| Steady-state error | {metrics.steady_state_error:.4g} {result.trace.unit} |",
            "",
            "## 结论",
            "",
            f"- {result.summary}",
            "",
        ]
    )


def build_experiment_csv(result: ExperimentResult) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["time_s", "target", "response", "unit"])
    for time_s, target, response in zip(result.trace.time_s, result.trace.target, result.trace.response):
        writer.writerow([f"{time_s:.9g}", f"{target:.9g}", f"{response:.9g}", result.trace.unit])
    return buffer.getvalue()


def save_experiment_artifacts(result: ExperimentResult, directory: str | Path) -> dict[str, Path]:
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{result.task.name}_{int(result.generated_at)}"
    csv_path = output_dir / f"{stem}.csv"
    report_path = output_dir / f"{stem}.md"
    csv_path.write_text(build_experiment_csv(result), encoding="utf-8")
    report_path.write_text(build_experiment_report(result), encoding="utf-8")
    return {"csv": csv_path, "report": report_path}


def _first_crossing(
    times: tuple[float, ...],
    values: tuple[float, ...],
    threshold: float,
    amplitude: float,
) -> float | None:
    for time_s, value in zip(times, values):
        if amplitude >= 0 and value >= threshold:
            return time_s
        if amplitude < 0 and value <= threshold:
            return time_s
    return None


def _settling_time(times: tuple[float, ...], values: tuple[float, ...], target: float, band: float) -> float | None:
    for index, time_s in enumerate(times):
        if all(abs(value - target) <= band for value in values[index:]):
            return time_s
    return None


def _final_target(targets: tuple[float, ...]) -> float:
    non_zero = [value for value in targets if abs(value) > 1e-12]
    return non_zero[-1] if non_zero else targets[-1]


def _summary(metrics: StepResponseMetrics) -> str:
    if metrics.settling_time_s is None:
        return "响应尚未进入 2% 稳态带，建议延长实验时间或降低环路带宽假设。"
    if metrics.overshoot_percent > 20.0:
        return "超调较大，后续可降低 Kp 或提高阻尼/滤波配置。"
    if abs(metrics.steady_state_error) > abs(metrics.target_value) * 0.05:
        return "稳态误差偏大，后续可检查积分增益、限幅和采样偏置。"
    return "Mock 电流环响应稳定，可作为后续真实硬件阶跃实验的 UI 与分析模板。"


def _format_optional(value: float | None, unit: str) -> str:
    return "--" if value is None else f"{value:.4g} {unit}"
