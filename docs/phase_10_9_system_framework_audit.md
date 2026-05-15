# Phase 10.9 System Framework Audit

## Goal

Check and lightly tighten the whole eMotor-Studio workbench framework after the recent UI iterations.

This phase keeps the project in Mock mode. It does not implement SerialBackend PING, real hardware communication, protocol changes, or AxDr_L firmware changes.

## Audit Findings

- The left navigation had become more compact after Phase 10.8, but several low-frequency pages were instantiated without a direct user path from the main workbench.
- The system tools page existed as a placeholder summary, while actual pages such as FOC, firmware, terminal, observer, filter/notch, and app settings were already available as page objects.
- Keeping every low-frequency page in the left navigation would make the sidebar noisy again.

## Framework Changes

- Kept the left navigation compact and workflow-oriented:
  - 仪表盘
  - 连接
  - 波形
  - 采样
  - 记录
  - 命令
  - 参数
  - 三环
  - 实验
  - 分析
  - 辨识
  - 故障
  - 报告
  - 工具
- Converted the system tools page into a real low-frequency tool container.
- Added second-level tabs inside 系统工具 for:
  - 电机设置
  - FOC
  - 滤波 / 陷波
  - 应用设置
  - 观测器
  - 数据分析
  - 固件
  - Terminal

## Why This Direction

This keeps the first-level workbench close to a practical motor-control workflow, while preserving access to deeper VESC-like configuration and developer pages.

The structure now has a clearer separation:

- high-frequency operation pages stay in the sidebar;
- low-frequency setup and developer pages are collected under 系统工具;
- future hardware communication can be added behind the existing page boundaries instead of being wired directly into UI widgets.

## Validation

- Added a main-window regression test for compact navigation labels.
- Added a main-window regression test for the system-tools tab container.
- Existing Scope, page, experiment, model, MockBackend, and SerialBackend placeholder tests remain active.

