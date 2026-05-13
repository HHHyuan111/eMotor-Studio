# eMotor-Studio

eMotor-Studio is a Python desktop application for motor-control debugging,
teaching, hardware tutorials, AI-assisted fault diagnosis, and future motor
control knowledge-base workflows.

The first milestone focuses on a stable local prototype:

- Python + PySide6 desktop UI
- pyqtgraph real-time plotting surface
- MockBackend for development without hardware
- Modular pages for Dashboard, Scope, Parameter, Command, Fault, Logger, Report
- Clear documentation for reference-project analysis and code provenance

## Current Status

This repository now has an AxDr_L-aligned V1.0 prototype. The application starts
in Mock mode, loads shared configs for signals/parameters/commands/faults, and
keeps a SerialBackend placeholder for the future firmware protocol. Real
hardware communication is intentionally not implemented yet.

## Quick Start

```powershell
python -m pip install -e ".[dev]"
python -m emotor_studio
```

Run tests:

```powershell
python -m pytest
```

## Planned Modules

- **MockBackend**: simulated telemetry, parameters, commands, and faults.
- **Dashboard**: live motor status, metrics, and connection overview.
- **Scope**: pyqtgraph-based real-time signal plotting.
- **Parameter**: editable motor/control parameter table.
- **Command**: common commands and custom command entry.
- **Fault**: active and historical fault display.
- **Logger**: telemetry/event capture and CSV export.
- **Report**: session report generation for teaching and troubleshooting.

## Backend Strategy

- `MockBackend` is the active V1.0 backend and is used by the GUI by default.
- `SerialBackend` is a Phase 6 interface placeholder. It loads the same configs
  but raises explicit protocol TODO errors for real command transport, parameter
  writes, and frame encode/decode.
- AxDr_L remains the target firmware reference; its source stays under
  `external/` and must not be committed.

## Reference Strategy

The current prototype is private-prototype first. Code from local reference
projects may be reused to speed up validation, but sources must be recorded.
Before any public release, course distribution, or commercial packaging, copied
or derived code must be reviewed for license compatibility and replaced when
needed.

See:

- `docs/project_brief.md`
- `docs/reference_repos.md`
- `docs/reference_analysis.md`
- `docs/function_mapping.md`
- `docs/codex_execution_plan.md`
