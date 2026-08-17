import json
import sys
import pathlib

样例文件路径 = pathlib.Path(__file__).parent / 'fixture.json'

if not 样例文件路径.exists():
    print("FAIL: fixture.json 不存在")
    sys.exit(1)

摘要数据 = json.loads(样例文件路径.read_text(encoding='utf-8'))

必填字段映射 = {
    '任务编号': str,
    '状态': str,
    '摘要': str,
}
for 字段名, 期望类型 in 必填字段映射.items():
    if 字段名 not in 摘要数据 or not isinstance(摘要数据[字段名], 期望类型):
        print(f"FAIL: 字段 {字段名} 缺失或类型错误")
        sys.exit(1)

合法状态集合 = {'已完成', '待开始', '进行中'}
if 摘要数据['状态'] not in 合法状态集合:
    print(f"FAIL: 状态值 {摘要数据['状态']} 不在合法集合 {合法状态集合} 中")
    sys.exit(1)

if '失败标签' in 摘要数据 and not isinstance(摘要数据['失败标签'], list):
    print("FAIL: 失败标签必须是列表")
    sys.exit(1)

if 'token消耗' in 摘要数据 and not isinstance(摘要数据['token消耗'], (int, float)):
    print("FAIL: token消耗必须是数值")
    sys.exit(1)

print("PASS: 子代理摘要格式合法")
