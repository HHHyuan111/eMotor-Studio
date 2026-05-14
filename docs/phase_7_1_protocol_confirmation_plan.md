# Phase 7.1 Protocol Confirmation Plan

## Goal

Phase 7.1 confirms the minimum AxDr_L host communication protocol before any real SerialBackend implementation. The goal is to freeze enough of the transport, frame, command, telemetry, parameter, and safety rules that Phase 7.2 can implement a minimal PING without guessing.

This is a planning phase only. It does not implement serial, CAN, J-Link RTT, or hardware connection code.

## Transport Decision For Phase 7.1

The recommended V1.1 default route is:

1. Use USB Type-C if it enumerates as a COM port and supports bidirectional bytes.
2. Otherwise use J1 UART through a 3.3 V USB-TTL adapter.
3. Use the same serial protocol for both physical paths.
4. Keep CAN as a later engineering-grade transport.
5. Keep J-Link / RTT as firmware debug support, not the app's main communication path.

## Questions To Confirm Before Real Hardware Communication

### Board And Physical Layer

- Does USB Type-C enumerate as a COM port on Windows?
- If yes, is it native USB CDC or a USB-to-UART bridge?
- If no, which J1 UART instance does `UART TX/RX` connect to in AxDr_L firmware?
- What baud rate should be used first: 115200, 256000, 921600, or another value?
- Are UART pins 3.3 V logic?
- Does the board need external power when using USB-TTL?
- Is GND shared safely between board and adapter?

### Firmware Availability

- Is there a currently enabled receive interrupt, DMA, or polling path for the chosen serial transport?
- Is there an existing command parser?
- Is existing VOFA telemetry still needed, or should it be separate from the new protocol?
- Which task or loop should process host commands without blocking the FOC ISR?
- Where should telemetry snapshots be assembled?

### Protocol Stability

- What protocol version starts V1.1?
- How does firmware report firmware version, build date, git hash, and schema version?
- How are command IDs synchronized with `configs/commands.json`?
- How are signal IDs synchronized with `configs/signals.json`?
- How are parameter IDs synchronized with `configs/parameters.json`?
- What is the maximum frame payload length?
- What is the timeout for host request/response?

### Safety

- Which commands are allowed while the motor is running?
- Which parameter writes require stopped state?
- Which fault bits are clearable by host command?
- What response should firmware return when a command is rejected for safety?
- How does the host detect stale telemetry or link loss?

## Recommended Minimum Protocol

The minimum useful protocol should support:

1. `PING`
2. `GET_FIRMWARE_INFO`
3. `GET_SCHEMA_VERSION`
4. `REQUEST_TELEMETRY_ONCE`
5. `START_TELEMETRY_STREAM`
6. `STOP_TELEMETRY_STREAM`
7. `READ_PARAMETER`
8. `WRITE_PARAMETER`
9. `MOTOR_ENABLE`
10. `MOTOR_STOP`
11. `CLEAR_FAULT`
12. `REQUEST_FAULT_STATUS`

The first implementation in Phase 7.2 should only implement `PING`.

## Frame Format Recommendation

Use a binary serial frame compatible with USB CDC or UART:

| Field | Size | Type | Description |
|---|---:|---|---|
| Magic | 2 | uint8[2] | `0xA5 0x5A` marks frame start. |
| Version | 1 | uint8 | Protocol version, start with `0x01`. |
| Command ID | 1 | uint8 | Command or response ID. |
| Sequence | 2 | uint16 LE | Host-generated request sequence, echoed in response. |
| Payload Length | 2 | uint16 LE | Number of payload bytes. |
| Payload | N | bytes | Command-specific payload. |
| CRC16 | 2 | uint16 LE | CRC over Version through Payload. |

Rationale:

- Magic supports byte-stream resynchronization.
- Sequence supports timeout and response matching.
- Payload length supports variable-size telemetry and parameter frames.
- CRC16 is more appropriate than checksum for noisy UART/CAN-adapter environments.
- The same command IDs can later map to CAN frames.

## ACK / NACK Recommendation

