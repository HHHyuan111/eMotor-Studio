# Function Mapping

## Purpose

This document maps reference-project capabilities to eMotor-Studio modules so
future work can be implemented without re-deciding the first architecture.

Phase 2.5 adds AxDr_L as the first target firmware. From Phase 3 onward,
reference-project inspiration remains useful for UX, but runtime signals,
parameters, faults, commands, and backend interfaces should align with AxDr_L
first.

| eMotor Module | Reference Inspiration | First Behavior | Later Expansion |
|---|---|---|---|
| MockBackend | `pid-motor-control` simulation, SimpleFOCStudio live monitor, AxDr_L `pm` object | Generate AxDr_L-style telemetry and accept AxDr_L-style commands | Add serial/CAN/device backends aligned with AxDr_L protocol plan |
| Dashboard | PID tuning GUI metrics, VESC real-time data, AxDr_L `pm.foc`/`pm.state_bit` | Show bus voltage, Id/Iq, speed, target, duty, temperature, mode, faults | Add motor state, power stage, bus health, AI hints |
| Scope | pyqtgraph examples in PID projects, AxDr_L signal mapping | Display channels defined by `configs/signals.json` | Channel presets, pause, export, triggers |
| Parameter | VESC parameter tables, SimpleFOC tuning views, AxDr_L `pm.para`/`pm.protect`/PI structs | Show AxDr_L-derived grouped parameters | Device schemas, validation, read/write transactions |
| Command | SimpleFOC custom commands, PID setpoint controls, AxDr_L state/mode/setpoint model | Enable/stop/clear fault/mode switch/set speed/current/position | Custom command templates and command history |
| Fault | VESC fault workflows, AxDr_L `pmsm_fault_t` | Decode AxDr_L fault bit names | Fault root-cause links and report snippets |
| Logger | VESC log analysis, PID telemetry buffers, AxDr_L telemetry plan | Record configured AxDr_L signal names | CSV export, replay, experiment metadata |
| Report | SimpleFOC code generation and teaching workflows, AxDr_L alignment docs | Placeholder for AxDr_L session report | Markdown/PDF summaries and diagnosis evidence |

## AxDr_L Target Mapping

| eMotor Artifact | AxDr_L Source | Phase 3 Output |
|---|---|---|
| `configs/signals.json` | `docs/axdr_l_signal_mapping.md`, `pm.foc`, `pm.ctrl`, `pm.mode`, `pm.fault` | Dashboard, Scope, Logger signal schema |
| `configs/parameters.json` | `docs/axdr_l_parameter_mapping.md`, `pm.para`, `pm.protect`, PI, encoder, observer, `pm.idpm` | ParameterPage schema |
| `configs/fault_codes.json` | `pmsm_fault_t` in `AxDr_App/User/motor/common.h` | FaultPage decoder and report fault table |
| `configs/commands.json` | `docs/axdr_l_protocol_plan.md`, `pm.ctrl_bit`, `pm.mode`, `pm.ctrl` setpoints | CommandPage templates and MockBackend command handling |
| `BackendInterface` | `docs/axdr_l_protocol_plan.md` | Future SerialBackend/CANBackend contract |

## Data Flow

1. Backend loads AxDr_L-derived config schemas.
2. Backend emits telemetry samples using signal names from `configs/signals.json`.
3. MainWindow receives backend signals.
4. MainWindow updates shared status labels and forwards samples to pages.
5. Pages render samples or submit commands through backend methods.
6. Logger and Report subscribe to the same AxDr_L-aligned event stream.

## First-Milestone Module Boundaries

- UI pages should not parse serial frames.
- Backend should not directly mutate widgets.
- Models should remain plain dataclasses.
- MockBackend should be deterministic enough for tests while still looking live
  during manual GUI runs.
- Real transport code should remain behind BackendInterface.
- Phase 3 must not hard-code generic variables when an AxDr_L mapping exists.
