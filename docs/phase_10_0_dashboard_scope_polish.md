# Phase 10.0 Dashboard And Scope Polish

## Goal

Phase 10.0 improves the first two pages users see most often:

- `仪表盘`: quick motor-system judgement;
- `实时波形`: engineering oscilloscope workflow.

The goal is to move from a runnable prototype toward a professional upper-computer layout without entering real hardware communication.

## Dashboard Changes

- Rebuilt the dashboard into three sections:
  - system status;
  - quick safe controls;
  - realtime motor metrics.
- Added compact status cards for connection, run state, system mode, fault word, transport route and refresh rate.
- Added more complete realtime metrics:
  - speed;
  - speed target;
  - bus voltage/current;
  - d/q current;
  - MOS/coil temperature;
  - PWM duty;
  - power;
  - electrical and encoder angle.
- Reduced visual noise and made quick controls secondary to state judgement.

## Scope Changes

- Added channel presets:
  - 默认;
  - 电流环;
  - 速度环;
  - 角度/位置;
  - 温度/保护;
  - PWM.
- Added signal search.
- Added visible-channel select all / clear selection.
- Reduced curve palette saturation for better oscilloscope readability.
- Kept manual inspection behavior:
  - pause;
  - drag history;
  - mouse-wheel horizontal zoom;
  - Chinese right-click menu;
  - cursor readout.

## Boundaries

- No MockBackend core logic changed.
- No SerialBackend PING.
- No hardware protocol.
- No AxDr_L firmware changes.
- No real parameter write-back.

## Next Recommended Work

Next page-level pass should focus on `参数配置` and `三环调参`:

- Parameter page should support search, group filter and selected-parameter detail panel more cleanly.
- Three-loop tuning should move toward a wizard-like workflow: identify -> suggest -> validate -> export session.
