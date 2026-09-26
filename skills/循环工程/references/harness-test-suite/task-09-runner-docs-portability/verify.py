import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile


套件根 = pathlib.Path(__file__).resolve().parents[1]
技能根 = pathlib.Path(__file__).resolve().parents[3]
项目技能根 = 技能根.parent
专项技能 = ['代码需求实现器', '软件测试', 'Bug修复', '三轴审查', '方案审查', '生成PRD', '纾困复盘', '会话交接']
活动文件 = [
    技能根 / 'SKILL.md', 技能根 / 'HARNESS.md', 技能根 / 'BUDGET.md',
    技能根 / 'references' / 'EnvironmentEngineering.md', 技能根 / 'references' / 'Orchestrator-Headless模式.md',
    技能根 / 'references' / '子代理提示词模板.md', 技能根 / 'references' / 'PROGRESS模板.md',
    技能根 / 'references' / '前端验证技巧.md', 技能根 / 'references' / '推理增强.md',
    套件根 / 'run_all.py',
    项目技能根 / '代码需求实现器' / 'SKILL.md',
    项目技能根 / '代码需求实现器' / '经验教训-翻译管道Bug模式.md',
    项目技能根 / '代码需求实现器' / 'references' / '和我恋爱吧项目配置.md',
    项目技能根 / '代码需求实现器' / 'references' / 'XRM项目配置.md',
    项目技能根 / '软件测试' / 'SKILL.md',
    项目技能根 / 'Bug修复' / 'SKILL.md',
    项目技能根 / 'Bug修复' / 'evals' / 'evals.json',
    项目技能根 / '三轴审查' / 'SKILL.md',
    项目技能根 / '方案审查' / 'SKILL.md',
    项目技能根 / '生成PRD' / 'SKILL.md',
    项目技能根 / '纾困复盘' / 'SKILL.md',
    项目技能根 / '会话交接' / 'SKILL.md',
]
禁止词 = [
    'AskUserQuestion', 'general_purpose_task', 'general-purpose', 'subagent_type', 'response_language',
    'Reached the maximum turn limit', 'Task工具', 'Agent工具', 'Task 子代理', 'Task调用',
    'TodoWrite', 'Read/Grep/Glob', 'SearchCodebase', '/plan模式', 'CLAUDE.md',
    'mktemp', '/setup-matt-pocock-skills', 'file:///D:', 'The model service rejected this request', 'Playwright MCP',
]


def 查找禁止词(文本):
    return [词 for 词 in 禁止词 if 词 in 文本]


def 写模拟任务(根目录, 任务, 通过=True):
    任务目录 = 根目录 / 任务['id']
    任务目录.mkdir(parents=True, exist_ok=True)
    源码 = "print('PASS: test')\n" if 通过 else "print('FAIL: test')\nimport sys\nsys.exit(1)\n"
    (任务目录 / 'verify.py').write_text(源码, encoding='utf-8')
    (任务目录 / 'README.md').write_text('# test\n', encoding='utf-8')


def 运行模拟(清单, 模拟根):
    模拟清单 = json.loads(json.dumps(清单, ensure_ascii=False))
    for 任务 in 模拟清单.get('tasks', []):
        验证路径 = 模拟根 / 任务['verify']
        if 验证路径.is_file():
            任务['sha256'] = hashlib.sha256(验证路径.read_bytes()).hexdigest()
    清单路径 = 模拟根 / 'manifest.json'
    清单路径.write_text(json.dumps(模拟清单, ensure_ascii=False, indent=2), encoding='utf-8')
    return subprocess.run(
        [sys.executable, '-B', str(模拟根 / 'run_all.py')], cwd=模拟根, capture_output=True,
        text=True, encoding='utf-8', errors='replace', timeout=30, check=False,
    )


