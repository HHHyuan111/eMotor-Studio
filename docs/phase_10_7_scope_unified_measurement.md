# Phase 10.7 Scope Unified Measurement

## Goal

Make the Scope page behave more like a professional motor-control oscilloscope instead of a custom-channel-only plot.

This phase keeps eMotor-Studio in Mock mode. It does not implement hardware communication, protocol changes, SerialBackend PING, or AxDr_L firmware changes.

## Completed

- Moved the A/B cursor measurement panel out of the custom channel tab into a global Scope side panel.
- Shared hover, A cursor, and B cursor lines across all realtime tabs:
  - 电流
  - 温度
  - 转速
  - FOC
  - 转子位置
  - 自定义通道
- Right-click cursor placement now uses the clicked plot position before opening the Chinese context menu.
- The measurement table now follows the active tab:
  - fixed tabs measure their fixed engineering channels;
  - custom tab measures the selected custom channels.
- Current-view CSV export now follows the active tab's channels.
- Mouse hover readout can update from fixed plots as well as the custom plot.

## Why This Matters

Motor-control tuning often starts from a fixed engineering view: current loop, speed loop, temperature, or rotor angle. Users should not have to rebuild those views in a custom plot just to place A/B cursors or export the visible data window.

This also prepares later research workflows:

- current-loop bandwidth scan;
- speed-loop step response;
- filter and notch comparison;
- electrical-angle identification;
- observer versus encoder analysis.

## Validation

- Added regression coverage for fixed-tab A/B cursor measurement and current-view CSV export.
- Confirmed page tests pass after the Scope measurement changes.

