# eMotor-Studio UI Design System

Date: 2026-05-15

## Layout

- 左侧固定导航：按“实时监控 / 控制调试 / 数据诊断”组织页面。
- 顶部工程状态栏：显示后端、连接状态、运行状态、故障状态、通信策略和会话信息。
- 主工作区：统一 18px 左右的视觉节奏，页面以 PageHeader 开始，内容使用 SectionCard 分区。

## Colors

- 主背景：低饱和浅灰蓝工作区，降低长时间调试疲劳。
- 导航：石墨深色侧栏，突出当前页面和工作台结构。
- 卡片：近白背景 + 柔和边框 + 更统一的圆角。
- 主按钮：低饱和青蓝色，避免页面出现过多高饱和色块。
- 危险按钮：深红色，只用于故障注入、停止等高风险动作。
- 状态：绿色运行/正常，蓝色空闲，灰色停止，红色故障，黄色警告。
- Scope：深色曲线背景，曲线采用蓝、琥珀、青绿、柔紫等低饱和高可读色。

## Phase 10.2 Visual Tokens

- `window`: outer application background.
- `workspace`: main engineering work area.
- `sidebar`: persistent navigation frame.
- `card` / `card_soft`: normal and soft surfaces.
- `primary`: main action accent.
- `ok` / `idle` / `stop` / `fault` / `warning`: semantic status colors.
- `scope_bg`: oscilloscope plotting surface.

## Components

- `PageHeader`：页面标题和简短说明。
- `SectionCard`：页面主要分区容器。
- `KpiCard`：关键状态和实时指标。
- `StatusChip`：顶部状态栏标签。
- `InfoBox`：提示、说明和安全注意事项。

## Page Structure

- Dashboard：系统状态总览、核心实时指标、快速控制区。
- Scope：信号栏、曲线区、底部控制栏。
- Parameter：操作栏、参数表、参数说明和安全提示。
- Command：常用命令、目标设定、自定义命令、命令历史。
- Fault：当前故障卡片、故障字、活动故障和历史表。
- Logger：记录状态、样本数量、导出路径和最近样本。
- Report：报告说明、会话摘要、操作栏和 Markdown 预览。
- Hardware：通信策略总览，不提供真实连接入口。

## Why This Fits Motor Debugging

- 工程调试需要快速判断状态，因此关键指标采用 KPI 卡片。
- 参数和命令需要防误操作，因此页面强调分区和状态提示。
- 波形页需要最大化曲线区域，因此图例移到信号栏，控制放到底部。
- 真实硬件接入前，UI 明确显示 Mock 模式，避免误导。

## Next UI Iterations

- 增加图标库，但不使用 VESC 图标或商标。
- 增加小型趋势图和状态时间线。
- 增加用户偏好保存：窗口大小、最近页面、Scope 通道选择。
- Phase 7.2 后增加真实连接页中的端口选择和 PING 状态。
