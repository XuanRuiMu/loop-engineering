import subprocess
import sys
import pathlib
import shutil


def 查找可用python():
    """在某些宿主环境中，默认 python 可能返回 9009，需要 fallback。"""
    候选列表 = [sys.executable]
    候选列表.extend([shutil.which(name) for name in ['python', 'python3', 'py'] if shutil.which(name)])
    for python路径 in 候选列表:
        if not python路径:
            continue
        try:
            结果 = subprocess.run([python路径, '--version'], capture_output=True, text=True, timeout=10)
            if 结果.returncode == 0:
                return python路径
        except Exception:
            continue
    return sys.executable


python解释器 = 查找可用python()

任务根目录 = pathlib.Path(__file__).parent
任务目录列表 = sorted([d for d in 任务根目录.iterdir() if d.is_dir() and d.name.startswith('task-')])
通过数 = 0

for 任务目录 in 任务目录列表:
    验证脚本 = 任务目录 / 'verify.py'
    if not 验证脚本.exists():
        print(f"{任务目录.name}: SKIP - 缺少 verify.py")
        continue
    结果 = subprocess.run([python解释器, str(验证脚本)], capture_output=True, text=True)
    状态 = 'PASS' if 结果.returncode == 0 else 'FAIL'
    if 状态 == 'PASS':
        通过数 += 1
    输出 = 结果.stdout.strip() or 结果.stderr.strip()
    print(f"{任务目录.name}: {状态} - {输出}")

print(f"\n总计: {通过数}/{len(任务目录列表)} 通过")
sys.exit(0 if 通过数 == len(任务目录列表) else 1)
