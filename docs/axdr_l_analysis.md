# AxDr_L Target Firmware Analysis

## Snapshot

- Repository: `https://github.com/HHHyuan111/AxDr_L`
- Local path: `external/target_firmware/AxDr_L`
- Fetch method: `git clone`
- Branch: `main`
- Commit: `7c2241061ae5318d9a47d3404cec92412767b802`
- Clone/verification time: `2026-05-13T19:31:02.8863865+08:00`
- Existing host protocol found: partial telemetry only. USB CDC, UART, and FDCAN plumbing exists; a complete command/parameter protocol parser was not found in the scanned application code.

## Project Structure

| Path | Role |
|---|---|
| `README.md` | Project overview for the AxDr learning board firmware. |
| `0.AxDr_simulink/` | Simulink reference material. |
| `1.AxDr_Drag_VF/` | Earlier V/F drag-control STM32 project. |
| `AxDr_App/` | Main STM32G474 firmware project analyzed for eMotor-Studio alignment. |
| `AxDr_App/Core/` | STM32Cube generated peripheral init, interrupts, and main entry. |
| `AxDr_App/User/motor/` | PMSM/FOC control, state machine, observers, encoder, calibration, identification. |
| `AxDr_App/User/bsp/` | UART, FDCAN, flash, GPIO support wrappers. |
| `AxDr_App/User/moldue/` | LCD/display, VOFA telemetry, W25Q flash module code. |
| `AxDr_App/USB_Device/` | USB CDC device stack glue. |
| `AxDr_App/MDK-ARM/` | Keil project and generated build artifacts. |
| `AxDr_App/Drivers/`, `AxDr_App/Middlewares/` | STM32 HAL/CMSIS/USB vendor code; not target logic. |

## Main Entry

Main entry is `AxDr_App/Core/Src/main.c`.

Important startup sequence:

- Initializes GPIO, DMA, SPI1, TIM1, TIM3, USB CDC, ADC1, ADC2, USART3, FDCAN1, SPI3.
- Starts TIM3 base timer.
- Calibrates ADC1/ADC2.
- Starts ADC injected conversion: ADC1 interrupt mode, ADC2 non-interrupt injected mode.
- Starts regular ADC DMA buffers for ADC1 and ADC2.
- Starts TIM1 channel 4 PWM compare trigger.
- Calls `pmsm_init()` and `foc_pwm_start()`.
- Initializes LCD and calls `display_foc()`.

The `while (1)` loop is mostly idle. It contains a 1 ms tick section with `vofa_start()` commented out. The real control work is therefore interrupt/callback driven, not main-loop driven.

## Main Control Loop

The motor control loop is implemented in `AxDr_App/User/motor/foc_ctrl.c` inside `HAL_ADCEx_InjectedConvCpltCallback`.

Observed callback sequence:

1. `send_encoder_read_command(&pm)`
2. `pos_calc(&pm)`
3. `foc_adc_sample(&pm)`
4. `foc_para_calc(&pm)`
5. Optional/commented display, control set, fault check, VOFA telemetry.
6. `pmsm_state_ctrl(&pm)`

This callback is triggered by injected ADC conversion. `AxDr_App/AxDr.ioc` configures injected ADC conversion from TIM1 CC4, so this is effectively the high-rate FOC cycle.

## Periodic Tasks And Interrupts

| Item | Location | Notes |
|---|---|---|
| ADC injected conversion complete | `User/motor/foc_ctrl.c` | Core FOC callback. |
| ADC regular DMA | `Core/Src/main.c`, `Core/Src/adc.c` | Regular ADC buffers started for ADC1/ADC2. |
| TIM1 PWM trigger | `Core/Src/main.c`, `Core/Src/tim.c` | TIM1 channel 4 compare starts PWM/ADC timing. |
| USB CDC receive/transmit | `USB_Device/App/usbd_cdc_if.c` | Receive callback only re-arms USB reception. |
| UART idle DMA callbacks | `User/bsp/bsp_uart.c` | Weak `uart_rx_callback` and `uart_tx_callback`; no app parser located. |
| FDCAN RX FIFO callback | `User/bsp/bsp_fdcan.c` | Weak `fdcan1_rx_callback`; no app parser located. |

