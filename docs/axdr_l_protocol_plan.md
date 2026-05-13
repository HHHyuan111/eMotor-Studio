# AxDr_L Protocol Plan

## Current Protocol Status

No complete upper-computer protocol was found in the scanned AxDr_L application code.

Found transport and telemetry pieces:

- USB CDC transmit/receive glue exists in `AxDr_App/USB_Device/App/usbd_cdc_if.c`.
- UART helper APIs exist in `AxDr_App/User/bsp/bsp_uart.c`.
- FDCAN helper APIs exist in `AxDr_App/User/bsp/bsp_fdcan.c`.
- VOFA telemetry exists in `AxDr_App/User/moldue/vofa.c`, sending raw little-endian floats followed by frame tail `00 00 80 7f`.

Not found:

- No command dispatcher for host commands.
- No parameter read/write protocol.
- No stable telemetry descriptor.
- No fault upload frame beyond fields available in `pm.fault`.

Therefore eMotor-Studio V1.0 should remain MockBackend-only, but its command and frame model should be designed so AxDr_L V1.1 firmware can implement it without changing the GUI data model.

## Design Goals For V1.1

- Keep the same command IDs for serial and CAN where practical.
- Use AxDr_L object names as protocol object IDs: `pm.foc`, `pm.ctrl`, `pm.para`, `pm.protect`, `pm.mode`, `pm.fault`.
- Make telemetry schema-driven through `signals.json`.
- Make parameters schema-driven through `parameters.json`.
- Permit low-rate full snapshots and high-rate selected telemetry streams.
- Make all writes acknowledged and range checked by firmware.

## Serial Frame Proposal

Recommended serial/USB CDC frame:

| Field | Size | Description |
|---|---:|---|
| Magic | 2 | `0xA5 0x5A` |
| Version | 1 | Protocol version, start with `0x01`. |
| Command ID | 1 | Command type. |
| Sequence | 2 | Host-generated sequence for request/response matching. |
| Payload Length | 2 | Little-endian byte count. |
| Payload | N | Command-specific payload. |
| CRC16 | 2 | CRC over version through payload. |

Payload values should use little-endian numeric encoding. Text names should be avoided in real-time frames; use numeric IDs generated from config files.

## CAN / FDCAN Proposal

AxDr_L currently uses FDCAN FD/BRS support and can send up to 64-byte payloads. Suggested mapping:

- Standard command service base ID: `0x120`
- Telemetry stream base ID: `0x180`
- Fault event base ID: `0x1A0`
- Response base ID: request ID + `0x80`

For CAN FD, payload can mirror the serial frame minus magic and CRC when bus-level CRC is sufficient. For classic CAN compatibility, split long payloads into segmented frames with sequence and segment index.

## Command ID Design

