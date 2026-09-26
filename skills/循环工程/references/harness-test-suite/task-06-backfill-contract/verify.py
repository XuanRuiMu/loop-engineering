import pathlib
import re
import sys


技能根 = pathlib.Path(__file__).resolve().parents[3]


def 验证补位契约(预算内容, 主流程内容):
    错误 = []
    字段行 = re.search(r'(?m)^\|`orchestrator_backfill_limit`\|整数\|.*\|(\d+)\|$', 预算内容)
    if not 字段行 or int(字段行.group(1)) != 3:
        错误.append('orchestrator_backfill_limit默认值不是3')
    if '达到补位上限后停止继续补位' not in 主流程内容:
        错误.append('主流程缺少停止补位动作')
    if '改派新代理' not in 主流程内容:
        错误.append('主流程缺少改派新代理动作')
    熔断区 = re.search(r'## 熔断规则(.*?)(?:\n## |\Z)', 预算内容, re.S)
    if not 熔断区 or 'orchestrator_backfill_limit' not in 熔断区.group(1):
        错误.append('BUDGET缺少补位熔断规则')
    return 错误


def 验证契约协调(文本):
    必要语义 = ['公开契约变化', '旧值到新值', '尚未被消费者吸收', '并行前扫描', '把增量注入', '立即删除']
    return [语义 for 语义 in 必要语义 if 语义 not in 文本]


def main():
    预算路径 = 技能根 / 'BUDGET.md'
    主流程路径 = 技能根 / 'SKILL.md'
    if not 预算路径.is_file() or not 主流程路径.is_file():
        print('FAIL: 缺少BUDGET.md或SKILL.md')
        return 1
    预算内容 = 预算路径.read_text(encoding='utf-8')
    主流程内容 = 主流程路径.read_text(encoding='utf-8')
    错误 = 验证补位契约(预算内容, 主流程内容)

    契约区 = re.search(r'#### 并行与契约(.*?)(?:\n#### |\n### |\Z)', 主流程内容, re.S)
    契约文本 = 契约区.group(1) if 契约区 else ''
    错误.extend(验证契约协调(契约文本))
    if 契约区 and 验证契约协调(契约文本.replace('立即删除', '以后再说')) == []:
        错误.append('契约清理负例被错误接受')

    模板内容 = (技能根 / 'references' / 'PROGRESS模板.md').read_text(encoding='utf-8')
    for 文本 in ['## 契约增量', '旧值到新值', '未吸收消费者']:
        if 文本 not in 模板内容:
            错误.append(f'PROGRESS模板缺少契约字段: {文本}')

    if 错误:
        print('FAIL: 补位熔断或契约协调语义不完整')
        for 项 in 错误:
            print(f'  - {项}')
        return 1
    print('PASS: 补位熔断与契约增量协调语义完整')
    return 0


if __name__ == '__main__':
    sys.exit(main())
