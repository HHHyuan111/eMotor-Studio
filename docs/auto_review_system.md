# Auto Review System

Date: 2026-05-14

## Why We Need It

AI generated code can move quickly, but it can also:

- break architecture boundaries;
- introduce copied code without provenance records;
- damage MockBackend behavior;
- make UI changes that are hard to maintain;
- weaken tests;
- add large or unmaintainable files;
- change protocol assumptions without updating docs.

The review system keeps eMotor-Studio runnable and traceable while we move fast.

## Review Layers

- Git diff review: confirm changed files match task scope.
- Test review: run `python -m pytest`.
- Structure review: check package layout, configs, docs, tests.
- UI smoke review: optionally start the main window offscreen.
- License/provenance review: ensure external reference use is recorded.
- Architecture boundary review: UI pages must not parse hardware frames.
- Documentation sync review: protocol, UI, provenance and README stay aligned.

## Required After Each Codex Task

At minimum run:

- `git status --short`
- `python -m pytest`
- optional GUI smoke
- check forbidden files
- check new external-code reuse has provenance
- check MockBackend was not changed unexpectedly
- check protocol changes have matching docs
- check UI text or structure changes do not break tests

## Suggested Scripts

- `scripts/review_task.ps1`: branch, status, commits, pytest, provenance/docs checks, external tracking checks.
- `scripts/run_tests.ps1`: run pytest.
- `scripts/gui_smoke_test.py`: offscreen Qt main-window startup.
- `scripts/check_provenance.py`: later check changed files against provenance requirements.

## Future GitHub Actions

Later CI can run:

- pytest;
- ruff;
- pyright or mypy;
- pip-audit;
- license checks;
- provenance checks;
- GUI smoke.

## Current Minimum Standard

Before handoff:

1. Run `python -m pytest`.
2. Run `powershell -ExecutionPolicy Bypass -File scripts\review_task.ps1` when scripts are available.
3. Summarize changed files, tests, provenance status and next recommended phase.
