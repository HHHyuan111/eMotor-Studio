# AGENTS.md

This file defines working rules for agents contributing to eMotor-Studio.

## Project Goal

eMotor-Studio is now positioned as a domestic VESC-like motor-control development platform for AxDr_L and future self-developed hardware.

It is not a simple serial assistant, not a PySide demo, and not a one-off GUI. The long-term product includes:

- Python/PySide upper-computer application;
- AxDr_L firmware adaptation;
- self-developed motor-control hardware support;
- Chinese engineering debugging workflow;
- realtime plots, sampled data, parameters, commands and faults;
- logging and reports;
- AI-assisted debugging;
- course/tutorial ecosystem.

## Execution Rules

- Keep the project runnable after each task.
- Prefer small, verifiable increments.
- Use MockBackend first when hardware behavior is not implemented.
- Never break MockBackend behavior without explicit request.
- Keep UI pages decoupled from hardware transport.
- Do not parse serial/CAN frames inside UI pages.
- Route backend updates into Qt UI code through signal/slot boundaries.
- Keep configs, models, backend interfaces and docs aligned.

## Reference Code Policy

The current repository is in private-prototype mode.

Reference or reuse from local `reference_projects` is allowed when it helps speed, stability, UI maturity, or protocol design. However:

- Every copied, adapted, or strongly derived implementation must be recorded in `docs/code_provenance.md`.
- Record source project, source path, source license, reuse type, target file, scope, purpose, risk and future action.
- GPL and no-license projects are allowed for private prototype exploration, but are high risk before public release.
- MIT/BSD/Apache sources are easier to keep, but attribution still matters.
- Before public release, course distribution, or commercial packaging, complete a license cleanup pass.

## Review Rules

After every coding task, run:

```powershell
python -m pytest
```

Prefer also running:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\review_task.ps1
```

For GUI changes, run:

```powershell
python scripts\gui_smoke_test.py
```

## Forbidden Unless Explicitly Requested

- Implementing real hardware communication before the relevant phase.
- Implementing SerialBackend PING outside Phase 7.2.
- Modifying AxDr_L firmware from this repository.
- Tracking `external/` or `reference_projects/` in git.
- Directly copying external code without provenance.
- Coupling UI logic to hardware transport.
- Lowering test quality to make tests pass.

## Required Handoff Summary

Every completed task should report:

- changed files;
- added files;
- test result;
- GUI smoke result when applicable;
- provenance status;
- whether Mock mode still works;
- whether communication logic changed;
- recommended next phase.
