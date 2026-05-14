# Phase 9.9 UI Direction Cleanup

## Goal

This phase pauses feature expansion and adjusts the overall UI direction. The previous workbench had useful pages, but the visual language was too mixed and the left navigation contained overlapping entries. The goal is to make eMotor-Studio feel calmer and more coherent before continuing deeper algorithm work.

## Changes

- Reduced the color palette to a more stable blue-gray engineering style.
- Lowered saturation for status colors so the UI does not feel visually noisy.
- Simplified the left navigation into six main areas:
  - 总览
  - 实时调试
  - 控制算法
  - 实验与辨识
  - 数据与诊断
  - 开发工具
- Merged repeated concepts:
  - connection belongs under 总览;
  - command and parameters belong under 实时调试;
  - loop tuning, filters, FOC and app settings belong under 控制算法;
  - research and identification belong under 实验与辨识;
  - sampled data, logs, reports and faults belong under 数据与诊断.
- Removed the bottom quick-control strip from the main frame for now because it duplicated the command page and made the UI feel busy.
- Simplified the global toolbar to connection, config, realtime data and session-entry placeholders.

## Boundaries

- No MockBackend logic changed.
- No real hardware communication added.
- No SerialBackend PING added.
- No page business logic removed.
- No AxDr_L firmware changes.

## Next UI Direction

The next UI pass should focus on page-level hierarchy:

- Dashboard: compact overview instead of oversized boxes.
- Scope: professional plot controls and clearer signal grouping.
- Parameter: searchable grouped engineering table.
- Experiment/Identification: wizard-like workflow with left steps, middle plot, right result panel.

The main frame should stay stable while individual pages improve inside it.
