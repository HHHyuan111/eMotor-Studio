# Code Reuse Strategy

Date: 2026-05-14

## Private Prototype Strategy

eMotor-Studio 当前处于私有原型阶段。为了快速得到可用产品形态，可以参考或复用本地 `reference_projects` 中的开源实现，优先验证功能、界面、协议和工作流。

所有复用都必须记录来源，方便后续授权、开源合规、替换或 clean-room 重写。

## Reuse Types

| Reuse Type | Meaning |
|---|---|
| `reference_only` | 只参考思路、页面结构、交互习惯或文档，不复制代码。 |
| `adapted` | 改写、移植或根据源码结构重做实现。 |
| `direct_copy` | 直接复制代码、样式、资源或协议实现。 |
| `generated_from_reference` | AI 阅读参考实现后生成相近实现。 |
| `replaced_later` | 临时复用，后续需要替换。 |

## Required Provenance Fields

每条记录必须包含：

- 来源项目；
- 来源文件路径；
- 来源许可证；
- 复用类型；
- 目标文件；
- 复制行数或复用范围；
- 复用目的；
- 风险等级；
- 后续处理计划；
- 备注。

## License Handling

- GPL：私有原型阶段可以研究、参考或复用；公开发布、课程分发或商业使用前必须决定 GPL-compatible、授权、替换或 clean-room 重写。
- MIT / BSD / Apache：相对宽松，但仍需保留版权声明和来源记录。
- 未知许可证：不要直接用于公开发布；私有原型中也要标为高风险。
- 后续联系原作者授权时，应在 `docs/code_provenance.md` 中记录授权状态。

## VESC Tool Policy

VESC Tool 是主要对标对象：

- 可以学习产品架构、页面组织、实时数据、采样数据、终端、固件和参数配置流程。
- 私有原型阶段可以研究实现、改写交互模式或迁移页面结构。
- 若直接复制或派生，必须在 `docs/code_provenance.md` 中标明。
- 公开发布前必须选择：GPL-compatible、获得授权、替换、自研或 clean-room 重写。

## Provenance Template

| Date | Phase | Source Project | Source Path | Source License | Reuse Type | Target File | Copied Lines/Scope | Purpose | Risk Level | Future Action | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | Phase X | Project | path | MIT/GPL/etc | reference_only/adapted/direct_copy | file | scope | why | low/medium/high | keep_with_notice/request_permission/replace_before_release/rewrite_clean_room/open_source_compatible/unknown | note |
