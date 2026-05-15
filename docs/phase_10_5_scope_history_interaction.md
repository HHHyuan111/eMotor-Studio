# Phase 10.5 Scope History And Interaction Polish

Date: 2026-05-15

## Goal

Make the oscilloscope behave more like a practical debugging tool before hardware bring-up.

## Problem

The previous Scope implementation made the visible time window feel like the available data window. When users zoomed or inspected, it looked like only one short segment of data was valid.

## Changes

- Increased default history cache from 600 points to 6000 points.
- Kept acquisition history separate from the visible time window.
- Kept CSV export based on the full cached history.
- Changed toolbar and context-menu zoom buttons to zoom the current X-axis view instead of rewriting the recent-window setting.
- Status text now shows sampling state, manual/realtime mode, cached point count and visible window width.
- Added a regression test to ensure X-axis zoom does not truncate stored history.

## Boundaries

- No hardware communication changes.
- No SerialBackend PING.
- No MockBackend core logic changes.
- No external source copied.

## Next Non-Hardware Polish Candidates

- Add a compact cursor table showing values for selected channels at the cursor.
- Add configurable channel groups and saved Scope presets.
- Add export session metadata: selected channels, sample rate, view window and notes.
- Add page-level layout consistency pass for command, report and identification pages.
- Add a visual safety review for buttons that will eventually affect real hardware.
