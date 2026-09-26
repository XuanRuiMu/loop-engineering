# 任务10：推理增强

验证 `references/推理增强.md` 的三道推理门、方法库、决策卡和来源完整，且已接入主流程、Worker提示词和四个专项Skill。删除G3门、推翻条件或提问上限的负例必须失败；推理门不得进入Worker返回字段，也不得写入 `PROGRESS.md` 模板。

```bash
python -B task-10-reasoning-enhancement/verify.py
```
