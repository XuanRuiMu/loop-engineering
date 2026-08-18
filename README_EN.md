# Loop Engineering

> Turn any coding agent into an autonomous engineering loop that ships tested, reviewed, and delivered features — then improves itself.

[![Stars](https://img.shields.io/github/stars/XuanRuiMu/loop-engineering?style=flat&logo=github)](https://github.com/XuanRuiMu/loop-engineering/stargazers)
[![License: MIT](https://img.shields.io/github/license/XuanRuiMu/loop-engineering)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering/commits/main)
[![Issues](https://img.shields.io/github/issues/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering/issues)
[![Repo Size](https://img.shields.io/github/repo-size/XuanRuiMu/loop-engineering)](https://github.com/XuanRuiMu/loop-engineering)
[![Type](https://img.shields.io/badge/type-agent--skill-blue)](https://github.com/XuanRuiMu/loop-engineering)

> 🌐 [中文](README.md) ｜ English

---

## What it looks like

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

## Introduction

**Loop Engineering** is a methodology + skill pack that turns a coding agent from a "one-shot assistant" into an **autonomous engineering loop**. You set a goal; it breaks the goal into feature points, dispatches fresh-context sub-agents to implement each one, verifies the result with tests, runs a three-axis code review, circuit-breaks on runaway loops, and — after every single task — runs a meta-loop that **improves its own rules**.

It was built to solve the thing agents are worst at: *finishing*. Agents are great at one file and terrible at "ship the whole project." They lose context, drift off-scope, loop forever on a bug, skip tests, and never get better at being an agent. Loop Engineering externalizes project state into a tiny `PROGRESS.md` (only what's needed *now*), runs each feature point in a **fresh-context sub-agent** so the main thread never bloats, enforces tests + review before anything counts as done, and wraps the whole thing in a **circuit-breaker** plus a **self-improving meta-loop**.

It is a *meta*-skill: it orchestrates, and a bundle of companion skills (three-axis review, stuck-state reset, pre-implementation adversarial review, TDD implementation, bug-fix, testing, PRD, and session handoff) do the actual work. All are included, so the repo is self-contained. The `SKILL.md` format is the Anthropic Agent Skills format, so it loads in Claude Code, CodeBuddy/WorkBuddy, and any agent that reads `SKILL.md`.

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

No script, no network tooling — grab `loop-engineering-skills.zip` from the [Releases page](https://github.com/XuanRuiMu/loop-engineering/releases) and unzip it straight into your skills directory:

```bash
# 1) download loop-engineering-skills.zip from the release, then:
unzip loop-engineering-skills.zip -d ~/.agents/skills     # CodeBuddy / WorkBuddy
# or
unzip loop-engineering-skills.zip -d ~/.claude/skills      # Claude Code
```

Checksum (verify integrity after download, **optional**):

```
SHA256: 28b29f6b9673948d47a4db3c1cd4820533ce9425cb7d4af4d9236b88a0183664
```

```bash
# Linux / macOS
sha256sum loop-engineering-skills.zip
# Windows (PowerShell)
Get-FileHash loop-engineering-skills.zip -Algorithm SHA256
```

The zip's top level *is* the 9 skill folders, so one unzip drops them all in. Re-download anytime to upgrade.

### Prefer to copy by hand?

The `skills/` folder holds 9 ready-to-use skills — drop them into your agent's skills directory:

| Agent | Where to copy |
| --- | --- |
| **Claude Code** | `~/.claude/skills/` (global) or `skills/` (project) |
| **CodeBuddy / WorkBuddy** | `.agents/skills/` |
| **Cursor / Windsurf** | point your rules at the `SKILL.md` files, or use the skills loader |

Then just say:

> **"loop: fix every failing test in this project until all pass"**
> **"loop: add 5 new spells to this plugin, run autonomously until all implemented and tested"**
> **"autonomous loop: extract all Chinese hard-coded strings in this project to a translation file, keep going"**
> **"auto-develop: refactor the auth module, advance feature point by feature point in dependency order, breaker cap 30"**

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

## Examples

See [`examples/`](examples/) for copy-paste material:

- [`examples/PROGRESS.sample.md`](examples/PROGRESS.sample.md) — a filled-in `PROGRESS.md` for a real refactor.
- [`examples/loop-transcript.sample.md`](examples/loop-transcript.sample.md) — a full annotated loop session.

---

## Compared to the alternatives

| Capability | Vanilla agent | You babysitting | **Loop Engineering** |
| --- | --- | --- | --- |
| Finishes without you | No | Sometimes | **Yes** |
| Survives the context window | No | Sometimes | **Yes** (fresh-context sub-agents) |
| Stops runaway loops | No | Sometimes | **Yes** (circuit-breaker) |
| Tests before claiming done | Sometimes | Sometimes | **Yes** (mandatory) |
| Code review on every change | No | Sometimes | **Yes** (3-axis) |
| Improves itself over time | No | No | **Yes** (Self-Harness) |

---

## FAQ

**Does it work with Claude Code?** Yes. The `SKILL.md` format (YAML `name` + `description` frontmatter) is the Anthropic Agent Skills format, so it loads in Claude Code, CodeBuddy/WorkBuddy, and any agent that reads `SKILL.md`.

**Is it only for code?** The loop is generic; the bundled companions target software tasks, but you can wire in your own skills at the dispatch mapping.

**What if a sub-agent gets stuck?** After 5 failed fix attempts it's marked blocked, the Orchestrator skips it and continues; if it blocks everything downstream, the loop stops and (on a direction problem) runs 纾困复盘 before reporting.

---

## Roadmap

- Metrics export (loops used, tokens, breakers triggered) for self-improvement dashboards
- English-localized companion skills alongside the Chinese originals
- More pre-built regression task suites per companion skill

---

## Contributing

Bug fixes, new companion skills, and better harness rules are all welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). The Self-Harness philosophy applies here too: propose changes as evidence-backed, graded fixes.

---

## License

[MIT](LICENSE) — do whatever you want, just keep the attribution.

---

## Connect

- Star the repo if Loop Engineering saved you a context window. ⭐
- File issues for failure patterns you'd like the harness to handle.
- Share your best "loop:" prompts in Discussions.

Built as a self-improving methodology. The repo itself runs Loop Engineering's Self-Harness after every release.
