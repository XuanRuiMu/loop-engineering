import hashlib
import json
import os
import pathlib
import subprocess
import sys


预期任务 = {
    'task-01-progress-md': ('task-01-progress-md/verify.py', 'task-01-progress-md/README.md'),
    'task-02-subagent-summary': ('task-02-subagent-summary/verify.py', 'task-02-subagent-summary/README.md'),
    'task-03-skill-structure': ('task-03-skill-structure/verify.py', 'task-03-skill-structure/README.md'),
    'task-04-evidence-structure': ('task-04-evidence-structure/verify.py', 'task-04-evidence-structure/README.md'),
    'task-05-subagent-output-format': ('task-05-subagent-output-format/verify.py', 'task-05-subagent-output-format/README.md'),
    'task-06-backfill-contract': ('task-06-backfill-contract/verify.py', 'task-06-backfill-contract/README.md'),
    'task-07-meta-review-guard': ('task-07-meta-review-guard/verify.py', 'task-07-meta-review-guard/README.md'),
    'task-08-permission-risk-guards': ('task-08-permission-risk-guards/verify.py', 'task-08-permission-risk-guards/README.md'),
    'task-09-runner-docs-portability': ('task-09-runner-docs-portability/verify.py', 'task-09-runner-docs-portability/README.md'),
    'task-10-reasoning-enhancement': ('task-10-reasoning-enhancement/verify.py', 'task-10-reasoning-enhancement/README.md'),
}


def 配置输出():
    for 流 in [sys.stdout, sys.stderr]:
        if hasattr(流, 'reconfigure'):
            流.reconfigure(encoding='utf-8', errors='replace')


def 在根目录内(根目录, 目标):
    try:
        目标.resolve().relative_to(根目录.resolve())
        return True
    except ValueError:
        return False


def 读取任务清单():
    清单路径 = pathlib.Path(__file__).resolve().parent / 'manifest.json'
    if not 清单路径.is_file():
        raise RuntimeError(f'缺少固定任务清单: {清单路径.name}')
    数据 = json.loads(清单路径.read_text(encoding='utf-8'))
    if 数据.get('schema_version') != 1:
        raise RuntimeError('manifest.json 的 schema_version 必须为 1')
    任务列表 = 数据.get('tasks')
    if not isinstance(任务列表, list):
        raise RuntimeError('manifest.json 的 tasks 必须是数组')
    if len(任务列表) != len(预期任务):
        raise RuntimeError(f'固定任务数必须为{len(预期任务)}，实际为{len(任务列表)}')
    任务编号 = [任务.get('id') for 任务 in 任务列表]
    if len(任务编号) != len(set(任务编号)):
        raise RuntimeError('manifest.json 包含重复任务编号')
    if set(任务编号) != set(预期任务):
        raise RuntimeError('manifest.json 的任务集合与固定清单不一致')
    return 任务列表


def 解析套件内路径(套件根, 相对路径, 任务编号):
    if not isinstance(相对路径, str) or not 相对路径:
        raise RuntimeError(f'{任务编号} 的路径为空')
    路径 = pathlib.Path(相对路径)
    if 路径.is_absolute() or '..' in 路径.parts:
        raise RuntimeError(f'{任务编号} 的路径不安全: {相对路径}')
    解析后 = (套件根 / 路径).resolve()
    if not 在根目录内(套件根, 解析后):
        raise RuntimeError(f'{任务编号} 的路径越出套件目录: {相对路径}')
    return 解析后


def 预检任务(套件根, 任务列表):
    实际编号 = {目录.name for 目录 in 套件根.iterdir() if 目录.is_dir() and 目录.name.startswith('task-')}
    if 实际编号 != set(预期任务):
        缺少 = sorted(set(预期任务) - 实际编号)
        多余 = sorted(实际编号 - set(预期任务))
        raise RuntimeError(f'任务目录与固定集合不一致; 缺少={缺少}; 多余={多余}')
    for 任务 in 任务列表:
        编号 = 任务['id']
        预期验证, 预期说明 = 预期任务[编号]
        if 任务.get('verify') != 预期验证 or 任务.get('readme') != 预期说明:
            raise RuntimeError(f'{编号} 的verify或readme路径与固定映射不一致')
        验证脚本 = 解析套件内路径(套件根, 任务['verify'], 编号)
        说明文件 = 解析套件内路径(套件根, 任务['readme'], 编号)
        if not 验证脚本.is_file():
            raise RuntimeError(f'{编号} 缺少 verify.py')
        if not 说明文件.is_file():
            raise RuntimeError(f'{编号} 缺少 README.md')
        实际哈希 = hashlib.sha256(验证脚本.read_bytes()).hexdigest()
        if 任务.get('sha256') != 实际哈希:
            raise RuntimeError(f'{编号} 的verify.py哈希与manifest不一致')
    return len(预期任务)


def 主函数():
    配置输出()
    套件根 = pathlib.Path(__file__).resolve().parent
    try:
        任务列表 = 读取任务清单()
        总任务数 = 预检任务(套件根, 任务列表)
    except Exception as 错误:
        print(f'预检失败: {错误}')
        return 1

    环境 = os.environ.copy()
    环境['PYTHONIOENCODING'] = 'utf-8'
    环境['PYTHONDONTWRITEBYTECODE'] = '1'
    通过数 = 0
    for 任务 in 任务列表:
        验证脚本 = 解析套件内路径(套件根, 任务['verify'], 任务['id'])
        超时 = False
        try:
            结果 = subprocess.run(
                [sys.executable, '-B', str(验证脚本)],
                cwd=套件根,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60,
                env=环境,
                check=False,
            )
            输出 = f'{结果.stdout}\n{结果.stderr}'
            状态 = 'PASS' if 结果.returncode == 0 and 'PASS:' in 输出 and 'FAIL:' not in 输出 else 'FAIL'
        except subprocess.TimeoutExpired:
            状态 = 'FAIL'
            超时 = True
            结果 = None
        except OSError as 错误:
            状态 = 'FAIL'
            print(f'{任务["id"]}: 无法启动 - {错误}')
            结果 = None

        if 状态 == 'PASS':
            通过数 += 1
        print(f"{任务['id']}: {状态}")
        if 结果 is not None:
            if 结果.stdout.strip():
                print(结果.stdout.rstrip())
            if 结果.stderr.strip():
                print(结果.stderr.rstrip())
        elif 超时:
            print('子任务超过60秒未完成')

    print(f'\n总计: {通过数}/{总任务数} 通过')
    return 0 if 通过数 == 总任务数 else 1


if __name__ == '__main__':
    sys.exit(主函数())