def 验证Runner行为(原始清单):
    错误 = []
    with tempfile.TemporaryDirectory() as 临时目录:
        模拟根 = pathlib.Path(临时目录)
        shutil.copy2(套件根 / 'run_all.py', 模拟根 / 'run_all.py')
        for 任务 in 原始清单['tasks']:
            写模拟任务(模拟根, 任务)

        if 运行模拟(原始清单, 模拟根).returncode != 0:
            错误.append('完整模拟套件未通过')

        def 直接运行():
            return subprocess.run(
                [sys.executable, '-B', str(模拟根 / 'run_all.py')], cwd=模拟根, capture_output=True,
                text=True, encoding='utf-8', errors='replace', timeout=30, check=False,
            )

        首个验证 = 模拟根 / 原始清单['tasks'][0]['verify']
        正确源码 = 首个验证.read_text(encoding='utf-8')
        首个验证.write_text("print('FAIL: test')\nimport sys\nsys.exit(0)\n", encoding='utf-8')
        if 直接运行().returncode == 0:
            错误.append('verify打印FAIL但退出0仍被判通过')
        首个验证.write_text("print('PASS: changed')\n", encoding='utf-8')
        if 直接运行().returncode == 0:
            错误.append('verify内容变化但哈希未更新仍成功')
        首个验证.write_text(正确源码, encoding='utf-8')
        缩减 = {'schema_version': 1, 'tasks': 原始清单['tasks'][:1]}
        if 运行模拟(缩减, 模拟根).returncode == 0:
            错误.append('同步缩减任务后仍成功')
        额外 = dict(原始清单)
        额外任务 = dict(原始清单['tasks'][-1])
        额外任务['id'] = 'task-88-extra'
        额外任务['verify'] = 'task-88-extra/verify.py'
        额外任务['readme'] = 'task-88-extra/README.md'
        额外['tasks'] = 原始清单['tasks'] + [额外任务]
        写模拟任务(模拟根, 额外任务)
        if 运行模拟(额外, 模拟根).returncode == 0:
            错误.append('同步扩张任务后仍成功')
        shutil.rmtree(模拟根 / 'task-88-extra')

        别名 = json.loads(json.dumps(原始清单))
        for 任务 in 别名['tasks']:
            任务['verify'] = 'task-01-progress-md/verify.py'
            任务['readme'] = 'task-01-progress-md/README.md'
        if 运行模拟(别名, 模拟根).returncode == 0:
            错误.append('任务脚本别名后仍成功')

        首个 = 模拟根 / 原始清单['tasks'][0]['id']
        shutil.rmtree(首个)
        if 运行模拟(原始清单, 模拟根).returncode == 0:
            错误.append('删除任务后仍成功')
        写模拟任务(模拟根, 原始清单['tasks'][0])
        空清单 = {'schema_version': 1, 'tasks': []}
        if 运行模拟(空清单, 模拟根).returncode == 0:
            错误.append('空任务清单仍成功')
        (模拟根 / 'task-99-extra').mkdir()
        if 运行模拟(原始清单, 模拟根).returncode == 0:
            错误.append('未登记任务仍成功')
        shutil.rmtree(模拟根 / 'task-99-extra')
        (首个 / 'verify.py').unlink()
        if 运行模拟(原始清单, 模拟根).returncode == 0:
            错误.append('缺少verify.py仍成功')
        写模拟任务(模拟根, 原始清单['tasks'][0])
        写模拟任务(模拟根, 原始清单['tasks'][1], 通过=False)
        if 运行模拟(原始清单, 模拟根).returncode == 0:
            错误.append('子任务失败仍成功')
    return 错误


