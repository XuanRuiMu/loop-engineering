# 任务 4：验证证据目录结构

## 描述
确认循环工程 skill 的 `.agents/evidence/` 目录按 `EVIDENCE.md` 规范存在，且包含 `traces/`、`proposals/`、`validations/` 三个子目录；同时确认 `EVIDENCE.md` 本身存在并包含必要章节。

## 输入
- 项目根目录下的 `.agents/evidence/` 及其子目录
- skill 根目录下的 `EVIDENCE.md`

## 预期输出
- `PASS: 证据目录结构符合规范`

## 验证命令

```bash
python task-04-evidence-structure/verify.py
```
