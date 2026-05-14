# VESC-like UI Map for eMotor-Studio

Date: 2026-05-14

## Goal

eMotor-Studio 的 UI 目标是做成类似 VESC Tool 的电机控制调试工作台，但底层对象、参数、命令和协议匹配 AxDr_L。

本阶段先搭页面地图和布局，不实现真实硬件通信。

## VESC Tool Page Pattern Observed

VESC Tool 主窗口采用左侧页面列表 + 中央堆叠页面，核心分组包括：

- Welcome & Wizards
- Connection
- Firmware
- Motor Settings
- App Settings
- Data Analysis
- VESC Dev Tools
- SWD / ESP Programmer

Phase 8.1 深度阅读后补充：

- 主窗口还包含菜单栏、全局工具栏、CAN/设备列表和底部快速控制条。
- Connection 页面采用多标签方式组织 USB/Serial、CAN bus、TCP 等连接方式。
- Realtime Data 页面按 Current、Temperature、RPM、FOC、Rotor Position 分标签。
- Sampled Data 页面按 Current、BEMF、Filter/FFT 分标签，并有采样触发、保存、加载和缩放控制。
- Terminal 页面是文本输出区 + 命令输入行 + 帮助/发送/清空按钮。

实时数据相关页面包括：

- Realtime Data
- Sampled Data
- Experiment Plot
- Log Analysis

电机配置相关页面包括：

- Motor Settings
- General
- BLDC / DC / FOC
- PID Controllers
- Additional Info
- Experiments

## eMotor-Studio Mapping

| VESC Tool Concept | eMotor-Studio Page | Current Status |
|---|---|---|
| Welcome / Wizards | 仪表盘 | Mock KPI and quick control available |
| Connection | 连接 | Communication strategy overview |
| Firmware | 固件 | Placeholder, firmware info later |
| Motor Settings | 电机参数 | Placeholder for AxDr_L motor parameters |
| Motor General / Config | 参数配置 | Mock parameter table available |
| FOC | FOC | Placeholder for current/speed/position loop and observer tuning |
| App Settings | 应用设置 | Placeholder for control mode and app behavior |
| App UART / command interface | 控制命令 | Mock command panel available |
| Realtime Data | 实时数据 | pyqtgraph realtime scope available |
| Sampled Data | 采样数据 | Placeholder for future high-speed triggered sampling |
| Fault / Debug | 故障诊断 | Mock fault page available |
| Log Analysis | 数据记录 / 调试报告 / 数据分析 | Logger and report available; analysis placeholder |
| Terminal | Terminal | Placeholder for serial/debug terminal |

## Phase 8.1 Framework Update

本次已把 eMotor-Studio 的框架进一步对齐 VESC Tool：

- `MainWindow` 增加中文菜单栏、全局工具条、左侧设备/CAN 区和底部快速控制条。
- `HardwarePage` 改为连接多标签页：串口/USB CDC、CAN bus、TCP/调试桥、J-Link RTT。
- `ScopePage` 改为实时数据多标签页：电流、温度、转速、FOC、转子位置、自定义通道。
- `SampledDataPage` 改为采样数据多标签页：Current、BEMF、Filter/FFT，并保留采样控制框架。
- `TerminalPage` 改为控制台风格布局。

所有真实连接、读写配置、采样触发、终端发送仍保持禁用或占位，等待 AxDr_L 协议确认。

## Next Filling Order

1. Phase 7.1-B: AxDr_L serial protocol draft.
2. Phase 7.2-A: SerialBackend minimum PING.
3. Firmware page: read firmware info.
4. Realtime Data page: receive real telemetry.
5. Parameter pages: read/write real parameters.
6. Command page: real enable/stop/clear fault/setpoint commands.
7. Sampled Data page: high-speed triggered capture.

## Source Reuse Note

The UI structure is adapted from VESC Tool page organization. No VESC logos, names, trademarked branding, or Qt/C++ source files are copied into eMotor-Studio.
