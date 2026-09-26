# Loop Engineering

A high-cost quality-compensation orchestrator for medium-to-large, multi-work-item, and weaker-model tasks. It reduces context drift, omissions, and false completion through a minimal state snapshot, host-neutral independent agents, local verification, controlled parallelism, circuit breakers, recovery, and a final gate.

## Capabilities

- External state: `PROGRESS.md` keeps only current information; completed and stale entries are deleted immediately.
- Host neutral: the contract defines semantic roles, never host-specific tool names, parameters, or agent types.
- Permissions: the agent has the permissions the current project needs; high-risk actions require a plain-language explanation and confirmation.
- Headless: independent agents and specialist skills never interact with the user or deliver final results; unresolved items return as `待用户确认`.
- Quality gates: local tests, builds, lint, evidence, independent review, and a serial final gate.
- Circuit breakers: loops, agent instances, repairs, stalls, backfills, wall-clock time, and independent-review capability.
- Self-improvement: harness proposals require new, reproducible, cross-task evidence.

## Specialist skills

`代码需求实现器`, `软件测试`, `Bug修复`, `三轴审查`, `方案审查`, `生成PRD`, `纾困复盘`, and `会话交接` all support `headless_mode=true`.

## Verification

CI (`.github/workflows/ci.yml`) runs three independent gates on every push and pull request:

| Gate | Command | Purpose |
| --- | --- | --- |
| Regression | `python -B skills/循环工程/references/harness-test-suite/run_all.py` | 10 fixed tasks; each `verify.py` is pinned by SHA-256 in `manifest.json`, so neither editing a task script nor emptying the task list can fake a pass |
| Structure | `python -B tools/校验仓库结构.py` | Every `skills/*/SKILL.md` present, all text strictly UTF-8 without mojibake, relative links in docs resolve to real paths |
| Format | `npx markdownlint-cli "**/*.md"` | Markdown formatting, configured by `.markdownlint.json` at the repo root |

Run the regression gate alone from the release root:

```powershell
python -B .\skills\循环工程\references\harness-test-suite\run_all.py
```

Success requires `总计: 10/10 通过` and exit code 0. Offline tests validate contracts and validators; they do not prove live model behavior, nor that weaker models reach stronger-model reasoning quality through this harness.

## Installation

The installer requires an explicit target directory and an audited source state. It reports file-copy completion only; runtime loading must be verified separately.

## License

MIT
