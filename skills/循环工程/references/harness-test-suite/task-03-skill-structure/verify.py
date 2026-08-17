import sys
import pathlib

技能根目录 = pathlib.Path(__file__).resolve().parents[3]

必需文件列表 = [
    技能根目录 / 'SKILL.md',
]
必需引用文件列表 = [
    技能根目录 / 'references' / '子代理提示词模板.md',
    技能根目录 / 'references' / 'Orchestrator-Headless模式.md',
    技能根目录 / 'references' / 'PROGRESS模板.md',
]

缺失文件列表 = [str(文件) for 文件 in 必需文件列表 + 必需引用文件列表 if not 文件.exists()]
if 缺失文件列表:
    print(f"FAIL: 缺失文件: {缺失文件列表}")
    sys.exit(1)

任务集目录 = 技能根目录 / 'references' / 'harness-test-suite'
if not 任务集目录.exists():
    print("FAIL: harness-test-suite 目录不存在")
    sys.exit(1)

任务目录列表 = [d for d in 任务集目录.iterdir() if d.is_dir() and d.name.startswith('task-')]
if len(任务目录列表) < 3:
    print(f"FAIL: harness-test-suite 下任务目录数量不足 3 个，实际 {len(任务目录列表)}")
    sys.exit(1)

print("PASS: skill 目录结构符合规范")
