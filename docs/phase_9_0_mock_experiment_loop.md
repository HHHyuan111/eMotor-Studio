# Phase 9.0 Mock Experiment Loop

## Goal

Phase 9.0 turns the research and teaching direction into a small runnable loop before real hardware is available:

- define experiment task/result models;
- generate a Mock q-axis current-loop step response;
- compute step-response metrics;
- preview a Markdown report;
- expose the workflow in the 自动分析 page.

This phase does not implement SerialBackend PING, CAN, J-Link RTT, or any real AxDr_L board communication.

## Implemented Pieces

- `ExperimentTask`: describes experiment name, target signal, duration, sample rate, and parameters.
- `ExperimentTrace`: stores time, target, response, and unit.
- `StepResponseMetrics`: stores rise time, settling time, overshoot, final value, target value, and steady-state error.
- `ExperimentResult`: binds task, trace, metrics, summary, and timestamp.
- `CurrentLoopStepExperiment`: generates deterministic Mock current-loop data.
- `analyze_step_response`: computes basic control metrics from trace data.
- `build_experiment_report`: generates Markdown output for later export.
- `ExperimentAnalysisPage`: runs the Mock experiment, displays KPI cards, plots target/response, fills a metrics table, and previews the report.

## Why This Matters

The project goal is not only live control. eMotor-Studio should support teaching, research, and engineering workflows:

- current-loop step-response experiments;
- bandwidth and Bode-analysis preparation;
- paper-friendly CSV/figure/report output;
- future automatic test tasks for AxDr_L hardware.

This phase keeps analysis logic outside Qt widgets so later real telemetry can reuse the same analysis/reporting path.

## Current Limits

- The response is synthetic Mock data, not measured from hardware.
- Bandwidth scan and Bode tabs are still placeholders.
- No CSV/PNG/PDF export is implemented in this phase.
- Safety limits for real current injection are not implemented yet.

## Suggested Next Steps

1. Phase 9.1: add CSV export and PNG plot export for Mock experiments. Completed in `docs/phase_9_1_experiment_export_and_identification_plan.md`.
2. Phase 9.2: add speed-loop step-response Mock workflow.
3. Phase 9.3: draft real hardware experiment safety gates before enabling current injection.
4. Phase 7.1-B or 7.2-A can proceed when the AxDr_L serial protocol is ready.