## Motor Control Modules

| Module | Location | Notes |
|---|---|---|
| Core types and global `pm` object | `User/motor/common.h`, `User/motor/foc_drv.c` | `pmsm_t pm` is the central runtime object. |
| State and mode control | `User/motor/foc_ctrl.c` | `pmsm_state_ctrl`, `pmsm_mode_ctrl`, debug/release/calibration/halt logic. |
| FOC math | `User/motor/foc_calc.c` | Clarke/Park/inverse transforms and SVM. |
| FOC driver/control loops | `User/motor/foc_drv.c` | Motor defaults, board/protect init, PI calc, voltage/current/speed/position control, ADC sample, PWM output. |
| PID | `User/motor/pid.c` | Parallel PID, serial PID, PDFF style control. |
| Position calculation | `User/motor/pos_calc.c` | Sensor and sensorless position paths. |
| Encoders | `User/motor/encoder.c` | MA732, MT6816, MT6825, DM485 encoder stubs/commented code. |
| Calibration | `User/motor/calibration.c` | Magnetic encoder calibration and LUT flow. |
| Parameter identification | `User/motor/idpm.c` | Rs, Ld/Lq/Ls, flux, Js/B identification sequence. |
| Observers | `User/motor/nlob.c`, `alob.c`, `scvm.c`, `eh_observer.c`, `pll.c` | Sensorless and torque/speed observer logic. |
| Trajectory | `User/motor/trap_traj.c` | Speed and position trajectory planning/evaluation. |

## Communication Code

| Transport | Location | Finding |
|---|---|---|
| USB CDC | `USB_Device/App/usbd_cdc_if.c` | `CDC_Transmit_FS` works; `CDC_Receive_FS` only re-arms reception. No command parser found. |
| VOFA telemetry | `User/moldue/vofa.c` | Sends float channels and VOFA frame tail `00 00 80 7f`; currently many candidate channels are commented. |
| UART3 | `User/bsp/bsp_uart.c`, `Core/Src/usart.c` | Send, DMA send, receive-to-idle helpers and weak callbacks exist. No application protocol found. |
| FDCAN1 | `User/bsp/bsp_fdcan.c`, `Core/Src/fdcan.c` | FDCAN FD/BRS send/receive wrappers and weak RX callback exist. No application protocol found. |
| DM485 encoder | `User/motor/encoder.c` | Read/mod command functions and UART ISR are currently commented/stubbed. |

Conclusion: AxDr_L has useful physical transports and a VOFA-style debug telemetry path, but no located full host protocol for enable/stop, parameter read/write, control-mode switching, or target setpoints.

## Parameter Definition Locations

| Parameter Area | Source Location | Examples |
|---|---|---|
| Motor parameters | `User/motor/common.h`, `User/motor/foc_drv.c` | `pn`, `Rs`, `Ld`, `Lq`, `Ls`, `Ldif`, `flux`, `B`, `Js`, `Gr`, `Kt`, offsets. |
| Control setpoints/limits | `User/motor/common.h`, `User/motor/foc_drv.c` | `vd_set`, `vq_set`, `id_set`, `iq_set`, `wr_set`, `wm_set`, `posm_set`, `pmax_iq`, `pmax_vel`. |
| PI/PID parameters | `User/motor/common.h`, `User/motor/foc_drv.c`, `User/motor/pid.c` | `id_pi`, `iq_pi`, `spd_pi`, `pos_pi`, limits, sampling times. |
| Protection thresholds | `User/motor/common.h`, `User/motor/foc_drv.c` | `uv_value`, `ov_value`, `oc_value`, `ot_value`, `omt_value`, `ov_speed_value`, debounce counts. |
| Encoder parameters | `User/motor/common.h`, `User/motor/encoder.c` | encoder type, direction, CPR, bit width, offset. |
| Identification parameters | `User/motor/common.h`, `User/motor/idpm.c` | `is_max`, `vs_step`, `vd_plus`, `vq_plus`, `fiq_ref`, `we_l`, `we_h`, `Jiq_max`, `lambda`. |
| Observer parameters | `User/motor/common.h`, `User/motor/nlob.c`, `alob.c`, `scvm.c` | observer gains, PLL gains, sample time, flux/current pointers. |

