# VESC Tool UI Research Notes

Date: 2026-05-14

## Scope

This pass studied VESC Tool's UI code to improve the eMotor-Studio framework before implementing real AxDr_L hardware functions.

Sources checked:

- `D:\MotorControlWorkspace\reference_projects\vesc_tool\mainwindow.ui`
- `D:\MotorControlWorkspace\reference_projects\vesc_tool\mainwindow.cpp`
- `D:\MotorControlWorkspace\reference_projects\vesc_tool\pages\pageconnection.ui`
- `D:\MotorControlWorkspace\reference_projects\vesc_tool\pages\pagertdata.ui`
- `D:\MotorControlWorkspace\reference_projects\vesc_tool\pages\pagesampleddata.ui`
- `D:\MotorControlWorkspace\reference_projects\vesc_tool\pages\pagesampleddata.cpp`
- `D:\MotorControlWorkspace\reference_projects\vesc_tool\pages\pageterminal.ui`
- Public GitHub project page: `https://github.com/vedderb/vesc_tool`

## MainWindow Pattern

VESC Tool uses:

- left page list;
- grouped page hierarchy;
- central stacked pages;
- menu bar for file/config/wizard/terminal/developer/help workflows;
- global toolbar actions for reconnect, disconnect, read/write motor config, read/write app config, realtime data, alive and CAN forward;
- left device/CAN list and scan button;
- bottom always-visible quick controls for duty, current, speed, position, brake and stop.

eMotor-Studio now mirrors this structure in a Chinese AxDr_L-specific way, while keeping hardware actions disabled.

## Page Hierarchy Pattern

Observed VESC Tool groups:

- Welcome & Wizards
- Connection
- Firmware
- VESC Packages
- Motor Settings
- App Settings
- Data Analysis
- VESC Dev Tools

eMotor-Studio maps these to:

- Start: 仪表盘、连接、固件
- Motor Settings: 电机设置、参数配置、FOC
- App Settings: 应用设置、控制命令
- Data Analysis: 实时数据、采样数据、故障诊断、数据记录、调试报告、数据分析
- Dev Tools: Terminal

## Realtime Data Pattern

VESC `PageRtData` uses tabs:

- Current
- Temperature
- RPM
- FOC
- Rotor Position

It also has side controls for autoscale, horizontal zoom, vertical zoom, rescale and logging.

eMotor-Studio now uses PySide6 + pyqtgraph tabs:

- 电流
- 温度
- 转速
- FOC
- 转子位置
- 自定义通道

The custom channel page keeps AxDr_L signal selection, pause inspection, x-axis drag, mouse-wheel x zoom, CSV export and Chinese right-click menu.

## Sampled Data Pattern

VESC `PageSampledData` uses:

- tabbed current/BEMF/filter views;
- sampling buttons for immediate, start-triggered, fault-triggered, stop, save and load;
- side controls for sampling count, decimation, raw/filter/FFT settings;
- plot range drag/zoom and rescale behavior.

eMotor-Studio now provides a matching framework page, with all real sampling actions disabled until AxDr_L has a sampling protocol.

## Connection Pattern

VESC `PageConnection` has tabs for:

- USB/Serial;
- CAN bus;
- TCP;
- other transport/debug-oriented paths.

eMotor-Studio now uses tabs for:

- 串口 / USB CDC;
- CAN bus;
- TCP / 调试桥;
- J-Link RTT.

The V1.1 recommendation remains serial-first.

## Terminal Pattern

VESC terminal is a text console with a command line and help/send/clear buttons.

eMotor-Studio now has the same shell-like structure, but command sending is disabled until SerialBackend PING and firmware terminal commands exist.

## Reuse Status

No VESC icons, logos, image assets, trademarks or generated Qt files were copied. The implementation is Python/PySide6 code shaped after the observed UI organization. This is still recorded as `adapted` in `docs/code_provenance.md` because the layout and page framework closely follow VESC Tool.
