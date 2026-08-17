# 任务 1：验证 PROGRESS.md 解析

## 描述
确认循环工程 skill 的 `PROGRESS.md` 结构合法：含必要章节（元信息 / 范围边界 / 功能点 / 已完成 / 当前决策）与至少一条 `FP-` 前缀功能点记录。无运行时实例时，以 `references/PROGRESS模板.md` 为结构基准（EV-008），使干净仓库默认通过。

## 输入
- 候选：`skill 根目录/PROGRESS.md` 或 `项目根/PROGRESS.md`；均不存在时回退 `references/PROGRESS模板.md`

## 预期输出
- `PASS: PROGRESS.md 结构正确（<路径>）` 或 `PASS: 基于模板校验通过（仓库无运行时 PROGRESS.md，模板即结构规范：PROGRESS模板.md）`

## 验证命令

```bash
python task-01-progress-md/verify.py
```
