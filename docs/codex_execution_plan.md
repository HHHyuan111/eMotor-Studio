# eMotor-Studio Phase 0-2 Execution Plan

## Goal

Complete the project foundation, reference analysis, and a runnable Python +
PySide6 + pyqtgraph skeleton.

## Phase 0: Foundation

Create or update:

- `README.md`
- `AGENTS.md`
- `docs/project_brief.md`
- `docs/reference_repos.md`
- `docs/codex_execution_plan.md`

Acceptance:

- The project is described as a long-term motor-control tool, not a one-off demo.
- The private-prototype-first code reuse policy is explicit.

## Phase 1: Reference Analysis

Create:

- `docs/reference_analysis.md`
- `docs/function_mapping.md`

Acceptance:

- Each local reference project is analyzed for reusable ideas and license risk.
- The mapping document guides MockBackend, Dashboard, Scope, Parameter, Command,
  Fault, Logger, and Report.

## Phase 2: Runnable Skeleton

Create:

- `pyproject.toml`
- `src/emotor_studio/`
- `tests/`

Acceptance:

- `python -m emotor_studio` starts the application after dependencies are
  installed.
- The app defaults to Mock mode.
- Dashboard receives live simulated telemetry.
- Scope contains a pyqtgraph plotting area.
- Other pages are present as placeholders.
- `python -m pytest` passes.

## Suggested Next Phases

- Phase 3: Implement MockBackend + Dashboard deeply.
- Phase 4: Implement Scope, Parameter, and Command workflows.
- Phase 5: Implement Fault, Logger, and Report.
- Phase 6: Add quality gates, packaging notes, and hardware backend interface
  refinement.
