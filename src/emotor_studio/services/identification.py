"""Mock parameter-identification services."""

from __future__ import annotations

from math import exp, sin
from statistics import mean

from emotor_studio.models import (
    IdentificationEstimate,
    IdentificationResult,
    IdentificationTask,
    IdentificationTrace,
)


class MockResistanceIdentification:
    """Generate a Mock Rs identification trace and estimate phase resistance."""

    def __init__(
        self,
        injection_voltage_v: float = 1.2,
        true_resistance_ohm: float = 0.185,
        duration_s: float = 0.35,
        sample_rate_hz: float = 2000.0,
        current_limit_a: float = 8.0,
        temperature_limit_deg_c: float = 70.0,
    ) -> None:
        self.task = IdentificationTask(
            name="mock_phase_resistance_identification",
            title="Mock 相电阻 Rs 辨识",
            module="resistance",
            duration_s=duration_s,
            sample_rate_hz=sample_rate_hz,
            signals=("phase_current", "voltage_q", "bus_voltage", "temperature_mos"),
            safety_limits={
                "current_limit_a": current_limit_a,
                "temperature_limit_deg_c": temperature_limit_deg_c,
            },
            parameters={
                "injection_voltage_v": injection_voltage_v,
                "true_resistance_ohm": true_resistance_ohm,
            },
        )

    def run(self) -> IdentificationResult:
        voltage = float(self.task.parameters["injection_voltage_v"])
        true_resistance = float(self.task.parameters["true_resistance_ohm"])
        sample_count = max(2, int(self.task.duration_s * self.task.sample_rate_hz))
        dt = 1.0 / self.task.sample_rate_hz
        tau = 0.018
        steady_current = voltage / true_resistance

        times: list[float] = []
        current: list[float] = []
        voltage_q: list[float] = []
        bus_voltage: list[float] = []
        temperature: list[float] = []
        for index in range(sample_count):
            t = index * dt
            command_voltage = voltage if t >= 0.02 else 0.0
            if t < 0.02:
                measured_current = 0.0
            else:
                measured_current = steady_current * (1.0 - exp(-(t - 0.02) / tau))
            measured_current += 0.015 * sin(index * 0.37) + 0.006 * sin(index * 0.11)
            times.append(t)
            current.append(measured_current)
            voltage_q.append(command_voltage + 0.002 * sin(index * 0.19))
            bus_voltage.append(24.0 + 0.04 * sin(index * 0.02))
            temperature.append(32.0 + 1.2 * (1.0 - exp(-max(0.0, t - 0.02) / 0.25)))

        trace = IdentificationTrace(
            time_s=tuple(times),
            channels={
                "phase_current": tuple(current),
                "voltage_q": tuple(voltage_q),
                "bus_voltage": tuple(bus_voltage),
                "temperature_mos": tuple(temperature),
            },
            units={
                "phase_current": "A",
                "voltage_q": "V",
                "bus_voltage": "V",
                "temperature_mos": "degC",
            },
        )
        estimate = _estimate_resistance(trace)
        confidence = _confidence(estimate, true_resistance)
        summary = (
            f"Mock Rs 辨识完成：估计相电阻 {estimate:.4f} ohm，"
            f"与基准模型偏差 {abs(estimate - true_resistance) / true_resistance * 100.0:.2f}%。"
        )
        return IdentificationResult(
            task=self.task,
            trace=trace,
            estimates=(
                IdentificationEstimate(
                    key="phase_resistance",
                    value=estimate,
                    unit="ohm",
                    confidence=confidence,
                    status="suggested",
                    description="由稳态注入电压 / 电流估计，真实硬件阶段需温度补偿和多次重复验证。",
                ),
                IdentificationEstimate(
                    key="rs_temperature_coeff",
                    value="pending",
                    unit="%/degC",
                    confidence=None,
                    status="reserved",
                    description="需要多温度点实验，本阶段仅预留字段。",
                ),
            ),
            summary=summary,
        )


