# Phase 10.6 Scope Professionalization

Date: 2026-05-15

## Goal

Improve Scope from a basic live plot into a more useful motor-debugging oscilloscope.

## Changes

- Added a measurement panel beside the custom-channel plot.
- Added A/B cursor markers.
- Added cursor delta time display.
- Added a selected-channel measurement table:
  - channel name;
  - value at cursor A;
  - difference from cursor A to cursor B.
- Added "export current view" CSV support.
- Added right-click actions for:
  - export current view;
  - set current cursor as A;
  - set current cursor as B.
- Added tests for cursor measurement and view-window export.

## Boundaries

- No hardware communication.
- No SerialBackend PING.
- No MockBackend core logic change.
- No external source copied.

## Next Scope Candidates

- Persistent user presets for selected channels.
- Dual-axis or per-group scaling for signals with different magnitudes.
- Cursor statistics for visible window: min, max, mean, RMS.
- Trigger markers for commands, faults and experiment phases.
- Screenshot/PNG export of the current plot.
