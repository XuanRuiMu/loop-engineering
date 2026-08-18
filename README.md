# Loop Engineering · 循环工程

> 让任意编程智能体把一个目标自主循环成「已测试、已审查、可交付」的功能，并在每次任务后自我改进。

[![Stars](https://img.shields.io/github/stars/XuanRuiMu/loop-engineering?style=flat&logo=github)](https://github.com/XuanRuiMu/loop-engineering/stargazers)
[![License: MIT](https://img.shields.io/github/license/XuanRuiMu/loop-engineering)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering/commits/main)
[![Issues](https://img.shields.io/github/issues/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering/issues)
[![Repo Size](https://img.shields.io/github/repo-size/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering)
[![Type](https://img.shields.io/badge/type-agent--skill-blue)](https://github.com/XuanRuiMu/loop-engineering)

> 🌐 简体中文 ｜ [English](README_EN.md)

---

## 运行效果

```
You ❯ loop: fix every failing test in this plugin, don't stop until green

↻ Loop Engineering started
  ▸ Phase 1  Goal: all tests pass · stop = 0 failures · breaker = 30 loops
  ▸ Phase 2  12 feature points written to PROGRESS.md
  ▸ Phase 3  autonomous loop…
     FP-01  sub-agent → TDD + tests      ✅ 14/14  (summarized, context freed)
     FP-02  sub-agent → TDD + tests      ✅ 11/11  (summarized, context freed)
     FP-07  sub-agent → blocked, retried 5× → circuit-break ⚡
             → 纾困复盘: wrong API was assumed → re-planned
     FP-07  re-dispatched (fresh context) → ✅ 9/9
     … 10/12 done, 2 skipped (out of scope)
  ▸ Phase 4  Self-Harness: found 1 weakness → auto-patched a harness rule
  ✓ Delivered: 10 done · 2 skipped · 0 blocked · loops used 14 / 30
```

---

## 中文介绍

**循环工程** 是一套「方法论 + 技能包」，把编程智能体从「一次性的助手」升级为**自主工程循环**：你给目标，它把目标拆成功能点，派发全新上下文的子代理逐个实现，用测试验证、用三轴审查把关、用熔断机制防止死循环，并在**每次任务后**跑元循环**自我改进自身的规则**。

它要解决的，正是智能体最弱的一环：*把事做完*。智能体改一个文件很在行，但「把整个项目交付」就不行了——上下文会爆、范围会漂、会在一个 bug 上死循环、会跳过测试，而且永远不会「越用越会干」。循环工程把项目状态外置到一个极小的 `PROGRESS.md`（只保留「现在需要什么」），每个功能点都在**全新上下文的子代理**里跑（主线程永不膨胀），强制「先测试 + 审查才算完成」，并叠加**熔断机制**与**自我改进的元循环**。

它本质是**元技能**：负责编排，真正的活由一整套随附技能干——三轴审查、纾困复盘、方案审查、代码需求实现器、Bug修复、软件测试、生成PRD、会话交接，全部打包在内、开箱即用。`SKILL.md` 采用 Anthropic Agent Skills 格式，可被 Claude Code、CodeBuddy/WorkBuddy 及任何读取 `SKILL.md` 的智能体加载。

---

## 能力一览

- **自主循环**：主代理派发子代理，只有「阻塞 / 熔断 / 完成」三种情况才停下找你。
- **抗上下文爆炸**：状态在文件里，不在对话里；子代理用全新上下文，只回简短摘要。
- **可验证停止条件**：拒绝「优化一下」这种模糊目标，必须是「测试全过 + lint 零报错」。
- **熔断机制**：同一问题修 5 次仍失败就跳过；总轮次到上限就停下汇报。不死循环。
- **三轴审查（强制）**：规范轴 + 规格轴 + 盲区轴，并行子代理执行，绝不跳过。
- **元循环自检**：每次任务后挖掘自身失败模式，按级别自动 / 待确认 / 禁止自动地改进自身 harness。
- **契约协调**：跨功能点的公开契约变更以增量记录，避免并行子代理基于旧假设实现。

---

## 安装

一行命令，无构建步骤，无依赖：

```bash
# Linux / macOS —— 安装到 Claude Code 的全局技能目录（~/.claude/skills）
bash -c "$(curl -fsSL https://raw.githubusercontent.com/XuanRuiMu/loop-engineering/main/install.sh)"

# Windows（PowerShell）—— 安装到 ~/.claude/skills
irm https://raw.githubusercontent.com/XuanRuiMu/loop-engineering/main/install.ps1 | iex
```

两条脚本都接受可选的目标目录，例如 `install.sh /path/to/your-project/.agents/skills`。

### 或下载压缩包

不用脚本、无需联网工具——从 [Releases 页](https://github.com/XuanRuiMu/loop-engineering/releases) 下载 `loop-engineering-skills.zip`，直接解压进技能目录即可：

```bash
# 1) 从 Releases 下载 loop-engineering-skills.zip，然后：
unzip loop-engineering-skills.zip -d ~/.agents/skills     # CodeBuddy / WorkBuddy
# 或者
unzip loop-engineering-skills.zip -d ~/.claude/skills      # Claude Code
```

校验和（下载后核对完整性，**可选**）：

```
SHA256: 28b29f6b9673948d47a4db3c1cd4820533ce9425cb7d4af4d9236b88a0183664
```

```bash
# Linux / macOS
sha256sum loop-engineering-skills.zip
# Windows（PowerShell）
Get-FileHash loop-engineering-skills.zip -Algorithm SHA256
```

压缩包顶层就是 9 个技能文件夹，一次解压全部就位；想升级随时重新下载。

### 想手动复制？

`skills/` 目录里就是 9 个开箱即用的技能，把它们放进对应智能体的技能目录即可：

| 智能体 | 复制到哪里 |
| --- | --- |
| **Claude Code** | `~/.claude/skills/`（全局）或 `skills/`（项目） |
| **CodeBuddy / WorkBuddy** | `.agents/skills/` |
| **Cursor / Windsurf** | 把 rules 指向各 `SKILL.md`，或使用 skills loader |

然后直接说：

> **"循环工程：把这个项目的所有测试失败修复，直到全部通过"**
> **"loop：给某插件添加 5 个新法术，自主循环直到全部实现并通过测试"**
> **"自主循环：把某项目的所有中文硬编码提取到翻译文件，别停下一直做"**
> **"自动开发：重构认证模块，按依赖顺序逐个功能点推进，熔断上限 30 轮"**

---

## 工作原理

四个阶段，外面再裹一层熔断机制与自我改进循环：

1. **目标定义**：把需求变成可验证停止条件 + 熔断预算 + 明确的范围边界（"做 / 不做 / 绝不碰"）。
2. **任务拆解**：拆成粗粒度功能点，写入精简的 `PROGRESS.md`。
3. **自主循环（核心）**：主代理读进度、选下一个功能点、派发子代理、收简短摘要、压缩记录、循环。派发前做依赖与契约校验。
4. **交付确认**：重跑全量测试、跑元循环自检，再用 `AskUserQuestion` 交付完整报告，并按需清理过程文件。

**熔断机制**在以下情况停下：同一问题修 5 次、总轮次到上限、关键功能点阻塞、或 token 预算耗尽。

**元循环**从刚完成的任务中挖掘可复用的失败模式（必须有证据，禁止编造），提出 harness 层修复，用回归任务集验证，自动级直接落地，待确认级交给你决策。

---

## 随附技能包

循环工程是**元技能**：它负责编排，随附技能负责具体干活。全部打包在内，开箱即用。

| 技能 | 在循环中的角色 |
| --- | --- |
| **循环工程**（本技能）| 编排 + 循环 + 熔断 + 元循环 |
| **三轴审查** | 强制三轴代码审查（规范 / 规格 / 盲区，并行子代理）|
| **纾困复盘** | 卡顿 / 熔断时的方向复盘 |
| **方案审查** | 实施前的对抗性审查（quick / deep / grill 三档）|
| **代码需求实现器** | 派发给子代理的 TDD 实现 |
| **Bug修复** | 派发给子代理的诊断 + 修复流程 |
| **软件测试** | 测试执行与验证 |
| **生成PRD** | 复杂任务细化拆解 |
| **会话交接** | 跨会话续跑的上下文交接 |

---

## 示例

见 [`examples/`](examples/) 中的可复制素材：

- [`examples/PROGRESS.sample.md`](examples/PROGRESS.sample.md) —— 一个真实重构任务填好的 `PROGRESS.md`。
- [`examples/loop-transcript.sample.md`](examples/loop-transcript.sample.md) —— 一段完整的带注释循环会话。

---

## 对比

| 能力 | 裸用智能体 | 你盯着保姆式 | **循环工程** |
| --- | --- | --- | --- |
| 不用你盯着也能做完 | 否 | 有时 | **是** |
| 扛得住上下文窗口 | 否 | 有时 | **是**（全新上下文子代理）|
| 止住失控死循环 | 否 | 有时 | **是**（熔断机制）|
| 声称完成前先跑测试 | 有时 | 有时 | **是**（强制）|
| 每次改动都做代码审查 | 否 | 有时 | **是**（三轴）|
| 随时间自我改进 | 否 | 否 | **是**（元循环）|

---

## 常见问题

**它兼容 Claude Code 吗？** 兼容。`SKILL.md` 用的是 Anthropic Agent Skills 格式（YAML 前置 `name` + `description`），可被 Claude Code、CodeBuddy/WorkBuddy 及任何读取 `SKILL.md` 的智能体加载。

**只能用于写代码吗？** 循环本身是通用的；随附技能面向软件任务，但你可以在派发映射里接入自己的技能。

**子代理卡住了怎么办？** 修复 5 次仍失败就标记为阻塞，主代理跳过继续；若它阻塞了后续所有依赖项，循环停下，并在方向性问题时先跑纾困复盘再汇报。

---

## 路线

- 指标导出（已用轮次、token、触发熔断次数）用于自我改进看板
- 在中文原版之外提供英文版随附技能
- 为每个随附技能补充更多预置回归任务集

---

## 贡献

Bug 修复、新随附技能、更好的 harness 规则都欢迎。见 [CONTRIBUTING.md](CONTRIBUTING.md)。元循环理念在这里同样适用：把改动作为「有证据支撑、分级处理」的修复来提议。

---

## 许可证

[MIT](LICENSE) —— 随便用，保留署名即可。

---

## 关注

- 如果循环工程帮你省下了上下文窗口，给仓库点个 Star。⭐
- 遇到想让 harness 处理的失败模式，尽管提 Issue。
- 在 Discussions 里分享你最得意的 "loop:" 提示词。

本项目本身就是一套自我改进的方法论。每次发版后，仓库都会跑一遍循环工程的元循环。
