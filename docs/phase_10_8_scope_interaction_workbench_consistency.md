# Phase 10.8 Scope Interaction And Workbench Consistency

## Goal

Continue polishing eMotor-Studio as a VESC-like teaching, research, and engineering motor-control workbench before real hardware integration.

This phase remains Mock-only. It does not implement SerialBackend PING, real telemetry, protocol changes, or AxDr_L firmware changes.

## Scope Improvements

- A/B cursor lines are now draggable.
- Dragged A/B cursors snap to the nearest sampled data point after release.
- A/B cursor state is synchronized across fixed realtime tabs and the custom channel tab.
- The measurement table can highlight the selected channel's curve.
- Right-click menu adds:
  - clear A/B cursors;
  - clear curve highlight.
- Clearing Scope data also clears cursor state and channel highlight state.

## Workbench Consistency Improvements

- Left navigation labels were shortened to reduce repeated wording and make the sidebar feel more like a professional workbench menu.
- The navigation still keeps the same functional coverage:
  - overview and connection;
  - realtime debug;
  - control and tuning;
  - research and identification;
  - diagnostics and reports;
  - system tools.

## Current Boundary

The UI is intentionally moving toward a stable framework first. The next hardware-facing work should still wait until the protocol plan is confirmed and Phase 7.2 starts.

## Validation

- Added regression coverage for dragged cursor snapping.
- Added regression coverage for measurement-row channel highlighting.
- Existing Scope history, current-view export, and fixed-tab measurement tests remain active.

