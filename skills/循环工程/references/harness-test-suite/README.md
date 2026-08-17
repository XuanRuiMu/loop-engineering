# 固定回归任务集

本目录包含循环工程 skill 的最小固定回归任务集，用于在每次迭代后快速验证 skill 元文件与约定结构未被意外破坏。

## 任务清单

> `run_all.py` 会自动发现本目录下所有以 `task-` 开头的子目录并依次运行其 `verify.py`，因此新增回归任务只需新建 `task-XX-*/verify.py` 即可被套件覆盖，无需手动维护下表——但下表须与磁盘实际任务保持一致，避免文档漂移。

| 任务 | 目录 | 验证目标 |
|---|---|---|
| 任务 1 | `task-01-progress-md/` | 验证 `PROGRESS.md` 结构（元信息/范围边界/功能点/已完成/当前决策）含 `FP-` 前缀记录；无运行时实例时以 `references/PROGRESS模板.md` 为结构基准（EV-008） |
| 任务 2 | `task-02-subagent-summary/` | 验证子代理摘要字段与类型符合约定 |
| 任务 3 | `task-03-skill-structure/` | 验证 skill 目录结构符合规范（含本任务集） |
| 任务 4 | `task-04-evidence-structure/` | 验证 `.agents/evidence/` 目录及子目录存在，且 `EVIDENCE.md` 包含必要章节 |
| 任务 5 | `task-05-subagent-output-format/` | 验证子代理摘要 `token_estimate` / `failure_tags` / `evidence_link` 字段格式（含 7 个失败分支样本 + 1 有效路径） |
| 任务 6 | `task-06-backfill-contract/` | 验证补位熔断（`orchestrator_backfill_limit` / 「补位熔断」）与契约变更协调（`契约变更协调` / PROGRESS模板·子代理模板「契约变更」）两项盲点修复已落地（EV-005 / EV-006） |
| 任务 7 | `task-07-meta-review-guard/` | 验证元循环确认偏差修复（SKILL.md 引用「方案审查」快速模式独立审查自动级核心提案）与「无新证据即停」须经独立确认已落地（EV-007 / EV-014） |

## 运行方式

一次性运行全部任务：

```bash
python run_all.py
```

单独运行某个任务：

```bash
python task-01-progress-md/verify.py
python task-02-subagent-summary/verify.py
python task-03-skill-structure/verify.py
python task-04-evidence-structure/verify.py
```

每个验证脚本成功时打印 `PASS` 并返回退出码 `0`，失败时打印 `FAIL` 并返回非零退出码。
