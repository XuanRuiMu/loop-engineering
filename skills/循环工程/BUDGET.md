# 循环工程预算与熔断

本文件定义循环工程运行时的资源预算字段、默认上限和熔断规则。

## 预算字段定义

| 字段 | 类型 | 说明 | 当前状态 |
| --- | --- | --- | --- |
| `total_token_limit` | 整数或 `null` | 整个循环任务的总 token 上限 | **不可获取**（FP-01 结论），保持 `null` |
| `per_subagent_token_limit` | 整数或 `null` | 单个子代理调用的 token 上限 | **不可获取**（FP-01 结论），保持 `null` |
| `subagent_call_limit` | 整数 | 整个循环任务中调用 Task 子代理的总次数上限 | 默认 30，与 `total_turn_limit` 一致 |
| `total_turn_limit` | 整数 | 主代理与子代理交互的总轮次上限 | 默认 30 |
| `per_fp_attempt_limit` | 整数 | 单个功能点内部修复次数上限 | 默认 5 |
| `wall_clock_limit_minutes` | 整数 | 任务总 wall-clock 时间上限（分钟） | 默认 120 |
| `self_estimated_token_limit` | 整数或 `null` | 主代理根据子代理返回摘要自行估算的 token 上限 | 默认 `null`（可选） |
| `orchestrator_backfill_limit` | 整数 | 主代理（Orchestrator）在单次循环任务中亲自补位完成的功能点数量上限；达上限后禁止继续亲自补位，须改派全新 Task 子代理或停下汇报 | 默认 3 |
| `budget_source` | 字符串 | token 数据来源说明：`HOST_ENV_TASK`、`USER_ESTIMATE`、`UNAVAILABLE` | `UNAVAILABLE`（FP-01 结论） |

## 默认预算上限

| 类型 | 默认值 | 说明 |
| --- | --- | --- |
| 总循环次数 | 30 | 与 PROGRESS.md 中"熔断上限：总循环 30 轮"一致 |
| 子代理调用次数 | 30 | 与 `total_turn_limit` 一致，作为 token 不可获取时的主要熔断维度 |
| 单问题修复次数 | 5 | 与 PROGRESS.md 中"单问题修复上限 5 次"一致 |
| Token 总预算 | `null` | 不可获取（FP-01 结论回填） |
| 单个子代理 Token 预算 | `null` | 不可获取（FP-01 结论回填） |
| 自估算 Token 预算 | `null` | 可选辅助维度，由用户或主代理按需设置 |
| Wall-clock 时间 | 120 分钟 | 防止任务无限运行；用户可覆盖 |
| 主代理补位次数 | 3 | 防止主代理亲自干活过多导致主上下文膨胀，撞上 Context Wall（与 Headless 设计目标对冲） |

## 熔断规则

| 条件 | 动作 | 记录位置 |
| --- | --- | --- |
| 同一问题修复次数达到 `per_fp_attempt_limit` | 停止该功能点修复，标记为"已阻塞"，返回主代理 | PROGRESS.md 待处理功能点状态列 |
| 总循环次数达到 `total_turn_limit` | 停止整个循环，用 AskUserQuestion 汇报当前状态 | PROGRESS.md 元信息"状态"改为"已熔断" |
| 子代理调用次数达到 `subagent_call_limit` | 停止整个循环，用 AskUserQuestion 汇报 | PROGRESS.md 元信息"状态"改为"已熔断" |
| Wall-clock 时间达到 `wall_clock_limit_minutes` | 停止整个循环，提示用户时间耗尽 | PROGRESS.md 元信息"状态"改为"已熔断" |
| 自估算 token 达到 `self_estimated_token_limit`（若设置） | 停止整个循环，提示用户预算耗尽 | BUDGET.md 当前状态 + AskUserQuestion |
| 遇到无法自行解决的阻塞 | 立即停下，用 AskUserQuestion 汇报 | PROGRESS.md"阻塞与遗留问题"小节 |
| 主代理补位次数达到 `orchestrator_backfill_limit` | 停止主代理亲自补位；改派全新 Task 子代理（新上下文无锚定偏差），仍失败则标记阻塞；无 Task 工具环境下降级为强制高亮上下文风险 | PROGRESS.md 当前决策 + 元信息"补位计数" |

> **说明**：`total_token_limit` 与 `per_subagent_token_limit` 不可获取，故不作为熔断条件；Token 相关熔断仅当用户显式设置 `self_estimated_token_limit` 时生效（见下方 FP-01 结论回填）。

## FP-01 结论回填

FP-01 已完成验证，结论如下：

