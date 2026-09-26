import json
import pathlib
import re
import sys


任务目录 = pathlib.Path(__file__).parent
样本目录 = 任务目录 / 'samples'
清单路径 = 任务目录 / 'cases.json'
技能根 = pathlib.Path(__file__).resolve().parents[3]
预算路径 = 技能根 / 'BUDGET.md'
字段顺序 = [
    '摘要版本', '功能点', '状态', '结果', '失败标签', '证据', '验证', '计数',
    '修改文件', '树状态', '后台任务', '审查', '遗留', '前提证伪', '契约变更', '下一步',
]
合法状态 = {'已完成', '已阻塞', '已跳过', '待用户确认'}
合法标签 = {'鉴权', '网络', '数据', '逻辑', '依赖', '未知'}


def 读取预算上限():
    内容 = 预算路径.read_text(encoding='utf-8')
    字段 = {
        'total_turn_limit': '总循环',
        'subagent_call_limit': '子代理实例',
        'per_fp_attempt_limit': '修复',
        'per_fp_stall_limit': 'stall',
    }
    结果 = {}
    for 字段名, 显示名 in 字段.items():
        匹配 = re.search(rf'(?m)^\|`{字段名}`\|[^|]*\|[^|]*\|(\d+)\|$', 内容)
        if 匹配:
            结果[显示名] = int(匹配.group(1))
    return 结果


def 查找项目根():
    for 候选 in [技能根, *技能根.parents]:
        if (候选 / '.agents' / 'evidence').is_dir():
            return 候选
    return 技能根


def 解析摘要(内容):
    字段 = []
    值 = {}
    for 行 in 内容.splitlines():
        if not 行.strip():
            continue
        if '：' not in 行:
            return None
        名称, 内容值 = 行.split('：', 1)
        字段.append(名称)
        值[名称] = 内容值.strip()
    return 字段, 值


def 验证证据(值, 项目根):
    if 值 == '无':
        return True
    if not 值 or '\\' in 值 or ':' in 值 or '|' in 值:
        return False
    路径 = pathlib.PurePosixPath(值)
    if 路径.is_absolute() or '..' in 路径.parts or not 值.startswith('.agents/evidence/'):
        return False
    类别 = 路径.parts[2] if len(路径.parts) > 2 else ''
    if 类别 not in {'traces', 'proposals', 'validations'}:
        return False
    证据根 = (项目根 / '.agents' / 'evidence').resolve()
    目标 = (项目根 / pathlib.Path(*路径.parts)).resolve()
    try:
        目标.relative_to(证据根)
    except ValueError:
        return False
    return 目标.is_file()


def 验证摘要(内容, 项目根):
    解析结果 = 解析摘要(内容)
    if 解析结果 is None:
        return ['存在无法解析的行']
    字段, 值 = 解析结果
    错误 = []
    if 字段 != 字段顺序:
        错误.append('字段集合或顺序错误')
    if 值.get('摘要版本') != '2':
        错误.append('摘要版本必须为2')
    if 值.get('状态') not in 合法状态:
        错误.append('状态值非法')
    if not re.match(r'^FP-\w+', 值.get('功能点', '')):
        错误.append('功能点必须使用FP-xx编号')
    for 名称 in 字段顺序:
        if not 值.get(名称):
            错误.append(f'字段为空: {名称}')

    标签 = 值.get('失败标签', '')
    if 标签 != '无' and (not 标签 or any(项 not in 合法标签 for 项 in 标签.split(','))):
        错误.append('失败标签非法')

    证据 = 值.get('证据', '')
    if not 验证证据(证据, 项目根):
        错误.append('证据路径不存在或越界')

    验证 = 值.get('验证', '')
    验证项 = 验证.split('；')
    if not 验证项 or not 验证项[0] in {'通过', '环境限制', '真实失败'}:
        错误.append('验证三态格式错误')
    键值 = {}
    for 项 in 验证项[1:]:
        if '=' not in 项:
            错误.append('验证键值格式错误')
            continue
        键, 内容值 = 项.split('=', 1)
        if 键 in 键值:
            错误.append(f'验证存在重复键: {键}')
        键值[键] = 内容值.strip()
    for 键 in ['命令', '目标', '结果']:
        if not 键值.get(键) or 键值[键].strip() == '无':
            错误.append(f'验证缺少有效{键}')
    if 证据 == '无' and ('命令' not in 键值 or '目标' not in 键值):
        错误.append('无证据文件时验证必须包含命令和目标')
    if 验证项 and 验证项[0] == '通过' and ('失败' in 键值.get('结果', '') or '未通过' in 键值.get('结果', '')):
        错误.append('验证三态与结果文本矛盾')

    计数 = 值.get('计数', '')
    匹配 = re.fullmatch(r'修复=(\d+);stall=(\d+);轮次=(\d+);估算=(\d+);宿主上限=(未知|\d+);嵌套=(\d+)', 计数)
    if not 匹配:
        错误.append('计数字段格式错误')
    else:
        修复, stall, 轮次, 估算, 嵌套 = int(匹配.group(1)), int(匹配.group(2)), int(匹配.group(3)), int(匹配.group(4)), int(匹配.group(6))
        上限 = 读取预算上限()
        if 修复 > 0 and stall > 0:
            错误.append('修复和stall不能同时大于0')
        if 估算 <= 0:
            错误.append('派发估算必须大于0')
        if 修复 > 上限.get('修复', 5):
            错误.append('修复次数超过BUDGET上限')
        if stall > 上限.get('stall', 2):
            错误.append('stall次数超过BUDGET上限')
        if 轮次 > 上限.get('总循环', 30):
            错误.append('轮次超过BUDGET总循环上限')
        if 嵌套 > 上限.get('子代理实例', 30):
            错误.append('嵌套代理数超过BUDGET上限')

    修改文件 = 值.get('修改文件', '')
    if 修改文件 != '无' and ('无' in [项.strip() for 项 in 修改文件.split(',')]):
        错误.append('修改文件不能把“无”与路径混列')
    if 修改文件 != '无':
        路径列表 = 修改文件.split(',')
        if len(路径列表) > 5:
            错误.append('修改文件超过5项')
        for 路径 in 路径列表:
            路径 = 路径.strip()
            纯路径 = pathlib.PurePosixPath(路径)
            if not 路径 or '\\' in 路径 or ':' in 路径 or 纯路径.is_absolute() or '..' in 纯路径.parts:
                错误.append('修改文件路径必须是相对路径')

    树状态 = 值.get('树状态', '')
    if not (树状态 == '绿' or 树状态 == '已回滚' or 树状态.startswith('红(')):
        错误.append('树状态格式错误')
    后台任务 = 值.get('后台任务', '')
    if 后台任务 not in {'无后台任务', '已回收'} and not 后台任务.startswith('存活('):
        错误.append('后台任务格式错误')
    审查 = 值.get('审查', '')
    if not (审查 == '通过' or 审查.startswith('问题(') or 审查.startswith('待主代理补位(')):
        错误.append('审查格式错误')

    遗留 = 值.get('遗留', '')
    恢复匹配 = re.search(r'(?:^|；)恢复=([^；]+)', 遗留)
    if 值.get('状态') in {'已阻塞', '待用户确认'} and (not 恢复匹配 or 恢复匹配.group(1).strip() in {'', '无'}):
        错误.append('阻塞或待确认时遗留必须包含有效恢复动作')

    if 后台任务.startswith('存活('):
        错误.append('任何返回状态都不得遗留存活后台任务')

    if 值.get('状态') == '已跳过':
        if 树状态.startswith('红('):
            错误.append('跳过状态不得把工作树留在红态')
        if 审查 != '通过':
            错误.append('跳过状态必须完成适用审查')

    if 值.get('状态') == '已完成':
        if 验证项[0] != '通过':
            错误.append('已完成但验证不是通过')
        if 树状态 != '绿':
            错误.append('已完成但树状态不是绿')
        if 后台任务 not in {'无后台任务', '已回收'}:
            错误.append('已完成但存在存活后台任务')
        if 审查 != '通过':
            错误.append('已完成但审查未通过或仍有门禁缺口')
        if 标签 != '无':
            错误.append('已完成但仍有失败标签')
    return 错误


