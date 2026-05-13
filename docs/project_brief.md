# eMotor-Studio Project Brief

## Positioning

eMotor-Studio is a desktop upper-computer tool for motor-control development and
education. The first usable version should help a learner or engineer inspect a
motor controller, tune parameters, send commands, observe faults, record logs,
and generate troubleshooting reports.

## Audience

- Motor-control course students
- Engineers debugging BLDC/PMSM/DC motor systems
- Hardware tutorial authors
- Developers building AI-assisted fault diagnosis workflows
- Future maintainers of a motor-control knowledge base

## Product Principles

- Start with a reliable MockBackend so UI and workflow can evolve without
  hardware.
- Keep transport-specific code out of pages.
- Make telemetry, parameters, faults, and commands explicit data models.
- Prefer clear engineering UI over marketing-style screens.
- Keep the application modular enough for future Serial, CAN, and device-specific
  backends.

## First Milestone

Phase 0-2 delivers:

- Foundational project documentation
- Reference-project analysis
- A runnable PySide6 application skeleton
- Mock telemetry stream
- Dashboard and Scope surfaces
- Placeholder pages for Parameter, Command, Fault, Logger, and Report
- Basic unit tests for models and MockBackend

## Out of Scope for First Milestone

- Real hardware communication
- Firmware flashing
- Full report rendering
- Full logger export workflow
- AI diagnosis implementation
- Installer or release packaging

## Long-Term Modules

- **Dashboard**: quick status and high-priority telemetry.
- **Scope**: real-time signal plotting and channel selection.
- **Parameter**: safe parameter reading, editing, and write-back.
- **Command**: command panel, custom command entry, and command history.
- **Fault**: active faults, history, and reset workflow.
- **Logger**: telemetry/session capture and export.
- **Report**: structured debugging reports for courses and field diagnosis.
