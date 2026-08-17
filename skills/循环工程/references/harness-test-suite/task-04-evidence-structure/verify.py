import sys
import pathlib
import re

技能根目录 = pathlib.Path(__file__).resolve().parents[3]

证据规范文件路径 = 技能根目录 / 'EVIDENCE.md'
if not 证据规范文件路径.exists():
    print("FAIL: EVIDENCE.md 不存在")
    sys.exit(1)

文件内容 = 证据规范文件路径.read_text(encoding='utf-8')

# 检查必要章节
必要章节列表 = ['## 证据记录格式', '## 活跃证据']
缺失章节列表 = [章节 for 章节 in 必要章节列表 if 章节 not in 文件内容]
if 缺失章节列表:
    print(f"FAIL: EVIDENCE.md 缺少必要章节: {缺失章节列表}")
    sys.exit(1)

# 检查至少有一条证据记录
if not re.search(r'(?m)^\|\s*\d{4}-\d{2}-\d{2}\s*\|', 文件内容):
    print("FAIL: EVIDENCE.md 中至少应包含一条带日期的证据记录")
    sys.exit(1)

print("PASS: 证据目录结构符合规范")
