# VESC Core Replication Standard

This document defines the minimum VESC-like upper-computer experience that
eMotor-Studio should converge toward for teaching and local motor-control
development.

It is not a full VESC Tool clone. The goal is to reproduce the main learning,
tuning, monitoring, and debugging workflows while adapting all data, commands,
and parameters to local hardware and AxDr_L-style firmware.

## Product Boundary

eMotor-Studio should be a domestic, teaching-friendly motor-control workbench.
It should feel familiar to users who have seen VESC Tool, but it must remain
simple enough for local development, classroom explanation, firmware debugging,
and repeated parameter experiments.

Required product qualities:

- Engineering workbench, not a generic serial assistant.
- Chinese-first UI text, with concise engineering terminology.
- Mock mode always runnable for teaching without hardware.
- Hardware backend isolated behind the existing backend interface.
- Config-driven signals, parameters, commands, and faults.
- Clear safety state before any command that can move the motor.
- No VESC branding, logos, icons, UI files, or copied source assets.

Non-goals:

- Firmware flashing.
- SWD, ESP, bootloader, or package tools.
- Lisp, QML scripting, app store, plugins, or scripting IDEs.
- BMS, IMU, GNSS, BLE pairing, TCP hub, and mobile-specific features.
- Multi-node CAN management beyond future optional expansion.
- Full industrial production workflow.

## Required Main UI Structure

The application should use a left-side navigation plus a main work area, similar
in organization to VESC Tool but simplified.

Minimum navigation groups:

1. Start / Overview
2. Connection
3. Motor Settings
4. App / Control Settings
5. Realtime Data
6. Fault Diagnosis
7. Data Log / Report
8. Debug Tools

Each page must have a stable purpose. Avoid adding duplicate pages that expose
the same backend action in different ways.

## Required Pages

### 1. Start / Overview

Purpose:

- Give the user a quick understanding of current device, state, and risk.
- Provide teaching-friendly entry points into common workflows.

Required content:

- Connection status.
- Backend type: Mock, Serial placeholder, or real hardware when implemented.
- Firmware or schema version if available.
- Run state: stopped, ready, running, fault.
- Key realtime values: bus voltage, current, speed, temperature, fault summary.
- Quick buttons for connect, stop, clear fault, open parameters, open realtime
  data.

Acceptance:

- A new user can tell within five seconds whether the app is connected, running,
  or faulted.
- Stop/fault state is visually stronger than decorative UI.
- Mock mode shows believable values without pretending real hardware is present.

### 2. Connection

Purpose:

- Manage transport selection and make hardware readiness explicit.

Required content:

- Backend selector.
- Mock connect/disconnect.
- Serial port selector when real serial is implemented.
- Baud rate or protocol preset.
- Connect, disconnect, refresh, ping.
- Last response/status message.
- Clear indication when a backend is placeholder-only.

Acceptance:

- UI never claims real hardware communication until implemented.
- Connection errors are visible and actionable.
- The rest of the app can remain open in disconnected mode without crashing.

### 3. Motor Settings

Purpose:

- Expose the main motor and control parameters needed for teaching and local
  tuning.

Required parameter groups:

- Motor basic: rated voltage, pole pairs, phase resistance, d/q inductance,
  flux, inertia, gear ratio.
- Encoder: electrical offset, rotor offset, phase order, angle source.
- Current loop: Id/Iq Kp, Ki, limits, bandwidth-related values.
- Speed loop: Kp/Ki/feedforward/damping, speed limits.
- Position loop: Kp/Ki/Kd or equivalent position controller values if used.
- Protection: voltage limits, current limits, temperature limits, fault
  debounce or latch settings.

Required behavior:

- Parameters come from `configs/parameters.json` or equivalent schema.
- Each parameter has display name, type, default, unit, min/max, group, and
  source mapping.
- Invalid values are rejected before reaching the backend.
- High-risk parameters are marked clearly.
- Writing high-risk parameters while running is blocked unless a future firmware
  contract explicitly allows it.

Acceptance:

- No important editable parameter is hardcoded only in a widget.
- UI grouping follows the schema, not scattered page-specific constants.
- Parameter edits can be tested against MockBackend.

### 4. App / Control Settings

Purpose:

