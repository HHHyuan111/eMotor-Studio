# AxDr_L Signal Mapping

This document proposes the Phase 3 source for `configs/signals.json`. It is analysis-only for Phase 2.5; no config file is created here.

| name | source_in_axdr_l | display_name | type | unit | description | dashboard | scope | logger |
|---|---|---|---|---|---|---|---|---|
| `phase_current_a` | `pm.foc.i_a` | Phase Current A | float | A | Phase A current after offset compensation and scaling. | true | true | true |
| `phase_current_b` | `pm.foc.i_b` | Phase Current B | float | A | Phase B current after offset compensation and scaling. | false | true | true |
| `phase_current_c` | `pm.foc.i_c` | Phase Current C | float | A | Phase C current after offset compensation and scaling. | false | true | true |
| `current_alpha` | `pm.foc.i_alph` | Alpha Current | float | A | Clarke alpha current. | false | true | true |
| `current_beta` | `pm.foc.i_beta` | Beta Current | float | A | Clarke beta current. | false | true | true |
| `current_d` | `pm.foc.i_d` | D-Axis Current | float | A | Park d-axis current feedback. | true | true | true |
| `current_q` | `pm.foc.i_q` | Q-Axis Current | float | A | Park q-axis current feedback. | true | true | true |
| `current_abs` | `pm.foc.i_abs` | Current Magnitude | float | A | Current magnitude used for monitoring/protection. | true | true | true |
| `voltage_d` | `pm.foc.v_d` | D-Axis Voltage | float | V | D-axis voltage command/output. | false | true | true |
| `voltage_q` | `pm.foc.v_q` | Q-Axis Voltage | float | V | Q-axis voltage command/output. | false | true | true |
| `voltage_alpha` | `pm.foc.v_alph` | Alpha Voltage | float | V | Inverse Park alpha voltage. | false | true | true |
| `voltage_beta` | `pm.foc.v_beta` | Beta Voltage | float | V | Inverse Park beta voltage. | false | true | true |
| `bus_voltage` | `pm.foc.vbus` | Bus Voltage | float | V | DC bus voltage derived from ADC sample and board scaling. | true | true | true |
| `bus_current` | `pm.foc.ibus` | Bus Current | float | A | DC bus current estimate. | true | true | true |
| `electrical_angle` | `pm.foc.p_e` | Electrical Angle | float | rad | Electrical rotor angle used by FOC. | true | true | true |
| `control_theta` | `pm.foc.theta` | Control Theta | float | rad | Angle used inside FOC transform in the current control step. | false | true | true |
| `encoder_angle` | `pm.foc.e_pr` | Encoder Angle | float | rad | Raw primary encoder position mapped to radians. | true | true | true |
| `rotor_position_single` | `pm.foc.sp_r` | Rotor Position | float | rad | Single-turn rotor position. | false | true | true |
| `rotor_position_multi` | `pm.foc.mp_r` | Multi-Turn Rotor Position | float | rad | Multi-turn rotor-side position. | false | true | true |
| `mechanical_position_single` | `pm.foc.sp_m` | Mechanical Position | float | rad | Single-turn output/mechanical position. | false | true | true |
| `mechanical_position_multi` | `pm.foc.mp_m` | Multi-Turn Mechanical Position | float | rad | Multi-turn mechanical position after gear ratio. | true | true | true |
| `electrical_speed` | `pm.foc.we` | Electrical Speed | float | rad/s | Electrical angular velocity. | false | true | true |
| `rotor_speed` | `pm.foc.wr` | Rotor Speed | float | rad/s | Rotor-side angular velocity. | true | true | true |
| `rotor_speed_filtered` | `pm.foc.wr_f` | Filtered Rotor Speed | float | rad/s | Low-pass filtered rotor speed. | true | true | true |
| `mechanical_speed` | `pm.foc.wm` | Mechanical Speed | float | rad/s | Mechanical/output angular velocity. | true | true | true |
| `speed_target_rotor` | `pm.ctrl.wr_set` | Rotor Speed Target | float | rad/s | Rotor-side speed setpoint. | true | true | true |
| `speed_target_mechanical` | `pm.ctrl.wm_set` | Mechanical Speed Target | float | rad/s | Mechanical/output speed setpoint. | true | true | true |
| `current_target_d` | `pm.ctrl.id_set` | D Current Target | float | A | D-axis current setpoint. | true | true | true |
| `current_target_q` | `pm.ctrl.iq_set` | Q Current Target | float | A | Q-axis current setpoint. | true | true | true |
| `position_target_mechanical` | `pm.ctrl.posm_set` | Mechanical Position Target | float | rad | Mechanical/output position setpoint. | true | true | true |
| `position_target_rotor` | `pm.ctrl.posr_set` | Rotor Position Target | float | rad | Rotor-side position setpoint. | false | true | true |
| `torque_target_mechanical` | `pm.ctrl.torm_set` | Torque Target | float | N*m | Mechanical torque setpoint. | true | true | true |
| `duty_a` | `pm.foc.dtc_a` | PWM Duty A | float | ratio | SVPWM duty for phase A. | false | true | true |
| `duty_b` | `pm.foc.dtc_b` | PWM Duty B | float | ratio | SVPWM duty for phase B. | false | true | true |
| `duty_c` | `pm.foc.dtc_c` | PWM Duty C | float | ratio | SVPWM duty for phase C. | false | true | true |
| `duty_now` | `pm.foc.duty_now` | Duty Now | float | ratio | Current duty estimate if populated by firmware. | true | true | true |
| `coil_temperature` | `pm.foc.Tcoil` | Coil Temperature | float | degC | Motor coil/rotor temperature estimate. | true | true | true |
| `mos_temperature` | `pm.foc.Tmos` | MOS Temperature | float | degC | Power MOS temperature estimate. | true | true | true |
| `control_state` | `pm.ctrl_bit` | Control State | enum | state | `reset`, `start`, or `opera`. | true | false | true |
| `run_state` | `pm.state_bit` | Run State | enum | state | `stop`, `prech`, `runing`, or `fault`. | true | false | true |
| `system_mode` | `pm.mode.sys` | System Mode | enum | mode | Debug, release, calibration, or halt mode. | true | false | true |
| `debug_mode` | `pm.mode.debug` | Debug Mode | enum | mode | Debug-mode control selection. | false | false | true |
| `release_mode` | `pm.mode.release` | Release Mode | enum | mode | Release-mode control selection. | true | false | true |
| `calibration_mode` | `pm.mode.calibrat` | Calibration Mode | enum | mode | Calibration or identification flow selection. | false | false | true |
| `fault_word` | `pm.fault.all` | Fault Word | uint32 | bitmask | Aggregated PMSM fault bitmask. | true | true | true |
| `fault_over_current` | `pm.fault.bit.ov_curr` | Over Current | bool | flag | Overcurrent fault bit. | true | false | true |
| `fault_under_voltage` | `pm.fault.bit.un_volt` | Under Voltage | bool | flag | Undervoltage fault bit. | true | false | true |
| `fault_over_voltage` | `pm.fault.bit.ov_volt` | Over Voltage | bool | flag | Overvoltage fault bit. | true | false | true |
| `fault_mos_over_temp` | `pm.fault.bit.ov_tmos` | MOS Over Temperature | bool | flag | Power MOS over-temperature fault bit. | true | false | true |
| `fault_coil_over_temp` | `pm.fault.bit.ov_tcoi` | Coil Over Temperature | bool | flag | Coil/rotor over-temperature fault bit. | true | false | true |
| `fault_encoder_error` | `pm.fault.bit.enc_err` | Encoder Error | bool | flag | Encoder error fault bit. | true | false | true |
| `fault_current_offset` | `pm.fault.bit.ioff_err` | Current Offset Error | bool | flag | Current offset calibration fault bit. | true | false | true |
| `fault_link_lost` | `pm.fault.bit.off_link` | Link Lost | bool | flag | Host link timeout fault bit. | true | false | true |
| `fault_over_speed` | `pm.fault.bit.ov_speed` | Over Speed | bool | flag | Overspeed fault bit. | true | false | true |

## Notes

- Phase 3 should use these names as the first source of truth when generating `configs/signals.json`.
- Units are inferred from symbols and control equations. Firmware should eventually expose a versioned signal descriptor to remove inference.
- `pm.foc.Tcoil`, `pm.foc.Tmos`, `pm.foc.ibus`, and `pm.foc.duty_now` exist as runtime fields, but their update paths should be verified on hardware before treating them as always valid.
- The VOFA telemetry function currently streams ADC raw channels by default, with many richer channels commented out. eMotor-Studio should not assume a stable VOFA channel order.
