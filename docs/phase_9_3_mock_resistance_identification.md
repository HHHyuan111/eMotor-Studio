# Phase 9.3 Mock Resistance Identification

## Goal

Phase 9.3 adds the first runnable parameter-identification loop: Mock phase-resistance identification.

The purpose is to validate the architecture before hardware exists:

- identification task/result models;
- independent service-layer identification logic;
- UI trigger and result refresh;
- trace display and event log;
- tests that lock the behavior.

This phase still does not connect real hardware, does not inject current into a motor, and does not write parameters to AxDr_L.

## Added Data Models

- `IdentificationTask`: module name, duration, sample rate, signals, safety limits, and parameters.
- `IdentificationTrace`: time vector plus named signal channels and units.
- `IdentificationEstimate`: parameter key, value, unit, confidence, status, and description.
- `IdentificationResult`: task, trace, estimates, summary, and timestamp.

## Added Service

`MockResistanceIdentification` generates a synthetic Rs-identification trace:

- injects a small q-axis voltage after an initial delay;
- simulates first-order current rise;
- records current, q-axis voltage, bus voltage, and MOS temperature;
- estimates `phase_resistance` from steady-state voltage/current;
- reserves temperature-coefficient output for future multi-temperature tests.

## UI Integration

The 参数辨识 page now allows only the Rs module to run a Mock identification:

- result table updates with `phase_resistance`;
- waveform panel refreshes with generated channels;
- event log records task title, sample count, summary, and the Mock-only boundary.

Other identification modules remain framework-only and disabled.

## Safety Boundary

Real Rs identification will require:

- protocol support for controlled injection;
- current, voltage, temperature and time limits;
- motor state check;
- emergency stop;
- repeated-run validation;
- explicit user confirmation before writing parameters.

## Next Steps

1. Add Mock Ld/Lq identification using current-slope estimation.
2. Add report/export support for identification results.
3. Add shared safety-gate objects before any real hardware experiment.
4. Later map results back to `configs/parameters.json` and AxDr_L parameter writes.