def main():
    if not 清单路径.is_file() or not 样本目录.is_dir():
        print('FAIL: cases.json或samples目录缺失')
        return 1
    try:
        用例清单 = json.loads(清单路径.read_text(encoding='utf-8'))['cases']
    except Exception as 错误:
        print(f'FAIL: cases.json解析失败: {错误}')
        return 1

    声明文件 = {用例['file'] for 用例 in 用例清单}
    实际文件 = {路径.name for 路径 in 样本目录.glob('*.txt')}
    必须样本 = {
        'valid.txt', 'invalid_missing.txt', 'invalid_empty_count.txt', 'invalid_typo.txt',
        'invalid_missing_count.txt', 'invalid_failure_tags_bad.txt', 'invalid_evidence_prefix.txt',
        'invalid_evidence_missing.txt',
    }
    if 声明文件 != 必须样本 or 实际文件 != 必须样本 or len(用例清单) != 8:
        print(f'FAIL: 样本数量或固定集合被缩减; 声明={sorted(声明文件)}; 实际={sorted(实际文件)}')
        return 1
    if 声明文件 != 实际文件:
        print(f'FAIL: 样本声明与磁盘不一致; 声明={sorted(声明文件)}; 实际={sorted(实际文件)}')
        return 1

    项目根 = 查找项目根()
    错误列表 = []
    for 用例 in 用例清单:
        内容 = (样本目录 / 用例['file']).read_text(encoding='utf-8')
        错误 = 验证摘要(内容, 项目根)
        实际通过 = not 错误
        if 实际通过 != 用例['expected']:
            错误列表.append(f"{用例['file']}: 预期={用例['expected']} 实际={实际通过}; {错误}")

    有效内容 = (样本目录 / 'valid.txt').read_text(encoding='utf-8')
    变异 = {
        '空命令': 有效内容.replace('命令=python -B run_all.py', '命令= '),
        '零估算': 有效内容.replace('估算=10', '估算=0'),
        '无目标': 有效内容.replace('目标=固定回归任务集', '目标=无'),
        '完成态审查未通过': 有效内容.replace('审查：通过', '审查：问题(未修)'),
        '完成态有失败标签': 有效内容.replace('失败标签：无', '失败标签：鉴权'),
        '修改文件混列': 有效内容.replace('修改文件：src/example.py', '修改文件：无,src/example.py'),
        '非完成态留红和后台': 有效内容.replace('树状态：绿', '树状态：红(测试未通过)').replace('后台任务：无后台任务', '后台任务：存活(2)'),
    }
    for 名称, 内容变异 in 变异.items():
        if not 验证摘要(内容变异, 项目根):
            错误列表.append(f'内存负例被接受: {名称}')
    if 错误列表:
        print('FAIL: Worker摘要正负例契约不一致')
        for 错误 in 错误列表:
            print(f'  - {错误}')
        return 1
    print(f'PASS: Worker摘要v2的{len(用例清单)}个正负例符合契约')
    return 0


if __name__ == '__main__':
    sys.exit(main())
