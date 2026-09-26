# 任务1：精简PROGRESS快照

验证`references/PROGRESS模板.md`只包含当前推进必需字段、预算、功能点和可选未决信息；运行时模板不超过55行，不含已完成历史、当前决策或重复计数。缺字段、恢复旧节和预算越界负例必须失败。

```bash
python -B task-01-progress-md/verify.py
```