## Real-Time Variables

The primary real-time variable source is `pmsm_foc_t` in `User/motor/common.h`, updated by `foc_adc_sample`, `foc_para_calc`, `pos_calc`, and control functions.

Important groups:

- Current feedback: `pm.foc.i_a`, `i_b`, `i_c`, `i_d`, `i_q`, `i_abs`, filtered variants.
- Voltage feedback/control: `pm.foc.vbus`, `ibus`, `v_d`, `v_q`, `v_alph`, `v_beta`, phase voltages.
- Speed/position: `pm.foc.p_e`, `theta`, `sp_r`, `mp_r`, `sp_m`, `mp_m`, `we`, `wr`, `wr_f`, `wm`.
- PWM/duty: `pm.foc.dtc_a`, `dtc_b`, `dtc_c`, `duty_now`.
- Thermal: `pm.foc.Tcoil`, `Tmos`.
- Control state: `pm.ctrl_bit`, `pm.state_bit`, `pm.mode.*`.
- Fault state: `pm.fault.all`, `pm.fault.bit.*`.

## Fault Codes

Faults are represented as a bitfield union `pmsm_fault_t` in `User/motor/common.h`.

Located bits:

| Bit Name | Meaning |
|---|---|
| `ov_curr` | Over current. |
| `un_volt` | Under voltage. |
| `ov_volt` | Over voltage. |
| `ov_tmos` | MOSFET over temperature. |
| `ov_tcoi` | Coil over temperature. |
| `enc_err` | Encoder error. |
| `ioff_err` | Current offset error. |
| `off_link` | Communication/link timeout. |
| `ov_speed` | Over speed. |

`pmsm_fault_check()` implements link timeout, overspeed, MOS/coil temperature, undervoltage, and overvoltage checks. The callback currently has `pmsm_fault_check(&pm)` commented out, so fault checking may be disabled in the current firmware build unless enabled elsewhere.

## Control State Machine

### Power State

`pm.ctrl_bit`:

- `reset`
- `start`
- `opera`

`pm.state_bit`:

- `stop`
- `prech`
- `runing`
- `fault`

`pmsm_state_ctrl()` maps `ctrl_bit` and `fault` state into PWM start/stop, reset, precharge/run/fault states. If any fault bit is set, `state_bit` becomes `fault` and `ctrl_bit` is forced to `reset`.

### Mode State

`pm.mode.sys`:

- `debug_mode`
- `release_mode`
- `calibrat_mode`
- `halt_mode`

`debug_mode` supports V/F, I/F, voltage open-loop, current closed-loop, speed-current cascade, and position-speed-current cascade. Some speed-voltage modes are declared but not implemented.

`release_mode` supports MIT, torque, velocity, position, CST, CSV, and CSP style modes.

`calibrat_mode` supports rotor encoder calibration, motor parameter identification, and anticogging calibration.

`halt_mode` supports quick stop and fault stop.

## Host Interface Concerns For eMotor-Studio

eMotor-Studio should align its V1 MockBackend and V1.1 protocol with these AxDr_L objects:

- Runtime telemetry from `pm.foc`, `pm.ctrl`, `pm.mode`, `pm.state_bit`, and `pm.fault`.
- Writable parameters from `pm.para`, `pm.ctrl`, `pm.app_ctrl`, `pm.protect`, encoder structs, observer structs, and identification structs.
- Commands should map to `ctrl_bit`, `mode`, `cmd`, and selected `ctrl` fields instead of generic GUI-only state.
- Fault display should map to the exact `pmsm_fault_t` bit names.
- Serial/CAN protocol should be added as a thin transport over the same command and parameter model.

## Not Found Or Uncertain

- No complete structured host command protocol was found.
- No parameter read/write protocol was found.
- No stable public signal schema file was found in AxDr_L.
- `pmsm_fault_check()` exists but is commented out in the observed ADC callback.
- Current overcurrent protection bit exists, but full current-protection implementation was not clearly located in `pmsm_fault_check()`.
- Some declared modes have stubs or no obvious implementation in the scanned code.
- Some source comments appear mojibake due encoding, so conclusions are based primarily on symbol names and code flow.
