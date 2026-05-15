# Phase 10.4 Unified Workbench Layout

Date: 2026-05-15

## Goal

Make the workbench feel less like a set of independent prototype pages and more like one coherent motor-control application.

## Changes

- Removed the secondary global toolbar. The top area now only shows status chips.
- Reduced left navigation to high-frequency workbench pages.
- Added a `SystemToolsPage` to collect low-frequency tools:
  - FOC configuration
  - application settings
  - firmware information
  - terminal/debug console
- Kept low-frequency tool pages instantiated in code, but no longer exposed every one as a left-navigation top-level item.
- Reworked Scope interaction:
  - mouse wheel zooms the X axis around the cursor;
  - left drag pans the X axis in pause/manual mode;
  - double click restores recent window;
  - fixed signal tabs and custom channel tab share the same X-axis range behavior.

## Boundaries

- No real hardware communication.
- No SerialBackend PING.
- No protocol changes.
- No MockBackend core changes.
- No VESC source, UI XML, icon, logo or asset copied.

## Acceptance

- Main window opens in Mock mode.
- Navigation remains functional.
- Scope can still build channels, presets and export data.
- Tests, GUI smoke and review script pass.
