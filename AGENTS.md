# AGENTS.md

This file defines working rules for agents contributing to eMotor-Studio.

## Project Goal

eMotor-Studio is a long-lived Python + PySide6 + pyqtgraph motor-control
debugging upper-computer application. It is not a one-off demo. The codebase
should remain suitable for teaching, engineering debugging, hardware tutorials,
AI fault diagnosis, and a future motor-control knowledge base.

## Execution Rules

- Keep the project runnable after each phase.
- Prefer small, verifiable increments over large untested rewrites.
- Use MockBackend first when hardware behavior is not yet defined.
- Keep UI pages decoupled from hardware transport details.
- Route backend updates into Qt UI code through signal/slot boundaries.
- Record copied or strongly derived code in the reference-analysis documents or
  a future `docs/code_provenance.md`.

## Branch Naming

Recommended phase branches:

- `phase-0-project-foundation`
- `phase-1-reference-analysis`
- `phase-2-app-skeleton`
- `phase-3-mock-dashboard`
- `phase-4-scope-parameter-command`
- `phase-5-fault-logger-report`
- `phase-6-dev-quality`

## Testing

- Run `python -m pytest` before handing off code changes.
- For GUI changes, also run `python -m emotor_studio` after dependencies are
  installed.
- Tests should cover backend behavior and data-model contracts before hardware
  integration is added.

## Reference Code Policy

The current repository is in private-prototype mode. Direct reuse from local
reference projects is allowed when it improves stability and speed, but:

- Keep source attribution.
- Avoid mixing incompatible modules unless the resulting license obligations are
  understood.
- Before public release, course distribution, or commercial use, complete a
  license cleanup pass.
- Treat GPL and no-license projects as high-risk sources that may need
  replacement before distribution.
