import hashlib
import json
import pathlib
import sys


套件根 = pathlib.Path(__file__).resolve().parents[1]
技能根 = pathlib.Path(__file__).resolve().parents[3]
清单路径 = 套件根 / 'manifest.json'
预期任务 = {
    'task-01-progress-md', 'task-02-subagent-summary', 'task-03-skill-structure',
    'task-04-evidence-structure', 'task-05-subagent-output-format', 'task-06-backfill-contract',
    'task-07-meta-review-guard', 'task-08-permission-risk-guards', 'task-09-runner-docs-portability',
    'task-10-reasoning-enhancement',
}


def main():
    错误 = []
    核心文件 = [
        技能根 / 'SKILL.md', 技能根 / 'HARNESS.md', 技能根 / 'BUDGET.md', 技能根 / 'EVIDENCE.md',
        技能根 / 'references' / 'PROGRESS模板.md', 技能根 / 'references' / '子代理提示词模板.md',
        技能根 / 'references' / 'EnvironmentEngineering.md', 技能根 / 'references' / 'Orchestrator-Headless模式.md',
        技能根 / 'references' / '前端验证技巧.md', 技能根 / 'references' / '推理增强.md',
    ]
    for 路径 in 核心文件:
        if not 路径.is_file():
            错误.append(f'缺少核心文件: {路径.name}')

    if not 清单路径.is_file():
        错误.append('缺少manifest.json')
    else:
        try:
            清单 = json.loads(清单路径.read_text(encoding='utf-8'))
            任务列表 = 清单.get('tasks', [])
            清单任务 = {任务.get('id') for 任务 in 任务列表}
            if len(任务列表) != 10:
                错误.append(f'manifest任务数不是10: {len(任务列表)}')
            if 清单任务 != 预期任务:
                错误.append(f'manifest任务集合错误: {sorted(清单任务)}')
            for 任务 in 任务列表:
                for 键 in ['verify', 'readme']:
                    相对路径 = pathlib.Path(任务.get(键, ''))
                    if 相对路径.is_absolute() or '..' in 相对路径.parts:
                        错误.append(f"{任务.get('id')} 的{键}路径不安全")
                        continue
                    路径 = (套件根 / 相对路径).resolve()
                    try:
                        路径.resolve().relative_to(套件根.resolve())
                    except ValueError:
                        错误.append(f"{任务.get('id')} 的{键}路径越界")
                        continue
                    if not 路径.is_file():
                        错误.append(f"{任务.get('id')} 缺少{键}: {任务.get(键)}")
                    if 键 == 'verify' and 路径.is_file():
                        实际哈希 = hashlib.sha256(路径.read_bytes()).hexdigest()
                        if 任务.get('sha256') != 实际哈希:
                            错误.append(f"{任务.get('id')} 的verify.py哈希与manifest不一致")
        except Exception as 异常:
            错误.append(f'manifest解析失败: {异常}')

    实际任务 = {路径.name for 路径 in 套件根.iterdir() if 路径.is_dir() and 路径.name.startswith('task-')}
    if 实际任务 != 预期任务:
        错误.append(f'实际任务集合与固定清单不一致: {sorted(实际任务)}')

    if 错误:
        print('FAIL: Skill结构或固定任务清单不合规')
        for 项 in 错误:
            print(f'  - {项}')
        return 1
    print('PASS: Skill核心文件与10项固定任务清单一致')
    return 0


if __name__ == '__main__':
    sys.exit(main())
