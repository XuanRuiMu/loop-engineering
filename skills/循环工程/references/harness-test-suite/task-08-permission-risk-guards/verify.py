import pathlib
import re
import sys


技能根 = pathlib.Path(__file__).resolve().parents[3]
环境路径 = 技能根 / 'references' / 'EnvironmentEngineering.md'
主流程路径 = 技能根 / 'SKILL.md'


def 提取权限区(内容):
    匹配 = re.search(r'## 2\. 权限与风险(.*?)(?=\n## 3\. |\Z)', 内容, re.S)
    return 匹配.group(1) if 匹配 else ''


def 验证权限契约(区段):
    矛盾语句 = ['默认只允许访问白名单路径', '禁止读取版本控制目录', '权限默认禁止所有路径']
    必要语义 = [
        '默认拥有完成当前任务所需的最高项目权限',
        '不设置白名单或黑名单',
        '不等于突破宿主沙箱',
        '最小权限原则',
        '用户WIP',
        '高危操作',
        '要做什么',
        '为什么做',
        '可能影响',
        '如何恢复',
        '普通项目开发',
    ]
    错误 = [语义 for 语义 in 必要语义 if 语义 not in 区段]
    错误.extend(f'存在矛盾权限语句: {语句}' for 语句 in 矛盾语句 if 语句 in 区段)
    if re.search(r'(默认|一律).{0,10}(禁止|只允许).{0,10}(访问|读取|路径)', 区段):
        错误.append('存在同义形式的默认禁止权限语句')
    return 错误


def main():
    if not 环境路径.is_file() or not 主流程路径.is_file():
        print('FAIL: 缺少权限规范或主流程')
        return 1
    环境内容 = 环境路径.read_text(encoding='utf-8')
    主流程内容 = 主流程路径.read_text(encoding='utf-8')
    区段 = 提取权限区(环境内容)
    错误 = 验证权限契约(区段)
    if not 区段:
        错误.append('缺少权限与风险区段')
    if 验证权限契约(区段.replace('默认拥有完成当前任务所需的最高项目权限', '默认只允许访问白名单路径')) == []:
        错误.append('默认高权限负例被错误接受')
    if 验证权限契约(区段.replace('如何恢复', '无需说明恢复')) == []:
        错误.append('高危恢复说明负例被错误接受')
    if '高危操作提醒' not in 主流程内容:
        错误.append('SKILL缺少高危操作提醒规则')
    if '.git/' in 主流程内容 and '禁止读取' in 主流程内容:
        错误.append('SKILL仍把版本控制目录作为读取黑名单')

    if 错误:
        print('FAIL: 默认最高权限与高危提醒契约不合规')
        for 项 in 错误:
            print(f'  - {项}')
        return 1
    print('PASS: 默认最高权限、用户WIP保护和高危通俗提醒均已声明')
    return 0


if __name__ == '__main__':
    sys.exit(main())
