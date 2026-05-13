# Reference Repositories

Local reference root: `D:\MotorControlWorkspace\reference_projects`

## Summary

The current strategy is private-prototype first. Code may be reused from local
references to quickly validate a stable application, but provenance must be
recorded. Before any public release, course distribution, or commercial use,
license compatibility must be reviewed.

| Project | Local Path | Stack | License Status | Reuse Level |
|---|---|---|---|---|
| SimpleFOCStudio | `reference_projects\SimpleFOCStudio` | PyQt5, pyqtgraph, pyserial | MIT | Direct reuse allowed with attribution |
| pid-motor-control | `reference_projects\pid-motor-control` | PyQt5, pyqtgraph, firmware simulation | No LICENSE file found | Private prototype only; replace or clarify before distribution |
| vesc_tool | `reference_projects\vesc_tool` | Qt/C++, QML | GPL-3.0 | Private prototype only; high public-release risk |
| odrive-gui | `reference_projects\odrive-gui` | NiceGUI, ODrive Python | MIT | Direct reuse allowed with attribution |
| Spectral-motor-GUI | `reference_projects\Spectral-motor-GUI` | Python GUI | MIT | Direct reuse allowed with attribution |
| Interactive_PID_Controller | `reference_projects\Interactive_PID_Controller` | PyQt5, pyqtgraph, Arduino | No LICENSE file found | Private prototype only; replace or clarify before distribution |

## Reuse Rules

- Preserve attribution when copying MIT-licensed code.
- Keep copied code isolated where possible so later cleanup is practical.
- Mark GPL/no-license derived code as private-prototype only.
- Record copied files, adapted functions, or design-heavy derivations in
  `docs/reference_analysis.md` or future `docs/code_provenance.md`.

## First-Milestone Decision

Phase 0-2 will implement an original PySide6 skeleton while borrowing common
ideas from the references: mock data generation, real-time plotting, parameter
tables, command panels, fault displays, and logging/report workflows.
