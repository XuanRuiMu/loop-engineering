# Loop Engineering · 循环工程

> 让任意智能体把一个目标自主循环成「已测试、已审查、可交付」的成果，并在每次任务后自我改进。

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

## 介绍

**循环工程** 是一套「方法论 + 技能包」，它的核心主张只有一句：

> **在 TRAE、WorkBuddy 这类内置中低等级模型的工具里，让普通 AI 大模型用「更多的 token 和更长的时间」，换取出货质量比肩世界级顶级模型的水平。**

顶级模型很贵、也很聪明；但大多数日常工具（TRAE、WorkBuddy、Cursor、Claude Code 等）默认跑的是更便宜的中低等级模型。循环工程不靠换模型，而是靠**工程化约束**把质量拉满：

- 你给一个目标，它把目标拆成功能点，派发**全新上下文**的子代理逐个实现；
- 每个功能点都必须**先跑测试、再跑三轴审查**才算完成，绝不「声称做完」；
- 用**熔断机制**防止在某个 bug 上死循环；
- 并在**每次任务后**跑元循环**自我改进自身的规则**。

它要解决的，正是智能体最弱的一环：*把事做完、做对*。智能体改一个文件很在行，但「把整个项目交付」就不行了——上下文会爆、范围会漂、会在一个 bug 上死循环、会跳过测试，而且永远不会「越用越会干」。循环工程把项目状态外置到一个极小的 `PROGRESS.md`（只保留「现在需要什么」），主线程永不膨胀，强制验证与审查，并叠加熔断与自我改进。

它本质是**元技能**：负责编排，真正的活由一整套随附技能干——三轴审查、纾困复盘、方案审查、代码需求实现器、Bug修复、软件测试、生成PRD、会话交接，全部打包在内、开箱即用。`SKILL.md` 采用 Anthropic Agent Skills 格式，可被 Claude Code、CodeBuddy/WorkBuddy、TRAE、Cursor 及任何读取 `SKILL.md` 的智能体加载。

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

从 [Releases 页](https://github.com/XuanRuiMu/loop-engineering/releases) 下载 `loop-engineering-skills.zip`，解压到对应工具的技能目录即可：

- **CodeBuddy / WorkBuddy / TRAE**：解压到 `.agents/skills/`
- **Claude Code**：解压到 `~/.claude/skills/`（全局）或项目内 `skills/`
- **Cursor / Windsurf**：把各 `SKILL.md` 接入 skills loader 或指向 rules

压缩包顶层就是 9 个技能文件夹，一次解压全部就位；想升级随时重新下载。（下载后可用 SHA256 `28b29f6b9673948d47a4db3c1cd4820533ce9425cb7d4af4d9236b88a0183664` 核对完整性。）

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

## 对比

循环工程的对手不是「另一个 AI」，而是「你自己盯着 AI 干」和「工具自带的单次目标指令」。

| 能力 | 裸用智能体 | 单次目标指令（如 Claude Code 的 `/goal`、Codex 的 `/目标`）| **循环工程** |
| --- | --- | --- | --- |
| 不用你盯着也能做完 | 否 | 部分 | **是**（自主循环到停止条件）|
| 扛得住上下文窗口 | 否 | 否（单上下文易爆）| **是**（全新上下文子代理 + PROGRESS.md）|
| 止住失控死循环 | 否 | 通常无 | **是**（熔断机制）|
| 声称完成前先跑测试 + 审查 | 有时 | 通常无 | **是**（强制三轴）|
| 随附开箱即用技能包 | 否 | 否 | **是**（9 个技能打包）|
| 随时间自我改进 | 否 | 否 | **是**（元循环）|

> 和同类循环 / 自动化 skill 相比，循环工程的差异点在于：它**自带一整套随附技能**（三轴审查、纾困复盘、方案审查、TDD 实现、Bug 修复、测试、PRD、会话交接），并强制「测试 + 三轴审查才算完成」+ 熔断 + 自我改进元循环——而不是只给一个空壳循环框架让你自己填。

> 它**不替代** Claude Code 的 `/goal` 或 Codex 的 `/目标`：你完全可以在这些工具里调用循环工程，把一次性的目标指令升级成「带审查、带熔断、会自我改进」的工程循环。

---

## 常见问题

**它只能写代码吗？** 不。循环本身是通用的——任何能被拆成「可验证步骤 + 明确停止条件」的创造性或生产性任务都能用。随附技能默认面向软件任务，但你可以把派发映射接到自己的技能。举几个非代码的例子：

- **写长篇小说**：`loop: 把这本 30 万字小说按大纲拆成章节，逐章写，每章跑三轴审查（人物声纹一致性 / 情节逻辑 / 文风签名），人设前后矛盾就熔断回写。` 中低等级模型靠多轮循环 + 逐章审查，照样能写出人物稳定、伏笔回收、文风统一的成稿，而不是一次生成就崩。
- **写音乐 / 专辑**：`loop: 写一张 10 首歌的专辑，逐首生成，每首跑审查（和声进行 / 曲式结构 / 主题动机统一 / 编曲层次），主题动机前后不统一就重做。` 模型用更多 token 把「一首还行」打磨成「整张概念统一」。
- **写研究报告 / 论文**：`loop: 把这份课题拆成文献综述、方法、实验、讨论，逐节写并跑事实核查与引用审查，数据来源缺失就标记阻塞。`

核心思路一致：**用更便宜的模型 + 更多循环轮次 + 强制验证，换世界级产出**。这正是它在 TRAE、WorkBuddy 这类中低等级模型工具里价值最大的原因。

**子代理卡住了怎么办？** 修复 5 次仍失败就标记为阻塞，主代理跳过继续；若它阻塞了后续所有依赖项，循环停下，并在方向性问题时先跑纾困复盘再汇报。