- Configure high-level operation mode and issue controlled setpoints.

Required content:

- System mode selection: debug, release, calibration, halt if supported.
- Debug mode selection: voltage open-loop, current loop, speed-current loop,
  position-speed-current loop or local equivalents.
- Release mode selection: torque, velocity, position, MIT/CSP/CSV/CST if
  supported by local firmware.
- Control command panel:
  - motor enable
  - motor stop
  - clear fault
  - set current target
  - set speed target
  - set position target
  - set torque target

Required behavior:

- Commands come from `configs/commands.json` or equivalent schema.
- Every command has an ID/name, payload description, target mapping, and
  direction.
- All dangerous commands require visible connection and safety state.
- Motor stop remains available even if other controls are disabled.

Acceptance:

- The user can teach the difference between mode selection, setpoint command,
  and enable/stop state.
- Command history or last command status is visible.
- MockBackend reflects state transitions.

### 5. Realtime Data

Purpose:

- Provide VESC-like realtime observation for motor-control tuning.

Required signal groups:

- Electrical: bus voltage, phase/current input if available, Id, Iq.
- Mechanical: speed, speed target, position, encoder angle.
- PWM/FOC: duty or phase duty, electrical angle, Vd/Vq if available.
- Thermal: MOS/board temperature, motor/coil temperature.
- State: run state, mode, fault word.

Required behavior:

- Signals come from `configs/signals.json` or equivalent schema.
- Plot can start/stop without disconnecting.
- User can choose signals to plot.
- Recent window and full-history view are available.
- Y-axis auto range can be toggled.
- Current numeric values remain visible beside or above plots.

Acceptance:

- Realtime page can explain current loop, speed loop, and fault response during
  teaching.
- It remains usable at mock rates and future hardware telemetry rates.
- Plotting code does not know firmware object internals directly.

### 6. Fault Diagnosis

Purpose:

- Decode local firmware fault state into readable teaching/debugging output.

Required content:

- Current fault word.
- Decoded active fault bits.
- Latched or recent fault events if available.
- State bits: stopped, precharge, running, fault, protection reset or local
  equivalents.
- Clear fault command with status result.

Required behavior:

- Fault definitions come from `configs/fault_codes.json`.
- Unknown bits are shown as unknown, not silently ignored.
- Clearing a fault must show remaining fault state.

Acceptance:

- Fault page can be used to teach why the motor will not enable.
- MockBackend can inject or simulate faults for UI testing.

### 7. Data Log / Report

Purpose:

- Record enough runtime data to review an experiment or class demo.

Required content:

- Start/stop logging.
- Selected signal list.
- Sample count and duration.
- Export or report summary using existing project format.
- Event markers for connect, disconnect, enable, stop, command, fault.

Acceptance:

- Logged values come from the same telemetry stream as realtime plots.
- Reports do not invent values unavailable from telemetry or events.

### 8. Debug Tools

Purpose:

- Keep low-level diagnostics available without turning the app into a serial
  assistant.

Required content:

- Protocol/command history.
- Optional text terminal only if firmware supports terminal-style commands.
- Raw frame view is optional and should be marked advanced.

Acceptance:

- Debug tools help diagnose protocol/backend issues.
- Normal teaching workflows do not depend on raw command entry.

## Required Architecture Standard

The following separation must hold throughout development:

- UI pages render schemas and call backend methods.
- BackendInterface defines the application contract.
- MockBackend implements the same contract as the future hardware backend.
- SerialBackend or future hardware backend owns transport, frame encoding, and
  parsing.
- Config files define signals, parameters, commands, and faults.
- Models define shared runtime objects used by UI, logger, report, and backend.

Forbidden coupling:

- UI directly parsing serial bytes.
- UI directly reading AxDr_L source code.
- Parameter widgets containing hidden firmware write logic.
- Mock-only fields becoming required real-hardware assumptions.

## Required Config Schema Standard

### Parameters

Each parameter must include:

- `name`
- `source_in_axdr_l` or local firmware source
- `display_name`
- `type`
- `default`
- `unit`
- `min`
- `max`
- `group`
- `description`

Recommended additions:

- `writable`
- `risk_level`: low, medium, high
- `requires_stopped`
- `requires_fault_clear`
- `persistent`
- `protocol_id`

