# Phase 10.3 Information Architecture Cleanup

Date: 2026-05-15

## Goal

Reduce duplicated and verbose UI entry points while preserving the current Mock-only workbench functionality.

This phase keeps eMotor-Studio moving toward a polished domestic VESC-like platform, but avoids adding hardware communication or new backend logic.

## Changes

- Reordered left navigation by usage priority:
  - 总览
  - 实时调试
  - 控制与参数
  - 科研与辨识
  - 数据与诊断
  - 系统工具
- Moved high-frequency runnable pages earlier.
- Moved future/framework pages later.
- Reduced the global toolbar from several concrete disabled actions into broader status-level entries.
- Shortened repetitive page explanations.
- Kept Mock mode and safety boundaries visible where they matter.

## Boundaries

- No real hardware communication.
- No SerialBackend PING.
- No MockBackend core changes.
- No communication protocol changes.
- No external code or VESC source copied.

## Acceptance

- Page switching remains functional.
- Mock mode remains runnable.
- Tests, GUI smoke and review script pass.