def main():
    错误 = []
    for 路径 in 活动文件:
        if not 路径.is_file():
            错误.append(f'缺少活动文件: {路径}')
            continue
        命中 = 查找禁止词(路径.read_text(encoding='utf-8'))
        if 命中:
            错误.append(f'{路径} 含固定宿主词: {命中}')

    证据内容 = (技能根 / 'EVIDENCE.md').read_text(encoding='utf-8')
    当前证据 = 证据内容.split('## 2026-09-25 跨宿主与精简状态优化', 1)[-1]
    历史命中 = 查找禁止词(当前证据)
    if 历史命中:
        错误.append(f'EVIDENCE当前证据区含固定宿主词: {历史命中}')

    for 技能名 in 专项技能:
        路径 = 项目技能根 / 技能名 / 'SKILL.md'
        内容 = 路径.read_text(encoding='utf-8')
        if 'headless_mode=true' not in 内容:
            错误.append(f'{技能名} 缺少headless_mode=true')
        if '不支持Headless' in 内容 or '禁用 `headless_mode=true`' in 内容:
            错误.append(f'{技能名} 存在否定Headless的语句')

    主流程内容 = (技能根 / 'SKILL.md').read_text(encoding='utf-8')
    组合区 = re.search(r'## 专项 Skill 组合(.*?)(?=\n## |\Z)', 主流程内容, re.S)
    登记技能 = set()
    if 组合区:
        for 行 in 组合区.group(1).splitlines():
            if not 行.startswith('|') or '场景' in 行 or set(行.replace('|', '').strip()) <= {'-', ':'}:
                continue
            单元 = [项.strip().strip('`') for 项 in 行.strip('|').split('|')]
            if len(单元) >= 2 and 单元[1]:
                登记技能.add(单元[1])
    if 登记技能 != set(专项技能):
        错误.append(f'SKILL组合表与Headless检查名单不一致: {sorted(登记技能)}')

    必要区段 = {
        技能根 / 'SKILL.md': ['## 不可破坏的规则', '## 跨宿主能力适配', '## Self-Harness'],
        技能根 / 'references' / '子代理提示词模板.md': ['## 返回约束', '## Worker 返回格式 v2'],
        技能根 / 'references' / 'EnvironmentEngineering.md': ['### 高危操作', '## 5. 用户交互'],
        技能根 / 'BUDGET.md': ['## 预算字段', '## 熔断规则', '## 能力降级'],
        技能根 / 'references' / '推理增强.md': ['## 三道推理门', '## 决策卡', '## 禁止做法'],
    }
    for 路径, 区段列表 in 必要区段.items():
        内容 = 路径.read_text(encoding='utf-8')
        for 区段 in 区段列表:
            if 区段 not in 内容:
                错误.append(f'{路径.name} 缺少区段: {区段}')
    规则区 = re.search(r'## 不可破坏的规则(.*?)(?=\n## |\Z)', 主流程内容, re.S)
    核心语义 = ['状态极简', '单写者', '用户WIP保护', '高危操作提醒', '可验证完成', '修复阶梯', 'stall分类', '防假完成', '嵌套代理计数', '独立性不可伪造', '推理门']
    for 语义 in 核心语义:
        if not 规则区 or 语义 not in 规则区.group(1):
            错误.append(f'SKILL核心规则缺少: {语义}')
    提示词内容 = (技能根 / 'references' / '子代理提示词模板.md').read_text(encoding='utf-8')
    if re.search(r'第\s*3\s*[、,，]\s*4\s*次|第\s*5\s*次|第五次', 主流程内容 + 提示词内容):
        错误.append('主流程或Worker模板硬编码修复次数，应以BUDGET字段为权威')
    预算内容 = (技能根 / 'BUDGET.md').read_text(encoding='utf-8')
    熔断区 = re.search(r'## 熔断规则(.*?)(?:\n## |\Z)', 预算内容, re.S)
    熔断行数 = len([行 for 行 in 熔断区.group(1).splitlines() if 行.startswith('|')]) - 1 if 熔断区 else 0
    if 熔断行数 < 8:
        错误.append(f'BUDGET熔断规则不足8条: {熔断行数}')

    if not 查找禁止词(''.join(禁止词)):
        错误.append('禁止词检测器自检失败')

    清单 = json.loads((套件根 / 'manifest.json').read_text(encoding='utf-8'))
    错误.extend(验证Runner行为(清单))
    任务编号 = [任务['id'] for 任务 in 清单['tasks']]
    README = (套件根 / 'README.md').read_text(encoding='utf-8')
    for 编号 in 任务编号:
        if README.count(编号) != 1:
            错误.append(f'README中的任务{编号}出现次数不是1')
    if 'python -B references/harness-test-suite/run_all.py' not in README:
        错误.append('README缺少项目根全量运行命令')
    if 'manifest.json' not in README:
        错误.append('README未声明固定任务清单')

    if 错误:
        print('FAIL: 跨宿主中立性或套件文档契约不合规')
        for 项 in 错误:
            print(f'  - {项}')
        return 1
    print('PASS: 活动Skill跨宿主中立，8个专项支持Headless，runner与README防漂移')
    return 0


if __name__ == '__main__':
    sys.exit(main())
