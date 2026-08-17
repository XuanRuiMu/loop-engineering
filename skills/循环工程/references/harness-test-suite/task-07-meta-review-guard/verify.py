# 回归任务 7：验证元循环确认偏差修复（EV-007）是否真实落地
# - SKILL.md Proposal Validation 须引用「方案审查」快速模式（反对者子代理）独立审查自动级核心提案
# - SKILL.md 须声明「无新证据即停」须经独立确认（封堵确认偏差残角，EV-013 补面）
import pathlib
import sys

技能根 = pathlib.Path(__file__).resolve().parents[3]
检查项 = [
    (技能根 / "SKILL.md", "方案审查", "元循环确认偏差修复缺失：SKILL.md 未引用『方案审查』快速模式独立审查自动级核心提案"),
    (技能根 / "SKILL.md", "无新证据", "确认偏差残角未封堵：Self-Harness 停止条件未声明『无新证据即停』须经独立确认"),
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

print("PASS - 元循环确认偏差修复与无新证据独立确认均已落地")
sys.exit(0)
