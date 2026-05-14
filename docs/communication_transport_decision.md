# Communication Transport Decision

## Scope

This document records the Phase 7.1-A transport decision for connecting eMotor-Studio to the AxDr_L development board. It is a planning document only. It does not implement SerialBackend, CAN, J-Link, RTT, or any real hardware communication.

## Board Communication Resources

Known AxDr_L board resources:

| Connector | Signals | Likely Role |
|---|---|---|
| J1 debug interface | `3.3V`, `SWDIO`, `SWCLK`, `UART TX`, `UART RX`, `GND` | SWD debug/programming plus a board-level UART suitable for host communication through a USB-TTL adapter. |
| J2 CAN interface | `CAN_L`, `CAN_H` | CAN bus connection for multi-node or industrial-style communication. |
| USB Type-C | Unknown: power only, USB CDC, or USB-to-UART bridge | Must be confirmed on hardware and in firmware/device manager. |

## J1 SWD + UART Role Split

J1 combines two different classes of interface:

- SWD: `SWDIO`, `SWCLK`, `GND`, and optionally power reference.
- UART: `UART TX`, `UART RX`, `GND`.

Recommended role split:

| Resource | Recommended Use |
|---|---|
| SWD / J-Link | Firmware flashing, breakpoints, watch variables, debug sessions, low-level bring-up, emergency diagnosis. |
| J-Link RTT | Optional engineering debug trace or special internal-variable tap when firmware enables RTT. |
| J1 UART | First reliable host communication path if USB Type-C does not enumerate as a COM port. |

Do not treat SWD as the default user-facing upper-computer transport. It is powerful for debugging but awkward for a general motor-control GUI workflow.

## USB Type-C Confirmation Items

Before choosing the physical transport, confirm what the Type-C connector exposes:

1. Does Windows Device Manager show a new COM port after plugging Type-C in?
2. Does it enumerate as USB CDC, USB serial bridge, DFU, composite device, or no data device?
3. Does AxDr_L firmware initialize USB CDC receive/transmit paths for this connector?
4. Does the board need external power for USB data to work?
5. Can the Type-C path send and receive bytes with a serial terminal?
6. Does it share the same UART as J1, or is it native USB CDC?

If Type-C enumerates as a COM port and supports bidirectional bytes, it should be the first V1.1 physical path because it requires the least extra hardware.

If Type-C is power-only, use J1 UART through a 3.3 V USB-TTL adapter.

## CAN Applicability

CAN is important, but it is not the shortest path for V1.1.

CAN is best for:

- Multi-axis systems.
- Long cable runs and noisy environments.
- Distributed motor nodes.
- Industrial-style integration.
- Deterministic bus arbitration and node IDs.
- Future real robot or actuator-network workflows.

CAN is less convenient for the first bring-up because:

- It requires a CAN adapter on the PC.
- The app needs adapter selection, bitrate setup, and frame mapping.
- Firmware and GUI need node ID and bus error handling earlier.
- It adds more variables before basic ping/telemetry are proven.

Recommendation: keep CAN in the architecture and protocol plan, but implement it after the serial/USB CDC protocol proves the command and telemetry model.

## J-Link / RTT Applicability

J-Link and RTT are useful, but not recommended as the main eMotor-Studio V1.1 transport.

Best uses:

- Firmware flashing.
- Breakpoints and stepping.
- Watching internal variables during control-loop development.
- Capturing debug logs without consuming UART.
- Comparing firmware internal values against eMotor-Studio telemetry.
- Emergency inspection when the normal protocol fails.

Limitations as main upper-computer transport:

- Requires a debugger and vendor tooling.
- Less friendly for students, courses, and non-debug workflows.
- Not a normal field or user-facing transport.
- Harder to share with CAN/serial production workflows.
- Can disturb timing or require debug-build-only firmware features.
- Does not naturally model ACK/NACK, command safety, telemetry rate, or multi-device addressing.

Conclusion: J-Link / RTT should be a debug auxiliary path, not the default host communication path.

## Reference Project Transport Comparison

Local reference projects were checked lightly through README files and communication-related source files.

| Project | Main Transport Observed | Notes For eMotor-Studio |
|---|---|---|
| SimpleFOCStudio | Serial / UART / USB serial via pyserial | README states serial port communication with SimpleFOC Commander; code uses `serial.Serial` and 115200-style port config. Strong match for V1.1 serial-first approach. |
| pid-motor-control | UART serial binary protocol | README documents CRC-8 frames at 115200 baud; firmware has UART parser and GUI has `serial_client.py`. Strong match for minimum ping/telemetry/command protocol. |
| Interactive_PID_Controller | Serial over Arduino USB | README and `interfaz.py` use serial commands and a read thread. Good teaching-oriented precedent. |
| Spectral-motor-GUI | UART serial first; CAN planned/partially surfaced | Requirements include `pyserial` and `python-can`; UI has UART fields and CAN fields; README TODO mentions CAN bus. Good precedent for serial-first, CAN-later. |
| odrive-gui | ODrive Python stack over USB discovery; optional device path such as `/dev/ttyUSB0` | Web UI uses `odrive.start_discovery(odrive.default_usb_search_path)`. Good precedent for hiding transport behind a device/backend package. |
| vesc_tool | Serial/USB, CAN, BLE UART, TCP/UDP | Mature tool supports multiple transports. It still has serial USB connection and CAN scan concepts; good long-term architecture precedent, too broad for Phase 7.1 implementation. |

