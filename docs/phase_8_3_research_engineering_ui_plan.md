# Phase 8.3 Research / Teaching / Engineering UI Iteration

Date: 2026-05-14

## Goal

This iteration shifts eMotor-Studio from a generic VESC-like frame toward a teaching, research, and engineering motor-control workbench for AxDr_L.

The UI should still feel familiar to users who know VESC Tool, but the main value should be local:

- teach current/speed/position loops;
- tune filters and notch filters;
- generate experiment data;
- automatically analyze exported data;
- support motor, electrical-angle, encoder, and observer identification;
- keep Mock mode runnable until hardware is available.

## Reference Direction

Online and local references checked:

- VESC Tool: mature motor-control page grouping, realtime/sample workflow.
- SimpleFOC Studio: teaching-friendly serial monitor and tuning mindset.
- ODrive GUI: parameter/config/debug separation.
- Qt Material / QDarkStyle concepts: restrained Qt theme, compact workbench look.
- pyqtgraph documentation direction: scientific plotting, pan/zoom, frequency-domain plots.

No new dependency was added.

## Navigation Changes

The visible navigation now focuses on actual user workflows:

- 概览 / 连接
- 实时监控
- 环路调参
- 控制命令
- 科研实验
- 工程辨识
- 诊断 / 报告
- 调试工具

Industrial-only or currently unnecessary tools are de-emphasized.

## New Preset Pages

### 三环调参

Reserved windows for:

- d/q current loop PI tuning;
- speed loop PI/FF tuning;
- position loop PID tuning;
- step response;
- bandwidth scan;
- overshoot and settling-time analysis.

### 滤波 / 陷波

Reserved windows for:

- current-sampling low-pass filter;
- speed-estimation filter;
- mechanical resonance notch filter;
- observer/PLL filtering;
- frequency-response preview.

### 实验工作台

Reserved workflows for:

- stall / current-loop experiment;
- speed step experiment;
- sine/chirp/PRBS sweep;
- repeatability experiment;
- CSV/plot/report output.

### 自动分析

Reserved analysis tabs for:

- current-loop bandwidth scan;
- step response;
- Bode plot;
- paper figure export.

### 参数辨识

Reserved workflows for:

- phase resistance / inductance identification;
- flux / torque constant estimation;
- electrical angle / encoder offset identification;
- inertia / friction estimation.

### 观测器

Reserved workflows for:

- encoder vs observer angle comparison;
- low-speed sensorless evaluation;
- PLL tuning;
- observer fault correlation.

## Implementation Boundary

This phase only adds UI structure and placeholders.

Not implemented:

- hardware communication;
- SerialBackend PING;
- real experiment execution;
- real identification algorithms;
- real Bode fitting;
- file import/export beyond existing logger/report paths.

## Next Suggestions

1. Review whether the new navigation matches the product direction.
2. Pick one page to make functional first.
3. Recommended first functional target: `三环调参` + Mock step-response analysis, because it supports teaching, research, and later hardware integration.
