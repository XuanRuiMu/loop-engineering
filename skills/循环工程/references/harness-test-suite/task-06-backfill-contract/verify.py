# 回归任务 6：验证盲点修复是否落地
# - 盲点1（补位无上限）：BUDGET.md 须含 orchestrator_backfill_limit，SKILL.md 须含「补位熔断」
# - 盲点2（跨功能点契约耦合）：PROGRESS模板/子代理提示词模板/SKILL.md 须含「契约变更」协调
import pathlib
import sys

技能根 = pathlib.Path(__file__).resolve().parents[3]
检查项 = [
    (技能根 / "BUDGET.md", "orchestrator_backfill_limit", "盲点1预算字段缺失"),
    (技能根 / "SKILL.md", "补位熔断", "盲点1补位熔断规则缺失"),
    (技能根 / "SKILL.md", "契约变更协调", "盲点2契约变更协调小节缺失"),
    (技能根 / "references" / "PROGRESS模板.md", "契约变更", "盲点2 PROGRESS 契约变更节缺失"),
    (技能根 / "references" / "子代理提示词模板.md", "契约变更", "盲点2 子代理提示词契约变更字段缺失"),
]

失败 = []
for 路径, 关键词, 说明 in 检查项:
    if not 路径.exists():
        失败.append(f"{说明}：文件不存在 {路径}")
        continue
    文本 = 路径.read_text(encoding="utf-8")
    if 关键词 not in 文本:
        失败.append(f"{说明}：{路径.name} 未含『{关键词}』")

if 失败:
    for f in 失败:
        print(f"FAIL - {f}")
    sys.exit(1)

print("PASS - 补位熔断与契约变更协调两项盲点修复均已落地")
sys.exit(0)
