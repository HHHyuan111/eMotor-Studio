# Phase 9.4 Mock Ld/Lq Inductance Identification

## Goal

Phase 9.4 adds the second runnable identification loop: Mock d/q-axis inductance identification.

This phase still does not connect real hardware, does not inject current into a motor, and does not write parameters to AxDr_L.

## Implemented Service

`MockInductanceIdentification` generates a synthetic current-slope experiment:

- applies a small d-axis voltage pulse;
- applies a small q-axis voltage pulse;
- simulates d/q current ramps from the configured Ld/Lq model;
- records `current_d`, `current_q`, `voltage_d`, `voltage_q`, and `electrical_angle`;
- estimates:
  - `d_inductance`;
  - `q_inductance`;
  - `current_loop_initial_bandwidth`.

The simplified estimator uses:

```text
L = V / (di/dt)
```

Real hardware implementation will need resistance compensation, PWM/sample delay compensation, current sensor offset calibration, voltage-limit checks, and repeated runs.

## UI Integration

The 参数辨识 page now supports Mock runs for:

- Rs 电阻;
- Ld / Lq 电感.

When Ld/Lq Mock identification runs, the page updates:

- waveform trace;
- result table;
- event log;
- last result cache.

## Safety Boundary

Before real Ld/Lq identification, the application must check:

- electrical-angle calibration status;
- phase-order sanity;
- bus voltage range;
- current limit;
- voltage pulse amplitude;
- pulse duration;
- temperature;
- fault-free state;
- emergency stop path.

## Next Steps

1. Add identification export/report generation.
2. Add current-loop PI initial-value suggestion based on Rs/Ld/Lq.
3. Add electrical-angle/phase-order Mock workflow.
4. Later connect the same model to AxDr_L telemetry after protocol support exists.
