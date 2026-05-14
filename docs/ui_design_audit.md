# UI Design Audit

Date: 2026-05-14

## Current Issues

- 页面能用，但视觉语言不统一：卡片、表格、按钮、状态标签各页样式不一致。
- Dashboard 旧版信息块过大，留白多，关键状态不够“一眼可判”。
- Scope 需要更明确的“信号栏 + 曲线区 + 控制栏”，避免变量名或图例遮挡曲线。
- Parameter 旧版更像普通长表，缺少工程配置面板所需的筛选、搜索和参数说明区。
- Command 需要区分常用命令、目标设定、自定义命令和历史记录，并明确 Mock 模式。
- Fault / Logger / Report / Hardware 页面需要统一的状态卡片和分区结构。
- 顶部状态栏和左侧导航需要分组，贴近电机调试软件的工作流。

## Reference Direction

- VESC Tool: 左侧工程导航、顶部状态、配置/监控/故障分区组织。
- SimpleFOCStudio: 串口优先、监控和参数调试工作流。
- ODrive GUI: 设备连接逻辑和控制页面解耦。

本阶段仅参考界面组织思想，没有复制 VESC Logo、名称、商标、资源或源码。

## Phase 7.0-UI-2 Plan

- 建立 `theme.py` 作为统一 QSS 和颜色系统。
- 新增 `ui/components.py`，封装 PageHeader、SectionCard、KpiCard、StatusChip、InfoBox。
- 主窗口改为分组导航：实时监控、控制调试、数据诊断。
- Dashboard 改为三段式：系统状态、核心指标、快速控制。
- Scope 改为信号栏、曲线区、底部控制栏。
- Parameter 改为分组/搜索/表格/说明区。
- Command 改为常用命令、目标设定、自定义命令、历史记录。
- 支撑页统一为状态卡片 + 分区表格布局。
