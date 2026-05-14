# Phase 7 Plan: AxDr_L Hardware Integration

## Goal

Phase 7 connects eMotor-Studio to a real AxDr_L development board. The objective is not to bypass the existing architecture, but to replace MockBackend data with real firmware data through a transport backend that keeps UI pages unchanged where possible.

V1.0-MVP is Mock-only. Phase 7 begins the V1.1 hardware path.

Phase 7.1-A transport decision: V1.1 should use a serial protocol first, preferably over USB Type-C if it enumerates as a COM port, otherwise over J1 UART through a 3.3 V USB-TTL adapter. J-Link / RTT is reserved for firmware debugging, and CAN is planned as a later engineering-grade extension after the serial protocol is proven.

## Why Serial Logic Must Not Go Into UI

Serial or CAN logic must stay out of Dashboard, Scope, Parameter, Command, Fault, Logger, and Report pages because:

- UI pages should render application state, not know byte framing details.
- Hardware communication must be testable without Qt widgets.
- Serial/CAN error handling, retries, timeouts, and packet parsing need their own lifecycle.
- Future CAN support should reuse command, telemetry, parameter, and fault contracts.
- Keeping transport behind `BackendInterface` avoids rewriting pages when the protocol changes.

The UI should continue to call:

- `send_command()`
- `read_parameters()`
- `write_parameter()`
- `read_signal_schema()`
- `read_command_schema()`
- `read_fault_schema()`

Hardware transport should live in `SerialBackend` or a future `CanBackend`.

## Protocol Questions To Confirm First

Do not implement full hardware communication before these are answered:

1. Which physical transport is first target: USB CDC, UART, CAN, or FDCAN?
2. What baud rate, serial settings, or CAN bitrate should be used?
3. Does AxDr_L firmware already include a host command parser, or must one be added?
4. What frame format will be used: magic/version/id/sequence/length/payload/crc, VOFA-style float stream, or another format?
5. What checksum/CRC is required?
6. How are command acknowledgements represented?
7. How are errors reported: NACK, fault frame, timeout, or fault word?
8. How are signal IDs generated and synchronized with `configs/signals.json`?
9. How are parameter IDs generated and synchronized with `configs/parameters.json`?
10. Which commands are safe while the motor is running?
11. Which parameter writes require motor stop or reboot?
12. What telemetry rate is safe without disturbing the control loop?
13. What firmware timestamp or sample counter should telemetry use?
14. How should protocol version and schema version be exchanged?

## AxDr_L Items To Confirm

Before real connection, confirm these in AxDr_L:

### Variables

- `pm.foc.vbus`
- `pm.foc.ibus`
- `pm.foc.i_a`, `pm.foc.i_b`, `pm.foc.i_c`
- `pm.foc.i_d`, `pm.foc.i_q`
- `pm.foc.v_d`, `pm.foc.v_q`
- `pm.foc.p_e`
- `pm.foc.e_pr`
- `pm.foc.mp_m`
- `pm.foc.wr_f`
- `pm.foc.wm`
- `pm.foc.dtc_a`, `pm.foc.dtc_b`, `pm.foc.dtc_c`
- `pm.foc.Tmos`, `pm.foc.Tcoil`
- `pm.ctrl.wm_set`
- `pm.ctrl.id_set`, `pm.ctrl.iq_set`
- `pm.ctrl.posm_set`
- `pm.ctrl_bit`
- `pm.state_bit`
- `pm.mode.sys`
- `pm.mode.release`
- `pm.fault.all`

### Parameters

- Motor constants in `pm.para`.
- Encoder offsets and phase order.
- Current loop PI values.
- Speed and position loop values.
- Velocity, torque, and current limits.
- Protection thresholds.
- Observer parameters.
- Identification parameters.

### Commands

- Motor enable.
- Motor stop.
- Clear fault.
- Set system mode.
- Set release/debug/calibration mode.
- Set speed target.
- Set current target.
- Set position target.
- Read parameter.
- Write parameter.
- Start/stop telemetry stream.
- Request fault status.

### Fault Codes

- Confirm bit positions in `pm.fault`.
- Confirm which faults are latched.
- Confirm which faults can be cleared from the host.
- Confirm whether `off_link` is a firmware communication timeout fault or a placeholder.

## Recommended Phase Split

### Phase 7.1: AxDr_L Communication Protocol Confirmation

Tasks:

- Decide first physical transport: USB CDC, UART, or CAN/FDCAN.
- Confirm or create the firmware-side command parser plan.
- Freeze the minimal frame format.
- Define command IDs, response IDs, status codes, and error codes.
- Define schema/version handshake.
- Decide telemetry stream format and rate.
- Decide fault status/event frame format.
- Update `docs/axdr_l_protocol_plan.md`.
- Update configs if names or IDs change.

Acceptance criteria:

- Protocol document has one chosen first transport.
- Ping request/response payload is fully specified.
- Telemetry payload format is fully specified for at least five signals.
- Parameter read/write payloads are specified.
- Command ACK/NACK behavior is specified.
- Safety restrictions are documented.

### Phase 7.2: SerialBackend Minimal Handshake / Ping

Tasks:

- Implement serial port open/close in `SerialBackend`.
- Implement frame encode/decode for `ping` only.
- Add timeout handling.
- Add sequence number matching.
- Add tests for frame encoding/decoding without hardware.
- Add manual test notes for a connected board.

Acceptance criteria:

- Mock-free frame encode/decode tests pass.
- `SerialBackend.connect()` can open a configured serial port.
- `send_command(MotorCommand(name="ping"))` can receive a valid firmware response on hardware.
- UI remains unchanged.
- Failures produce clear errors, not UI freezes.

### Phase 7.3: Telemetry Real-Time Data Receive

Tasks:

- Implement telemetry frame parsing.
- Map signal IDs to `TelemetrySample.signals`.
- Emit telemetry through the same callback path used by MockBackend.
- Keep serial reading off the UI thread.
- Add rate and timeout guards.

Acceptance criteria:

- Dashboard can display real `bus_voltage`, `current_q`, and speed-related values.
- Scope can plot at least three real signals.
- Logger can record real telemetry.
- UI remains responsive during telemetry streaming.
- Missing/unknown signal IDs are handled gracefully.

### Phase 7.4: Parameter Read / Write

Tasks:

- Implement parameter ID mapping.
- Implement parameter read command.
- Implement parameter write command.
- Implement firmware ACK/NACK handling.
- Enforce UI and firmware-side range checks.
- Mark unsafe writes and require stop state where needed.

Acceptance criteria:

- ParameterPage can read at least one motor parameter from AxDr_L.
- ParameterPage can write one safe test parameter and read it back.
- Out-of-range writes are rejected clearly.
- Writes while running follow documented safety rules.
- No UI freeze on timeout or NACK.

### Phase 7.5: Motor Enable / Stop / Clear Fault

Tasks:

- Implement `motor_enable`.
- Implement `motor_stop`.
- Implement `clear_fault`.
- Implement `request_fault_status`.
- Ensure FaultPage decodes real fault word.
- Add user-visible status for command result.

Acceptance criteria:

- Motor enable command produces a documented state transition or safe failure.
- Motor stop command reliably stops or requests stop.
- Clear fault updates `fault_word` after firmware response.
- FaultPage reflects real fault bits.
- Commands are logged with timestamp and result.

### Phase 7.6: Real Board Joint Debugging And Logging

Tasks:

- Run end-to-end tests with an AxDr_L development board.
- Capture startup, ping, telemetry, parameter read/write, enable/stop, and fault logs.
- Record known firmware/app mismatches.
- Update docs with wiring, port settings, and safety checklist.
- Decide whether V1.1 should target USB CDC, UART, or CAN as the default public workflow.

Acceptance criteria:

- A documented hardware session can be repeated.
- Logger exports real board telemetry CSV.
- Report generates a usable hardware session summary.
- Known issues are documented with reproduction steps.
- No copied AxDr_L source is added to eMotor-Studio.

## Safety Rules For Phase 7

- Start with no motor power or a safe bench setup.
- Do not enable motor commands until ping, telemetry, and fault status are reliable.
- Do not write protection thresholds during early tests.
- Do not perform high-speed or high-current commands from unvalidated UI controls.
- Keep a physical emergency stop or power cutoff available during motor tests.

## Documentation To Update During Phase 7

- `docs/axdr_l_protocol_plan.md`
- `docs/architecture.md`
- `docs/phase_7_axdr_l_hardware_integration_plan.md`
- `README.md`
- Config files if IDs, names, or fields change:
  - `configs/signals.json`
  - `configs/parameters.json`
  - `configs/fault_codes.json`
  - `configs/commands.json`

## Stop Condition

Phase 7 should not begin implementation until Phase 7.1 freezes the first communication protocol. The next smallest useful task is protocol confirmation, not serial code.
