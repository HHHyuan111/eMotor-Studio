# UI Layout Iteration Notes

Date: 2026-05-14

## Goal

This iteration applies `docs/vesc_core_replication_standard.md` to reduce cramped layout, clipped text, and unstable page sizing.

## Problems Addressed

- Top status and toolbar could squeeze controls when the window was not wide enough.
- Dashboard KPI cards were too large and verbose.
- Parameter table columns were resized by content, causing wide cells and clipped surrounding panels.
- Connection and sampled-data controls were arranged in long rows.
- Bottom quick-control strip consumed too much width.
- Pages did not share a consistent scroll behavior.

## Changes

- Added a reusable scroll container for pages with a stable minimum content width.
- Added horizontal scrolling for the top status bar and global toolbar.
- Reduced default font, button padding, KPI value size, navigation row height and tab padding.
- Reduced bottom command strip height and shortened labels.
- Dashboard now uses compact KPI text and fixed minimum card widths.
- Parameter table uses stable column widths and row resizing instead of aggressive content-width resizing.
- Command, connection and sampled-data control areas now use grid layouts instead of one long row.
- Connection route cards wrap into rows instead of overflowing.
- Sampled-data trigger buttons wrap into two rows.

## Result

The UI remains VESC-like but should behave more like an engineering workbench:

- controls are less likely to overlap;
- text is less likely to be clipped;
- wide pages can scroll instead of collapsing;
- key pages keep a clearer hierarchy.

## Remaining UI Work

- Add icons from a permissive icon set later.
- Add a real responsive breakpoint strategy if the app must support small laptop screens.
- Tune individual table columns after AxDr_L protocol fields are finalized.
- Add screenshots to docs once a stable visual baseline is accepted.
