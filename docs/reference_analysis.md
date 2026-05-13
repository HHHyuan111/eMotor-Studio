# Reference Analysis

## Overview

This analysis converts local motor-control GUI projects into practical guidance
for eMotor-Studio. The current repository is a private prototype, so direct
reuse is allowed when it helps stability. Public release still requires a
license-cleanup pass.

## SimpleFOCStudio

- **Path**: `D:\MotorControlWorkspace\reference_projects\SimpleFOCStudio`
- **Stack**: PyQt5, pyqtgraph, pyserial
- **License**: MIT
- **Useful ideas**: serial connection setup, motor parameter tuning, live
  monitoring, custom commands, code-generation workflow.
- **eMotor mapping**: Parameter, Command, Scope, future report/code-export tools.
- **Reuse note**: MIT code can be reused with attribution, but this skeleton uses
  original PySide6 code to avoid early framework mismatch.

## pid-motor-control

- **Path**: `D:\MotorControlWorkspace\reference_projects\pid-motor-control`
- **Stack**: PyQt5, pyqtgraph, Python simulation, embedded firmware examples
- **License**: no LICENSE file found
- **Useful ideas**: Mock/simulated controller, PID telemetry, binary frame
  thinking, real-time plot buffers, simple gain/setpoint commands.
- **eMotor mapping**: MockBackend, Dashboard, Scope, Command.
- **Reuse note**: private-prototype only unless licensing is clarified.

## vesc_tool

- **Path**: `D:\MotorControlWorkspace\reference_projects\vesc_tool`
- **Stack**: Qt/C++, QML, extensive motor-controller pages
- **License**: GPL-3.0
- **Useful ideas**: rich page organization, parameter tables, real-time data
  pages, sampled data, terminal, fault and configuration workflows.
- **eMotor mapping**: all long-term pages, especially Parameter, Fault, Logger,
  and future hardware backend boundaries.
- **Reuse note**: high-risk for public release. Direct use is acceptable only for
  private prototype experiments unless eMotor-Studio accepts GPL obligations.

## odrive-gui

- **Path**: `D:\MotorControlWorkspace\reference_projects\odrive-gui`
- **Stack**: NiceGUI, odrive Python package, matplotlib
- **License**: MIT
- **Useful ideas**: dynamic device discovery, per-device control panels, simple
  web-based control organization.
- **eMotor mapping**: future device discovery, backend abstraction, Dashboard.
- **Reuse note**: MIT code can be reused with attribution, but its web UI stack is
  not directly aligned with PySide6.

## Spectral-motor-GUI

- **Path**: `D:\MotorControlWorkspace\reference_projects\Spectral-motor-GUI`
- **Stack**: Python GUI project
- **License**: MIT
- **Useful ideas**: product-specific motor-driver GUI flow, packaging direction,
  BLDC-focused presentation.
- **eMotor mapping**: Dashboard, Parameter, future hardware tutorials.
- **Reuse note**: MIT code can be reused with attribution.

## Interactive_PID_Controller

- **Path**: `D:\MotorControlWorkspace\reference_projects\Interactive_PID_Controller`
- **Stack**: PyQt5, pyqtgraph, Arduino
- **License**: no LICENSE file found
- **Useful ideas**: teaching-friendly PID controls, simple real-time graphing,
  Arduino serial interaction.
- **eMotor mapping**: Scope, Command, course-facing Dashboard.
- **Reuse note**: private-prototype only unless licensing is clarified.

## Provenance for Current Skeleton

The Phase 0-2 skeleton is newly written for eMotor-Studio. It borrows broad
workflow ideas from the references but does not intentionally copy source files.
Future copied or heavily adapted code should be recorded here or moved to a
dedicated `docs/code_provenance.md`.
