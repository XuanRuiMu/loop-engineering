# 循环工程

面向中大型、多功能点和弱模型场景的高成本质量补偿编排器。它通过精简状态快照、跨宿主独立代理、局部验证、并行协作、熔断、恢复和最终门，降低上下文漂移、漏项和假完成。

## 核心能力

- 状态外置：`PROGRESS.md`只保存当前推进所需信息，完成项和失效信息立即删除。
- 跨宿主：只定义语义职责，不绑定任何宿主的工具名、参数名或代理类型。
- 权限策略：默认拥有当前项目所需权限；高危操作用通俗语言说明影响并确认。
- Headless：独立代理和专项Skill不直接交互或替主代理交付，未决事项返回“待用户确认”。
- 质量门：局部测试、构建、lint、证据、独立审查和主代理最终门。
- 熔断：循环、代理实例、修复、stall、补位、墙钟和独立审查能力。
- 自我改进：只有新的、可复现且可跨任务复用的证据才触发Harness提案。

## 组合专项Skill

`代码需求实现器`、`软件测试`、`Bug修复`、`三轴审查`、`方案审查`、`生成PRD`、`纾困复盘`和`会话交接`均支持`headless_mode=true`。

## 文件

|路径|用途|
|---|---|
|`skills/循环工程/SKILL.md`|主流程、跨宿主适配、权限、循环、恢复和Self-Harness|
|`skills/循环工程/BUDGET.md`|预算字段、计数口径和熔断权威来源|
|`skills/循环工程/references/`|环境、Worker、状态、推理增强和前端验证协议|
|`skills/循环工程/references/harness-test-suite/`|固定manifest和10项回归任务|

## 验证

本仓 CI（`.github/workflows/ci.yml`）在每次推送与 PR 上跑三道独立门禁：

|门禁|命令|作用|
|---|---|---|
|回归门禁|`python -B skills/循环工程/references/harness-test-suite/run_all.py`|10 项固定任务，`verify.py` 按 `manifest.json` 的 SHA-256 锁定，防改脚本绕过与空集假绿|
|结构门禁|`python -B tools/校验仓库结构.py`|全仓 `skills/*/SKILL.md` 齐备、文本严格 UTF-8 无乱码、文档相对链接指向真实路径|
|格式门禁|`npx markdownlint-cli "**/*.md"`|Markdown 格式规范，规则集见仓库根 `.markdownlint.json`|

单独运行回归门禁（从发布源根目录）：

```powershell
python -B .\skills\循环工程\references\harness-test-suite\run_all.py
```

成功标准：输出`总计: 10/10 通过`且退出码为0。离线测试不证明真实模型行为，也不证明弱模型经此达到高能力模型的推理效果；真实循环仍需隔离工作区并记录有/无Skill对照、实际写入和工具轨迹。

## 安装

安装脚本是独立发布工具。目标目录必须显式传入；脏源树默认拒绝安装，审阅后显式使用`-AllowDirty`；远程安装必须提供已审计的完整commit SHA。安装器只报告复制完成，运行时加载必须另行验证。

## 许可证

MIT
