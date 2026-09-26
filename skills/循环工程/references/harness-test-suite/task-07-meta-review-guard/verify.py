import pathlib
import re
import sys


技能根 = pathlib.Path(__file__).resolve().parents[3]
主流程路径 = 技能根 / 'SKILL.md'


def 提取区段(内容, 标题):
    匹配 = re.search(rf'## {re.escape(标题)}(.*?)(?=\n## |\Z)', 内容, re.S)
    return 匹配.group(1) if 匹配 else ''


def 验证SelfHarness(区段):
    必要语义 = [
        '新的、可复现且可跨任务复用',
        '判定“没有新弱点”前必须由独立审计者复核',
        '独立反对审查',
        '用户确认',
        'python -B',
        '失败立即回滚',
    ]
    return [语义 for 语义 in 必要语义 if 语义 not in 区段]


def main():
    if not 主流程路径.is_file():
        print('FAIL: 缺少SKILL.md')
        return 1
    内容 = 主流程路径.read_text(encoding='utf-8')
    区段 = 提取区段(内容, 'Self-Harness')
    错误 = 验证SelfHarness(区段)
    if not 区段:
        错误.append('缺少Self-Harness区段')
    反向区段 = 区段.replace('判定“没有新弱点”前必须由独立审计者复核', '主代理可以直接判定没有新弱点')
    if not 验证SelfHarness(反向区段):
        错误.append('无新证据停止负例被错误接受')
    反向核心 = 区段.replace('独立反对审查', '主代理自行判断')
    if not 验证SelfHarness(反向核心):
        错误.append('核心提案独立审查负例被错误接受')

    if 错误:
        print('FAIL: Self-Harness触发和治理契约不完整')
        for 项 in 错误:
            print(f'  - {项}')
        return 1
    print('PASS: Self-Harness停止需独立复核，核心改动保持独立审查')
    return 0


if __name__ == '__main__':
    sys.exit(main())
