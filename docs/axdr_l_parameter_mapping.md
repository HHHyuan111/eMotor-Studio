# AxDr_L Parameter Mapping

This document proposes the Phase 3 source for `configs/parameters.json`. It is analysis-only for Phase 2.5; no config file is created here.

`min` and `max` values marked as `TBD` should be confirmed against hardware limits before real writes are allowed. Defaults come from current AxDr_L initialization where found, especially `pmsm_2312s_init()` because `pmsm_init()` currently calls it.

| name | source_in_axdr_l | display_name | type | default | unit | min | max | group | description |
|---|---|---|---|---|---|---|---|---|---|
| `motor_rated_voltage` | `pm.para.rated_voltage` | Rated Voltage | float | 24.0 | V | 0 | 60 | Motor | Rated motor voltage. |
| `motor_rated_speed` | `pm.para.rated_speed` | Rated Speed | float | `10000/9.55` | rad/s | 0 | TBD | Motor | Rated mechanical speed, initialized from rpm conversion. |
| `motor_rated_torque` | `pm.para.rated_torque` | Rated Torque | float | 0.8 | N*m | 0 | TBD | Motor | Rated torque. |
| `motor_peak_torque` | `pm.para.peak_torque` | Peak Torque | float | 2.0 | N*m | 0 | TBD | Motor | Peak torque used by software limits. |
| `motor_peak_speed` | `pm.para.peak_speed` | Peak Speed | float | `10000/9.55` | rad/s | 0 | TBD | Motor | Peak speed used by software limits. |
| `motor_pole_pairs` | `pm.para.pn` | Pole Pairs | float | 7 | count | 1 | TBD | Motor | Motor pole-pair count. |
| `motor_phase_resistance` | `pm.para.Rs` | Phase Resistance | float | 0.108945489 | ohm | 0 | TBD | Motor | Stator phase resistance used by PI and observers. |
| `motor_inductance_d` | `pm.para.Ld` | D Inductance | float | `1.97248246e-05` | H | 0 | TBD | Motor | D-axis inductance. |
| `motor_inductance_q` | `pm.para.Lq` | Q Inductance | float | `2.02818483e-05` | H | 0 | TBD | Motor | Q-axis inductance. |
| `motor_inductance_s` | `pm.para.Ls` | Stator Inductance | float | `2.00033355e-07` | H | 0 | TBD | Motor | Scalar inductance used by current PI and observers. Value should be verified because it differs sharply from Ld/Lq. |
| `motor_inductance_diff` | `pm.para.Ldif` | Inductance Difference | float | `5.57023668e-07` | H | TBD | TBD | Motor | Difference between d/q inductance identification results. |
| `motor_flux` | `pm.para.flux` | Flux Linkage | float | `0.000884152076` | Wb | 0 | TBD | Motor | Flux linkage used by torque constant and observers. |
| `motor_viscous_friction` | `pm.para.B` | Viscous Friction | float | `0.000188353` | N*m*s/rad | 0 | TBD | Motor | Mechanical damping/friction parameter. |
| `motor_inertia` | `pm.para.Js` | Inertia | float | `2.19904655e-06` | kg*m^2 | 0 | TBD | Motor | Rotor/load inertia estimate. |
| `motor_gear_ratio` | `pm.para.Gr` | Gear Ratio | float | 1.0 | ratio | 0 | TBD | Motor | Gear ratio from rotor side to output side. |
| `motor_current_loop_bandwidth` | `pm.para.ibw` | Current Loop Bandwidth | float | 500.0 | rad/s | 0 | TBD | Current Loop | Bandwidth used by `foc_cur_pi_calc()`. |
| `motor_control_delta` | `pm.para.delta` | Control Delta | float | 4.0 | ratio | 0 | TBD | Speed Loop | Tuning factor used by speed PI calculation. |
| `encoder_electrical_offset` | `pm.para.e_off` | Electrical Offset | float | 2.34354496 | rad | `-2*pi` | `2*pi` | Encoder | Electrical angle offset. |
| `encoder_rotor_offset` | `pm.para.r_off` | Rotor Offset | float | 2.12998796 | rad | `-2*pi` | `2*pi` | Encoder | Rotor mechanical offset. |
| `encoder_mechanical_offset` | `pm.para.m_off` | Mechanical Offset | float | 0.0 | rad | `-2*pi` | `2*pi` | Encoder | Output/mechanical offset. |
| `encoder_phase_order` | `pm.para.phase_order` | Phase Order | enum | `ACB_PHASE` | enum | `ABC_PHASE` | `ACB_PHASE` | Encoder | Phase order used when assigning PWM outputs. |
| `encoder_primary_type` | `pm.pos_box.sensory1` | Primary Encoder | enum | `MT6816` | enum | TBD | TBD | Encoder | Primary sensor type. |
| `position_source_mode` | `pm.pos_box.pos_mode` | Position Source | enum | `Sensorsory_s` | enum | TBD | TBD | Encoder | Single sensor, dual sensor, or sensorless position source. |
| `sensorless_observer` | `pm.pos_box.senless` | Sensorless Observer | enum | `Scvm` | enum | TBD | TBD | Observer | Sensorless observer selection. |
| `id_current_kp` | `pm.id_pi.kp` | Id Kp | float | computed | V/A | 0 | TBD | Current Loop | D-axis current loop proportional gain computed from `Ls * ibw`. |
| `id_current_ki` | `pm.id_pi.ki` | Id Ki | float | computed | V/(A*s) | 0 | TBD | Current Loop | D-axis current loop integral gain computed from `Rs * ibw`. |
| `iq_current_kp` | `pm.iq_pi.kp` | Iq Kp | float | computed | V/A | 0 | TBD | Current Loop | Q-axis current loop proportional gain computed from `Ls * ibw`. |
| `iq_current_ki` | `pm.iq_pi.ki` | Iq Ki | float | computed | V/(A*s) | 0 | TBD | Current Loop | Q-axis current loop integral gain computed from `Rs * ibw`. |
| `current_output_limit` | `pid_limit_init(&pm.id_pi/iq_pi, ...)` | Current PI Output Limit | float | 11.0 | V | 0 | TBD | Current Loop | Positive/negative output and integral limit for current PI. |
| `speed_kfp` | `pm.spd_pi.kfp` | Speed Feedforward Kfp | float | 1.1 | ratio | 0 | TBD | Speed Loop | Feedforward gain used by speed loop. |
| `speed_kf_damp` | `pm.spd_pi.kf_damp` | Speed Damping | float | 0.25 | ratio | 0 | TBD | Speed Loop | Damping factor used by speed loop. |
| `speed_kp` | `pm.spd_pi.kp` | Speed Kp | float | computed | A/(rad/s) | 0 | TBD | Speed Loop | Speed PI proportional gain computed by `foc_spd_pi_calc()`. |
| `speed_ki` | `pm.spd_pi.ki` | Speed Ki | float | A/rad | 0 | TBD | Speed Loop | Speed PI integral gain computed by `foc_spd_pi_calc()`. |
| `speed_output_limit` | `pid_limit_init(&pm.spd_pi, ...)` | Speed PI Output Limit | float | 20.0 | A | 0 | TBD | Speed Loop | Positive/negative speed PI output and integral limit. |
| `position_kp` | `pm.pos_pi.kp` | Position Kp | float | 12.0 | rad/s/rad | 0 | TBD | Position Loop | Position loop proportional gain. |
| `position_output_limit` | `pid_limit_init(&pm.pos_pi, ...)` | Position PI Output Limit | float | 200.0 | rad/s | 0 | TBD | Position Loop | Positive/negative position PI output and integral limit. |
| `velocity_acceleration` | `pm.ctrl.wm_acc` | Velocity Acceleration | float | 200.0 | rad/s^2 | 0 | TBD | Limits | Mechanical velocity acceleration limit. |
| `velocity_deceleration` | `pm.ctrl.wm_dec` | Velocity Deceleration | float | 200.0 | rad/s^2 | 0 | TBD | Limits | Mechanical velocity deceleration limit. |
| `positive_torque_limit` | `pm.app_ctrl.pmax_torm` | Positive Torque Limit | float | `peak_torque*0.8` | N*m | 0 | TBD | Limits | Positive output torque limit. |
| `negative_torque_limit` | `pm.app_ctrl.nmax_torm` | Negative Torque Limit | float | `-peak_torque*0.8` | N*m | TBD | 0 | Limits | Negative output torque limit. |
| `positive_velocity_limit` | `pm.app_ctrl.pmax_velm` | Positive Velocity Limit | float | `peak_speed*0.8` | rad/s | 0 | TBD | Limits | Positive mechanical speed limit. |
| `negative_velocity_limit` | `pm.app_ctrl.nmax_velm` | Negative Velocity Limit | float | `-peak_speed*0.8` | rad/s | TBD | 0 | Limits | Negative mechanical speed limit. |
| `positive_position_limit` | `pm.app_ctrl.pmax_posm` | Positive Position Limit | float | 20000.0 | rad | 0 | TBD | Limits | Positive multi-turn position limit. |
| `negative_position_limit` | `pm.app_ctrl.nmax_posm` | Negative Position Limit | float | -20000.0 | rad | TBD | 0 | Limits | Negative multi-turn position limit. |
| `protection_under_voltage` | `pm.protect.uv_value` | Under Voltage Threshold | float | 15.0 | V | 0 | 60 | Protection | DC bus undervoltage threshold. |
| `protection_over_voltage` | `pm.protect.ov_value` | Over Voltage Threshold | float | 60.0 | V | 0 | TBD | Protection | DC bus overvoltage threshold. |
| `protection_over_current` | `pm.protect.oc_value` | Over Current Threshold | float | 80.0 | A | 0 | TBD | Protection | Overcurrent threshold. Implementation should be verified. |
| `protection_mos_temp` | `pm.protect.ot_value` | MOS Temperature Threshold | float | 100.0 | degC | 0 | TBD | Protection | MOSFET over-temperature threshold. |
| `protection_coil_temp` | `pm.protect.omt_value` | Coil Temperature Threshold | float | 100.0 | degC | 0 | TBD | Protection | Coil/rotor over-temperature threshold. |
| `protection_link_timeout` | `pm.protect.link_out_time` | Link Timeout | float | 0.1 | s | 0 | TBD | Protection | Host link timeout debounce time. `time_value` is currently initialized to 0 in code. |
| `protection_overspeed` | `pm.protect.ov_speed_value` | Over Speed Threshold | float | TBD | rad/s | 0 | TBD | Protection | Overspeed threshold field exists; default assignment not clearly located. |
| `idpm_current_max` | `pm.idpm.is_max` | Identification Current Max | float | 5.0 | A | 0 | TBD | Identification | Current limit for resistance identification. |
| `idpm_current_threshold` | `pm.idpm.is_thre` | Identification Current Threshold | float | 0.1 | A | 0 | TBD | Identification | Current convergence threshold for identification. |
| `idpm_voltage_step` | `pm.idpm.vs_step` | Identification Voltage Step | float | 0.0001 | V | 0 | TBD | Identification | Voltage step for Rs identification. |
| `idpm_ld_voltage_plus` | `pm.idpm.vd_plus` | Ld Positive Voltage | float | 0.6 | V | TBD | TBD | Identification | Positive d-axis voltage for inductance identification. |
| `idpm_ld_voltage_minus` | `pm.idpm.vd_minu` | Ld Negative Voltage | float | -0.6 | V | TBD | TBD | Identification | Negative d-axis voltage for inductance identification. |
| `idpm_lq_voltage_plus` | `pm.idpm.vq_plus` | Lq Positive Voltage | float | 0.6 | V | TBD | TBD | Identification | Positive q-axis voltage for inductance identification. |
| `idpm_lq_voltage_minus` | `pm.idpm.vq_minu` | Lq Negative Voltage | float | -0.6 | V | TBD | TBD | Identification | Negative q-axis voltage for inductance identification. |
| `idpm_flux_iq_ref` | `pm.idpm.fiq_ref` | Flux Identification Iq | float | 5.0 | A | 0 | TBD | Identification | Iq reference for flux identification. |
| `idpm_speed_low` | `pm.idpm.we_l` | Flux Low Electrical Speed | float | 500.0 | rad/s | 0 | TBD | Identification | Low electrical speed used by flux identification. |
| `idpm_speed_high` | `pm.idpm.we_h` | Flux High Electrical Speed | float | 1000.0 | rad/s | 0 | TBD | Identification | High electrical speed used by flux identification. |
| `idpm_speed_acc` | `pm.idpm.we_acc` | Identification Acceleration | float | 500.0 | rad/s^2 | 0 | TBD | Identification | Acceleration for identification speed ramp. |
| `idpm_js_iq_max` | `pm.idpm.Jiq_max` | Inertia Identification Iq Max | float | 1.0 | A | 0 | TBD | Identification | Current limit for inertia identification. |
| `idpm_lambda` | `pm.idpm.lambda` | Identification Lambda | float | 31.4 | ratio | 0 | TBD | Identification | Identification tuning coefficient. |
| `observer_scvm_alpha0` | `pm.scvm.alpha0` | SCVM Alpha0 | float | 1500 | ratio | 0 | TBD | Observer | SCVM observer gain. |
| `observer_scvm_lambda1` | `pm.scvm.lamda1` | SCVM Lambda1 | float | 0.99 | ratio | 0 | 2 | Observer | SCVM observer lambda. |
| `observer_scvm_id_gain` | `pm.scvm.id_gain` | SCVM Id Gain | float | 0.8 | ratio | 0 | 2 | Observer | SCVM d-axis current injection gain. |
| `observer_nlob_gain` | `pm.nlob.gain` | NLOB Gain | float | 1000.0 | ratio | 0 | TBD | Observer | Nonlinear observer gain. |
| `observer_nlob_id_gain` | `pm.nlob.id_gain` | NLOB Id Gain | float | 1.0 | ratio | 0 | 2 | Observer | Nonlinear observer d-axis current injection gain. |
| `observer_pll_bandwidth` | `pm.nlob.pll.wn`, `alob.pll.wn` | Observer PLL Bandwidth | float | `100*2*pi` | rad/s | 0 | TBD | Observer | PLL natural frequency for angle tracking. |
| `observer_pll_damping` | `pm.nlob.pll.damp`, `alob.pll.damp` | Observer PLL Damping | float | 0.707 | ratio | 0 | TBD | Observer | PLL damping ratio. |

## Phase 3 Notes

- Generate `parameters.json` from this table, but mark risky real-hardware fields as read-only until AxDr_L exposes an explicit write protocol.
- Keep `source_in_axdr_l` in the config or in generated documentation for traceability.
- Defaults should reflect `pmsm_2312s_init()` for V1.0 MockBackend unless the user selects a PR60/other profile.
- Computed PI values can be displayed as parameters, but a future firmware protocol should clarify whether the GUI writes gains directly or writes high-level bandwidth/delta values.