| ID | Name | Direction | Payload | AxDr_L Target |
|---:|---|---|---|---|
| `0x01` | `ping` | Host -> Device | none | Protocol health check. |
| `0x02` | `get_firmware_info` | Host -> Device | none | Return commit/version/build if firmware adds metadata. |
| `0x03` | `get_schema_version` | Host -> Device | none | Return signal/parameter/fault schema versions. |
| `0x10` | `motor_enable` | Host -> Device | optional mode | Set `pm.ctrl_bit = opera` after safety checks. |
| `0x11` | `motor_stop` | Host -> Device | stop type | Set `pm.ctrl_bit = reset` or `pm.mode.halt = quick_mode`. |
| `0x12` | `clear_fault` | Host -> Device | clear mask | Clear `pm.fault` bits if safe and reset protect latch. |
| `0x13` | `set_control_state` | Host -> Device | `ctrl_bit` | Explicit state request: reset/start/opera. |
| `0x20` | `set_system_mode` | Host -> Device | `sys_mode` | Write `pm.mode.sys`. |
| `0x21` | `set_debug_mode` | Host -> Device | `debug_mode` | Write `pm.mode.debug`. |
| `0x22` | `set_release_mode` | Host -> Device | `release_mode` | Write `pm.mode.release`. |
| `0x23` | `set_calibration_mode` | Host -> Device | `calibrat_mode` | Write `pm.mode.calibrat`. |
| `0x30` | `set_current_target` | Host -> Device | `id_set`, `iq_set` | Write `pm.ctrl.id_set`, `pm.ctrl.iq_set`. |
| `0x31` | `set_speed_target` | Host -> Device | `wm_set` or `wr_set` | Write mechanical/rotor speed target. |
| `0x32` | `set_position_target` | Host -> Device | `posm_set` or `posr_set` | Write mechanical/rotor position target. |
| `0x33` | `set_torque_target` | Host -> Device | `torm_set` | Write torque target. |
| `0x40` | `read_parameter` | Host -> Device | parameter ID | Return one parameter value. |
| `0x41` | `write_parameter` | Host -> Device | parameter ID, typed value | Write one parameter after bounds validation. |
| `0x42` | `read_parameter_group` | Host -> Device | group ID | Return all parameters in a group. |
| `0x43` | `save_parameters` | Host -> Device | optional mask | Persist selected parameters if firmware adds flash storage. |
| `0x50` | `request_telemetry_once` | Host -> Device | signal set ID | Return one telemetry frame. |
| `0x51` | `start_telemetry_stream` | Host -> Device | signal set ID, rate Hz | Start periodic upload. |
| `0x52` | `stop_telemetry_stream` | Host -> Device | stream ID | Stop periodic upload. |
| `0x60` | `request_fault_status` | Host -> Device | none | Return `pm.fault.all` and decoded bits. |
| `0x61` | `inject_mock_fault` | GUI Mock only | fault code | MockBackend-only; do not implement on real firmware unless test build. |
| `0x70` | `start_encoder_calibration` | Host -> Device | calibration options | Set calibration mode and start rotor/output encoder calibration. |
| `0x71` | `start_parameter_identification` | Host -> Device | id type | Start Rs/Ls/flux/Js identification flow. |
| `0x72` | `start_anticogging_calibration` | Host -> Device | options | Start anticogging calibration. |

## Parameter Read

Request payload:

| Field | Type | Description |
|---|---|---|
| `parameter_id` | uint16 | ID generated from `parameters.json`. |

Response payload:

| Field | Type | Description |
|---|---|---|
| `status` | uint8 | `0` success, nonzero error. |
| `parameter_id` | uint16 | Echoed parameter ID. |
| `value_type` | uint8 | Float, int, enum, bool. |
| `value` | typed | Current value. |

## Parameter Write

Request payload:

| Field | Type | Description |
|---|---|---|
| `parameter_id` | uint16 | ID generated from `parameters.json`. |
| `value_type` | uint8 | Float, int, enum, bool. |
| `value` | typed | New value. |

Firmware responsibilities:

- Validate writable flag.
- Validate min/max or enum range.
- Apply safety gates: do not allow high-risk motor, observer, or protection writes while running unless explicitly allowed.
- Return the actual applied value.

## Telemetry Upload

Use signal IDs generated from `signals.json`.

Recommended telemetry payload:

| Field | Type | Description |
|---|---|---|
| `timestamp_us` | uint32 | Firmware monotonic timestamp. |
| `sample_counter` | uint32 | Incrementing sample count. |
| `signal_count` | uint8 | Number of signal entries. |
| `entries` | repeated | `signal_id:uint16`, `value_type:uint8`, `value`. |

Default V1.1 stream should include:

- `bus_voltage`
- `current_d`
- `current_q`
- `rotor_speed_filtered`
- `mechanical_speed`
- `speed_target_mechanical`
- `electrical_angle`
- `encoder_angle`
- `duty_a`, `duty_b`, `duty_c`
- `mos_temperature`, `coil_temperature`
- `run_state`, `system_mode`, `release_mode`
- `fault_word`

