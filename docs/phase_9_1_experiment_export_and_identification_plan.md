# Phase 9.1 Experiment Export And Identification Plan

## Scope

Phase 9.1 extends the Mock experiment loop from "can analyze" to "can produce research material":

- CSV trace export;
- Markdown report export;
- PNG plot snapshot export from the analysis page;
- a clearer plan for modular parameter-identification workflows.

This phase still does not connect real AxDr_L hardware and does not implement SerialBackend PING.

## Implemented Export Flow

The current 自动分析 page can run a Mock q-axis current step experiment and export:

- `*.csv`: `time_s`, `target`, `response`, `unit`;
- `*.md`: experiment configuration, metrics, and summary;
- `*.png`: current plot snapshot from the UI.

The export functions live in the service layer where possible, while the PNG snapshot remains in the Qt page because it depends on the plot widget.

## Parameter Identification Should Be Modular

The 参数辨识 module should not become one large opaque button. Each parameter family should have its own workflow, signals, plots, fitting method, safety guard, and write-back decision.

Recommended modules:

| Module | Goal | Key Signals To Show | Typical Output |
|---|---|---|---|
| Phase resistance | Estimate Rs | current, voltage, duty, temperature | `phase_resistance` |
| D/Q inductance | Estimate Ld/Lq | Id/Iq, Vd/Vq, current slope | `d_inductance`, `q_inductance` |
| Flux / torque constant | Estimate flux and Kt | speed, voltage, current, bus voltage | `motor_flux`, `torque_constant` |
| Encoder/electrical angle | Find offset and phase order | encoder angle, electrical angle, estimated angle, phase current | `encoder_electrical_offset`, `phase_order` |
| Inertia/friction | Estimate J/B | speed, torque/current, acceleration | `inertia`, `friction` |
| Observer parameters | Tune sensorless observer | estimated angle, encoder angle, speed, observer error | PLL/observer gains |
| Filter/notch | Tune filters | raw signal, filtered signal, FFT/frequency response | cutoff, notch frequency, Q |

## UI Principle

Every identification workflow should show live or recorded variables during identification:

- left side: experiment setup and safety limits;
- center: main waveform/frequency plot;
- right side: fitted parameters and confidence;
- bottom: event log, export buttons, and write-back recommendation.

This makes the tool useful for teaching, research, and engineering because users can see how the parameter was obtained instead of only receiving a final number.

## AxDr_L Algorithm Windows

It is reasonable to eventually map AxDr_L algorithm joints into fixed UI windows:

- current loop;
- speed loop;
- position loop;
- SVPWM/modulation;
- encoder and electrical-angle calibration;
- observer/sensorless estimation;
- protection/fault handling;
- filters/notches;
- parameter-identification routines.

The UI should not let users write arbitrary firmware code directly inside the upper-computer first. A better path is:

1. Define fixed algorithm modules and parameter schemas.
2. Expose safe parameters, signals, and experiment actions in eMotor-Studio.
3. Let advanced users edit firmware in AxDr_L and use eMotor-Studio to validate waveforms, parameters, and reports.
4. Later consider plugin/script hooks for advanced research workflows.

## Next Technical Steps

1. Add reusable `ExperimentArtifact` / export metadata if report handling grows.
2. Add speed-loop step experiment.
3. Add identification page tabs for Rs/Ld/Lq/encoder/observer instead of one placeholder page.
4. Before real current injection, add safety gates: current limit, temperature limit, bus voltage range, emergency stop, and explicit user confirmation.