class MockInductanceIdentification:
    """Generate a Mock Ld/Lq current-slope identification trace."""

    def __init__(
        self,
        voltage_step_v: float = 0.08,
        true_ld_h: float = 0.00021,
        true_lq_h: float = 0.00026,
        duration_s: float = 0.08,
        sample_rate_hz: float = 20000.0,
        current_limit_a: float = 4.0,
        temperature_limit_deg_c: float = 70.0,
    ) -> None:
        self.task = IdentificationTask(
            name="mock_dq_inductance_identification",
            title="Mock d/q 轴电感辨识",
            module="inductance",
            duration_s=duration_s,
            sample_rate_hz=sample_rate_hz,
            signals=("current_d", "current_q", "voltage_d", "voltage_q", "electrical_angle"),
            safety_limits={
                "current_limit_a": current_limit_a,
                "temperature_limit_deg_c": temperature_limit_deg_c,
            },
            parameters={
                "voltage_step_v": voltage_step_v,
                "true_ld_h": true_ld_h,
                "true_lq_h": true_lq_h,
            },
        )

    def run(self) -> IdentificationResult:
        voltage = float(self.task.parameters["voltage_step_v"])
        true_ld = float(self.task.parameters["true_ld_h"])
        true_lq = float(self.task.parameters["true_lq_h"])
        sample_count = max(2, int(self.task.duration_s * self.task.sample_rate_hz))
        dt = 1.0 / self.task.sample_rate_hz
        d_start = 0.01
        q_start = 0.04
        pulse_width = 0.018

        times: list[float] = []
        current_d: list[float] = []
        current_q: list[float] = []
        voltage_d: list[float] = []
        voltage_q: list[float] = []
        electrical_angle: list[float] = []
        id_value = 0.0
        iq_value = 0.0
        for index in range(sample_count):
            t = index * dt
            vd = voltage if d_start <= t < d_start + pulse_width else 0.0
            vq = voltage if q_start <= t < q_start + pulse_width else 0.0
            id_value += (vd / true_ld) * dt
            iq_value += (vq / true_lq) * dt
            id_measured = id_value + 0.002 * sin(index * 0.41)
            iq_measured = iq_value + 0.002 * sin(index * 0.37 + 0.4)
            times.append(t)
            current_d.append(id_measured)
            current_q.append(iq_measured)
            voltage_d.append(vd + 0.0005 * sin(index * 0.17))
            voltage_q.append(vq + 0.0005 * sin(index * 0.13))
            electrical_angle.append(0.8 + 0.015 * sin(index * 0.01))

        trace = IdentificationTrace(
            time_s=tuple(times),
            channels={
                "current_d": tuple(current_d),
                "current_q": tuple(current_q),
                "voltage_d": tuple(voltage_d),
                "voltage_q": tuple(voltage_q),
                "electrical_angle": tuple(electrical_angle),
            },
            units={
                "current_d": "A",
                "current_q": "A",
                "voltage_d": "V",
                "voltage_q": "V",
                "electrical_angle": "rad",
            },
        )
        ld_estimate = _estimate_inductance(trace, "current_d", "voltage_d", d_start, d_start + pulse_width)
        lq_estimate = _estimate_inductance(trace, "current_q", "voltage_q", q_start, q_start + pulse_width)
        ld_confidence = _confidence(ld_estimate, true_ld)
        lq_confidence = _confidence(lq_estimate, true_lq)
        bandwidth_hz = _current_loop_bandwidth_hint(ld_estimate, lq_estimate)
        summary = (
            f"Mock Ld/Lq 辨识完成：Ld={ld_estimate:.6g} H，"
            f"Lq={lq_estimate:.6g} H，建议电流环初始带宽约 {bandwidth_hz:.1f} Hz。"
        )
        return IdentificationResult(
            task=self.task,
            trace=trace,
            estimates=(
                IdentificationEstimate(
                    key="d_inductance",
                    value=ld_estimate,
                    unit="H",
                    confidence=ld_confidence,
                    status="suggested",
                    description="由 d 轴小电压阶跃下的电流斜率估计，真实硬件阶段需补偿 Rs 和采样延迟。",
                ),
                IdentificationEstimate(
                    key="q_inductance",
                    value=lq_estimate,
                    unit="H",
                    confidence=lq_confidence,
                    status="suggested",
                    description="由 q 轴小电压阶跃下的电流斜率估计，真实硬件阶段需补偿 Rs 和采样延迟。",
                ),
                IdentificationEstimate(
                    key="current_loop_initial_bandwidth",
                    value=bandwidth_hz,
                    unit="Hz",
                    confidence=min(ld_confidence, lq_confidence),
                    status="hint",
                    description="用于后续电流环 PI 初值提示，不自动写入。",
                ),
            ),
            summary=summary,
        )


def _estimate_resistance(trace: IdentificationTrace) -> float:
    current = trace.channels["phase_current"]
    voltage = trace.channels["voltage_q"]
    window = max(4, int(len(current) * 0.2))
    steady_current = mean(current[-window:])
    steady_voltage = mean(voltage[-window:])
    if abs(steady_current) < 1e-12:
        raise ValueError("Cannot estimate resistance with near-zero steady current.")
    return steady_voltage / steady_current


def _estimate_inductance(
    trace: IdentificationTrace,
    current_key: str,
    voltage_key: str,
    start_s: float,
    end_s: float,
) -> float:
    times = trace.time_s
    current = trace.channels[current_key]
    voltage = trace.channels[voltage_key]
    start_index = _nearest_index(times, start_s + (end_s - start_s) * 0.2)
    end_index = _nearest_index(times, start_s + (end_s - start_s) * 0.8)
    dt = times[end_index] - times[start_index]
    if dt <= 0.0:
        raise ValueError("Inductance estimation window must have positive duration.")
    di_dt = (current[end_index] - current[start_index]) / dt
    avg_voltage = mean(voltage[start_index:end_index + 1])
    if abs(di_dt) < 1e-12:
        raise ValueError("Cannot estimate inductance with near-zero current slope.")
    return avg_voltage / di_dt


def _nearest_index(values: tuple[float, ...], target: float) -> int:
    return min(range(len(values)), key=lambda index: abs(values[index] - target))


def _current_loop_bandwidth_hint(ld: float, lq: float) -> float:
    average_l = max((abs(ld) + abs(lq)) * 0.5, 1e-9)
    return max(50.0, min(1200.0, 0.08 / average_l / 6.283185307179586))


def _confidence(estimate: float, reference: float) -> float:
    relative_error = abs(estimate - reference) / max(abs(reference), 1e-9)
    return max(0.0, min(1.0, 1.0 - relative_error * 4.0))