## Fault Upload

Fault status response:

| Field | Type | Description |
|---|---|---|
| `fault_word` | uint32 | `pm.fault.all`. |
| `latched_fault_word` | uint32 | Optional latched historical bits. |
| `state_bit` | uint8 | Current `pm.state_bit`. |
| `protect_rst` | uint8 | `pm.protect.rst`. |

Recommended fault event frame:

- Emit on fault word transition.
- Include `timestamp_us`, `fault_word`, `new_bits`, `cleared_bits`, `state_bit`.

## Control Commands

### Motor Enable

Command: `motor_enable`

Firmware target:

- If no active fault and preconditions are met, set `pm.ctrl_bit = opera`.
- Return current `ctrl_bit`, `state_bit`, and `fault_word`.

### Motor Stop

Command: `motor_stop`

Stop types:

- `reset_stop`: set `pm.ctrl_bit = reset`.
- `quick_stop`: set `pm.mode.sys = halt_mode`, `pm.mode.halt = quick_mode`.
- `fault_stop`: set `pm.mode.sys = halt_mode`, `pm.mode.halt = fault_mode`.

### Clear Fault

Command: `clear_fault`

Firmware target:

- Clear selected `pm.fault` bits only when safe.
- Reset protection counters/latch as needed.
- Return remaining `fault_word`.

### Control Mode Switch

Commands:

- `set_system_mode`
- `set_debug_mode`
- `set_release_mode`
- `set_calibration_mode`

The GUI should present these as constrained enums derived from AxDr_L:

- Debug: `drag_vf`, `drag_if`, `volt_op`, `curr_cl`, `spd_curr_cl`, `pos_spd_curr_cl`.
- Release: `mit_mode`, `tor_mode`, `vel_mode`, `pos_mode`, `cst_mode`, `csv_mode`, `csp_mode`.
- Calibration: `rotor_enc_cali`, `iden_pm`, `anticogging_pm`.

### Speed / Current / Position Setpoints

Setpoint commands should write high-level targets, not raw PI internals:

- Current: `pm.ctrl.id_set`, `pm.ctrl.iq_set`.
- Speed: prefer `pm.ctrl.wm_set` for mechanical speed in release velocity mode; support `pm.ctrl.wr_set` for low-level debug mode.
- Position: prefer `pm.ctrl.posm_set` for mechanical position; support `pm.ctrl.posr_set` for rotor-side debug mode.
- Torque: `pm.ctrl.torm_set`.

## eMotor-Studio V1.0 MockBackend Alignment

Phase 3 MockBackend should implement the command IDs and state changes above in Python only. It should not claim hardware connectivity, but it should make Dashboard, ParameterPage, CommandPage, FaultPage, Logger, and Report speak the same object language expected by AxDr_L V1.1.

## Open Firmware Work For V1.1

- Add a protocol parser around USB CDC receive or UART idle receive.
- Add parameter ID table and safe read/write dispatcher.
- Add telemetry stream scheduler decoupled from the 20 kHz FOC interrupt.
- Add fault event publishing.
- Decide whether CAN uses the same command IDs or a compact actuator-style subset.
- Add firmware version/schema metadata.

## Phase 6 Application Boundary

Phase 6 adds an eMotor-Studio `SerialBackend` placeholder only. It is not a real AxDr_L transport and does not open a serial port.

The placeholder is allowed to:

- Load the same signal, parameter, command, and fault schemas as MockBackend.
- Expose `BackendInterface` so UI pages can be tested against the future hardware backend shape.
- Record attempted commands in memory.
- Provide reserved hooks named `build_command_frame()` and `parse_telemetry_frame()`.

The placeholder must raise `ProtocolNotImplementedError` for:

- Real command sending.
- Real parameter writes.
- Command frame encoding.
- Telemetry frame decoding.

This keeps V1.0 stable around MockBackend while leaving V1.1 insertion points for the firmware protocol that will be developed later.
