# 固定回归任务集

本目录验证循环工程的精简状态、跨宿主提示词、默认最高权限与高危提醒、预算契约、证据路径、推理增强和Self-Harness边界。

## 唯一任务清单

`manifest.json`固定10个任务。`run_all.py`不会动态发现任务；少任务、多任务、缺脚本、非法路径或任一测试失败都会返回非零。

|任务|验证目标|
|---|---|
|`task-01-progress-md`|PROGRESS模板是可覆盖的精简快照，无完成历史和重复状态|
|`task-02-subagent-summary`|Worker摘要v2字段完整，旧JSON契约被拒绝|
|`task-03-skill-structure`|核心文件和10项固定任务与manifest完全一致|
|`task-04-evidence-structure`|证据目录、记录和真实路径边界有效|
|`task-05-subagent-output-format`|完整摘要正负例和三态交叉约束有效|
|`task-06-backfill-contract`|补位熔断与契约增量协调语义完整|
|`task-07-meta-review-guard`|Self-Harness停止判定需要独立复核，核心改动保持独立审查|
|`task-08-permission-risk-guards`|默认最高权限、用户WIP和高危通俗提醒有效|
|`task-09-runner-docs-portability`|核心与专项Skill不绑定固定宿主API，README不漂移|
|`task-10-reasoning-enhancement`|推理增强三门、方法库、决策卡、接线与负例均有效|

## 运行

```bash
python -B references/harness-test-suite/run_all.py
```

从套件目录运行时使用：

```bash
python -B run_all.py
```

成功标准：输出`总计: 10/10 通过`且退出码为0。
