# Loop Engineering

> In tools like TRAE and WorkBuddy, when using a lower-tier model, let an ordinary AI model spend *more tokens and more time* to produce output that rivals the world's top-tier models.

[![Stars](https://img.shields.io/github/stars/XuanRuiMu/loop-engineering?style=flat&logo=github)](https://github.com/XuanRuiMu/loop-engineering/stargazers)
[![License: MIT](https://img.shields.io/github/license/XuanRuiMu/loop-engineering)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering/commits/main)
[![Issues](https://img.shields.io/github/issues/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering/issues)
[![Repo Size](https://img.shields.io/github/repo-size/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering)
[![Type](https://img.shields.io/badge/type-agent--skill-blue)](https://github.com/XuanRuiMu/loop-engineering)

> 🌐 [中文](README.md) ｜ English

---

## A real example: building a csv2json tool with Loop Engineering

You issue one instruction:

> loop: write a Python CLI tool csv2json that converts CSV to JSON; include unit tests, CLI flags (-i input, -o output, stdin support), and error handling. Stop condition = pytest all green + three-axis review clean.

Loop Engineering runs it as one autonomous loop:

**① Goal definition** — verifiable stop condition: `pytest` green, `ruff` clean, three-axis review with no blockers; circuit-breaker budget 20 loops; scope boundary "no GUI, no database".

**② Decomposition** — written into a tiny `PROGRESS.md` (the only state the main thread keeps):

```text
FP-1 CLI flag parsing (-i / -o / stdin)
FP-2 CSV reading (encoding detection + header)
FP-3 JSON output (ensure_ascii=False)
FP-4 Unit tests (normal / empty file / bad CSV)
FP-5 Error handling (no crash, readable errors)
```

**③ Autonomous loop** — the Orchestrator reads progress, dispatches fresh-context sub-agents, each returning only a short summary:

```text
FP-1 sub-agent → TDD        ✅ 6/6 tests pass
FP-2 sub-agent → TDD        ✅ 4/4 tests pass
FP-3 sub-agent → implement  ⚠ three-axis review caught it: JSON used default
                                ensure_ascii=True, Chinese became \uXXXX → fixed ✅
FP-4 sub-agent → TDD        ✅ 9/9 tests pass
FP-5 sub-agent → implement  ✅ edge cases covered; bad CSV tripped the
                                circuit-breaker once → re-dispatched ✅
```

After each feature point, `PROGRESS.md` keeps only "done" and "what's next", so the main thread's context never bloats.

**④ Delivery + self-improvement** — full suite green, three-axis review passed; the meta-loop mined one pattern from this task: "whenever file I/O is involved, sub-agents often miss encoding or exception branches", so it auto-added a harness rule "file-related feature points must check encoding and exception list in the three-axis review". The next similar task benefits immediately.

You spoke the goal once and never babysat the edits; a lower-tier model, through *more tokens + more time + mandatory verification*, shipped output on par with a top-tier model.

---

## Introduction

**Loop Engineering** is a methodology + skill pack. Top models are expensive and smart; most everyday tools (TRAE, WorkBuddy, Cursor, Claude Code…) default to cheaper lower-tier models. Loop Engineering doesn't swap the model — it uses **engineering constraints** to max out quality:

- You set a goal; it breaks it into feature points and dispatches **fresh-context** sub-agents to implement each one.
- Every feature point must pass **tests first, then a three-axis review** before it counts as done — no "I'm finished" without proof.
- A **circuit-breaker** stops runaway loops on a single bug.
- And after *every* task, a meta-loop **improves its own rules**.

It was built to fix the thing agents are worst at: *finishing and getting it right*. Agents are great at one file and terrible at "ship the whole project" — they lose context, drift off-scope, loop forever on a bug, skip tests, and never get better at being an agent. Loop Engineering externalizes state into a tiny `PROGRESS.md` (only what's needed *now*), keeps the main thread from ever bloating, enforces verification + review, and wraps it all in a circuit-breaker plus a self-improving meta-loop.

It is a *meta*-skill: it orchestrates, and a bundle of companion skills (three-axis review, stuck-state reset, pre-implementation adversarial review, TDD implementation, bug-fix, testing, PRD, and session handoff) do the actual work. All are included, so the repo is self-contained. The `SKILL.md` format is the Anthropic Agent Skills format, so it loads in Claude Code, CodeBuddy/WorkBuddy, TRAE, Cursor, and any agent that reads `SKILL.md`.

---

## Features

- **Autonomous loop** — Orchestrator dispatches Headless sub-agents; you only stop in three cases: blocked, circuit-break, or done.
- **Context-wall proof** — State lives in `PROGRESS.md`, not in any LLM window. Sub-agents use fresh contexts and return only short summaries.
- **Verifiable stop conditions** — "optimize it" is rejected; "all tests pass + lint clean" is required.
- **Circuit-breaker** — Same bug fixed 5× → skip. Total loops hit cap → stop and report. No infinite loops.
- **Three-axis review (mandatory)** — Standards + Spec + BlindSpot, run as parallel sub-agents, never skipped.
- **Self-Harness meta-loop** — After each task, it mines its own failure patterns and patches its own rules (graded auto / confirm / forbidden).
- **Contract coordination** — Cross-feature API/schema changes are tracked as deltas so parallel sub-agents don't build on stale assumptions.

---

## Install

One line, no build step, no dependencies:

```bash
# Linux / macOS — installs into Claude Code's global skills dir (~/.claude/skills)
bash -c "$(curl -fsSL https://raw.githubusercontent.com/XuanRuiMu/loop-engineering/main/install.sh)"

# Windows (PowerShell) — installs into ~/.claude/skills
irm https://raw.githubusercontent.com/XuanRuiMu/loop-engineering/main/install.ps1 | iex
```

Both scripts accept an optional target directory, e.g. `install.sh /path/to/your-project/.agents/skills`.

### Or download the zip

Grab `loop-engineering-skills.zip` from the [Releases page](https://github.com/XuanRuiMu/loop-engineering/releases) and unzip it into your tool's skills directory:

- **CodeBuddy / WorkBuddy / TRAE** — unzip into `.agents/skills/`
- **Claude Code** — unzip into `~/.claude/skills/` (global) or project `skills/`
- **Cursor / Windsurf** — point your skills loader / rules at the `SKILL.md` files

The zip's top level *is* the 9 skill folders, so one unzip drops them all in. Re-download anytime to upgrade. (After download you can verify integrity with SHA256 `28b29f6b9673948d47a4db3c1cd4820533ce9425cb7d4af4d9236b88a0183664`.)

---

## How it works

Four phases, with a circuit-breaker and a self-improvement loop wrapped around them:

1. **Goal definition** — turn the request into a verifiable stop condition + circuit-breaker budget + explicit scope boundaries ("do / don't / never touch").
2. **Decomposition** — split into coarse feature points, written into a *compact* `PROGRESS.md`.
3. **Autonomous loop (core)** — Orchestrator reads `PROGRESS.md`, picks the next ready feature point, dispatches a Headless sub-agent, receives a short summary, compresses the entry, repeats. Dependency and contract checks run before each dispatch.
4. **Delivery** — re-run the full test suite, run the **Self-Harness meta-loop**, then deliver via `AskUserQuestion` with a complete report; optionally clean up process files.

**Circuit-breaker** stops the loop on: same problem fixed 5×, total loops at cap, a blocking feature that everything depends on, or token budget exceeded.

**Self-Harness** mines reusable failure patterns from the just-finished task (with evidence, never fabricated), proposes harness-level fixes, validates them against a regression task suite, and applies auto-grade fixes — then reports confirm-grade fixes to you.

---

## Companion skill pack

Loop Engineering is a *meta*-skill: it orchestrates, the companions do the work. All are bundled so the repo is self-contained.

| Skill (folder name) | Role in the loop |
| --- | --- |
| **循环工程** (Loop Engineering, this one) | Orchestrator + Headless loop, circuit-breaker, Self-Harness |
| **三轴审查** (Three-Axis Review) | Mandatory code review: Standards / Spec / BlindSpot (parallel sub-agents) |
| **纾困复盘** (Stuck-State Reset) | Direction reset when stuck / circuit-broken |
| **方案审查** (Adversarial Review) | Adversarial pre-implementation review (quick / deep / grill modes) |
| **代码需求实现器** (TDD Implementer) | TDD feature implementation dispatched to sub-agents |
| **Bug修复** (Bug Fix) | Diagnosis + fix flow dispatched to sub-agents |
| **软件测试** (Testing) | Test execution + verification |
| **生成PRD** (PRD Generator) | Fine-grained decomposition when needed |
| **会话交接** (Session Handoff) | Hand context to a new session for cross-session runs |

> The folder names above are the exact skill directory names — copy them verbatim into your skills directory.

---

## Compared to the alternatives

Loop Engineering's rivals aren't "another AI" — they're "you babysitting the AI" and "the single-goal directive your tool ships with."

| Capability | Vanilla agent | Single-goal directive (e.g. Claude Code `/goal`, Codex `/目标`) | **Loop Engineering** |
| --- | --- | --- | --- |
| Finishes without you | No | Partly | **Yes** (autonomous loop to stop condition) |
| Survives the context window | No | No (single context blows up) | **Yes** (fresh-context sub-agents + PROGRESS.md) |
| Stops runaway loops | No | Usually none | **Yes** (circuit-breaker) |
| Tests + review before claiming done | Sometimes | Usually none | **Yes** (mandatory 3-axis) |
| Bundled ready-to-use skill pack | No | No | **Yes** (9 skills included) |
| Improves itself over time | No | No | **Yes** (Self-Harness) |

> Versus other loop / automation skills, Loop Engineering's differentiator is that it ships a **full companion skill pack** (three-axis review, stuck-state reset, adversarial review, TDD implementer, bug-fix, testing, PRD, session handoff) and enforces "tests + 3-axis review before done" + circuit-breaker + self-improving meta-loop — not just an empty loop shell you have to fill yourself.

> It does **not replace** Claude Code's `/goal` or Codex's `/目标`: you can run Loop Engineering *inside* those tools to upgrade a one-shot goal directive into an "reviewed, circuit-broken, self-improving" engineering loop.

---

## FAQ

**Can it write novels or music too?** Yes. The loop is generic — any creative or productive task that can be broken into *verifiable steps + an explicit stop condition* works. A few non-code examples:

- **Writing a novel** — `loop: split this 300k-word novel into chapters by outline, write chapter by chapter, run a three-axis review on each (character-voice consistency / plot logic / prose signature), circuit-break and rewrite on character contradictions.` A lower-tier model, through many loop iterations + per-chapter review, still produces a coherent manuscript with stable characters and consistent voice — instead of collapsing after one giant generation.
- **Writing music / an album** — `loop: write a 10-track album, generate track by track, review each (harmonic progression / song structure / thematic-motif unity / arrangement depth), redo any track where the motif isn't consistent.` The model spends more tokens turning "one decent track" into "a conceptually unified album."
- **Writing a research report / paper** — `loop: split this topic into literature / method / experiment / discussion, write each section and run fact-check + citation review, flag any missing data source as blocked.`

The core idea is the same: **a cheaper model + more loop iterations + mandatory verification = world-class output.**

**What if a sub-agent gets stuck?** After 5 failed fix attempts it's marked blocked, the Orchestrator skips it and continues; if it blocks everything downstream, the loop stops and (on a direction problem) runs 纾困复盘 before reporting.
