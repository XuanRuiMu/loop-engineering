# 循环工程 Self-Harness 组件清单

本文件记录循环工程 skill 的 harness（约束与支撑结构）组件，用于 Self-Harness 元循环中的 Weakness Mining、Harness Proposal 和 Proposal Validation。

## 当前 Harness 组件清单

| 组件路径 | 作用 | 版本/最后修改时间 | 修改级别 |
| --- | --- | --- | --- |
| `SKILL.md` | 循环工程 skill 的主入口与完整工作流定义，包含 Orchestrator+Headless 模式、铁律、阶段跳过规则、完整工作流、停止条件、熔断规则与 Self-Harness 元循环 | 2026-08-16（新增补位熔断、契约变更协调、元循环独立审查、断点续跑rebaseline、契约变更清理增跳过/阻塞处理） | 禁止自动（必须先 AskUserQuestion 取得用户同意） |
| `references/子代理提示词模板.md` | Headless Worker 的提示词模板，规定子代理必须读取 PROGRESS.md、返回简短结构化摘要、禁止写历史；含 token_estimate / failure_tags / evidence_link 字段、P0 规则自审、UUID/强类型参数前置校验、全中文命名检查、三轴审查结果输出、debug 日志安全自审与翻译模板修改测试同步自审等强制检查项 | 2026-07-17 | 待确认（改动返回结构，已获用户同意） |
| `references/PROGRESS模板.md` | PROGRESS.md 的精简状态模板，规定只写当前状态、禁止写入历史/过程/文件清单 | — | 自动（仅格式模板调整，不改动业务规则） |
| `references/Orchestrator-Headless模式.md` | 核心架构原理说明，解释 Context Wall 问题与 Orchestrator+Headless 解法 | — | 禁止自动（架构原理变更须经用户确认） |
| `references/EnvironmentEngineering.md` | Environment Engineering 四维规范，定义 Permissions/Artifacts/Budget/Human-in-the-loop 约束与检查清单 | 2026-07-08 | 待确认（涉及权限/预算/HITL 规则变更时须用户确认） |
| `AGENTS.md` | 项目级通用 AI 开发规则，所有子代理启动时必须先读 | 用户选择不改 | 禁止自动（必须先 AskUserQuestion 取得用户同意） |

## 修改分级规则

| 级别 | 定义 | 触发条件 | 处理流程 |
| --- | --- | --- | --- |
| 自动 | 不违反 PROGRESS.md 铁律、不改动核心工作流、不涉及用户确认文件的修改 | 仅调整格式、新增纯说明性 references、补充示例、修复笔误（但 EnvironmentEngineering §2.3 受保护产物——harness-test-suite 测试文件、EVIDENCE.md 历史证据——除外，须按 §2.3 走 AskUserQuestion） | 子代理可直接修改，无需额外确认 |
| 待确认 | 可能影响核心工作流、返回结构或用户认知，但风险可控 | 修改提示词返回结构、调整 PROGRESS 字段、新增/删除熔断规则、扩展 budget 字段 | 修改前必须用 AskUserQuestion 向用户说明变更内容、原因、影响范围，取得同意后方可执行 |
| 禁止自动 | 涉及项目级规则或 skill 核心契约，必须由用户明确授权 | 修改 SKILL.md 核心流程、修改 AGENTS.md、删除铁律、变更停止条件/熔断上限默认值 | 任何子代理不得自动执行；仅可在用户通过 AskUserQuestion 明确回复同意后，由主代理或用户指定的代理执行 |

## Environment Engineering 组件引用

FP-07 新增的 `references/EnvironmentEngineering.md` 是 harness 的环境约束层，与 HARNESS.md 的关系如下：

| 文件 | 作用 | 与 HARNESS.md 的交互 |
| --- | --- | --- |
| `references/EnvironmentEngineering.md` | 定义 Permissions/Artifacts/Budget/Human-in-the-loop 四维约束 | HARNESS.md 将其列为待确认级组件；Self-Harness 元循环提出的涉及环境约束的提案需对照本文件 |
| `BUDGET.md` | 定义预算字段与熔断规则 | EnvironmentEngineering.md 中 Budget Engineering 维度的权威来源 |
| `EVIDENCE.md` | 定义证据目录结构与记录格式 | EnvironmentEngineering.md 中 Artifacts Engineering 维度的证据规范来源 |

Headless Worker 在实现功能点前，除读取本 HARNESS.md 外，还应读取 `references/EnvironmentEngineering.md`，确认当前操作符合四维约束。

## 兼容性声明

- 本文件自身属于新增 references 文件，修改级别为 **自动**。
- 本文件不修改 `SKILL.md` 或 `AGENTS.md`，与 PROGRESS.md 中"不自动改写 SKILL.md / AGENTS.md"的决策兼容。
- 本文件所列组件清单包含 `references/EnvironmentEngineering.md`；新增或调整 harness 组件时，其版本与修改级别需在此同步更新。
