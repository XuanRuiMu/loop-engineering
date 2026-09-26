# 任务9：跨宿主与文档一致性

扫描循环工程、8个组合专项Skill、项目配置和评测契约，禁止固定代理API、参数名、错误字符串、固定命令和绝对机器路径；验证每个专项都有`headless_mode=true`。`EVIDENCE.md`在2026-09-25之前的历史原文允许保留旧宿主词，当前证据区必须无禁止词。同时用临时套件验证runner拒绝缩减、扩张、别名、缺目录、缺脚本、哈希变化、假PASS和子任务失败。

```bash
python -B task-09-runner-docs-portability/verify.py
```
