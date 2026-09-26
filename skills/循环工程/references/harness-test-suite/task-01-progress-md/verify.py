import pathlib
import re
import sys


技能根 = pathlib.Path(__file__).resolve().parents[3]
模板路径 = 技能根 / 'references' / 'PROGRESS模板.md'
预算路径 = 技能根 / 'BUDGET.md'
预算映射 = {'总循环': 'total_turn_limit', '子代理实例': 'subagent_call_limit', '主代理补位': 'orchestrator_backfill_limit', '墙钟/min': 'wall_clock_limit_minutes'}


def 提取运行时模板(内容):
    匹配 = re.search(r'## 运行时模板\s+```markdown\s*(.*?)\s*```', 内容, re.S)
    return 匹配.group(1).strip() if 匹配 else ''


def 读取预算默认值():
    内容 = 预算路径.read_text(encoding='utf-8')
    结果 = {}
    for 显示名, 字段名 in 预算映射.items():
        匹配 = re.search(rf'(?m)^\|`{字段名}`\|[^|]*\|[^|]*\|(\d+)\|$', 内容)
        if 匹配:
            结果[显示名] = int(匹配.group(1))
    return 结果


def 验证模板(内容):
    错误 = []
    运行时模板 = 提取运行时模板(内容)
    if not 运行时模板:
        return ['缺少运行时模板代码块']
    必要标题 = ['# 循环工程进度', '## 预算', '## 功能点', '## 契约增量', '## 未决事项']
    for 标题 in 必要标题:
        if 标题 not in 运行时模板:
            错误.append(f'缺少标题: {标题}')
    必要字段 = ['状态：', '开始：', '更新：', '基线：', '目标：', '停止：', '下一步：', '边界：', '用户WIP：', '常量变更：', '已完成ID：']
    for 字段 in 必要字段:
        if not re.search(rf'(?m)^{re.escape(字段)}', 运行时模板):
            错误.append(f'缺少字段: {字段}')
    基线行 = re.search(r'(?m)^基线：(.+)$', 运行时模板)
    if 基线行 and ('证据路径' not in 基线行.group(1) or '关键文件=<数量>' in 基线行.group(1)):
        错误.append('基线必须指向含文件清单和哈希的证据路径，不能只写数量')

    标题列表 = re.findall(r'(?m)^#{1,6}\s+(.+)$', 运行时模板)
    禁止词 = ['历史', '已完成', '当前决策', '日志', '执行计数', '视觉基线', '并发写者登记']
    for 标题文本 in 标题列表:
        if any(词 in 标题文本 for 词 in 禁止词):
            错误.append(f'运行时模板残留历史节: {标题文本}')

    预算匹配 = re.findall(r'(?m)^\|(总循环|子代理实例|主代理补位|墙钟/min)\|(\d+)\|(\d+)\|$', 运行时模板)
    模板预算 = {名称: (int(上限), int(当前)) for 名称, 上限, 当前 in 预算匹配}
    if set(模板预算) != set(预算映射):
        错误.append('预算行与权威预算字段不一致')
    for 名称, (上限, 当前) in 模板预算.items():
        if 当前 > 上限:
            错误.append(f'预算当前值超过上限: {当前}/{上限}')
        权威值 = 读取预算默认值().get(名称)
        if 权威值 is not None and 上限 != 权威值:
            错误.append(f'{名称}上限与BUDGET不一致: {上限}/{权威值}')

    行数 = len(运行时模板.splitlines())
    if 行数 > 55:
        错误.append(f'运行时模板过长: {行数} 行')
    return 错误


def 查找项目根():
    for 候选 in [技能根, *技能根.parents]:
        if (候选 / 'AGENTS.md').is_file() and (候选 / '.agents').is_dir():
            return 候选
    return None


def 验证运行时实例():
    项目根 = 查找项目根()
    if 项目根 is None:
        return []
    实例 = 项目根 / 'PROGRESS.md'
    if not 实例.is_file():
        return []
    内容 = 实例.read_text(encoding='utf-8')
    错误 = []
    行数 = len(内容.splitlines())
    if 行数 > 70:
        错误.append(f'运行时PROGRESS.md超过70行: {行数}')
    for 字段 in ['状态：', '目标：', '停止：', '下一步：', '边界：', '用户WIP：', '## 预算', '## 功能点']:
        if 字段 not in 内容:
            错误.append(f'运行时PROGRESS.md缺少: {字段}')
    for 标题 in re.findall(r'(?m)^#{1,6}\s+(.+)$', 内容):
        if any(词 in 标题 for 词 in ['历史', '已完成', '当前决策', '日志', '执行计数']):
            错误.append(f'运行时PROGRESS.md含历史节: {标题}')
    return 错误


def main():
    if not 模板路径.is_file() or not 预算路径.is_file():
        print('FAIL: 缺少PROGRESS模板或BUDGET权威文件')
        return 1
    内容 = 模板路径.read_text(encoding='utf-8')
    错误 = 验证模板(内容)
    if 错误:
        print('FAIL: PROGRESS模板不符合精简快照契约')
        for 项 in 错误:
            print(f'  - {项}')
        return 1

    有效模板 = 提取运行时模板(内容)
    负例 = [
        有效模板.replace('## 预算', '## 已完成'),
        有效模板.replace('## 功能点', '## 循环历史'),
        有效模板.replace('下一步：', '历史记录：'),
        有效模板.replace('|子代理实例|30|0|', '|子代理实例|999|0|'),
        有效模板.replace('|子代理实例|30|0|', '|子代理实例|3|0|'),
        有效模板.replace('基线：<版本控制短哈希+证据路径|无>', '基线：关键文件=<数量或无>'),
        有效模板 + '\n' + '\n'.join(f'历史行{i}' for i in range(20)),
    ]
    for 索引, 内容负例 in enumerate(负例, 1):
        if not 验证模板(f'## 运行时模板\n\n```markdown\n{内容负例}\n```'):
            print(f'FAIL: 负例{索引}被错误接受')
            return 1

    实例错误 = 验证运行时实例()
    if 实例错误:
        print('FAIL: 运行时PROGRESS.md违反精简快照契约')
        for 项 in 实例错误:
            print(f'  - {项}')
        return 1

    print('PASS: PROGRESS模板与运行时实例均精简，且与BUDGET一致')
    return 0


if __name__ == '__main__':
    sys.exit(main())