No reviewed reference uses J-Link / RTT as the normal user-facing upper-computer transport.

## Transport Options

### Option A: USB Type-C As COM Port

Pros:

- Simplest user workflow if it enumerates.
- No extra USB-TTL adapter.
- Matches many motor GUI tools that use serial/USB CDC.
- Can reuse `SerialBackend` and `pyserial`.
- Good for courses and demos.

Cons:

- Type-C function is currently unconfirmed.
- Firmware USB CDC receive path may need work.
- USB reset/disconnect behavior must be handled.

### Option B: J1 UART Through USB-TTL

Pros:

- Explicit, debuggable, and hardware-simple.
- Fits the exposed J1 UART TX/RX pins.
- Works even if Type-C is power-only.
- Matches SimpleFOC/PID-style upper-computer patterns.
- Easy to test with a serial terminal.

Cons:

- Requires correct 3.3 V USB-TTL wiring.
- Requires TX/RX crossover and common GND.
- Less polished than one-cable Type-C.

Wiring rule:

- Board `UART TX` -> USB-TTL `RX`
- Board `UART RX` -> USB-TTL `TX`
- Board `GND` -> USB-TTL `GND`
- Use 3.3 V logic only.
- Do not connect 5 V TTL to 3.3 V UART pins.
- Use board power according to the hardware design; do not back-power through an adapter unless explicitly intended.

### Option C: CAN On J2

Pros:

- Best for multi-axis and industrial use.
- Robust in noisy environments.
- Natural for node addressing.
- Good long-term direction.

Cons:

- Requires PC CAN adapter and bus setup.
- More complex software and firmware bring-up.
- Less convenient for the first PING protocol.
- Needs termination and wiring discipline.

### Option D: J-Link / RTT

Pros:

- Excellent for firmware debugging.
- Can expose internal variables during development.
- Useful when normal protocol is not working.

Cons:

- Not suitable as default upper-computer transport.
- Requires debugger hardware and tooling.
- Debug-centric, not user-centric.
- Harder to evolve into multi-axis or course-friendly workflows.

## Recommended Priority

| Priority | Transport | Decision |
|---:|---|---|
| 1 | USB Type-C if it enumerates as a COM port | Use as V1.1 default physical path. |
| 2 | J1 UART through 3.3 V USB-TTL | Use as fallback and guaranteed serial bring-up path. |
| 3 | CAN on J2 | Add after serial protocol is proven, likely V1.2 or V2.0 depending on hardware goals. |
| 4 | J-Link / RTT | Keep as debug auxiliary, not main app transport. |

## Final V1.1 Default Route

Recommended V1.1 default route:

1. Confirm whether Type-C appears as a COM port.
2. If yes, implement the first `SerialBackend` PING over that COM port.
3. If no, use J1 UART with a 3.3 V USB-TTL adapter and implement the same SerialBackend protocol there.
4. Keep the protocol independent of whether the physical serial bytes come from USB CDC, USB-to-UART, or J1 UART.

In other words: V1.1 should be serial-protocol first, physical-port flexible.

Default app concept:

- Backend class: `SerialBackend`
- First command: `ping`
- First telemetry: a small fixed snapshot
- First configuration path: serial port name + baud rate
- UI pages remain transport-agnostic

## V1.2 / V2.0 Extension Route

Recommended expansion:

- V1.1: SerialBackend over USB CDC or J1 UART, with ping, firmware info, telemetry, parameter read/write, and basic motor commands.
- V1.2: Add CANBackend for single-node CAN and shared command IDs where practical.
- V1.3: Add multi-node CAN workflows, node scan, per-axis dashboard, and bus diagnostics.
- V2.0: Add industrial/multi-axis workflows, logging sessions across nodes, fault correlation, and optional J-Link/RTT debug overlay for firmware developers.

## Decision Summary

eMotor-Studio should not choose J-Link as the default upper-computer communication method. J-Link and RTT are valuable debug tools, but V1.1 should prioritize a serial protocol over USB Type-C COM if available, or J1 UART through USB-TTL if Type-C is power-only. CAN should remain a planned engineering-grade extension after the serial command and telemetry model is proven.
