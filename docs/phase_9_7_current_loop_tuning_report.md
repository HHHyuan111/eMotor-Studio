# Phase 9.7 Current Loop Tuning Report

## Goal

Phase 9.7 adds a report-export step to the first closed Mock tuning workflow:

1. run Mock Rs identification;
2. run Mock Ld/Lq identification;
3. generate d/q current-loop PI initial suggestions;
4. validate the q-axis PI suggestion with a Mock current-step response;
5. export a Markdown tuning report.

This makes the workflow closer to a teaching, research, and engineering tool: users can keep a reproducible record of identification inputs, suggested gains, validation metrics, and safety notes before any real hardware write-back exists.

## Implemented

- Added current-loop tuning report builder and file exporter in `src/emotor_studio/services/tuning.py`.
- Exposed report helpers through `src/emotor_studio/services/__init__.py`.
- Added an export button to the three-loop tuning page.
- The UI export path auto-generates PI suggestions and Mock validation if the user has not run them manually.
- Added service and page tests for Markdown report export.

## Report Contents

The exported report includes:

- Mock-only scope statement;
- Rs/Ld/Lq input values;
- d/q PI suggestions;
- Mock step validation metrics;
- hardware safety notes.

## Boundaries

- No real hardware communication was added.
- No SerialBackend PING was added.
- No AxDr_L parameter write-back was added.
- The generated PI values remain suggestions only.

## Acceptance Criteria

- `python -m pytest` passes.
- GUI smoke test passes.
- Review script passes.
- The three-loop tuning page can export a Markdown report into a selected directory.

## Next Recommended Work

Phase 9.8 should add an experiment session layer or report package format so CSV, Markdown, plot snapshots, firmware metadata, config snapshots, and future hardware logs can be exported together.

After that, the next engineering module should be electrical-angle and phase-order identification, because it is a critical bridge between the current-loop workflow and real AxDr_L FOC bring-up.
