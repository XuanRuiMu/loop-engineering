# Contributing to Loop Engineering · 循环工程

Thanks for helping the loop get better at looping.

## Principles · 原则

- **Evidence over opinion.** Any proposed change to a skill's harness must cite a real failure pattern (a `PROGRESS.md` entry, a sub-agent summary, or a trace). Fabricated evidence is rejected.
  重证据轻臆断。任何对 harness 的改动都必须引用真实失败模式，禁止编造证据。
- **Graded changes.** Proposals are classified **auto / confirm / forbidden**:
  - *auto* — template/format tweaks, or core fixes that passed an independent opponent review + regression suite.
  - *confirm* — needs a human decision before applying.
  - *forbidden* — core flow, AGENTS-level rules, or breaker defaults; never auto-applied.
- **Small, verifiable.** One failure pattern per proposal. Keep `PROGRESS.md` (and the repo) compact.

## How to contribute · 如何贡献

1. Fork and branch (`feat/...`, `fix/...`, `harness/...`).
2. Edit the relevant `skills/<name>/SKILL.md` (or its `references/`).
3. If you touched the harness, add/extend a case under `skills/循环工程/references/harness-test-suite/`.
4. Open a PR describing: the failure pattern, the evidence, the proposed fix, and its grade.
5. For `confirm`/`forbidden` grades, the maintainer decides — never auto-merged.

## Running the regression suite · 跑回归

```bash
python skills/循环工程/references/harness-test-suite/run_all.py
```

All tasks should pass before a harness change ships.