```yaml
budget_source: UNAVAILABLE  # 宿主环境 Task 工具无法提供子代理级 token 用量
actual_token_field_name: null  # TaskOutput 和任务跟踪器均无 token 字段
total_token_limit: null  # 不可获取，不作为熔断条件
per_subagent_token_limit: null  # 不可获取，不作为熔断条件
fallback_strategy: "子代理调用次数 + wall-clock 时间 + 可选的自估算 token 作为预算维度"
```

降级方案细节：

1. **子代理调用次数**：每发起一次 Task 工具调用即计数 +1，上限 30，与 `total_turn_limit` 一致。
2. **Wall-clock 时间**：从主代理首次读取 PROGRESS.md 开始计时，上限 120 分钟。
3. **自估算 token**：主代理根据子代理返回摘要的字数估算，仅作为可选辅助维度；不设置时不触发熔断。

原 `total_token_limit` 与 `per_subagent_token_limit` 字段保留但值为 `null`，用于记录 FP-01 结论，避免后续功能点重复验证。

## 兼容性声明

- 本文件默认上限与 PROGRESS.md 中现有熔断规则一致，不引入新的数值约束。
- FP-01 结论与降级方案见下方「FP-01 结论回填」，token 相关字段保持 `null`。
- 本文件是 Budget Engineering 维度的权威来源；`references/EnvironmentEngineering.md` §3 仅作交叉引用，不重复定义。

## 已知局限

- **预算为荣誉制软约束**：`wall_clock_limit_minutes` 与 `total_turn_limit` 依赖主代理自行计时/计数，无外部看门狗强制；仅当主代理准确遵守时才生效，不可理解为硬停保障——长任务仍可能因主代理未精确计数而超出上限。机器可强制的维度仅有回归任务集（如 `task-06`）的结构校验。
- **token 维度不可获取**：`total_token_limit` / `per_subagent_token_limit` 保持 `null`（FP-01 结论），不作为熔断条件；`self_estimated_token_limit` 为可选人工辅助维度，不设置时不触发。

## 环境问题规避

本节记录循环工程运行中遇到的环境问题及其规避方案，避免子代理重复踩坑。环境问题不属于代码缺陷，无法通过修改业务代码解决，只能通过运行参数规避。

| 环境问题 | 表现 | 规避方案 |
| --- | --- | --- |
| 构建工具 daemon 崩溃 | 特定 JDK/构建工具组合下 `build` 退出码异常，daemon 进程终止，构建失败 | 运行构建命令加 `--no-daemon`（或等价"禁用守护进程"标志）；或在构建配置中关闭 daemon |
| 测试任务默认被禁用 | 构建配置中测试任务默认关闭，输出 SKIPPED，易被误判为"测试通过" | 运行测试必须显式开启测试开关；确认测试真正执行而非被跳过 |
| 源码哈希/清单同步工具对测试目录无效 | 同步工具要求主源码路径前缀，对测试目录误用会污染清单 | 测试文件修改不需要运行该同步工具；该工具仅用于主源码目录 |
| 日志库异步落盘导致测试读空 | 测试中调用 flush 时数据尚未落盘，随后读取日志得到空内容 | 开发/测试模式改用同步直写并等待落盘后再读；生产模式保留原有异步轮转 |
| 运行环境无可用 Task 子代理工具 | 调用 Task 工具返回 unavailable，Orchestrator+Headless 与并行子代理无法派发 | 主代理补位亲自执行（实现/验证/审查单线程完成）——此情形下主代理亲自干属正常的兜底补位，不再视为降级；仍必须跑全量验证命令，并在决策表记录补位原因；补位次数仍计入 `orchestrator_backfill_limit`，达上限后在当前决策与交付中高亮『主上下文已被补位侵蚀』的 Context Wall 风险，并由 Self-Harness 标记为 harness 弱点（此环境下无法避免补位，故降级为可见风险而非硬停） |
| 托管的 Node 运行时未附带 npm | 托管 Node 目录下无 npm 可执行文件，无法运行项目 npm scripts | 回退到系统 Node.js；或预先为托管运行时安装 npm |
| Shell 环境缺少 nohup / sleep | 无法用 nohup 或 sleep 启动/等待后台服务，导致预览服务初次启动失败 | 使用后台运行原生机制；等待启动用对应阻塞读取机制 |

**使用约定**：

- 子代理在运行构建命令前，应先检查本节是否有对应环境的规避方案；若有，直接采用规避方案运行命令。
- 若遇到新的环境问题（非代码问题，如 JDK 兼容性、工具链缺失、沙箱限制等），子代理应在返回摘要中标注 `failure_tags: 依赖`，并在"遗留问题"中描述现象与规避方案；主代理在 Self-Harness 元循环中将该问题追加到本表。
- 环境问题不触发"单问题修复熔断"（因非代码问题无法通过修复解决），但应记录规避方案供后续子代理复用。