### Signals

Each signal must include:

- `name`
- `source_in_axdr_l` or local firmware source
- `display_name`
- `type`
- `unit`
- `group`
- `description`

Recommended additions:

- `rate_hint_hz`
- `plot_default`
- `min`
- `max`
- `protocol_id`

### Commands

Each command must include:

- `id`
- `name`
- `display_name`
- `direction`
- `description`
- `payload`, if any
- `target_in_axdr_l` or local firmware target

Recommended additions:

- `requires_connected`
- `requires_stopped`
- `requires_no_fault`
- `risk_level`
- `ack_required`

### Faults

Each fault entry must include:

- `bit` or `code`
- `name`
- `display_name`
- `severity`
- `description`
- `suggested_action`

## Required Communication Standard

When real hardware communication is implemented, it should provide:

- Protocol version.
- Command ID.
- Sequence number for request/response matching.
- Payload length.
- Typed payload encoding.
- Checksum or CRC.
- Acknowledgement for all writes.
- Explicit error codes.
- Timeout handling.
- Reconnect-safe state reset.

Minimum command set:

- `ping`
- `get_firmware_info`
- `get_schema_version`
- `motor_enable`
- `motor_stop`
- `clear_fault`
- `set_system_mode`
- `set_debug_mode`
- `set_release_mode`
- `set_calibration_mode`
- `set_current_target`
- `set_speed_target`
- `set_position_target`
- `set_torque_target`
- `read_parameter`
- `write_parameter`
- `request_telemetry_once`
- `start_telemetry_stream`
- `stop_telemetry_stream`
- `request_fault_status`

Minimum telemetry fields:

- timestamp
- sample counter
- bus voltage
- Id / Iq or equivalent current signals
- speed and speed target
- position or encoder angle
- duty or PWM output
- temperature
- run state
- mode
- fault word

## Safety Standard

Safety rules are mandatory even for teaching tools:

- Stop command is always visible on pages that can command motion.
- Motor enable is blocked when disconnected.
- Motor enable is blocked when active faults exist.
- Setpoint commands are blocked or clearly inert when not enabled.
- High-risk parameter writes are blocked while running.
- Parameter range validation happens before backend call.
- Backend validates again before accepting writes.
- Fault clear shows the post-clear fault result.
- UI must never hide an active fault behind a generic "ready" state.

## Visual / Interaction Standard

The UI should be restrained, compact, and engineering-oriented:

- Stable left navigation.
- Clear status area at the top or dashboard.
- Tables for parameters and faults.
- Plots for realtime signals.
- Buttons for commands.
- Selectors for modes.
- Inputs/sliders/spin boxes for numeric setpoints.
- Chinese labels by default.
- Units visible near every engineering value.
- Dangerous actions visually distinct from normal settings.

Avoid:

- Marketing landing pages.
- Decorative UI that competes with status and plots.
- Excessive card nesting.
- Hidden safety state.
- Long instructional paragraphs inside the app.

## Iteration Checklist

Use this checklist after each development iteration:

- The app still starts in Mock mode.
- The requested feature is available from the intended page.
- No unrelated feature was added just because VESC Tool has it.
- UI does not directly depend on serial/protocol internals.
- Config files remain the source of truth for parameters, signals, commands, and
  faults.
- Parameter validation exists in UI/backend path.
- Command safety checks exist for enable, stop, mode, and setpoints.
- Fault state is visible and decoded.
- Realtime values and logs share the same telemetry model.
- Tests pass.
- GUI smoke test passes when UI changed.
- No VESC trademark, icon, logo, UI file, or source asset was copied.
- Code provenance is updated if any external reference was adapted.

## Final Acceptance Standard

The local upper-computer can be considered aligned with this standard when:

- A user can connect Mock mode, observe telemetry, change safe parameters, issue
  mock control commands, trigger/clear faults, and record a short experiment.
- The same UI pages are ready to use real SerialBackend without redesign.
- Core VESC-like workflows are present: connection, motor settings, app/control
  settings, realtime data, fault diagnosis, logging/reporting, and debug tools.
- Complex VESC Tool features remain intentionally excluded.
- The project is useful for teaching motor-control concepts and local firmware
  development without claiming industrial completeness.
