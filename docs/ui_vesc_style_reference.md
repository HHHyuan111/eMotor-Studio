# UI Reference Notes: Engineering Workbench Style

## Purpose

Phase 7.0-UI improves eMotor-Studio from a runnable MVP into a more formal motor-control debugging workbench. The goal is to borrow mature organization ideas from motor-controller tools without using their names, logos, icons, trademarks, or source assets.

## Referenced Projects

| Project | Observed UI Idea | eMotor-Studio Use |
|---|---|---|
| VESC Tool | Left-side navigation, connection/status emphasis, rich motor configuration pages, real-time values, fault/config workflows. | Reference only for engineering-tool organization: navigation + status bar + grouped pages. |
| SimpleFOCStudio | Serial-first tuning workflow, parameter controls, live plotting, integrated terminal/monitoring concept. | Reference only for serial-first tuning and monitor workflow. |
| ODrive GUI | Device discovery and per-device control panels behind a backend package. | Reference only for keeping device logic separate from UI pages. |
| Spectral-motor-GUI | Product-specific motor GUI with UART first and CAN planned. | Reference only for UART-first / CAN-later UI messaging. |
| Interactive_PID_Controller | Teaching-oriented PID tuning controls and live plot. | Reference only for clear controls and simple plotting. |
| pid-motor-control | Binary serial protocol plus PyQt dashboard shape. | Reference only for command/telemetry page separation. |

## Direct Copy Status

No source code, UI files, icons, logos, trademarks, or image assets were directly copied from the reference projects in Phase 7.0-UI.

The changes are original PySide6 code in eMotor-Studio and use only general UI organization ideas:

- Dark left navigation.
- Top status bar.
- Grouped engineering pages.
- Dashboard metric cards.
- Scope signal selector and plot area.
- Parameter table.
- Command control panel.
- Fault table and current status.
- Logger and report tool pages.

Details are recorded in `docs/code_provenance.md`.

## eMotor-Studio UI Structure

Current pages:

- 仪表盘
- 实时波形
- 参数配置
- 控制命令
- 故障诊断
- 数据记录
- 调试报告
- 硬件连接

Current style direction:

- Left-side dark navigation.
- Light main workspace.
- Compact status chips.
- Group boxes for engineering panels.
- Tables with consistent row style.
- Status colors for running, idle, fault, and muted states.

## Follow-Up UI Suggestions

- Add icon support later, using a clean icon library rather than VESC assets.
- Add connection selector once SerialBackend PING exists.
- Add persistent user preferences for window size, selected page, and recent serial ports.
- Improve Chinese terminology after real AxDr_L protocol names are finalized.
- Add theme variants only after Phase 7.2 connection flow is stable.

## Phase 7.0-UI-2 Update

The second UI pass introduced a local design system instead of page-by-page styling:

- `src/emotor_studio/ui/theme.py` centralizes colors, typography, spacing, and QSS.
- `src/emotor_studio/ui/components.py` provides PageHeader, SectionCard, KpiCard, StatusChip, and InfoBox.
- Main navigation is grouped by real debugging workflow: realtime monitoring, control/debug, and data/diagnostics.
- Dashboard, Scope, Parameter, Command, Fault, Logger, Report, and Hardware pages now share common section/card patterns.

This remains reference-only. No VESC Tool source code, assets, logos, names, or trademarks were copied.

## Scope Interaction Update

The Scope page now follows the mature interaction model observed in VESC Tool realtime/sample pages:

- realtime follow mode while running;
- manual inspection mode when paused;
- horizontal drag and mouse-wheel zoom for historical data;
- recent-window and full-history fitting;
- Y-axis auto range;
- cursor readout for selected channels.

The implementation uses pyqtgraph in Python. It does not embed QCustomPlot or copy VESC Tool C++ source.

## Phase 8.1 VESC-like Framework Update

This pass studied VESC Tool UI files more directly:

- `mainwindow.ui` / `mainwindow.cpp`
- `pages/pageconnection.ui`
- `pages/pagertdata.ui`
- `pages/pagesampleddata.ui` / `pagesampleddata.cpp`
- `pages/pageterminal.ui`

eMotor-Studio now follows the same high-level framework:

- Menu bar for file, config backup, wizards, terminal, developer and help workflows.
- Global toolbar for reconnect, disconnect, read/write config, realtime data, alive and CAN forwarding placeholders.
- Left navigation plus a CAN/device list and scan button placeholder.
- Bottom quick-control strip for duty, current, speed, position, brake and stop placeholders.
- Connection page with serial, CAN, TCP/debug bridge and J-Link RTT tabs.
- Realtime data page with Current, Temperature, RPM, FOC, Rotor Position and custom-channel tabs.
- Sampled data page with Current, BEMF and Filter/FFT tabs.
- Terminal page with output area, command line and help/send/clear buttons.

The new code remains Python/PySide6 and pyqtgraph. No VESC assets, icons, logos or generated Qt UI files were copied into this repository.

## Phase 8.2 Layout Usability Update

After applying `docs/vesc_core_replication_standard.md`, the UI framework was tightened for daily use:

- page content now sits in a shared scroll container with a stable minimum width;
- top status and global toolbar can scroll horizontally instead of compressing labels;
- KPI cards, tabs, buttons and navigation rows use more compact dimensions;
- dashboard values emphasize short engineering numbers and units;
- parameter table columns use stable widths;
- connection and sampled-data controls wrap through grid layouts.

The intent is to keep a VESC-like workbench shape while avoiding crowded rows and clipped text on common laptop displays.