Every request that changes state or reads data should receive a response.

Recommended status byte:

| Status | Meaning |
|---:|---|
| `0x00` | OK |
| `0x01` | Unknown command |
| `0x02` | Invalid length |
| `0x03` | Invalid payload |
| `0x04` | CRC error |
| `0x05` | Busy |
| `0x06` | Rejected by safety state |
| `0x07` | Unknown parameter or signal ID |
| `0x08` | Read-only parameter |
| `0x09` | Value out of range |
| `0x0A` | Fault active |
| `0x0B` | Unsupported in this firmware |
| `0xFF` | Internal error |

Recommended response format:

| Field | Type | Description |
|---|---|---|
| `status` | uint8 | Status code above. |
| `request_command_id` | uint8 | Echo original command. |
| `response_payload` | bytes | Optional data. |

For commands with no data, an OK response can be just `status + request_command_id`.

## CRC / Checksum Recommendation

Use CRC16-CCITT-FALSE or another explicitly documented CRC16 variant.

Phase 7.1 must freeze:

- Polynomial.
- Initial value.
- Reflected or non-reflected behavior.
- Final XOR.
- Byte order in frame.
- Test vector.

Recommended default:

- Name: CRC-16/CCITT-FALSE
- Polynomial: `0x1021`
- Init: `0xFFFF`
- RefIn: false
- RefOut: false
- XorOut: `0x0000`
- Output byte order: little-endian in the frame

Add one test vector before Phase 7.2 implementation.

## Command Details

### PING

Purpose:

- Prove byte-level connection.
- Prove frame parser.
- Prove ACK path.
- Prove sequence echo.

Request:

- Command ID: `0x01`
- Payload: optional `uint32 nonce`

Response payload:

| Field | Type | Description |
|---|---|---|
| `status` | uint8 | `0x00` on success. |
| `request_command_id` | uint8 | `0x01`. |
| `nonce` | uint32 | Echo request nonce if present. |
| `protocol_version` | uint8 | Current protocol version. |

Acceptance for Phase 7.2:

- Host sends PING.
- Firmware returns valid frame.
- CRC verifies.
- Sequence matches.
- Timeout is handled without freezing UI.

### GET_FIRMWARE_INFO

Purpose:

- Identify board firmware before sending control commands.

Request:

- Command ID: `0x02`
- Payload: none.

Response payload:

| Field | Type | Description |
|---|---|---|
| `status` | uint8 | OK or error. |
| `request_command_id` | uint8 | `0x02`. |
| `fw_major` | uint8 | Firmware major version. |
| `fw_minor` | uint8 | Firmware minor version. |
| `fw_patch` | uint8 | Firmware patch version. |
| `git_hash` | char[8] or bytes | Optional short commit hash. |
| `build_flags` | uint32 | Optional feature flags. |

### GET_SCHEMA_VERSION

Purpose:

- Confirm that app configs match firmware schema.

Request:

- Command ID: `0x03`
- Payload: none.

Response payload:

- `status`
- `request_command_id`
- `signals_schema_crc32`
- `parameters_schema_crc32`
- `fault_schema_crc32`
- `command_schema_crc32`

If CRC32 is too much for firmware initially, use monotonically increasing schema version numbers.

### REQUEST_TELEMETRY_ONCE

Purpose:

- Read one safe snapshot before enabling streams.

Request:

- Command ID: `0x50`
- Payload: `signal_set_id:uint8` or explicit signal IDs.

Minimum response entries:

- `bus_voltage`
- `current_d`
- `current_q`
- `mechanical_speed`
- `speed_target_mechanical`
- `run_state`
- `system_mode`
- `fault_word`

Response payload:

| Field | Type | Description |
|---|---|---|
| `status` | uint8 | OK or error. |
| `request_command_id` | uint8 | `0x50`. |
| `timestamp_us` | uint32 | Firmware monotonic timestamp. |
| `sample_counter` | uint32 | Incrementing counter. |
| `signal_count` | uint8 | Number of entries. |
| entries | repeated | `signal_id:uint16`, `value_type:uint8`, typed value. |

