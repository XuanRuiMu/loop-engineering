# Loop Engineering

> A meta-skill that turns an ordinary low-tier model into an **autonomous engineering loop**: Orchestrator dispatch + Headless sub-agents + circuit breaker + forced three-axis review + meta-learning — using *more tokens and more time* to ship at the level of world-class models, inside TRAE, WorkBuddy, Cursor, Claude Code, and more.

[![Stars](https://img.shields.io/github/stars/XuanRuiMu/loop-engineering?style=flat&logo=github)](https://github.com/XuanRuiMu/loop-engineering/stargazers)
[![Forks](https://img.shields.io/github/forks/XuanRuiMu/loop-engineering?style=flat&logo=github)](https://github.com/XuanRuiMu/loop-engineering/forks)
[![License: MIT](https://img.shields.io/github/license/XuanRuiMu/loop-engineering)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering/commits/main)
[![Issues](https://img.shields.io/github/issues/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering/issues)
[![Release](https://img.shields.io/github/v/release/XuanRuiMu/loop-engineering?logo=github)](https://github.com/XuanRuiMu/loop-engineering/releases)
[![Repo Size](https://img.shields.io/github/repo-size/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering)
[![Type](https://img.shields.io/badge/type-meta--skill-orange)](https://github.com/XuanRuiMu/loop-engineering)
[![Skills](https://img.shields.io/badge/skills-9-blueviolet)](https://github.com/XuanRuiMu/loop-engineering/tree/main/skills)

> 🌐 [中文](README.md) ｜ English

---

## A real example: building a csv2json tool with Loop Engineering

You issue one instruction:

> loop: write a Python CLI tool csv2json that converts CSV to JSON; include unit tests, CLI flags (-i input, -o output, stdin support), and error handling. Stop condition = pytest all green + three-axis review clean.

Loop Engineering runs it as one autonomous loop:

**① Goal definition** — verifiable stop condition: `pytest` green, `ruff` clean, three-axis review with no blockers; circuit-breaker budget 20 loops; scope boundary "no GUI, no database".

**② Decomposition** — written into a tiny `PROGRESS.md` (the only state the main thread ever keeps):

```text
FP-1 CLI arg parsing (-i / -o / stdin)
FP-2 CSV reading (encoding detection + headers)
FP-3 JSON output (ensure_ascii=False)
FP-4 Unit tests (normal / empty / malformed CSV)
FP-5 Error handling (never crash, readable errors)
```

**③ Autonomous loop** — orchestrator reads progress, dispatches fresh-context sub-agents, each returns only a short summary:

```text
FP-1 sub-agent → TDD   ✅ 6/6 tests pass
FP-2 sub-agent → TDD   ✅ 4/4 tests pass
FP-3 sub-agent → impl  ⚠ blocked by review: JSON emitted \uXXXX for CJK
                        (ensure_ascii defaulted to True) → fixed ✅
FP-4 sub-agent → TDD   ✅ 9/9 tests pass
FP-5 sub-agent → impl  ✅ edge cases covered; bad CSV tripped breaker once → redispatch ✅
```

After each step, `PROGRESS.md` keeps only "done" + "what's next" — the main context never grows.

**④ Delivery + self-improvement** — all tests green, three-axis review clean; the meta-loop mines one pattern from this task: "file-I/O subtasks often miss encoding handling or error branches", so a harness rule is appended: *file-touching feature points must check encoding & error lists in the review*. Next task benefits immediately.

You said the goal once and never babysat it. A low-tier model, through "more tokens + more time + forced verification", shipped at top-model quality.

---

## What is it?

Loop Engineering is a **methodology + skill pack**. Top models are expensive and smart; but most daily tools (TRAE, WorkBuddy, Cursor, Claude Code, etc.) run cheaper low-tier models by default. Loop Engineering doesn't swap models — it forces quality through **engineering constraints**:

- You give a goal; it decomposes it into feature points and dispatches **fresh-context** sub-agents to implement each one;
- Every feature point must **run tests, then run a three-axis review** before it counts as done — never "claimed done";
- A **circuit breaker** stops death-loops on a single bug;
- After every task, a **meta-loop improves its own harness**.

It targets the weakest spot of agents: *finishing the whole job, correctly*. An agent is great at editing one file — but terrible at "delivering the whole project": context explodes, scope drifts, it loops on a bug, it skips tests, and it never gets better over time. Loop Engineering externalizes project state to a tiny `PROGRESS.md` ("what do I need right now"), keeps the main thread lean, enforces verification & review, and layers circuit-breaking and self-improvement on top.

It is a **meta-skill**: it orchestrates; the bundled skills do the actual work — 三轴审查, 纾困复盘, 方案审查, 代码需求实现器, Bug修复, 软件测试, 生成PRD, 会话交接 — all included, ready to use. `SKILL.md` follows the Anthropic Agent Skills format and can be loaded by Claude Code, CodeBuddy/WorkBuddy, TRAE, Cursor, or any agent that reads `SKILL.md`.

---

## Capabilities

- **Autonomous loop**: the orchestrator dispatches sub-agents and only comes back to you on *blocked / tripped / done*.
- **Context-explosion resistant**: state lives in files, not in the conversation; sub-agents run in fresh contexts and return short summaries.
- **Verifiable stop conditions**: rejects fuzzy goals like "make it better"; must be "all tests pass + lint clean".
- **Circuit breaker**: 5 failed fixes on the same issue → mark blocked and skip; total loop budget hit → stop and report. Never dead-loops.
- **Three-axis review (forced)**: standards + spec + blind-spot axes via parallel sub-agents, never skipped.
- **Meta-loop self-check**: after each task, mines its own failure modes and improves the harness (auto / needs-confirm / never-auto tiers).
- **Contract coordination**: cross-feature public-contract changes are recorded incrementally so parallel sub-agents never build on stale assumptions.
- **Backfill mechanism**: when a sub-agent fails or underdelivers, the orchestrator may step in personally (bounded budget), then re-dispatch a fresh-context worker to avoid anchoring bias.

---

## Repository layout

```text
loop-engineering/
├── README.md            # This doc (Chinese)
├── README_EN.md         # English version
├── install.sh           # One-line installer (Linux / macOS)
├── install.ps1          # One-line installer (Windows)
├── LICENSE              # MIT
└── skills/              # 9 bundled skills, ready to use
    ├── 循环工程/        # Meta-skill: orchestration + loop + breaker + meta-loop
    │   ├── SKILL.md     # Main skill doc (Anthropic Agent Skills format)
    │   ├── HARNESS.md   # Harness rules: guarantees, backfill, context wall
    │   ├── BUDGET.md    # Breaker / rounds / token budgets
    │   ├── EVIDENCE.md  # Evidence rules (no "done" without evidence)
    │   └── references/  # Sub-agent prompt templates, PROGRESS template,
    │                    # Orchestrator-Headless pattern, EnvironmentEngineering,
    │                    # frontend verification tips, harness regression suite
    ├── 三轴审查/        # Forced three-axis review (parallel sub-agents)
    ├── 纾困复盘/        # Direction review when stuck / tripped
    ├── 方案审查/        # Pre-implementation adversarial review (quick/deep/grill)
    ├── 代码需求实现器/  # TDD implementation worker
    ├── Bug修复/         # Diagnosis + fix workflow
    ├── 软件测试/        # Test execution & verification
    ├── 生成PRD/         # Decomposition of complex tasks
    └── 会话交接/        # Context handoff across sessions
```

---

## Install

One line. No build step, no dependencies:

```bash
# Linux / macOS — install into Claude Code's global skills dir (~/.claude/skills)
bash -c "$(curl -fsSL https://raw.githubusercontent.com/XuanRuiMu/loop-engineering/main/install.sh)"

# Windows (PowerShell)
irm https://raw.githubusercontent.com/XuanRuiMu/loop-engineering/main/install.ps1 | iex
```

Both scripts accept an optional target directory, e.g. `install.sh /path/to/your-project/.agents/skills`.

### Or download the archive

Grab `loop-engineering-skills.zip` from the [Releases page](https://github.com/XuanRuiMu/loop-engineering/releases) and unzip into your tool's skills directory:

- **CodeBuddy / WorkBuddy / TRAE**: unzip to `.agents/skills/`
- **Claude Code**: unzip to `~/.claude/skills/` (global) or `skills/` in-project
- **Cursor / Windsurf**: point the skills loader at the `SKILL.md` files

The archive contains all 9 skill folders at the top level — one unzip, everything in place; re-download anytime to upgrade. (Optional integrity check — SHA256 `28b29f6b9673948d47a4db3c1cd4820533ce9425cb7d4af4d9236b88a0183664`.)

---

## How it works

Four phases wrapped by a circuit breaker and a self-improvement loop:

1. **Goal definition**: turn the request into a verifiable stop condition + breaker budget + explicit scope ("do / don't / never").
2. **Decomposition**: split into coarse feature points, write into a slim `PROGRESS.md`.
3. **Autonomous loop (core)**: orchestrator reads progress → picks the next feature point → dispatches a sub-agent → collects a short summary → compresses the record → repeats. Dependency & contract checks before dispatch.
4. **Delivery & confirmation**: rerun full tests, run the meta-loop self-check, deliver a full report via `AskUserQuestion`, clean up process files.

**The circuit breaker stops** on: 5 failed fixes on the same issue, hitting the total loop budget, a blocked critical feature point, or exhausted token budget.

**The meta-loop** mines reusable failure patterns from the finished task (evidence required, no fabrication), proposes harness-level fixes, validates them with a regression task set, applies "auto" tier immediately and brings "needs-confirm" tier to you.

---

## Bundled skills

Loop Engineering is a meta-skill: it orchestrates, the bundled skills do the work. All included, ready to use.

| Skill | Role in the loop |
| --- | --- |
| **循环工程** (this skill) | Orchestration + loop + breaker + meta-loop |
| **三轴审查** | Forced three-axis code review (parallel sub-agents) |
| **纾困复盘** | Direction review when stuck / tripped |
| **方案审查** | Pre-implementation adversarial review (quick/deep/grill) |
| **代码需求实现器** | TDD implementation worker |
| **Bug修复** | Diagnosis + fix workflow |
| **软件测试** | Test execution & verification |
| **生成PRD** | Decomposition of complex tasks |
| **会话交接** | Cross-session context handoff |

---

## Comparison

Loop Engineering's real competitor is not "another AI" — it's *you babysitting the AI* and the *single-shot goal commands built into the tools*.

| Capability | Bare agent | One-shot goal (e.g. Claude Code `/goal`, Codex `/目标`) | **Loop Engineering** |
| --- | --- | --- | --- |
| Finishes without you watching | No | Partial | **Yes** (autonomous until stop condition) |
| Survives context limits | No | No (single context blows up) | **Yes** (fresh-context sub-agents + PROGRESS.md) |
| Stops runaway death loops | No | Usually not | **Yes** (circuit breaker) |
| Tests + reviews before claiming done | Sometimes | Usually not | **Yes** (forced three-axis) |
| Ships a ready-to-use skill pack | No | No | **Yes** (9 skills bundled) |
| Improves itself over time | No | No | **Yes** (meta-loop) |

> Compared with other loop/automation skills, Loop Engineering's edge: it **ships an entire bundled skill set** (三轴审查, 纾困复盘, 方案审查, TDD implementation, Bug fix, testing, PRD, handoff) and enforces "tests + three-axis review before done" + circuit breaker + self-improving meta-loop — not just an empty loop skeleton you must fill.

> It does **not replace** Claude Code's `/goal` or Codex's `/目标`: feel free to call Loop Engineering inside those tools to upgrade a one-shot goal into an engineering loop with review, breaker, and self-improvement.

---

## Tests & regression

`skills/循环工程/references/harness-test-suite` ships a full harness regression suite (`run_all.py`) covering:

- `PROGRESS.md` slimness & compression contract
- Sub-agent summary format (short summary, token estimate, failure tags)
- Skill directory structure integrity
- Evidence structure rules
- Meta-review guards

`run_all.py` green every loop is the machine-verifiable guarantee that "Loop Engineering itself hasn't regressed".

---

## FAQ

**Can I use Loop Engineering for novels or music?** Yes. The loop is generic — anything decomposable into "verifiable steps + explicit stop condition" works, including non-code work:

- **Writing a novel**: `loop: break this 300k-word novel into chapters by outline, write chapter by chapter, run a three-axis review each chapter (voice consistency / plot logic / style signature), trip-and-rewrite on character contradictions.` A low-tier model, with multi-round loops + per-chapter review, produces a finished draft that is stable, foreshadowed, and stylistically consistent — instead of one-shot collapse.
- **Writing an album**: `loop: write a 10-track album, generate track by track, review each (harmony / form / thematic-motif consistency / arrangement depth), redo on motif drift.`
- **Research reports / theses**: `loop: split the topic into literature review, method, experiments, discussion; write and fact-check section by section; mark missing sources as blocked.`

Same core idea: **cheaper model + more loop rounds + forced verification = world-class output**.

**What if a sub-agent gets stuck?** After 5 failed fixes, mark it blocked and move on; if it blocks all downstream dependencies, stop the loop and run a 纾困复盘 (direction review) before reporting, for directional issues.

---

## License

[MIT](LICENSE) © 2026 玄锐暮

**Made with ❤️ by 玄锐暮** — giving every ordinary model the power to ship world-class work.