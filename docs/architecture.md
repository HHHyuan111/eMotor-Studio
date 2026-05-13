# Architecture

## Purpose

eMotor-Studio is a Python + PySide6 + pyqtgraph upper-computer application for motor-control debugging, teaching, logging, reporting, and future AI-assisted diagnosis.

The project is now target-firmware aware. AxDr_L is the first target firmware, so V1.0 remains MockBackend-only, but its data model should mirror AxDr_L control objects.

## Current Layers

| Layer | Current Role | Phase 3+ Direction |
|---|---|---|
| UI pages | Dashboard, Scope, Parameter, Command, Fault, Logger, Report pages | Render config-driven AxDr_L signals, parameters, commands, and faults. |
| MainWindow | Navigation, shared status, sample fan-out | Stay transport-agnostic. |
| Models | Plain dataclasses for telemetry, parameters, faults, commands | Extend only when AxDr_L schema requires it. |
| BackendInterface | Abstract backend behavior | Shared contract for MockBackend and future hardware transports. |
| MockBackend | Current runnable simulator | Become AxDr_L-aligned simulator in Phase 3. |
| SerialBackend | Phase 6 placeholder only | Loads schemas and exposes TODO hooks for the future AxDr_L protocol. |

## Target Firmware: AxDr_L

AxDr_L is analyzed in:

- `docs/axdr_l_analysis.md`
- `docs/axdr_l_signal_mapping.md`
- `docs/axdr_l_parameter_mapping.md`
- `docs/axdr_l_protocol_plan.md`
- `docs/axdr_l_alignment_summary.md`

Local firmware path:

- `external/target_firmware/AxDr_L`

`external/` is ignored and must not be committed.

## AxDr_L Object Model

The primary AxDr_L runtime object is `pm`.

| AxDr_L Object | eMotor-Studio Meaning |
|---|---|
| `pm.foc` | Real-time current, voltage, speed, position, duty, and temperature signals. |
| `pm.ctrl` | Setpoints and control limits. |
| `pm.cmd` | High-level command values in some release modes. |
| `pm.mode` | System/debug/release/calibration/halt mode selection. |
| `pm.ctrl_bit` | Reset/start/operate command state. |
| `pm.state_bit` | Stop/precharge/running/fault runtime state. |
| `pm.para` | Motor constants and offsets. |
| `pm.protect` | Protection thresholds and debounce counters. |
| `pm.fault` | Fault word and bit-level fault state. |

## Planned Config Flow

Phase 3 should create these configs from Phase 2.5 docs:

- `configs/signals.json`
- `configs/parameters.json`
- `configs/fault_codes.json`
- `configs/commands.json`

These configs become the shared contract between MockBackend, UI pages, Logger, Report, and future hardware backends.

## Runtime Data Flow

1. Backend loads config schemas.
2. Backend emits telemetry samples keyed by signal names.
3. MainWindow forwards samples to pages.
4. Dashboard and Scope render configured signals.
5. ParameterPage reads/writes schema-defined parameters through BackendInterface.
6. CommandPage sends schema-defined commands through BackendInterface.
7. FaultPage decodes fault words through `fault_codes.json`.
8. Logger and Report consume the same event stream.

## Backend Direction

V1.0:

- Use MockBackend only.
- Simulate AxDr_L-like variables and state transitions.
- Keep all hardware communication disabled.
- Keep SerialBackend as an interface placeholder that raises explicit protocol TODO errors for command transport, parameter writes, and frame encoding/decoding.

V1.1:

- Add SerialBackend or CAN backend using `docs/axdr_l_protocol_plan.md`.
- Keep UI pages unchanged where possible.
- Implement firmware-side protocol in AxDr_L separately.

## Non-Goals For Phase 2.5

- Do not create formal configs yet.
- Do not copy AxDr_L source code into eMotor-Studio.
- Do not connect real hardware.

## Phase 6 SerialBackend Boundary

`src/emotor_studio/backend/serial_backend.py` is intentionally not a working hardware backend. It exists to freeze the application-side contract before the AxDr_L protocol is implemented in firmware.

Supported in Phase 6:

- Load `configs/signals.json`, `configs/parameters.json`, `configs/fault_codes.json`, and `configs/commands.json`.
- Expose the same schema methods as MockBackend.
- Allow connect/start/stop state transitions for UI wiring tests.
- Keep command history for attempted writes.

Not supported in Phase 6:

- Opening a real serial port.
- Sending bytes to AxDr_L.
- Writing real firmware parameters.
- Encoding or decoding protocol frames.
- Streaming real telemetry.

The unsupported operations raise `ProtocolNotImplementedError` so later V1.1 work has clear insertion points without pretending the hardware path is ready.
