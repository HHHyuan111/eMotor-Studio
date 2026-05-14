# Phase 9.2 Modular Identification Workbench

## Goal

Phase 9.2 turns 参数辨识 from a single placeholder into a modular workbench. The purpose is to avoid a future black-box "identify everything" button and instead give each parameter family its own experiment window, signal view, result table, and safety boundary.

This phase still does not connect real hardware, does not inject current, and does not write parameters to AxDr_L.

## Implemented UI Structure

The 参数辨识 page now has six modules:

1. Rs 电阻
2. Ld / Lq 电感
3. 磁链 / Kt
4. 电角度 / 相序
5. 惯量 / 摩擦
6. 观测器

Each module contains:

- experiment setup and safety notes;
- disabled action buttons for future task generation, start, stop, and export;
- a waveform preview area showing which variables should be observed;
- signal checkboxes showing the intended telemetry channels;
- fitted-parameter/result table;
- write-back guidance that keeps parameter writes behind checks and confirmation.

## Engineering Rationale

Motor-parameter identification should be split by physical meaning:

- Rs and Ld/Lq require electrical injection and current/voltage observation.
- Flux/Kt requires speed, voltage, current, and operating-condition notes.
- Electrical angle and phase order are safety-critical FOC coordinate checks.
- Inertia/friction belong to mechanical dynamics and need repeated motion tests.
- Observer parameters require comparison between estimated and measured angle.

Keeping these workflows separate makes the application easier to maintain and more useful for teaching, research, and engineering reports.

## Future Hardware Safety Gates

Before real identification is enabled, each module needs:

- connection and firmware-version check;
- bus-voltage valid range;
- current, speed, and temperature limits;
- fault-free state;
- explicit user confirmation;
- emergency stop path;
- log and export path;
- parameter write range validation.

## AxDr_L Algorithm Window Strategy

The long-term UI should mirror AxDr_L algorithm joints:

- current loop;
- speed loop;
- position loop;
- SVPWM;
- encoder/electrical-angle calibration;
- sensorless observer;
- protection/fault handling;
- filters/notches;
- identification routines.

The upper-computer should not become an arbitrary code editor first. The better approach is fixed algorithm windows with safe parameters, signals, experiments, reports, and optional advanced hooks later.