### START_TELEMETRY_STREAM

Purpose:

- Start periodic telemetry for Dashboard, Scope, Logger, and Report.

Request:

- Command ID: `0x51`
- Payload:
  - `stream_id:uint8`
  - `signal_set_id:uint8`
  - `rate_hz:uint16`

Rules:

- Start with 10-50 Hz for GUI bring-up.
- Do not stream from the FOC ISR.
- Snapshot variables safely outside time-critical code.

### STOP_TELEMETRY_STREAM

Purpose:

- Stop periodic telemetry.

Request:

- Command ID: `0x52`
- Payload: `stream_id:uint8`

### READ_PARAMETER

Purpose:

- Read one parameter by ID.

Request:

- Command ID: `0x40`
- Payload: `parameter_id:uint16`

Response:

- `status`
- `request_command_id`
- `parameter_id`
- `value_type`
- `value`

### WRITE_PARAMETER

Purpose:

- Write one safe parameter by ID.

Request:

- Command ID: `0x41`
- Payload:
  - `parameter_id:uint16`
  - `value_type:uint8`
  - `value`

Rules:

- Firmware must validate min/max and enum range.
- Firmware must reject read-only parameters.
- Firmware must reject unsafe writes while running.
- Firmware should echo the applied value.

### MOTOR_ENABLE

Purpose:

- Request operation state after safety checks.

Request:

- Command ID: `0x10`
- Payload: optional requested mode.

Response should include:

- `status`
- `ctrl_bit`
- `state_bit`
- `fault_word`

### MOTOR_STOP

Purpose:

- Stop motor safely.

Request:

- Command ID: `0x11`
- Payload: `stop_type:uint8`

Stop types:

- `0x00`: reset stop
- `0x01`: quick stop
- `0x02`: fault stop

### CLEAR_FAULT

Purpose:

- Clear clearable fault bits.

Request:

- Command ID: `0x12`
- Payload: `clear_mask:uint32`

Rules:

- Firmware decides which bits are safe to clear.
- Response returns remaining `fault_word`.

### REQUEST_FAULT_STATUS

Purpose:

- Read current fault status without changing state.

Request:

- Command ID: `0x60`
- Payload: none.

Response:

- `fault_word:uint32`
- optional `latched_fault_word:uint32`
- `state_bit:uint8`
- optional protection status.

## Safety Restrictions

Minimum safety rules before motor commands:

- PING must pass.
- Firmware info must be readable.
- Fault status must be readable.
- Telemetry snapshot must be readable.
- `fault_word` must be zero or in a known safe state.
- Motor enable must be blocked if communication is stale.
- Parameter writes to motor constants, protection thresholds, observer values, and encoder offsets should be blocked while running unless explicitly whitelisted.
- GUI must not block on serial timeouts.
- Firmware must rate-limit or reject unsupported stream rates.

## Phase 7.2 Implementation Boundary

Phase 7.2 should implement only:

- Serial port open/close in `SerialBackend`.
- Binary frame encode/decode helpers.
- CRC16 implementation and tests.
- Sequence number allocation.
- Timeout handling.
- `PING` command request/response.
- No Dashboard, Scope, Parameter, Command, Fault, Logger, or Report page changes unless a tiny connection selector is explicitly approved later.
- No motor enable, parameter write, or telemetry stream implementation yet.

Phase 7.2 acceptance:

- Unit tests cover frame encode/decode and CRC vector.
- SerialBackend can send PING and parse response on a connected AxDr_L board or loopback test firmware.
- Failure paths produce clear exceptions or status messages.
- UI architecture remains backend-driven.

## Phase 7.1 Deliverables

- Confirm Type-C behavior.
- Confirm J1 UART mapping and baud rate.
- Freeze binary frame format.
- Freeze CRC variant and test vector.
- Freeze PING command and response.
- Decide initial telemetry signal set.
- Update `docs/axdr_l_protocol_plan.md` if any protocol decisions differ from this plan.
- Keep eMotor-Studio source code unchanged until Phase 7.2.
