# eMotor-Studio

eMotor-Studio is a domestic VESC-like motor-control development platform for AxDr_L and future self-developed hardware.

It is not a simple serial assistant and not a PySide demo. The long-term goal is a Chinese motor-control toolchain entry point: upper-computer app, AxDr_L firmware adaptation, hardware debugging, realtime plots, parameters, commands, faults, logs, reports, AI-assisted diagnosis, tutorials and course ecosystem.

## Current Status

- Phase 0-6: Mock-only V1.0-MVP completed.
- Phase 7.1-A: communication transport decision completed.
- Phase 7.0-UI / UI-2: VESC-like Chinese workbench layout completed.
- Phase 8.1: VESC-like framework pass completed: menu bar, toolbar, device/CAN list, bottom quick controls, connection tabs, realtime data tabs, sampled data tabs and terminal framework.
- Phase 8.3: teaching/research/engineering workflow pass added loop tuning, filter/notch, experiment analysis, identification and observer page presets.
- Phase 9.0: Mock current-loop step experiment added with metrics, plot preview and Markdown report preview.
- Phase 9.1: Mock experiment export added for CSV, Markdown report and PNG plot snapshot.
- Phase 9.2: modular parameter-identification workbench added for Rs, Ld/Lq, flux/Kt, electrical angle, inertia/friction and observer workflows.
- Phase 9.3: first runnable Mock Rs identification loop added with task/result models, trace display and estimate refresh.
- Phase 9.4: runnable Mock Ld/Lq inductance identification added with current-slope estimation and current-loop bandwidth hint.
- Phase 9.5: current-loop PI initial suggestion added from Mock Rs/Ld/Lq results.
- Phase 9.6: Mock PI step-response validation added to close the first tuning loop.
- Phase 9.7: current-loop tuning report export added for Mock identification, PI suggestion and step validation.
- Phase 9.8: experiment session package export added for reports, CSV traces, metrics JSON, config snapshot placeholder and safety notes.
- Phase 9.9: UI direction cleanup started with calmer blue-gray palette, simplified navigation and reduced duplicate global controls.
- Phase 10.0: dashboard and scope polished with compact motor-status judgement, richer realtime metrics, scope presets and signal search.
- Phase 10.1: parameter page and tuning workflow polished with summary cards, writable filtering and visible tuning progress.
- Phase 10.2: premium UI system pass added calmer graphite/light workspace palette, refined cards, tables, status chips and oscilloscope colors.
- Phase 10.3: information architecture cleanup reduced duplicated global actions, reordered navigation and shortened repetitive page copy.
- Phase 10.4: unified workbench layout removed the secondary global toolbar, reduced top-level navigation and improved Scope X-axis mouse interaction.
- Phase 10.5: Scope history and interaction polish separated long cached history from the visible time window and improved X-axis zoom behavior.
- Phase 10.6: Scope professionalization added A/B cursor measurement, selected-channel readout table and current-view CSV export.
- Phase 10.7: Scope unified measurement made A/B cursors, readout and current-view export available on fixed realtime tabs as well as custom channels.
- Phase 10.8: Scope interaction polish added draggable snapping A/B cursors, measurement-row curve highlight and shorter workbench navigation labels.
- Phase 10.9: system framework audit kept the sidebar compact and turned System Tools into a real low-frequency page container.
- Phase 10.10: release-freeze check upgraded GUI smoke to traverse all pages and included it in the review script.
- Phase 10.11: visual cohesion pass refined the palette, spacing, cards, buttons, tabs, tables, scrollbars and window sizing.
- Current backend: MockBackend.
- AxDr_L-aligned configs: `signals`, `parameters`, `commands`, `faults`.
- Real hardware communication is not implemented yet.
- SerialBackend PING is planned for Phase 7.2, not current.

## Quick Start

```powershell
python -m pip install -e ".[dev]"
python -m emotor_studio
```

Run tests:

```powershell
python -m pytest
```

Run task review:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\review_task.ps1
```

Run GUI smoke:

```powershell
python scripts\gui_smoke_test.py
```

## Current UI Pages

- 概览 / 连接：仪表盘、连接。
- 实时监控：实时波形、采样数据。
- 环路调参：三环调参、滤波 / 陷波、参数配置、FOC。
- 控制命令：模式设置、控制命令。
- 科研实验：实验工作台、自动分析。
- 工程辨识：参数辨识、观测器、电机参数。
- 诊断 / 报告：故障诊断、数据记录、调试报告、数据分析。
- 调试工具：固件信息、Terminal。

The current frame intentionally resembles an engineering motor-control tool:

- top menu and global toolbar;
- left page navigation and CAN/device list placeholder;
- bottom quick command strip placeholder;
- connection page with Serial / CAN / TCP / J-Link RTT tabs;
- realtime data page with 电流、温度、转速、FOC、转子位置 and 自定义通道 tabs;
- sampled data page with Current / BEMF / Filter-FFT tabs;
- terminal page shell.
- research/engineering presets for current-loop bandwidth scans, step-response analysis, Bode plots, filter/notch tuning, motor identification, electrical-angle identification and sensorless observer comparison.
- runnable Mock q-axis current-loop step analysis in 自动分析, including rise time, settling time, overshoot, steady-state error, Markdown report preview and CSV/PNG/Markdown export.
- modular 参数辨识 page with separated workflow windows for electrical, sensor, mechanical and observer identification.
- runnable Mock Rs identification in 参数辨识, with phase-resistance estimate, generated signal trace and event log. Real parameter write-back is still disabled.
- runnable Mock Ld/Lq identification in 参数辨识, with d/q inductance estimates and initial current-loop bandwidth hint.
- 三环调参 page can generate Mock Id/Iq current-loop PI initial suggestions from Rs/Ld/Lq and target bandwidth. Real write-back remains disabled.
- 三环调参 page can validate the q-axis PI suggestion with a Mock current-loop step response and show rise time, settling time, overshoot and steady-state error.
- Three-loop tuning page can export a Markdown current-loop tuning report with Mock identification inputs, PI suggestions, step-response metrics and safety notes.
- Three-loop tuning page can export a structured experiment session package with manifest, report, PI CSV, validation trace CSV, metrics JSON, config snapshot placeholder and safety notes.

All real hardware actions in these new framework controls are disabled until the AxDr_L protocol and SerialBackend PING are implemented.

## Communication Strategy

- V1.1 default: serial protocol first.
- If Type-C enumerates as a COM port, use Type-C COM first.
- If Type-C is power-only, use J1 UART + 3.3 V USB-TTL.
- J-Link / RTT is for debugging assistance, not the main transport.
- CAN is planned for V1.2 / V2.0 for multi-axis and engineering use.

## Code Reuse And License Policy

The project is currently a private prototype. It may reference or reuse local open-source projects to accelerate product validation, especially VESC Tool, SimpleFOCStudio and ODrive GUI.

All direct copy, adaptation, or strongly derived work must be recorded in `docs/code_provenance.md`. Before public release, course distribution, or commercial packaging, copied or derived code must be reviewed for license compatibility, replaced, clean-room rewritten, or separately authorized.

Key docs:

- `docs/product_positioning_cn_vesc.md`
- `docs/code_reuse_strategy.md`
- `docs/code_provenance.md`
- `docs/auto_review_system.md`
- `docs/review_checklist.md`
- `docs/vesc_like_ui_map.md`
- `docs/vesc_ui_research.md`
