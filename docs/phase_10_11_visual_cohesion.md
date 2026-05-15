# Phase 10.11 Visual Cohesion

## Goal

Make the current Mock-only workbench feel more coordinated, calmer, and closer to a polished motor-control engineering application.

This phase only changes visual rhythm and UI presentation. It does not implement hardware communication, SerialBackend PING, protocol changes, or AxDr_L firmware changes.

## Design Direction

- Low-saturation graphite sidebar.
- Mist-white engineering workspace.
- Teal-blue primary action color.
- Softer status colors for ok, idle, warning, and fault states.
- Lighter borders and slightly calmer card geometry.
- Consistent table, tab, button, input, menu, progress, and scrollbar styling.

## Changes

- Refined the global color palette in `ui/theme.py`.
- Added pressed/hover/disabled states for buttons and ghost buttons.
- Added custom horizontal and vertical scrollbar styling.
- Softened table selection, header, tab, menu, and progress bar styles.
- Slightly reduced page minimum width to lower unnecessary horizontal scrolling.
- Slightly reduced sidebar width so the workspace breathes more at smaller window sizes.
- Tightened common component spacing in `PageHeader`, `SectionCard`, `KpiCard`, `StatusChip`, and `InfoBox`.

## Scope Boundary

This phase intentionally avoids page-specific redesign. The goal is visual cohesion across the whole application, not another feature pass.

## Validation

- Page tests remain active.
- Full GUI smoke traverses all 14 main pages and 8 system tool tabs.
- Review script includes pytest and GUI smoke.

